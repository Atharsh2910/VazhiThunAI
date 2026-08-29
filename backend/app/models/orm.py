from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    display_name = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    education = Column(String, nullable=True)
    current_role = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    interests = Column(JSON, nullable=True)
    preferred_formats = Column(JSON, nullable=True)
    weekly_hours = Column(Float, nullable=True)
    timezone = Column(String, nullable=True)
    learning_preferences = Column(JSON, nullable=True)

class Learner(Base):
    __tablename__ = "learners"
    learner_id = Column(String, primary_key=True, index=True)
    full_name = Column(String)
    gender = Column(String)
    city = Column(String)
    state = Column(String)
    college = Column(String)
    degree = Column(String)
    graduation_year = Column(Integer)
    current_role = Column(String)
    experience_level = Column(String)
    experience_years_numeric = Column(Float)
    weekly_study_hours = Column(Float)
    preferred_learning_format = Column(String)
    target_goal = Column(String)
    goal_deadline_months = Column(Float)
    preferred_language = Column(String)
    timezone = Column(String)

class Skill(Base):
    __tablename__ = "skills"
    skill_id = Column(String, primary_key=True, index=True)
    skill_name = Column(String)
    domain = Column(String)
    difficulty_tier = Column(String)
    difficulty_score = Column(Float)
    decay_rate = Column(Float)

class LearnerSkill(Base):
    __tablename__ = "learner_skills"
    learner_skill_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    skill_id = Column(String, ForeignKey("skills.skill_id"))
    skill_name = Column(String)
    mastery_score = Column(Float)
    mastery_band = Column(String)
    confidence_score = Column(Float)
    evidence_strength = Column(Float)
    source = Column(String)

class Assessment(Base):
    __tablename__ = "assessments"
    assessment_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    assessment_type = Column(String)
    skill_id = Column(String, ForeignKey("skills.skill_id"))
    skill_name = Column(String)
    num_questions = Column(Integer)
    difficulty_score = Column(Float)
    pass_threshold = Column(Float)

class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"
    attempt_id = Column(String, primary_key=True, index=True)
    assessment_id = Column(String, ForeignKey("assessments.assessment_id"))
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    skill_name = Column(String)
    score = Column(Float)
    passed = Column(Boolean)
    duration_seconds = Column(Integer)
    self_reported_confidence = Column(Float)

class Goal(Base):
    __tablename__ = "goals"
    goal_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    goal_title = Column(String)
    goal_type = Column(String)
    target_role = Column(String)
    core_target_skills = Column(Text)
    deadline_months = Column(Float)
    weekly_hours_committed = Column(Float)
    status = Column(String)
    priority = Column(String)

class LearningPath(Base):
    __tablename__ = "learning_paths"
    path_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    goal_id = Column(String, ForeignKey("goals.goal_id"))
    target_role = Column(String)
    total_required_items = Column(Integer)
    total_estimated_hours = Column(Float)
    weekly_hours_committed = Column(Float)
    projected_weeks_to_complete = Column(Float)
    deadline_weeks = Column(Float)
    status = Column(String)
    feasible_within_deadline = Column(Boolean)

class Resource(Base):
    __tablename__ = "resources"
    resource_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    provider = Column(String)
    resource_type = Column(String)
    format = Column(String)
    primary_skill_id = Column(String, ForeignKey("skills.skill_id"))
    primary_skill_name = Column(String)
    domain = Column(String)
    difficulty_score = Column(Float)
    duration_minutes = Column(Integer)
    language = Column(String)
    quality_score = Column(Float)
    status = Column(String)

class PathItem(Base):
    __tablename__ = "path_items"
    path_item_id = Column(String, primary_key=True, index=True)
    path_id = Column(String, ForeignKey("learning_paths.path_id"))
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    resource_id = Column(String, ForeignKey("resources.resource_id"))
    skill_id = Column(String, ForeignKey("skills.skill_id"))
    skill_name = Column(String)
    sequence_order = Column(Integer)
    status = Column(String)
    estimated_minutes = Column(Integer)
    required = Column(Boolean)

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    target_role = Column(String)
    difficulty_tier = Column(String)
    estimated_hours = Column(Float)
    portfolio_value_score = Column(Float)
    primary_skills = Column(Text)

class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"
    recommendation_event_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    resource_id = Column(String, ForeignKey("resources.resource_id"))
    skill_name = Column(String)
    score = Column(Float)
    reason = Column(Text)
    accepted = Column(Boolean)

class ResourceSkill(Base):
    __tablename__ = "resource_skills"
    mapping_id = Column(String, primary_key=True, index=True)
    resource_id = Column(String, ForeignKey("resources.resource_id"))
    skill_id = Column(String, ForeignKey("skills.skill_id"))
    skill_name = Column(String)
    coverage_score = Column(Float)

class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"
    prerequisite_edge_id = Column(String, primary_key=True, index=True)
    skill_id = Column(String, ForeignKey("skills.skill_id"))
    skill_name = Column(String)
    prerequisite_skill_id = Column(String, ForeignKey("skills.skill_id"))
    prerequisite_skill_name = Column(String)
    relationship_strength = Column(Float)

class ChatIntentDataset(Base):
    __tablename__ = "chat_intent_dataset"
    message_id = Column(String, primary_key=True, index=True)
    message_text = Column(Text)
    intent_label = Column(String)

class FeedbackDataset(Base):
    __tablename__ = "feedback_dataset"
    feedback_id = Column(String, primary_key=True, index=True)
    feedback_text = Column(Text)
    feedback_type = Column(String)


# ─────────────────────────────────────────────────
# Pitfall & Misconception Detection Models
# ─────────────────────────────────────────────────

class Concept(Base):
    """A granular concept within a skill that can have misconceptions."""
    __tablename__ = "concepts"
    concept_id = Column(String, primary_key=True, index=True)
    skill_id = Column(String, ForeignKey("skills.skill_id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    pitfalls = relationship("Pitfall", back_populates="concept")


class Pitfall(Base):
    """A documented misconception or common pitfall for a concept."""
    __tablename__ = "pitfalls"
    pitfall_id = Column(String, primary_key=True, index=True)
    concept_id = Column(String, ForeignKey("concepts.concept_id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    # The wrong mental model learners typically hold
    misconception = Column(Text)
    # The correct explanation to replace the misconception
    correct_mental_model = Column(Text)
    severity = Column(String, default="medium")   # low / medium / high
    source = Column(String, default="expert")      # expert / population
    # Deterministic fallback explanation (used when LLM is unavailable)
    remediation_text = Column(Text)
    status = Column(String, default="active")      # active / deprecated
    created_at = Column(DateTime, default=datetime.utcnow)

    concept = relationship("Concept", back_populates="pitfalls")
    questions = relationship("PitfallQuestion", back_populates="pitfall")
    learner_pitfalls = relationship("LearnerPitfall", back_populates="pitfall")


class PitfallQuestion(Base):
    """A multiple-choice question designed to detect a specific pitfall."""
    __tablename__ = "pitfall_questions"
    question_id = Column(String, primary_key=True, index=True)
    pitfall_id = Column(String, ForeignKey("pitfalls.pitfall_id"))
    concept_id = Column(String, ForeignKey("concepts.concept_id"))
    question_text = Column(Text, nullable=False)
    # Stored as JSON: {"A": "...", "B": "...", "C": "...", "D": "..."}
    options = Column(JSON, nullable=False)
    correct_option = Column(String, nullable=False)  # e.g. "A"
    explanation = Column(Text)  # explanation of the correct answer

    pitfall = relationship("Pitfall", back_populates="questions")
    option_mappings = relationship("PitfallOptionMapping", back_populates="question")
    attempts = relationship("PitfallAttempt", back_populates="question")


class PitfallOptionMapping(Base):
    """Maps each incorrect option to a specific pitfall/misconception."""
    __tablename__ = "pitfall_option_mappings"
    mapping_id = Column(String, primary_key=True, index=True)
    question_id = Column(String, ForeignKey("pitfall_questions.question_id"))
    option_key = Column(String, nullable=False)     # e.g. "B"
    pitfall_id = Column(String, ForeignKey("pitfalls.pitfall_id"), nullable=True)
    # Short explanation of WHY this option indicates that misconception
    misconception_hint = Column(Text)

    question = relationship("PitfallQuestion", back_populates="option_mappings")


class LearnerPitfall(Base):
    """Tracks a learner's relationship with a specific pitfall over time."""
    __tablename__ = "learner_pitfalls"
    id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    pitfall_id = Column(String, ForeignKey("pitfalls.pitfall_id"))
    # Status lifecycle: DETECTED → REMEDIATION → VERIFICATION → RESOLVED / UNRESOLVED
    status = Column(String, default="DETECTED")
    confidence_score = Column(Float, default=0.0)   # learner's self-reported confidence
    evidence_count = Column(Integer, default=1)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=1)
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_detected = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    pitfall = relationship("Pitfall", back_populates="learner_pitfalls")


class PitfallAttempt(Base):
    """Records each individual pitfall check attempt by a learner."""
    __tablename__ = "pitfall_attempts"
    attempt_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"))
    question_id = Column(String, ForeignKey("pitfall_questions.question_id"))
    selected_option = Column(String)   # e.g. "B"
    is_correct = Column(Boolean)
    # Learner's self-reported confidence 1-5
    confidence = Column(Integer, default=3)
    # Classification result: MASTERY / KNOWLEDGE_GAP / MISCONCEPTION
    classification = Column(String)
    # ID of the pitfall matched (if MISCONCEPTION)
    matched_pitfall_id = Column(String, ForeignKey("pitfalls.pitfall_id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    question = relationship("PitfallQuestion", back_populates="attempts")


# ─────────────────────────────────────────────────
# Adaptive Learning Path / Replanning Engine Models
# ─────────────────────────────────────────────────

class AdaptationEvent(Base):
    """Immutable audit log of every adaptation made to a learner's path."""
    __tablename__ = "adaptation_events"

    event_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"), nullable=False)
    event_type = Column(String, nullable=False)   # RESOURCE_REPLACED | REMEDIATION_INSERTED | PATH_REPLANNED | ITEM_SKIPPED | HOURS_UPDATED | DEADLINE_UPDATED
    trigger = Column(String, nullable=False)       # TOO_HARD | TOO_EASY | ALREADY_KNOWN | KNOWLEDGE_GAP | MISCONCEPTION | FALLING_BEHIND | HOURS_CHANGE | DEADLINE_CHANGE | FASTER_PATH | LIGHTER_PATH
    affected_item_id = Column(String, nullable=True)       # path_item_id
    old_resource_id = Column(String, nullable=True)
    new_resource_id = Column(String, nullable=True)
    old_path_snapshot = Column(JSON, nullable=True)        # serialized list of path item ids before change
    new_path_snapshot = Column(JSON, nullable=True)        # serialized list of path item ids after change
    reason = Column(Text, nullable=True)                   # structured reason string
    explanation = Column(Text, nullable=True)              # human-readable explanation (from LLM or deterministic)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AdaptivePathState(Base):
    """
    Live per-learner adaptive state for the ML Engineer path.
    Stores the path as a JSON array of path item descriptors so we can
    reconstruct both the current path and its history without losing data.
    """
    __tablename__ = "adaptive_path_states"

    state_id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("learners.learner_id"), nullable=False, unique=True)
    # Current path: JSON list of dicts with keys:
    #   id, title, skill_id, skill_name, resource_id, sequence_order,
    #   status, estimated_minutes, required, phase, item_type
    #   item_type: 'resource' | 'remediation' | 'verification' | 'project'
    current_path = Column(JSON, nullable=False, default=list)
    # Settings
    weekly_hours = Column(Float, default=8.0)
    deadline_weeks = Column(Float, default=20.0)
    # Progress tracking
    total_hours_logged = Column(Float, default=0.0)
    current_item_index = Column(Integer, default=0)
    # Computed fields updated on every adaptation
    remaining_hours = Column(Float, default=0.0)
    projected_completion_weeks = Column(Float, default=0.0)
    is_on_track = Column(Boolean, default=True)
    # Version counter for optimistic concurrency
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
