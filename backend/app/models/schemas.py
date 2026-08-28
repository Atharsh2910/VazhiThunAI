from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class UserSchema(BaseModel):
    id: str
    email: str
    display_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class LearnerProfileSchema(BaseModel):
    id: str
    user_id: str
    education: Optional[str] = None
    current_role: Optional[str] = None
    experience_years: Optional[int] = None
    interests: Optional[List[str]] = None
    preferred_formats: Optional[List[str]] = None
    weekly_hours: Optional[float] = None
    timezone: Optional[str] = None
    learning_preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class GoalSchema(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    goal_type: Optional[str] = None
    target_role: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class SkillSchema(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    domain: Optional[str] = None
    difficulty: Optional[float] = None
    parent_skill_id: Optional[str] = None

    class Config:
        from_attributes = True

class LearningPathSchema(BaseModel):
    id: str
    learner_id: str
    goal_id: str
    version: int
    status: str
    estimated_hours: Optional[float] = None
    estimated_completion_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResourceSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    provider: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None
    difficulty: Optional[float] = None
    duration_minutes: Optional[int] = None
    language: Optional[str] = None
    quality_score: Optional[float] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True
