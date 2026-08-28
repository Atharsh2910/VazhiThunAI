"""
Pitfall Analytics — population-level aggregation and pitfall scoring.

Calculates:
  prevalence            — fraction of learners who got the question wrong
  consistency           — concentration of wrong answers in one specific option
  high_confidence_error_rate — fraction of wrong answers that had high confidence
  recurrence            — fraction of learners who failed the same question more than once
  pitfall_score         — weighted combination (0.30/0.25/0.20/0.15/0.10)

Score thresholds (configurable):
  0.00-0.39 → insufficient_evidence
  0.40-0.59 → emerging
  0.60-0.79 → likely
  0.80-1.00 → confirmed
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.orm import (
    PitfallAttempt, PitfallQuestion, Pitfall, Concept, LearnerPitfall
)

# Configurable scoring weights
WEIGHTS = {
    "prevalence": 0.30,
    "consistency": 0.25,
    "high_confidence_error_rate": 0.20,
    "recurrence": 0.15,
    "downstream_impact": 0.10,
}

# Configurable thresholds
SCORE_THRESHOLDS = {
    "insufficient_evidence": (0.0, 0.40),
    "emerging": (0.40, 0.60),
    "likely": (0.60, 0.80),
    "confirmed": (0.80, 1.01),
}

# Minimum attempts before a pitfall is considered statistically meaningful
MIN_ATTEMPTS_FOR_EVIDENCE = 3


def classify_score(score: float) -> str:
    for label, (low, high) in SCORE_THRESHOLDS.items():
        if low <= score < high:
            return label
    return "insufficient_evidence"


def compute_pitfall_analytics(db: Session, pitfall_id: str) -> Dict[str, Any]:
    """
    Compute population-level analytics for a single pitfall.
    Returns a dict with all evidence metrics and the final pitfall_score.
    """
    # Get all questions belonging to this pitfall
    questions = db.query(PitfallQuestion).filter(
        PitfallQuestion.pitfall_id == pitfall_id
    ).all()
    question_ids = [q.question_id for q in questions]

    if not question_ids:
        return _empty_analytics(pitfall_id)

    # All attempts for these questions
    attempts = db.query(PitfallAttempt).filter(
        PitfallAttempt.question_id.in_(question_ids)
    ).all()

    total_attempts = len(attempts)
    if total_attempts < MIN_ATTEMPTS_FOR_EVIDENCE:
        return _empty_analytics(pitfall_id, total_attempts)

    unique_learners = len(set(a.learner_id for a in attempts))
    wrong_attempts = [a for a in attempts if not a.is_correct]
    wrong_count = len(wrong_attempts)

    # ── Prevalence ──────────────────────────────────────────────
    # Fraction of attempts that were wrong
    prevalence = wrong_count / total_attempts if total_attempts > 0 else 0.0

    # ── Consistency ─────────────────────────────────────────────
    # How concentrated are wrong answers in a single option
    # (1.0 = all wrong answers chose the same option)
    option_counts: Dict[str, int] = {}
    for a in wrong_attempts:
        if a.selected_option:
            option_counts[a.selected_option] = option_counts.get(a.selected_option, 0) + 1

    if wrong_count > 0 and option_counts:
        max_option_count = max(option_counts.values())
        consistency = max_option_count / wrong_count
    else:
        consistency = 0.0

    # ── High-confidence error rate ───────────────────────────────
    high_conf_wrong = [a for a in wrong_attempts if a.confidence and a.confidence >= 4]
    high_confidence_error_rate = (
        len(high_conf_wrong) / wrong_count if wrong_count > 0 else 0.0
    )

    # ── Recurrence ──────────────────────────────────────────────
    # Fraction of learners who failed the same question more than once
    from collections import Counter
    learner_wrong_counts = Counter(a.learner_id for a in wrong_attempts)
    repeated_learners = sum(1 for cnt in learner_wrong_counts.values() if cnt > 1)
    recurrence = repeated_learners / unique_learners if unique_learners > 0 else 0.0

    # ── Downstream impact ────────────────────────────────────────
    # Fraction of learners with active (unresolved) pitfall records for this pitfall
    total_lp = db.query(LearnerPitfall).filter(
        LearnerPitfall.pitfall_id == pitfall_id
    ).count()
    unresolved_lp = db.query(LearnerPitfall).filter(
        LearnerPitfall.pitfall_id == pitfall_id,
        LearnerPitfall.status != "RESOLVED"
    ).count()
    downstream_impact = unresolved_lp / total_lp if total_lp > 0 else 0.0

    # ── Pitfall score ────────────────────────────────────────────
    pitfall_score = (
        WEIGHTS["prevalence"] * prevalence
        + WEIGHTS["consistency"] * consistency
        + WEIGHTS["high_confidence_error_rate"] * high_confidence_error_rate
        + WEIGHTS["recurrence"] * recurrence
        + WEIGHTS["downstream_impact"] * downstream_impact
    )
    pitfall_score = min(1.0, max(0.0, pitfall_score))

    return {
        "pitfall_id": pitfall_id,
        "total_attempts": total_attempts,
        "unique_learners": unique_learners,
        "wrong_count": wrong_count,
        "prevalence": round(prevalence, 3),
        "consistency": round(consistency, 3),
        "high_confidence_error_rate": round(high_confidence_error_rate, 3),
        "recurrence": round(recurrence, 3),
        "downstream_impact": round(downstream_impact, 3),
        "wrong_option_distribution": option_counts,
        "pitfall_score": round(pitfall_score, 3),
        "status": classify_score(pitfall_score),
    }


def _empty_analytics(pitfall_id: str, attempts: int = 0) -> Dict[str, Any]:
    return {
        "pitfall_id": pitfall_id,
        "total_attempts": attempts,
        "unique_learners": 0,
        "wrong_count": 0,
        "prevalence": 0.0,
        "consistency": 0.0,
        "high_confidence_error_rate": 0.0,
        "recurrence": 0.0,
        "downstream_impact": 0.0,
        "wrong_option_distribution": {},
        "pitfall_score": 0.0,
        "status": "insufficient_evidence",
    }


def get_all_pitfall_analytics(db: Session) -> List[Dict[str, Any]]:
    """
    Compute analytics for ALL pitfalls and return sorted by pitfall_score desc.
    """
    pitfalls = db.query(Pitfall).filter(Pitfall.status == "active").all()
    results = []
    for pitfall in pitfalls:
        analytics = compute_pitfall_analytics(db, pitfall.pitfall_id)
        # Attach pitfall metadata
        concept = db.query(Concept).filter(
            Concept.concept_id == pitfall.concept_id
        ).first()
        analytics["title"] = pitfall.title
        analytics["severity"] = pitfall.severity
        analytics["concept_name"] = concept.name if concept else "Unknown"
        analytics["skill_id"] = concept.skill_id if concept else None
        results.append(analytics)

    results.sort(key=lambda x: x["pitfall_score"], reverse=True)
    return results


def get_learner_affected_percentage(db: Session, pitfall_id: str) -> float:
    """Returns the percentage of all learners affected by this pitfall."""
    from app.models.orm import Learner
    total_learners = db.query(Learner).count()
    if total_learners == 0:
        return 0.0

    affected = db.query(PitfallAttempt).filter(
        PitfallAttempt.matched_pitfall_id == pitfall_id,
        PitfallAttempt.is_correct == False
    ).distinct(PitfallAttempt.learner_id).count()

    return round((affected / total_learners) * 100, 1)
