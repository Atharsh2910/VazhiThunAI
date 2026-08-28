"""
Pitfall Evaluator — deterministic answer classification.

Classifies a learner's answer into:
  MASTERY        — correct + (any confidence)
  KNOWLEDGE_GAP  — incorrect + low confidence (1-2)
  MISCONCEPTION  — incorrect + high confidence (4-5) AND option maps to a pitfall
  UNCERTAINTY    — incorrect + medium confidence (3) or no option mapping
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.orm import PitfallQuestion, PitfallOptionMapping, Pitfall


# Confidence thresholds (1-5 scale)
HIGH_CONFIDENCE_MIN = 4
LOW_CONFIDENCE_MAX = 2


class EvaluationResult:
    def __init__(
        self,
        classification: str,
        is_correct: bool,
        confidence: int,
        pitfall_id: Optional[str] = None,
        misconception_hint: Optional[str] = None,
        pitfall: Optional[Any] = None,
        question: Optional[Any] = None,
    ):
        self.classification = classification   # MASTERY / KNOWLEDGE_GAP / MISCONCEPTION / UNCERTAINTY
        self.is_correct = is_correct
        self.confidence = confidence
        self.pitfall_id = pitfall_id
        self.misconception_hint = misconception_hint
        self.pitfall = pitfall
        self.question = question

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "classification": self.classification,
            "is_correct": self.is_correct,
            "confidence": self.confidence,
            "pitfall_id": self.pitfall_id,
            "misconception_hint": self.misconception_hint,
        }
        if self.pitfall:
            result["pitfall"] = {
                "pitfall_id": self.pitfall.pitfall_id,
                "title": self.pitfall.title,
                "misconception": self.pitfall.misconception,
                "correct_mental_model": self.pitfall.correct_mental_model,
                "severity": self.pitfall.severity,
                "remediation_text": self.pitfall.remediation_text,
            }
        if self.question:
            result["question"] = {
                "question_id": self.question.question_id,
                "question_text": self.question.question_text,
                "correct_option": self.question.correct_option,
                "explanation": self.question.explanation,
                "options": self.question.options,
            }
        return result


def evaluate_answer(
    db: Session,
    question_id: str,
    selected_option: str,
    confidence: int,
) -> EvaluationResult:
    """
    Deterministically classify a learner's answer.

    Args:
        db: database session
        question_id: the pitfall question being answered
        selected_option: the option key chosen by the learner (e.g. "A")
        confidence: learner's self-reported confidence on 1-5 scale

    Returns:
        EvaluationResult with classification and all relevant context
    """
    question = db.query(PitfallQuestion).filter(
        PitfallQuestion.question_id == question_id
    ).first()

    if not question:
        # Graceful fallback: cannot evaluate without a question
        return EvaluationResult(
            classification="UNKNOWN",
            is_correct=False,
            confidence=confidence,
        )

    is_correct = (selected_option.upper() == question.correct_option.upper())

    # ── Correct answer ──────────────────────────────────────────
    if is_correct:
        if confidence >= HIGH_CONFIDENCE_MIN:
            classification = "MASTERY"
        else:
            # Correct but under-confident — still mastery, flag calibration
            classification = "MASTERY"
        return EvaluationResult(
            classification=classification,
            is_correct=True,
            confidence=confidence,
            question=question,
        )

    # ── Incorrect answer ─────────────────────────────────────────
    # Look up if this option maps to a specific pitfall
    option_mapping = db.query(PitfallOptionMapping).filter(
        PitfallOptionMapping.question_id == question_id,
        PitfallOptionMapping.option_key == selected_option.upper()
    ).first()

    pitfall = None
    pitfall_id = None
    misconception_hint = None

    if option_mapping and option_mapping.pitfall_id:
        pitfall = db.query(Pitfall).filter(
            Pitfall.pitfall_id == option_mapping.pitfall_id
        ).first()
        pitfall_id = option_mapping.pitfall_id
        misconception_hint = option_mapping.misconception_hint

    # High confidence + maps to pitfall → MISCONCEPTION
    if confidence >= HIGH_CONFIDENCE_MIN and pitfall_id:
        classification = "MISCONCEPTION"
    # Low confidence → KNOWLEDGE_GAP
    elif confidence <= LOW_CONFIDENCE_MAX:
        classification = "KNOWLEDGE_GAP"
    # Medium confidence or no pitfall mapping → UNCERTAINTY
    else:
        classification = "UNCERTAINTY"

    return EvaluationResult(
        classification=classification,
        is_correct=False,
        confidence=confidence,
        pitfall_id=pitfall_id,
        misconception_hint=misconception_hint,
        pitfall=pitfall,
        question=question,
    )
