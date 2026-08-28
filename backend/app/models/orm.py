from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
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
