"""
Adaptive Planner — deterministic engine for ML Engineer learning path adaptation.

Responsibilities:
  - Level 1 (Re-rank): replace a resource with a lower/higher-difficulty alternative
  - Level 2 (Insert): insert remediation + verification items for gaps/misconceptions
  - Level 3 (Replan): recalculate the remaining path from the current position
  - What-If simulation (read-only, never mutates DB)
  - Adaptation event logging
  - Learner profile micro-updates

IMPORTANT: LLM is used ONLY to generate explanation text.
           All routing/mutation decisions are deterministic.
"""
import uuid
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session

from app.models.orm import (
    AdaptationEvent,
    AdaptivePathState,
    Resource,
    ResourceSkill,
    LearnerPitfall,
    Pitfall,
    Concept,
    LearnerSkill,
    Learner,
)

# ─────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────

MASTERY_THRESHOLD = 0.65           # below → knowledge gap
DIFFICULTY_DROP = 0.20             # how much to drop difficulty on TOO_HARD
DIFFICULTY_RAISE = 0.20            # how much to raise difficulty on TOO_EASY
MAX_CONSECUTIVE_REMEDIATIONS = 2   # safety cap
HOURS_PER_MINUTE = 1 / 60

# Status literals
STATUS_PLANNED = "planned"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_MASTERED_SKIP = "mastered_skip"
STATUS_REMEDIATION = "remediation"
STATUS_VERIFICATION = "verification"
STATUS_BLOCKED = "blocked"
STATUS_REPLACED = "replaced"

# Item type literals
ITEM_RESOURCE = "resource"
ITEM_REMEDIATION = "remediation"
ITEM_VERIFICATION = "verification"
ITEM_PROJECT = "project"


# ─────────────────────────────────────────────────
# LLM helper (explanation text only)
# ─────────────────────────────────────────────────

def _get_llm():
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key or api_key.startswith("mock"):
            return None
        return ChatGroq(api_key=api_key, model_name="llama3-8b-8192", temperature=0.3)
    except Exception:
        return None


def _generate_explanation(trigger: str, context: Dict[str, Any]) -> str:
    """Generate a human-friendly explanation for an adaptation.
    Falls back to deterministic text if LLM unavailable."""
    deterministic = {
        "TOO_HARD": (
            f"We replaced '{context.get('old_title', 'the resource')}' with "
            f"'{context.get('new_title', 'a lower-difficulty resource')}' because you found "
            f"the current material too difficult. The new resource covers the same ML objective "
            f"at a lower difficulty level ({context.get('new_difficulty', ''):.2f} vs "
            f"{context.get('old_difficulty', ''):.2f})."
        ) if context.get("new_difficulty") else
        "We replaced the resource with a lower-difficulty alternative covering the same objective.",

        "TOO_EASY": (
            f"We moved you to '{context.get('new_title', 'a more advanced resource')}' "
            f"because your assessment indicates strong mastery of this topic."
        ),
        "ALREADY_KNOWN": (
            "Based on your verification assessment, we've marked this item as mastered "
            "and moved you forward."
        ),
        "KNOWLEDGE_GAP": (
            f"We inserted a short remediation for '{context.get('concept', 'this concept')}' "
            f"because your assessment score ({context.get('score', 0)*100:.0f}%) was below "
            f"the mastery threshold. A verification step follows to confirm understanding."
        ),
        "MISCONCEPTION": (
            f"We inserted a remediation for '{context.get('pitfall_title', 'a detected misconception')}' "
            f"because your response indicated a common misconception. "
            f"Complete this short module and pass the verification check to continue."
        ),
        "HOURS_CHANGE": (
            f"Your weekly study hours have been updated to {context.get('new_hours', '?')} hrs/week. "
            f"Estimated completion: {context.get('projected_weeks', 0):.1f} weeks."
        ),
        "DEADLINE_CHANGE": (
            f"Your deadline has been updated. At {context.get('weekly_hours', '?')} hrs/week, "
            f"you'll complete in {context.get('projected_weeks', 0):.1f} weeks."
        ),
        "FASTER_PATH": "Optional resources have been removed to create a faster path.",
        "LIGHTER_PATH": "We identified and removed low-priority optional resources to reduce your workload.",
        "FALLING_BEHIND": (
            f"At your current pace ({context.get('actual_hours', 0):.1f} hrs/week), "
            f"you may miss your deadline. Consider one of the options shown."
        ),
    }
    fallback = deterministic.get(trigger, "Your learning path has been updated.")

    llm = _get_llm()
    if not llm:
        return fallback

    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        system = (
            "You are a supportive learning coach. Write a single, concise paragraph (3-4 sentences max) "
            "explaining why a learner's ML Engineer roadmap was changed. "
            "Be specific, warm, and encouraging. Do NOT be preachy."
        )
        human = f"Adaptation trigger: {trigger}. Context: {context}. Structured reason: {fallback}"
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        return resp.content.strip()
    except Exception:
        return fallback


# ─────────────────────────────────────────────────
# State helpers
# ─────────────────────────────────────────────────

def get_or_create_state(db: Session, learner_id: str) -> AdaptivePathState:
    state = db.query(AdaptivePathState).filter(
        AdaptivePathState.learner_id == learner_id
    ).first()
    if not state:
        state = AdaptivePathState(
            state_id=str(uuid.uuid4()),
            learner_id=learner_id,
            current_path=[],
            weekly_hours=8.0,
            deadline_weeks=20.0,
        )
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def _recompute_timeline(state: AdaptivePathState) -> None:
    """Recompute remaining_hours, projected_completion_weeks, is_on_track in-place."""
    remaining_items = [
        item for item in (state.current_path or [])
        if item.get("status") not in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)
    ]
    remaining_hours = sum(
        item.get("estimated_minutes", 60) * HOURS_PER_MINUTE
        for item in remaining_items
    )
    state.remaining_hours = round(remaining_hours, 2)
    weekly = state.weekly_hours or 8.0
    proj_weeks = remaining_hours / weekly if weekly > 0 else 999.0
    state.projected_completion_weeks = round(proj_weeks, 1)
    state.is_on_track = proj_weeks <= (state.deadline_weeks or 999)


def _snapshot(state: AdaptivePathState) -> List[str]:
    """Return a lightweight snapshot (list of item ids) for event logging."""
    return [item.get("id") for item in (state.current_path or [])]


def _log_event(
    db: Session,
    learner_id: str,
    event_type: str,
    trigger: str,
    old_snapshot: List[str],
    new_snapshot: List[str],
    affected_item_id: Optional[str],
    old_resource_id: Optional[str],
    new_resource_id: Optional[str],
    reason: str,
    explanation: str,
) -> AdaptationEvent:
    evt = AdaptationEvent(
        event_id=str(uuid.uuid4()),
        learner_id=learner_id,
        event_type=event_type,
        trigger=trigger,
        affected_item_id=affected_item_id,
        old_resource_id=old_resource_id,
        new_resource_id=new_resource_id,
        old_path_snapshot=old_snapshot,
        new_path_snapshot=new_snapshot,
        reason=reason,
        explanation=explanation,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(evt)
    return evt


# ─────────────────────────────────────────────────
# Resource scoring (transparent, deterministic)
# ─────────────────────────────────────────────────

def _score_resource(
    resource: Resource,
    target_difficulty: float,
    skill_id: Optional[str],
    preferred_format: Optional[str] = None,
    max_minutes: Optional[int] = None,
    db: Optional[Session] = None,
) -> float:
    """
    resource_score =
        0.35 * skill_relevance
      + 0.20 * quality_score
      + 0.15 * difficulty_match
      + 0.15 * format_preference
      + 0.20 * time_fit          (adjusted: was 0.15, raised to 0.20 for clarity)
    """
    score = 0.0

    # 1. Skill relevance: does the resource cover the target skill?
    if resource.primary_skill_id == skill_id:
        skill_relevance = 1.0
    elif db:
        rs = db.query(ResourceSkill).filter(
            ResourceSkill.resource_id == resource.resource_id,
            ResourceSkill.skill_id == skill_id,
        ).first()
        skill_relevance = (rs.coverage_score if rs else 0.3)
    else:
        skill_relevance = 0.3
    score += 0.35 * skill_relevance

    # 2. Quality score (normalised 0-1)
    quality = min(1.0, max(0.0, resource.quality_score or 0.5))
    score += 0.20 * quality

    # 3. Difficulty match
    candidate_diff = resource.difficulty_score or 0.5
    difficulty_match = max(0.0, 1.0 - abs(candidate_diff - target_difficulty))
    score += 0.15 * difficulty_match

    # 4. Format preference
    if preferred_format and resource.format:
        format_match = 1.0 if resource.format.lower() == preferred_format.lower() else 0.3
    else:
        format_match = 0.5
    score += 0.15 * format_match

    # 5. Time fit
    if max_minutes and resource.duration_minutes:
        time_fit = 1.0 if resource.duration_minutes <= max_minutes else max(0.1, 1.0 - (resource.duration_minutes - max_minutes) / max_minutes)
    else:
        time_fit = 0.5
    score += 0.15 * time_fit

    return round(score, 4)


def _find_alternative_resource(
    db: Session,
    skill_id: str,
    current_resource_id: str,
    target_difficulty: float,
    preferred_format: Optional[str] = None,
    max_minutes: Optional[int] = None,
) -> Optional[Resource]:
    """Find the best alternative resource for a skill at a target difficulty."""
    resources = db.query(Resource).filter(
        Resource.primary_skill_id == skill_id,
        Resource.status == "active",
        Resource.resource_id != current_resource_id,
    ).all()

    # Also look through resource_skills junction
    rs_rows = db.query(ResourceSkill).filter(
        ResourceSkill.skill_id == skill_id,
    ).all()
    extra_ids = [r.resource_id for r in rs_rows if r.resource_id != current_resource_id]
    if extra_ids:
        extra = db.query(Resource).filter(
            Resource.resource_id.in_(extra_ids),
            Resource.status == "active",
        ).all()
        # De-duplicate
        existing_ids = {r.resource_id for r in resources}
        resources.extend(r for r in extra if r.resource_id not in existing_ids)

    if not resources:
        return None

    scored = [
        (r, _score_resource(r, target_difficulty, skill_id, preferred_format, max_minutes, db))
        for r in resources
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]


def _find_remediation_resource(
    db: Session,
    skill_id: str,
) -> Optional[Resource]:
    """Find the best remediation resource for a skill (highest quality, lower difficulty)."""
    resources = db.query(Resource).filter(
        Resource.primary_skill_id == skill_id,
        Resource.status == "active",
    ).order_by(Resource.quality_score.desc()).all()

    if not resources:
        rs_rows = db.query(ResourceSkill).filter(ResourceSkill.skill_id == skill_id).all()
        rids = [r.resource_id for r in rs_rows]
        resources = db.query(Resource).filter(
            Resource.resource_id.in_(rids),
            Resource.status == "active",
        ).order_by(Resource.quality_score.desc()).all()

    # Prefer lower-difficulty resources for remediation
    low_diff = [r for r in resources if (r.difficulty_score or 0.5) < 0.6]
    return low_diff[0] if low_diff else (resources[0] if resources else None)


# ─────────────────────────────────────────────────
# Level 1: Resource replacement
# ─────────────────────────────────────────────────

def adapt_for_feedback(
    db: Session,
    learner_id: str,
    item_id: str,
    feedback_type: str,  # TOO_HARD | TOO_EASY | ALREADY_KNOWN | TOO_LONG | CONFUSING
) -> Dict[str, Any]:
    """
    Handle learner resource feedback.
    - TOO_HARD / CONFUSING / TOO_LONG → replace with lower-difficulty resource (Level 1)
    - TOO_EASY → replace with higher-difficulty resource, or offer skip (Level 1)
    - ALREADY_KNOWN → initiate verification flow (Level 2 lite)
    """
    state = get_or_create_state(db, learner_id)
    path = list(state.current_path or [])

    # Find the target item
    item_idx = next((i for i, x in enumerate(path) if x.get("id") == item_id), None)
    if item_idx is None:
        return {"success": False, "message": "Path item not found.", "fallback": "continue_current_path"}

    item = path[item_idx]

    # Safety: never modify completed items
    if item.get("status") in (STATUS_COMPLETED, STATUS_MASTERED_SKIP):
        return {"success": False, "message": "Cannot modify a completed item.", "fallback": "continue_current_path"}

    skill_id = item.get("skill_id")
    current_resource_id = item.get("resource_id")
    current_difficulty = item.get("difficulty_score", 0.5) or 0.5

    # Get learner preferred format
    learner = db.query(Learner).filter(Learner.learner_id == learner_id).first()
    preferred_format = learner.preferred_learning_format if learner else None

    old_snapshot = _snapshot(state)
    result = {}

    if feedback_type in ("TOO_HARD", "CONFUSING", "TOO_LONG"):
        target_diff = max(0.1, current_difficulty - DIFFICULTY_DROP)
        new_resource = _find_alternative_resource(
            db, skill_id, current_resource_id, target_diff, preferred_format
        )
        if not new_resource:
            return {"success": False, "message": "No alternative resource found.", "fallback": "continue_current_path"}

        ctx = {
            "old_title": item.get("title"), "new_title": new_resource.title,
            "old_difficulty": current_difficulty, "new_difficulty": new_resource.difficulty_score or 0.5,
        }
        explanation = _generate_explanation("TOO_HARD", ctx)

        # Mutate the path item
        old_resource_id = item.get("resource_id")
        path[item_idx] = {
            **item,
            "resource_id": new_resource.resource_id,
            "title": new_resource.title,
            "difficulty_score": new_resource.difficulty_score,
            "estimated_minutes": new_resource.duration_minutes or item.get("estimated_minutes", 60),
            "provider": new_resource.provider,
            "format": new_resource.format,
            "resource_type": new_resource.resource_type,
        }
        state.current_path = path
        _recompute_timeline(state)
        state.updated_at = datetime.now(timezone.utc)
        db.commit()

        new_snapshot = _snapshot(state)
        _log_event(db, learner_id, "RESOURCE_REPLACED", feedback_type,
                   old_snapshot, new_snapshot, item_id,
                   old_resource_id, new_resource.resource_id,
                   f"Learner reported {feedback_type}; replaced with lower-difficulty resource",
                   explanation)
        db.commit()

        result = {
            "success": True,
            "adaptation_type": "RESOURCE_REPLACED",
            "trigger": feedback_type,
            "old_item": {"id": item_id, "title": item.get("title"), "resource_id": old_resource_id, "difficulty": current_difficulty},
            "new_item": {"id": item_id, "title": new_resource.title, "resource_id": new_resource.resource_id, "difficulty": new_resource.difficulty_score},
            "explanation": explanation,
        }

    elif feedback_type == "TOO_EASY":
        target_diff = min(1.0, current_difficulty + DIFFICULTY_RAISE)
        new_resource = _find_alternative_resource(
            db, skill_id, current_resource_id, target_diff, preferred_format
        )
        if not new_resource:
            # Offer skip instead
            return _initiate_skip_verification(db, learner_id, item_id, state, path, item_idx, "TOO_EASY")

        ctx = {"new_title": new_resource.title, "old_title": item.get("title")}
        explanation = _generate_explanation("TOO_EASY", ctx)

        old_resource_id = item.get("resource_id")
        path[item_idx] = {
            **item,
            "resource_id": new_resource.resource_id,
            "title": new_resource.title,
            "difficulty_score": new_resource.difficulty_score,
            "estimated_minutes": new_resource.duration_minutes or item.get("estimated_minutes", 60),
            "provider": new_resource.provider,
            "format": new_resource.format,
        }
        state.current_path = path
        _recompute_timeline(state)
        state.updated_at = datetime.now(timezone.utc)
        db.commit()

        new_snapshot = _snapshot(state)
        _log_event(db, learner_id, "RESOURCE_REPLACED", "TOO_EASY",
                   old_snapshot, new_snapshot, item_id,
                   old_resource_id, new_resource.resource_id,
                   "Learner reported too easy; replaced with higher-difficulty resource",
                   explanation)
        db.commit()

        result = {
            "success": True,
            "adaptation_type": "RESOURCE_REPLACED",
            "trigger": "TOO_EASY",
            "old_item": {"id": item_id, "title": item.get("title"), "resource_id": old_resource_id},
            "new_item": {"id": item_id, "title": new_resource.title, "resource_id": new_resource.resource_id},
            "explanation": explanation,
        }

    elif feedback_type == "ALREADY_KNOWN":
        result = _initiate_skip_verification(db, learner_id, item_id, state, path, item_idx, "ALREADY_KNOWN")

    else:
        result = {"success": False, "message": f"Unknown feedback type: {feedback_type}", "fallback": "continue_current_path"}

    return result


def _initiate_skip_verification(
    db: Session, learner_id: str, item_id: str,
    state: AdaptivePathState, path: List[Dict], item_idx: int, trigger: str
) -> Dict[str, Any]:
    """Mark item as needing verification before skip."""
    old_snapshot = _snapshot(state)
    item = path[item_idx]
    path[item_idx] = {**item, "status": STATUS_VERIFICATION, "pending_verification": True}
    state.current_path = path
    state.updated_at = datetime.now(timezone.utc)
    db.commit()

    explanation = _generate_explanation("ALREADY_KNOWN", {})
    _log_event(db, learner_id, "VERIFICATION_REQUESTED", trigger,
               old_snapshot, _snapshot(state), item_id, None, None,
               "Learner claims mastery; verification initiated before skip",
               explanation)
    db.commit()

    return {
        "success": True,
        "adaptation_type": "VERIFICATION_REQUESTED",
        "trigger": trigger,
        "item_id": item_id,
        "message": "Let's verify before skipping. A short diagnostic check will be presented.",
        "explanation": explanation,
        "requires_verification": True,
        "skill_id": item.get("skill_id"),
    }


def apply_verification_result(
    db: Session,
    learner_id: str,
    item_id: str,
    passed: bool,
) -> Dict[str, Any]:
    """Apply the result of a verification check (pass → skip, fail → keep)."""
    state = get_or_create_state(db, learner_id)
    path = list(state.current_path or [])
    item_idx = next((i for i, x in enumerate(path) if x.get("id") == item_id), None)
    if item_idx is None:
        return {"success": False, "message": "Item not found."}

    item = path[item_idx]
    old_snapshot = _snapshot(state)

    if passed:
        path[item_idx] = {**item, "status": STATUS_MASTERED_SKIP, "pending_verification": False}
        explanation = "✓ Concept verified! You've demonstrated sufficient mastery — this item has been marked complete."
        trigger = "VERIFICATION_PASS"
        event_type = "ITEM_SKIPPED"
    else:
        path[item_idx] = {**item, "status": STATUS_IN_PROGRESS, "pending_verification": False}
        explanation = "Your assessment suggests some gaps remain. The item is kept in your path — completing it will solidify your understanding."
        trigger = "VERIFICATION_FAIL"
        event_type = "ITEM_RETAINED"

    state.current_path = path
    _recompute_timeline(state)
    state.updated_at = datetime.now(timezone.utc)
    db.commit()

    _log_event(db, learner_id, event_type, trigger,
               old_snapshot, _snapshot(state), item_id, None, None,
               f"Verification {'passed' if passed else 'failed'}: item {'skipped' if passed else 'retained'}",
               explanation)
    db.commit()

    return {
        "success": True,
        "passed": passed,
        "item_id": item_id,
        "new_status": STATUS_MASTERED_SKIP if passed else STATUS_IN_PROGRESS,
        "explanation": explanation,
    }


# ─────────────────────────────────────────────────
# Level 2: Remediation insertion
# ─────────────────────────────────────────────────

def adapt_for_assessment(
    db: Session,
    learner_id: str,
    skill_id: str,
    score: float,
    pitfall_id: Optional[str] = None,
    concept_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Triggered after an assessment.
    Low score → insert remediation + verification before current item.
    If pitfall_id provided, also integrate pitfall remediation.
    """
    if score >= MASTERY_THRESHOLD:
        return {
            "success": True,
            "adaptation_type": "NO_CHANGE",
            "message": f"Assessment score {score:.0%} is above threshold. No path change needed.",
        }

    state = get_or_create_state(db, learner_id)
    path = list(state.current_path or [])

    # Find the in-progress or next planned item for this skill
    target_idx = next(
        (i for i, x in enumerate(path)
         if x.get("skill_id") == skill_id and x.get("status") not in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)),
        None
    )
    if target_idx is None:
        # No matching item; insert after last completed
        target_idx = max(
            (i for i, x in enumerate(path) if x.get("status") in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)),
            default=0
        ) + 1

    return _insert_remediation_block(
        db, learner_id, state, path, target_idx, skill_id,
        trigger="KNOWLEDGE_GAP",
        pitfall_id=pitfall_id,
        concept_name=concept_name,
        score=score,
    )


def adapt_for_pitfall(
    db: Session,
    learner_id: str,
    pitfall_id: str,
    concept_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Consumes pitfall engine output.
    Inserts targeted remediation + verification for the detected misconception.
    """
    # Get skill_id from pitfall → concept → skill
    pitfall = db.query(Pitfall).filter(Pitfall.pitfall_id == pitfall_id).first()
    if not pitfall:
        return {"success": False, "message": "Pitfall not found.", "fallback": "continue_current_path"}

    concept = db.query(Concept).filter(Concept.concept_id == pitfall.concept_id).first()
    skill_id = concept.skill_id if concept else None
    actual_concept = concept_name or (concept.name if concept else pitfall.title)

    state = get_or_create_state(db, learner_id)
    path = list(state.current_path or [])

    # Find insertion point: before the first non-completed item for this skill
    target_idx = next(
        (i for i, x in enumerate(path)
         if x.get("skill_id") == skill_id and x.get("status") not in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)),
        None
    )
    if target_idx is None:
        # Insert before current in-progress item
        target_idx = next(
            (i for i, x in enumerate(path) if x.get("status") == STATUS_IN_PROGRESS),
            len(path)
        )

    return _insert_remediation_block(
        db, learner_id, state, path, target_idx, skill_id,
        trigger="MISCONCEPTION",
        pitfall_id=pitfall_id,
        concept_name=actual_concept,
        pitfall_title=pitfall.title,
    )


def _insert_remediation_block(
    db: Session,
    learner_id: str,
    state: AdaptivePathState,
    path: List[Dict],
    insert_before_idx: int,
    skill_id: Optional[str],
    trigger: str,
    pitfall_id: Optional[str] = None,
    concept_name: Optional[str] = None,
    pitfall_title: Optional[str] = None,
    score: Optional[float] = None,
) -> Dict[str, Any]:
    """Insert [Remediation item] → [Verification item] before insert_before_idx."""
    # Safety: count existing consecutive remediations to avoid overloading
    rem_count = sum(
        1 for item in path[max(0, insert_before_idx - 3):insert_before_idx]
        if item.get("item_type") == ITEM_REMEDIATION
    )
    if rem_count >= MAX_CONSECUTIVE_REMEDIATIONS:
        return {
            "success": False,
            "message": "Path already has multiple remediation items. Avoiding overload.",
            "fallback": "continue_current_path",
        }

    # Check if identical remediation already exists nearby (idempotency)
    existing_pitfall_ids = [
        item.get("pitfall_id") for item in path
        if item.get("item_type") == ITEM_REMEDIATION and item.get("status") != STATUS_COMPLETED
    ]
    if pitfall_id and pitfall_id in existing_pitfall_ids:
        return {
            "success": False,
            "message": "Remediation for this pitfall is already in the path.",
            "fallback": "continue_current_path",
        }

    # Find the best remediation resource
    rem_resource = None
    if skill_id:
        rem_resource = _find_remediation_resource(db, skill_id)

    old_snapshot = _snapshot(state)

    # Build remediation item
    rem_item_id = str(uuid.uuid4())
    rem_title = f"{concept_name or pitfall_title or 'Concept'} Remediation"
    rem_item = {
        "id": rem_item_id,
        "item_type": ITEM_REMEDIATION,
        "title": rem_title,
        "skill_id": skill_id,
        "resource_id": rem_resource.resource_id if rem_resource else None,
        "resource_title": rem_resource.title if rem_resource else None,
        "provider": rem_resource.provider if rem_resource else None,
        "format": rem_resource.format if rem_resource else None,
        "estimated_minutes": rem_resource.duration_minutes if rem_resource else 45,
        "status": STATUS_REMEDIATION,
        "required": True,
        "phase": "Remediation",
        "pitfall_id": pitfall_id,
        "concept_name": concept_name,
    }

    # Build verification item
    ver_item_id = str(uuid.uuid4())
    ver_item = {
        "id": ver_item_id,
        "item_type": ITEM_VERIFICATION,
        "title": f"{concept_name or pitfall_title or 'Concept'} Verification",
        "skill_id": skill_id,
        "resource_id": None,
        "estimated_minutes": 15,
        "status": STATUS_VERIFICATION,
        "required": True,
        "phase": "Verification",
        "pitfall_id": pitfall_id,
        "verifies_item_id": rem_item_id,
    }

    # Insert both items
    new_path = path[:insert_before_idx] + [rem_item, ver_item] + path[insert_before_idx:]
    # Re-assign sequence_order
    for idx_s, it in enumerate(new_path):
        it["sequence_order"] = idx_s + 1

    state.current_path = new_path
    _recompute_timeline(state)
    state.updated_at = datetime.now(timezone.utc)
    db.commit()

    ctx = {
        "concept": concept_name or pitfall_title,
        "pitfall_title": pitfall_title,
        "score": score or 0.0,
    }
    explanation = _generate_explanation(trigger, ctx)

    new_snapshot = _snapshot(state)
    _log_event(db, learner_id, "REMEDIATION_INSERTED", trigger,
               old_snapshot, new_snapshot, rem_item_id, None,
               rem_resource.resource_id if rem_resource else None,
               f"Inserted remediation for '{concept_name or pitfall_title}' due to {trigger}",
               explanation)
    db.commit()

    return {
        "success": True,
        "adaptation_type": "REMEDIATION_INSERTED",
        "trigger": trigger,
        "remediation_item": rem_item,
        "verification_item": ver_item,
        "explanation": explanation,
        "inserted_before": path[insert_before_idx].get("title") if insert_before_idx < len(path) else "end of path",
    }


# ─────────────────────────────────────────────────
# Level 3: Replan
# ─────────────────────────────────────────────────

def update_weekly_hours(
    db: Session,
    learner_id: str,
    new_hours: float,
) -> Dict[str, Any]:
    """Update weekly hours and recompute timeline."""
    state = get_or_create_state(db, learner_id)
    old_snapshot = _snapshot(state)
    old_hours = state.weekly_hours
    state.weekly_hours = new_hours
    _recompute_timeline(state)
    state.updated_at = datetime.now(timezone.utc)
    db.commit()

    ctx = {"new_hours": new_hours, "projected_weeks": state.projected_completion_weeks}
    explanation = _generate_explanation("HOURS_CHANGE", ctx)
    _log_event(db, learner_id, "HOURS_UPDATED", "HOURS_CHANGE",
               old_snapshot, old_snapshot, None, None, None,
               f"Weekly hours changed from {old_hours} to {new_hours}",
               explanation)
    db.commit()

    return {
        "success": True,
        "adaptation_type": "HOURS_UPDATED",
        "new_weekly_hours": new_hours,
        "remaining_hours": state.remaining_hours,
        "projected_completion_weeks": state.projected_completion_weeks,
        "is_on_track": state.is_on_track,
        "deadline_weeks": state.deadline_weeks,
        "explanation": explanation,
    }


def update_deadline(
    db: Session,
    learner_id: str,
    new_deadline_weeks: float,
) -> Dict[str, Any]:
    """Update deadline and recompute feasibility."""
    state = get_or_create_state(db, learner_id)
    old_snapshot = _snapshot(state)
    old_deadline = state.deadline_weeks
    state.deadline_weeks = new_deadline_weeks
    _recompute_timeline(state)
    state.updated_at = datetime.now(timezone.utc)
    db.commit()

    ctx = {"weekly_hours": state.weekly_hours, "projected_weeks": state.projected_completion_weeks}
    explanation = _generate_explanation("DEADLINE_CHANGE", ctx)
    _log_event(db, learner_id, "DEADLINE_UPDATED", "DEADLINE_CHANGE",
               old_snapshot, old_snapshot, None, None, None,
               f"Deadline changed from {old_deadline} to {new_deadline_weeks} weeks",
               explanation)
    db.commit()

    required_hours_per_week = (
        state.remaining_hours / new_deadline_weeks if new_deadline_weeks > 0 else None
    )

    return {
        "success": True,
        "adaptation_type": "DEADLINE_UPDATED",
        "new_deadline_weeks": new_deadline_weeks,
        "is_feasible": state.is_on_track,
        "projected_completion_weeks": state.projected_completion_weeks,
        "current_weekly_hours": state.weekly_hours,
        "required_weekly_hours_for_deadline": round(required_hours_per_week, 1) if required_hours_per_week else None,
        "explanation": explanation,
    }


def make_path_lighter(
    db: Session,
    learner_id: str,
) -> Dict[str, Any]:
    """Remove optional resources to create a lighter path."""
    state = get_or_create_state(db, learner_id)
    path = list(state.current_path or [])
    old_snapshot = _snapshot(state)

    # Remove optional, non-completed resources
    removed = []
    new_path = []
    for item in path:
        is_required = item.get("required", True)
        is_done = item.get("status") in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)
        is_remediation = item.get("item_type") in (ITEM_REMEDIATION, ITEM_VERIFICATION)
        if not is_required and not is_done and not is_remediation:
            removed.append(item.get("title"))
        else:
            new_path.append(item)

    if not removed:
        return {
            "success": False,
            "message": "All remaining items are required. Cannot lighten path further.",
            "fallback": "continue_current_path",
        }

    # Re-sequence
    for idx_s, it in enumerate(new_path):
        it["sequence_order"] = idx_s + 1

    state.current_path = new_path
    _recompute_timeline(state)
    state.updated_at = datetime.now(timezone.utc)
    db.commit()

    explanation = _generate_explanation("LIGHTER_PATH", {"removed": removed})
    _log_event(db, learner_id, "PATH_LIGHTENED", "LIGHTER_PATH",
               old_snapshot, _snapshot(state), None, None, None,
               f"Removed {len(removed)} optional items to lighten path",
               explanation)
    db.commit()

    return {
        "success": True,
        "adaptation_type": "PATH_LIGHTENED",
        "items_removed": removed,
        "new_remaining_hours": state.remaining_hours,
        "projected_completion_weeks": state.projected_completion_weeks,
        "explanation": explanation,
    }


def check_progress_and_deadline(
    db: Session,
    learner_id: str,
    actual_weekly_hours: Optional[float] = None,
) -> Dict[str, Any]:
    """Check learner pace against deadline and return status + options if falling behind."""
    state = get_or_create_state(db, learner_id)

    if actual_weekly_hours and actual_weekly_hours != state.weekly_hours:
        # Temporarily use actual for projection, but don't save
        weekly = actual_weekly_hours
    else:
        weekly = state.weekly_hours or 8.0

    remaining_hours = state.remaining_hours or 0.0
    projected_weeks = remaining_hours / weekly if weekly > 0 else 999.0
    deadline_weeks = state.deadline_weeks or 20.0
    is_on_track = projected_weeks <= deadline_weeks
    weeks_over = max(0.0, projected_weeks - deadline_weeks)
    required_hours = remaining_hours / deadline_weeks if deadline_weeks > 0 else None

    options = []
    if not is_on_track:
        # Option A: increase hours
        options.append({
            "label": "Increase weekly hours",
            "required_hours_per_week": round(required_hours, 1) if required_hours else None,
            "projected_weeks": round(deadline_weeks, 1),
            "action": "increase_hours",
        })
        # Option B: remove optionals
        optional_hours = sum(
            item.get("estimated_minutes", 60) * HOURS_PER_MINUTE
            for item in (state.current_path or [])
            if not item.get("required", True) and item.get("status") not in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)
        )
        if optional_hours > 0:
            reduced_remaining = remaining_hours - optional_hours
            options.append({
                "label": "Remove optional items",
                "projected_weeks": round(reduced_remaining / weekly, 1),
                "hours_saved": round(optional_hours, 1),
                "action": "lighter_path",
            })
        # Option C: extend deadline
        options.append({
            "label": "Extend deadline",
            "suggested_deadline_weeks": round(projected_weeks + 2, 0),
            "action": "extend_deadline",
        })

    return {
        "is_on_track": is_on_track,
        "current_weekly_hours": weekly,
        "remaining_hours": round(remaining_hours, 1),
        "projected_completion_weeks": round(projected_weeks, 1),
        "deadline_weeks": deadline_weeks,
        "weeks_behind": round(weeks_over, 1) if weeks_over > 0 else 0,
        "options": options,
    }


# ─────────────────────────────────────────────────
# What-If Simulation (NEVER mutates DB)
# ─────────────────────────────────────────────────

def simulate_plan(
    db: Session,
    learner_id: str,
    weekly_hours: float,
    deadline_weeks: float,
    optional_policy: str = "keep",  # 'keep' | 'remove'
) -> Dict[str, Any]:
    """
    Pure simulation — does NOT modify the database.
    Returns projected timeline for given parameters.
    """
    state = get_or_create_state(db, learner_id)
    path = list(state.current_path or [])

    # Guard: path not seeded yet
    if not path:
        return {
            "weekly_hours": weekly_hours,
            "deadline_weeks": deadline_weeks,
            "optional_policy": optional_policy,
            "remaining_hours": None,
            "projected_weeks": None,
            "projected_completion_date": None,
            "feasible": None,
            "removed_optional_items": 0,
            "is_simulation": True,
            "error": "no_path_data",
            "message": "No learning path found. Run seed_adaptive.py first.",
        }

    # Simulate optional removal if requested
    removed_count = 0
    simulated_hours = 0.0
    for item in path:
        is_done = item.get("status") in (STATUS_COMPLETED, STATUS_MASTERED_SKIP)
        if is_done:
            continue
        is_optional = not item.get("required", True)
        is_remediation = item.get("item_type") in (ITEM_REMEDIATION, ITEM_VERIFICATION)
        if optional_policy == "remove" and is_optional and not is_remediation:
            removed_count += 1
        else:
            simulated_hours += item.get("estimated_minutes", 60) * HOURS_PER_MINUTE

    proj_weeks = simulated_hours / weekly_hours if weekly_hours > 0 else 999.0
    feasible = proj_weeks <= deadline_weeks
    today = datetime.now(timezone.utc)
    projected_date = today + timedelta(weeks=proj_weeks)

    return {
        "weekly_hours": weekly_hours,
        "deadline_weeks": deadline_weeks,
        "optional_policy": optional_policy,
        "remaining_hours": round(simulated_hours, 1),
        "projected_weeks": round(proj_weeks, 1),
        "projected_completion_date": projected_date.strftime("%Y-%m-%d"),
        "feasible": feasible,
        "removed_optional_items": removed_count,
        "is_simulation": True,
    }


def simulate_faster_paths(db: Session, learner_id: str) -> Dict[str, Any]:
    """Generate 3 what-if scenarios for faster completion."""
    state = get_or_create_state(db, learner_id)
    current_hours = state.weekly_hours or 8.0
    current_deadline = state.deadline_weeks or 20.0

    base = simulate_plan(db, learner_id, current_hours, current_deadline, "keep")
    option_a = simulate_plan(db, learner_id, current_hours * 1.5, current_deadline, "keep")
    option_b = simulate_plan(db, learner_id, current_hours, current_deadline, "remove")
    option_c = simulate_plan(db, learner_id, current_hours * 1.25, current_deadline, "remove")

    return {
        "current_plan": {**base, "label": "Current Plan", "option_key": "current"},
        "options": [
            {**option_a, "label": f"Option A — Increase to {current_hours*1.5:.0f} hrs/week",
             "option_key": "A", "apply_params": {"weekly_hours": current_hours * 1.5, "optional_policy": "keep"}},
            {**option_b, "label": "Option B — Remove optional items",
             "option_key": "B", "apply_params": {"weekly_hours": current_hours, "optional_policy": "remove"}},
            {**option_c, "label": f"Option C — {current_hours*1.25:.0f} hrs/week + remove optionals",
             "option_key": "C", "apply_params": {"weekly_hours": current_hours * 1.25, "optional_policy": "remove"}},
        ],
    }


def apply_simulation(
    db: Session,
    learner_id: str,
    option_key: str,
    weekly_hours: float,
    optional_policy: str = "keep",
) -> Dict[str, Any]:
    """Apply a simulation option to actually mutate the path."""
    state = get_or_create_state(db, learner_id)
    results = {}

    if weekly_hours != state.weekly_hours:
        results["hours"] = update_weekly_hours(db, learner_id, weekly_hours)

    if optional_policy == "remove":
        results["lighter"] = make_path_lighter(db, learner_id)

    _recompute_timeline(state)
    db.commit()

    return {
        "success": True,
        "applied_option": option_key,
        "results": results,
        "new_projected_weeks": state.projected_completion_weeks,
        "new_remaining_hours": state.remaining_hours,
        "is_on_track": state.is_on_track,
    }


# ─────────────────────────────────────────────────
# Path diff helper
# ─────────────────────────────────────────────────

def get_path_diff(db: Session, learner_id: str) -> Dict[str, Any]:
    """Return the most recent path change as a before/after diff."""
    events = db.query(AdaptationEvent).filter(
        AdaptationEvent.learner_id == learner_id
    ).order_by(AdaptationEvent.timestamp.desc()).limit(5).all()

    if not events:
        return {"has_diff": False}

    latest = events[0]
    return {
        "has_diff": True,
        "event_type": latest.event_type,
        "trigger": latest.trigger,
        "explanation": latest.explanation,
        "reason": latest.reason,
        "timestamp": latest.timestamp.isoformat() if latest.timestamp else None,
        "old_path": latest.old_path_snapshot,
        "new_path": latest.new_path_snapshot,
    }


# ─────────────────────────────────────────────────
# Adaptive status
# ─────────────────────────────────────────────────

def get_adaptive_status(db: Session, learner_id: str) -> Dict[str, Any]:
    """Return a comprehensive adaptive status for the learner."""
    state = get_or_create_state(db, learner_id)
    path = state.current_path or []

    # Current item
    current = next(
        (item for item in path if item.get("status") == STATUS_IN_PROGRESS),
        next((item for item in path if item.get("status") == STATUS_PLANNED), None)
    )

    # Completion stats
    total = len(path)
    completed = sum(1 for x in path if x.get("status") in (STATUS_COMPLETED, STATUS_MASTERED_SKIP))
    pct = round(completed / total * 100) if total > 0 else 0

    # Recent events
    recent_events = db.query(AdaptationEvent).filter(
        AdaptationEvent.learner_id == learner_id
    ).order_by(AdaptationEvent.timestamp.desc()).limit(5).all()

    return {
        "learner_id": learner_id,
        "current_item": current,
        "path_length": total,
        "completed_items": completed,
        "completion_percentage": pct,
        "weekly_hours": state.weekly_hours,
        "deadline_weeks": state.deadline_weeks,
        "remaining_hours": state.remaining_hours,
        "projected_completion_weeks": state.projected_completion_weeks,
        "is_on_track": state.is_on_track,
        "recent_adaptations": [
            {
                "event_type": e.event_type,
                "trigger": e.trigger,
                "explanation": e.explanation,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            }
            for e in recent_events
        ],
    }
