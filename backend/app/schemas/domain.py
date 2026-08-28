from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    id: UUID
    email: str
    display_name: str
    status: str
    created_at: datetime
    updated_at: datetime

class LearnerProfile(BaseModel):
    id: UUID
    user_id: UUID
    education: Optional[str] = None
    current_role: Optional[str] = None
    experience_years: Optional[int] = None
    interests: List[str] = []
    preferred_formats: List[str] = []
    weekly_hours: Optional[int] = None
    timezone: Optional[str] = None
    learning_preferences: dict = {}
    created_at: datetime
    updated_at: datetime

class Goal(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    goal_type: str
    target_role: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = 0
    status: str
    created_at: datetime
    updated_at: datetime

class PathItem(BaseModel):
    id: UUID
    path_id: UUID
    resource_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    skill_id: UUID
    sequence_order: int
    phase: str
    required: bool = True
    estimated_minutes: int
    status: str
    reason: Optional[str] = None

class LearningPath(BaseModel):
    id: UUID
    learner_id: UUID
    goal_id: UUID
    version: int
    status: str
    estimated_hours: int
    estimated_completion_date: Optional[datetime] = None
    items: List[PathItem] = []
    created_at: datetime
    updated_at: datetime
