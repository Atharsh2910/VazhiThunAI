from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    display_name = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    profile = relationship("LearnerProfile", back_populates="user", uselist=False)
    goals = relationship("Goal", back_populates="user")
    paths = relationship("LearningPath", back_populates="learner")

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    education = Column(String)
    current_role = Column(String)
    experience_years = Column(Integer)
    interests = Column(JSON)
    preferred_formats = Column(JSON)
    weekly_hours = Column(Float)
    timezone = Column(String)
    learning_preferences = Column(JSON)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="profile")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    goal_type = Column(String)
    target_role = Column(String)
    deadline = Column(DateTime)
    priority = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="goals")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    domain = Column(String)
    difficulty = Column(Float)
    parent_skill_id = Column(String, ForeignKey("skills.id"))
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(String, primary_key=True, index=True)
    learner_id = Column(String, ForeignKey("users.id"))
    goal_id = Column(String, ForeignKey("goals.id"))
    version = Column(Integer)
    status = Column(String)
    estimated_hours = Column(Float)
    estimated_completion_date = Column(DateTime)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    learner = relationship("User", back_populates="paths")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    provider = Column(String)
    url = Column(String)
    resource_type = Column(String)
    difficulty = Column(Float)
    duration_minutes = Column(Integer)
    language = Column(String)
    quality_score = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
