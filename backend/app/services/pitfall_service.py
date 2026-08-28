"""
Pitfall Service — orchestrator for the pitfall & misconception detection feature.

Responsibilities:
  - Fetching pitfall check questions for a skill/concept
  - Persisting PitfallAttempt records
  - Updating LearnerPitfall state
  - Generating LLM explanations (with deterministic fallback)
  - Finding best remediation resource
  - Returning learner dashboard data
"""
import uuid
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.models.orm import (
    Concept, Pitfall, PitfallQuestion, PitfallAttempt,
    LearnerPitfall, Resource, ResourceSkill
)
from app.services.pitfall_evaluator import evaluate_answer, EvaluationResult
from app.services.pitfall_analytics import compute_pitfall_analytics


# ─────────────────────────────────────────────────────────────────────────────
# LLM helper — uses the project's existing ChatGroq setup
# ─────────────────────────────────────────────────────────────────────────────

def _get_llm():
    """Returns a ChatGroq instance or None if unavailable."""
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key or api_key.startswith("mock"):
            return None
        return ChatGroq(api_key=api_key, model_name="llama3-8b-8192", temperature=0.3)
    except Exception:
        return None


def _generate_llm_explanation(eval_result: EvaluationResult) -> str:
    """
    Asks the LLM to produce a learner-friendly explanation of the evaluation result.
    Falls back to deterministic text stored on the pitfall if LLM is unavailable.
    """
    llm = _get_llm()

    classification = eval_result.classification
    pitfall = eval_result.pitfall
    question = eval_result.question

    # ── Deterministic fallback ───────────────────────────────────
    if not llm:
        if classification == "MASTERY":
            return "Great work! You demonstrated a solid understanding of this concept."
        elif classification == "KNOWLEDGE_GAP":
            correct_option = question.correct_option if question else "?"
            explanation = question.explanation if question else ""
            return (
                f"It looks like this concept needs a bit more practice. "
                f"The correct answer was option {correct_option}. {explanation}"
            )
        elif classification == "MISCONCEPTION" and pitfall:
            return (
                f"Your answer suggests a common misconception: '{pitfall.title}'. "
                f"\n\nWhat you may have thought: {pitfall.misconception}"
                f"\n\nThe correct understanding: {pitfall.correct_mental_model}"
                f"\n\nQuick tip: {pitfall.remediation_text}"
            )
        else:
            correct_option = question.correct_option if question else "?"
            return (
                f"This one was tricky. The correct answer was option {correct_option}. "
                f"Review the concept and try again — it's a common area of confusion."
            )

    # ── LLM explanation ─────────────────────────────────────────
    from langchain_core.messages import SystemMessage, HumanMessage

    system_prompt = (
        "You are a supportive learning coach. Your job is to give a concise, "
        "empathetic, and clear explanation to a learner about their answer to a "
        "concept-check question. Be specific. Do NOT be preachy. Maximum 4 sentences."
    )

    if classification == "MASTERY":
        user_msg = (
            f"The learner answered correctly with confidence {eval_result.confidence}/5. "
            f"Question: '{question.question_text if question else ''}'. "
            f"Give a short, encouraging confirmation."
        )
    elif classification == "MISCONCEPTION" and pitfall:
        user_msg = (
            f"The learner chose option '{eval_result.question.options.get(eval_result.misconception_hint[:1], '') if eval_result.question else ''}' "
            f"with high confidence ({eval_result.confidence}/5). "
            f"This reveals a common misconception: '{pitfall.title}'. "
            f"What they probably thought: '{pitfall.misconception}'. "
            f"Correct understanding: '{pitfall.correct_mental_model}'. "
            f"Explain gently why their thinking was off and what the correct mental model is."
        )
    elif classification == "KNOWLEDGE_GAP":
        user_msg = (
            f"The learner got a question wrong with low confidence ({eval_result.confidence}/5). "
            f"Question: '{question.question_text if question else ''}'. "
            f"Correct answer: option {question.correct_option if question else '?'}. "
            f"Explanation: '{question.explanation if question else ''}'. "
            f"Give an encouraging but informative explanation."
        )
    else:
        user_msg = (
            f"The learner answered incorrectly with medium confidence. "
            f"Question: '{question.question_text if question else ''}'. "
            f"Correct answer: {question.correct_option if question else '?'}. "
            f"Explanation: '{question.explanation if question else ''}'. "
            f"Encourage further review."
        )

    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_msg)])
        return response.content.strip()
    except Exception:
        # LLM call failed — use deterministic fallback
        if pitfall:
            return pitfall.remediation_text or pitfall.correct_mental_model or "Please review this concept."
        if question:
            return question.explanation or "Please review this concept."
        return "Please review this concept."


# ─────────────────────────────────────────────────────────────────────────────
# Core service functions
# ─────────────────────────────────────────────────────────────────────────────

def get_pitfall_check_for_skill(
    db: Session,
    skill_id: str,
    learner_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Return a pitfall check question for a given skill.

    Prioritizes:
    1. Pitfalls the learner has previously shown evidence of
    2. High-severity pitfalls
    3. Falls back to first available
    """
    # Find concepts linked to this skill
    concepts = db.query(Concept).filter(Concept.skill_id == skill_id).all()
    if not concepts:
        return None

    concept_ids = [c.concept_id for c in concepts]

    # If learner provided, find their active pitfalls for this skill first
    prioritised_pitfall_ids = []
    if learner_id:
        active_lps = db.query(LearnerPitfall).filter(
            LearnerPitfall.learner_id == learner_id,
            LearnerPitfall.status.in_(["DETECTED", "UNRESOLVED"]),
        ).all()
        # Filter to pitfalls in this skill's concepts
        pitfall_ids_for_skill = [
            p.pitfall_id for p in
            db.query(Pitfall).filter(Pitfall.concept_id.in_(concept_ids)).all()
        ]
        for lp in active_lps:
            if lp.pitfall_id in pitfall_ids_for_skill:
                prioritised_pitfall_ids.append(lp.pitfall_id)

    # Get available pitfalls
    pitfalls = db.query(Pitfall).filter(
        Pitfall.concept_id.in_(concept_ids),
        Pitfall.status == "active"
    ).all()

    if not pitfalls:
        return None

    # Sort: prioritised first, then by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    pitfalls.sort(key=lambda p: (
        0 if p.pitfall_id in prioritised_pitfall_ids else 1,
        severity_order.get(p.severity, 1)
    ))

    selected_pitfall = pitfalls[0]
    concept = db.query(Concept).filter(
        Concept.concept_id == selected_pitfall.concept_id
    ).first()

    # Get a question for this pitfall
    question = db.query(PitfallQuestion).filter(
        PitfallQuestion.pitfall_id == selected_pitfall.pitfall_id
    ).first()

    if not question:
        return None

    return {
        "pitfall_id": selected_pitfall.pitfall_id,
        "pitfall_title": selected_pitfall.title,
        "concept_name": concept.name if concept else "Unknown",
        "severity": selected_pitfall.severity,
        "question": {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "options": question.options,
        }
    }


def submit_pitfall_answer(
    db: Session,
    learner_id: str,
    question_id: str,
    selected_option: str,
    confidence: int,
) -> Dict[str, Any]:
    """
    Process a learner's pitfall check answer:
    1. Deterministically evaluate
    2. Persist the attempt
    3. Update/create LearnerPitfall
    4. Generate LLM explanation
    5. Return structured response
    """
    # Step 1: Evaluate
    eval_result = evaluate_answer(db, question_id, selected_option, confidence)

    # Step 2: Persist attempt
    attempt = PitfallAttempt(
        attempt_id=str(uuid.uuid4()),
        learner_id=learner_id,
        question_id=question_id,
        selected_option=selected_option.upper(),
        is_correct=eval_result.is_correct,
        confidence=confidence,
        classification=eval_result.classification,
        matched_pitfall_id=eval_result.pitfall_id,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(attempt)

    # Step 3: Update learner pitfall state
    if eval_result.classification == "MISCONCEPTION" and eval_result.pitfall_id:
        _upsert_learner_pitfall(
            db, learner_id, eval_result.pitfall_id,
            confidence=confidence, passed=False
        )
    elif eval_result.classification == "MASTERY" and eval_result.question:
        # Check if learner had an active pitfall for this question's pitfall
        if eval_result.question.pitfall_id:
            _upsert_learner_pitfall(
                db, learner_id, eval_result.question.pitfall_id,
                confidence=confidence, passed=True
            )

    db.commit()

    # Step 4: Generate explanation
    explanation = _generate_llm_explanation(eval_result)

    # Step 5: Find remediation resource if misconception
    remediation = None
    if eval_result.classification in ("MISCONCEPTION", "KNOWLEDGE_GAP") and eval_result.pitfall_id:
        pitfall = eval_result.pitfall or db.query(Pitfall).filter(
            Pitfall.pitfall_id == eval_result.pitfall_id
        ).first()
        if pitfall:
            concept = db.query(Concept).filter(
                Concept.concept_id == pitfall.concept_id
            ).first()
            if concept and concept.skill_id:
                resource = _find_best_remediation_resource(db, concept.skill_id)
                if resource:
                    remediation = {
                        "resource_id": resource.resource_id,
                        "title": resource.title,
                        "provider": resource.provider,
                        "resource_type": resource.resource_type,
                        "duration_minutes": resource.duration_minutes,
                        "quality_score": resource.quality_score,
                    }

    return {
        **eval_result.to_dict(),
        "explanation": explanation,
        "remediation_resource": remediation,
    }


def get_learner_pitfall_dashboard(
    db: Session,
    learner_id: str
) -> Dict[str, Any]:
    """Returns dashboard data: active pitfalls, resolved pitfalls, stats."""
    all_lps = db.query(LearnerPitfall).filter(
        LearnerPitfall.learner_id == learner_id
    ).all()

    active = []
    resolved = []

    for lp in all_lps:
        pitfall = db.query(Pitfall).filter(Pitfall.pitfall_id == lp.pitfall_id).first()
        if not pitfall:
            continue
        concept = db.query(Concept).filter(Concept.concept_id == pitfall.concept_id).first()
        item = {
            "learner_pitfall_id": lp.id,
            "pitfall_id": lp.pitfall_id,
            "title": pitfall.title,
            "concept_name": concept.name if concept else "Unknown",
            "severity": pitfall.severity,
            "status": lp.status,
            "confidence_score": lp.confidence_score,
            "evidence_count": lp.evidence_count,
            "passed_checks": lp.passed_checks,
            "failed_checks": lp.failed_checks,
            "first_detected": lp.first_detected.isoformat() if lp.first_detected else None,
            "last_detected": lp.last_detected.isoformat() if lp.last_detected else None,
            "resolved_at": lp.resolved_at.isoformat() if lp.resolved_at else None,
        }
        if lp.status == "RESOLVED":
            resolved.append(item)
        else:
            active.append(item)

    # Sort active by severity then recency
    severity_order = {"high": 0, "medium": 1, "low": 2}
    active.sort(key=lambda x: (severity_order.get(x["severity"], 1),
                                x["last_detected"] or ""))

    return {
        "learner_id": learner_id,
        "active_pitfalls": active,
        "resolved_pitfalls": resolved,
        "stats": {
            "total_detected": len(all_lps),
            "active_count": len(active),
            "resolved_count": len(resolved),
            "high_severity_active": sum(1 for p in active if p["severity"] == "high"),
        }
    }


def start_remediation(
    db: Session,
    learner_id: str,
    pitfall_id: str
) -> Dict[str, Any]:
    """
    Mark the learner as in remediation for this pitfall and return the resource.
    """
    lp = db.query(LearnerPitfall).filter(
        LearnerPitfall.learner_id == learner_id,
        LearnerPitfall.pitfall_id == pitfall_id,
    ).first()

    if lp:
        lp.status = "REMEDIATION"
        db.commit()

    pitfall = db.query(Pitfall).filter(Pitfall.pitfall_id == pitfall_id).first()
    if not pitfall:
        return {"error": "Pitfall not found"}

    concept = db.query(Concept).filter(Concept.concept_id == pitfall.concept_id).first()
    resource = None
    if concept and concept.skill_id:
        res = _find_best_remediation_resource(db, concept.skill_id)
        if res:
            resource = {
                "resource_id": res.resource_id,
                "title": res.title,
                "provider": res.provider,
                "resource_type": res.resource_type,
                "duration_minutes": res.duration_minutes,
                "quality_score": res.quality_score,
            }

    return {
        "pitfall_id": pitfall_id,
        "pitfall_title": pitfall.title,
        "status": "REMEDIATION",
        "explanation": pitfall.correct_mental_model,
        "remediation_text": pitfall.remediation_text,
        "resource": resource,
    }


def submit_verification(
    db: Session,
    learner_id: str,
    pitfall_id: str,
    question_id: str,
    selected_option: str,
    confidence: int,
) -> Dict[str, Any]:
    """
    Process a verification attempt after remediation.
    If passed → RESOLVED. If failed → UNRESOLVED.
    """
    eval_result = evaluate_answer(db, question_id, selected_option, confidence)

    lp = db.query(LearnerPitfall).filter(
        LearnerPitfall.learner_id == learner_id,
        LearnerPitfall.pitfall_id == pitfall_id,
    ).first()

    if lp:
        if eval_result.is_correct:
            lp.status = "RESOLVED"
            lp.resolved_at = datetime.now(timezone.utc)
            lp.passed_checks = (lp.passed_checks or 0) + 1
        else:
            lp.status = "UNRESOLVED"
            lp.failed_checks = (lp.failed_checks or 0) + 1
        db.commit()

    # Record attempt
    attempt = PitfallAttempt(
        attempt_id=str(uuid.uuid4()),
        learner_id=learner_id,
        question_id=question_id,
        selected_option=selected_option.upper(),
        is_correct=eval_result.is_correct,
        confidence=confidence,
        classification=eval_result.classification,
        matched_pitfall_id=pitfall_id if not eval_result.is_correct else None,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.commit()

    return {
        "pitfall_id": pitfall_id,
        "resolved": eval_result.is_correct,
        "new_status": "RESOLVED" if eval_result.is_correct else "UNRESOLVED",
        "classification": eval_result.classification,
        "explanation": _generate_llm_explanation(eval_result),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _upsert_learner_pitfall(
    db: Session,
    learner_id: str,
    pitfall_id: str,
    confidence: float,
    passed: bool,
):
    lp = db.query(LearnerPitfall).filter(
        LearnerPitfall.learner_id == learner_id,
        LearnerPitfall.pitfall_id == pitfall_id,
    ).first()

    now = datetime.now(timezone.utc)

    if lp:
        lp.last_detected = now
        lp.evidence_count = (lp.evidence_count or 0) + 1
        lp.confidence_score = confidence
        if passed:
            lp.passed_checks = (lp.passed_checks or 0) + 1
            # Only resolve if consistently passing
            if lp.passed_checks >= 2 and lp.status not in ("RESOLVED",):
                lp.status = "VERIFICATION"
        else:
            lp.failed_checks = (lp.failed_checks or 0) + 1
            if lp.status in ("RESOLVED",):
                # Regression — reopen
                lp.status = "DETECTED"
                lp.resolved_at = None
    else:
        lp = LearnerPitfall(
            id=str(uuid.uuid4()),
            learner_id=learner_id,
            pitfall_id=pitfall_id,
            status="DETECTED",
            confidence_score=confidence,
            evidence_count=1,
            passed_checks=1 if passed else 0,
            failed_checks=0 if passed else 1,
            first_detected=now,
            last_detected=now,
        )
        db.add(lp)


def _find_best_remediation_resource(db: Session, skill_id: str) -> Optional[Resource]:
    """
    Find the highest-quality resource for a given skill.
    Prioritizes: quality_score × coverage_score, then appropriate difficulty.
    """
    # Try direct match via resource_skills junction
    resource_skill_rows = db.query(ResourceSkill).filter(
        ResourceSkill.skill_id == skill_id
    ).order_by(ResourceSkill.coverage_score.desc()).all()

    if resource_skill_rows:
        resource_ids = [rs.resource_id for rs in resource_skill_rows[:10]]
        resources = db.query(Resource).filter(
            Resource.resource_id.in_(resource_ids),
            Resource.status == "active"
        ).order_by(Resource.quality_score.desc()).all()
        if resources:
            return resources[0]

    # Fallback: direct primary_skill_id match
    resources = db.query(Resource).filter(
        Resource.primary_skill_id == skill_id,
        Resource.status == "active"
    ).order_by(Resource.quality_score.desc()).all()

    return resources[0] if resources else None
