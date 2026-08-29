"""
Adaptive Learning Path API endpoints.
All routes under /api/v1/adaptive/
"""
import uuid
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.base import APIResponse, MetaResponse
from app.models.database import SessionLocal
from app.models.orm import AdaptationEvent, AdaptivePathState, LearnerPitfall, Pitfall
from app.services import adaptive_planner as planner
from app.services.intent_classifier import classify_adaptive_intent
from app.services.chat_service import chat_service

adaptive_router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _meta() -> MetaResponse:
    return MetaResponse(request_id=str(uuid.uuid4()))


# ─────────────────────────────────────────────────
# Request models
# ─────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    learner_id: str
    item_id: str
    feedback_type: str  # TOO_HARD | TOO_EASY | ALREADY_KNOWN | TOO_LONG | CONFUSING | JUST_RIGHT


class AssessmentRequest(BaseModel):
    learner_id: str
    skill_id: str
    score: float          # 0.0 – 1.0
    pitfall_id: Optional[str] = None
    concept_name: Optional[str] = None


class PitfallAdaptRequest(BaseModel):
    learner_id: str
    pitfall_id: str
    concept_name: Optional[str] = None


class SimulateRequest(BaseModel):
    learner_id: str
    weekly_hours: float
    deadline_weeks: float
    optional_policy: str = "keep"   # 'keep' | 'remove'


class ApplySimulationRequest(BaseModel):
    learner_id: str
    option_key: str         # A | B | C | current
    weekly_hours: float
    optional_policy: str = "keep"


class VerificationResultRequest(BaseModel):
    learner_id: str
    item_id: str
    passed: bool


class HoursUpdateRequest(BaseModel):
    learner_id: str
    new_hours: float


class DeadlineUpdateRequest(BaseModel):
    learner_id: str
    new_deadline_weeks: float


class AdaptiveChatRequest(BaseModel):
    learner_id: str
    user_message: str
    current_item_id: Optional[str] = None
    history: List[Dict[str, str]] = []


class CompleteItemRequest(BaseModel):
    learner_id: str
    item_id: str


# ─────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────

@adaptive_router.post("/feedback", response_model=APIResponse[Dict[str, Any]])
def handle_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Handle learner resource feedback (too hard / too easy / already known / etc.)
    Triggers deterministic adaptation.
    """
    if request.feedback_type == "JUST_RIGHT":
        return APIResponse(
            success=True,
            data={"adaptation_type": "NO_CHANGE", "message": "Great! Keep going."},
            meta=_meta()
        )
    try:
        result = planner.adapt_for_feedback(
            db, request.learner_id, request.item_id, request.feedback_type
        )
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        return APIResponse(
            success=False,
            data={"success": False, "message": str(e), "fallback": "continue_current_path"},
            meta=_meta()
        )


@adaptive_router.post("/assessment", response_model=APIResponse[Dict[str, Any]])
def handle_assessment(request: AssessmentRequest, db: Session = Depends(get_db)):
    """Submit assessment result. Low score triggers remediation insertion."""
    try:
        result = planner.adapt_for_assessment(
            db, request.learner_id, request.skill_id, request.score,
            request.pitfall_id, request.concept_name
        )
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        return APIResponse(
            success=False,
            data={"success": False, "message": str(e), "fallback": "continue_current_path"},
            meta=_meta()
        )


@adaptive_router.post("/pitfall", response_model=APIResponse[Dict[str, Any]])
def handle_pitfall(request: PitfallAdaptRequest, db: Session = Depends(get_db)):
    """
    Integrate pitfall engine output into the adaptive path.
    Inserts remediation + verification for the detected misconception.
    """
    try:
        result = planner.adapt_for_pitfall(
            db, request.learner_id, request.pitfall_id, request.concept_name
        )
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        return APIResponse(
            success=False,
            data={"success": False, "message": str(e), "fallback": "continue_current_path"},
            meta=_meta()
        )


@adaptive_router.post("/simulate", response_model=APIResponse[Dict[str, Any]])
def simulate_plan(request: SimulateRequest, db: Session = Depends(get_db)):
    """
    What-if simulation. DOES NOT modify the database.
    Returns projected timeline for given parameters.
    """
    result = planner.simulate_plan(
        db, request.learner_id, request.weekly_hours,
        request.deadline_weeks, request.optional_policy
    )
    return APIResponse(success=True, data=result, meta=_meta())


@adaptive_router.post("/simulate/faster", response_model=APIResponse[Dict[str, Any]])
def simulate_faster(learner_id: str, db: Session = Depends(get_db)):
    """Generate 3 faster-path what-if scenarios."""
    result = planner.simulate_faster_paths(db, learner_id)
    return APIResponse(success=True, data=result, meta=_meta())


@adaptive_router.post("/apply", response_model=APIResponse[Dict[str, Any]])
def apply_simulation(request: ApplySimulationRequest, db: Session = Depends(get_db)):
    """Apply a previously simulated plan option — this DOES mutate the path."""
    try:
        result = planner.apply_simulation(
            db, request.learner_id, request.option_key,
            request.weekly_hours, request.optional_policy
        )
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@adaptive_router.post("/verify", response_model=APIResponse[Dict[str, Any]])
def apply_verification(request: VerificationResultRequest, db: Session = Depends(get_db)):
    """Apply verification result — pass → skip, fail → retain."""
    try:
        result = planner.apply_verification_result(
            db, request.learner_id, request.item_id, request.passed
        )
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@adaptive_router.post("/hours", response_model=APIResponse[Dict[str, Any]])
def update_hours(request: HoursUpdateRequest, db: Session = Depends(get_db)):
    """Update learner's weekly study hours and recompute timeline."""
    try:
        result = planner.update_weekly_hours(db, request.learner_id, request.new_hours)
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@adaptive_router.post("/deadline", response_model=APIResponse[Dict[str, Any]])
def update_deadline(request: DeadlineUpdateRequest, db: Session = Depends(get_db)):
    """Update learner's deadline and recompute feasibility."""
    try:
        result = planner.update_deadline(db, request.learner_id, request.new_deadline_weeks)
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@adaptive_router.post("/lighter", response_model=APIResponse[Dict[str, Any]])
def make_lighter(learner_id: str, db: Session = Depends(get_db)):
    """Remove optional resources to create a lighter path."""
    try:
        result = planner.make_path_lighter(db, learner_id)
        return APIResponse(success=True, data=result, meta=_meta())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@adaptive_router.post("/complete-item", response_model=APIResponse[Dict[str, Any]])
def complete_item(request: CompleteItemRequest, db: Session = Depends(get_db)):
    """Mark a path item as completed."""
    try:
        state = planner.get_or_create_state(db, request.learner_id)
        path = list(state.current_path or [])
        idx = next((i for i, x in enumerate(path) if x.get("id") == request.item_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="Item not found")
        path[idx] = {**path[idx], "status": "completed"}
        # Move next planned to in_progress
        for i in range(idx + 1, len(path)):
            if path[i].get("status") == "planned":
                path[i] = {**path[i], "status": "in_progress"}
                break
        state.current_path = path
        planner._recompute_timeline(state)
        state.updated_at = __import__("datetime").datetime.utcnow()
        db.commit()
        return APIResponse(success=True, data={"item_id": request.item_id, "status": "completed"}, meta=_meta())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@adaptive_router.get("/status/{learner_id}", response_model=APIResponse[Dict[str, Any]])
def get_status(learner_id: str, db: Session = Depends(get_db)):
    """Get the current adaptive status for a learner."""
    result = planner.get_adaptive_status(db, learner_id)
    return APIResponse(success=True, data=result, meta=_meta())


@adaptive_router.get("/progress/{learner_id}", response_model=APIResponse[Dict[str, Any]])
def get_progress_check(learner_id: str, actual_weekly_hours: Optional[float] = None, db: Session = Depends(get_db)):
    """Check learner pace against deadline."""
    result = planner.check_progress_and_deadline(db, learner_id, actual_weekly_hours)
    return APIResponse(success=True, data=result, meta=_meta())


@adaptive_router.get("/history/{learner_id}", response_model=APIResponse[Dict[str, Any]])
def get_history(learner_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Get the full adaptation event history for a learner."""
    events = db.query(AdaptationEvent).filter(
        AdaptationEvent.learner_id == learner_id
    ).order_by(AdaptationEvent.timestamp.desc()).limit(limit).all()

    data = [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "trigger": e.trigger,
            "affected_item_id": e.affected_item_id,
            "old_resource_id": e.old_resource_id,
            "new_resource_id": e.new_resource_id,
            "reason": e.reason,
            "explanation": e.explanation,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]
    return APIResponse(success=True, data={"events": data, "total": len(data)}, meta=_meta())


@adaptive_router.get("/path-diff/{learner_id}", response_model=APIResponse[Dict[str, Any]])
def get_path_diff(learner_id: str, db: Session = Depends(get_db)):
    """Get the most recent path diff (before/after the last adaptation)."""
    result = planner.get_path_diff(db, learner_id)
    return APIResponse(success=True, data=result, meta=_meta())


@adaptive_router.get("/path/{learner_id}", response_model=APIResponse[Dict[str, Any]])
def get_path(learner_id: str, db: Session = Depends(get_db)):
    """Get the current adaptive ML Engineer path for a learner."""
    state = planner.get_or_create_state(db, learner_id)
    return APIResponse(
        success=True,
        data={
            "learner_id": learner_id,
            "path": state.current_path or [],
            "weekly_hours": state.weekly_hours,
            "deadline_weeks": state.deadline_weeks,
            "remaining_hours": state.remaining_hours,
            "projected_completion_weeks": state.projected_completion_weeks,
            "is_on_track": state.is_on_track,
            "version": state.version,
        },
        meta=_meta()
    )


@adaptive_router.post("/chat", response_model=APIResponse[Dict[str, Any]])
def adaptive_chat(request: AdaptiveChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint with adaptive intent detection.
    Maps natural language to deterministic planner actions.
    """
    classification = classify_adaptive_intent(request.user_message)
    intent = classification["intent"]
    extracted = classification.get("extracted", {})

    adaptation_result = None
    simulation_result = None
    requires_confirmation = False

    try:
        if intent == "TOO_HARD":
            if request.current_item_id:
                adaptation_result = planner.adapt_for_feedback(
                    db, request.learner_id, request.current_item_id, "TOO_HARD"
                )

        elif intent == "TOO_EASY":
            if request.current_item_id:
                adaptation_result = planner.adapt_for_feedback(
                    db, request.learner_id, request.current_item_id, "TOO_EASY"
                )

        elif intent == "ALREADY_KNOWN":
            if request.current_item_id:
                adaptation_result = planner.adapt_for_feedback(
                    db, request.learner_id, request.current_item_id, "ALREADY_KNOWN"
                )

        elif intent == "REQUEST_FASTER":
            simulation_result = planner.simulate_faster_paths(db, request.learner_id)
            requires_confirmation = True

        elif intent == "REQUEST_LIGHTER":
            simulation_result = planner.simulate_plan(
                db, request.learner_id,
                planner.get_or_create_state(db, request.learner_id).weekly_hours or 8.0,
                planner.get_or_create_state(db, request.learner_id).deadline_weeks or 20.0,
                "remove"
            )
            requires_confirmation = True

        elif intent == "CHANGE_HOURS":
            new_hours = extracted.get("new_hours")
            if new_hours:
                adaptation_result = planner.update_weekly_hours(db, request.learner_id, new_hours)
            else:
                pass  # Fall through to general chat

        elif intent == "CHANGE_DEADLINE":
            deadline_weeks = extracted.get("deadline_weeks")
            if deadline_weeks:
                adaptation_result = planner.update_deadline(db, request.learner_id, deadline_weeks)
            else:
                pass

        elif intent == "WHY_CHANGED":
            diff = planner.get_path_diff(db, request.learner_id)
            return APIResponse(
                success=True,
                data={
                    "intent": intent,
                    "response": diff.get("explanation", "I haven't made any changes to your path recently."),
                    "path_diff": diff,
                    "adaptation_result": None,
                },
                meta=_meta()
            )

        elif intent == "WHAT_IF":
            state = planner.get_or_create_state(db, request.learner_id)
            simulation_result = planner.simulate_faster_paths(db, request.learner_id)
            requires_confirmation = True

    except Exception as e:
        # Never break the chat on adaptation error
        pass

    # Generate conversational response
    if intent == "GENERAL_CHAT" or (adaptation_result is None and simulation_result is None):
        chat_response = chat_service.generate_chat_response(
            user_message=request.user_message,
            history=request.history
        )
    elif adaptation_result:
        chat_response = adaptation_result.get("explanation", "Your path has been updated.")
    elif simulation_result and requires_confirmation:
        chat_response = (
            "I've prepared some scenarios for you. Check the options below and click 'Apply' "
            "on the one you'd like to use. Your path won't change until you confirm."
        )
    else:
        chat_response = "Got it! Let me know if you need anything else."

    return APIResponse(
        success=True,
        data={
            "intent": intent,
            "confidence": classification.get("confidence"),
            "response": chat_response,
            "adaptation_result": adaptation_result,
            "simulation_result": simulation_result,
            "requires_confirmation": requires_confirmation,
        },
        meta=_meta()
    )
