from sqlalchemy.orm import Session
from app.models.orm import LearnerProfile, Goal, LearningPath, PathItem
from typing import Optional, List
import uuid

def get_learner_profile(db: Session, user_id: str) -> Optional[LearnerProfile]:
    return db.query(LearnerProfile).filter(LearnerProfile.user_id == user_id).first()

def create_goal(db: Session, learner_id: str, goal_title: str, goal_type: str, target_role: str, deadline_months: float, weekly_hours_committed: float) -> Goal:
    new_goal = Goal(
        goal_id=str(uuid.uuid4()),
        learner_id=learner_id,
        goal_title=goal_title,
        goal_type=goal_type,
        target_role=target_role,
        deadline_months=deadline_months,
        weekly_hours_committed=weekly_hours_committed,
        status="active"
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

def get_goal(db: Session, goal_id: str) -> Optional[Goal]:
    return db.query(Goal).filter(Goal.goal_id == goal_id).first()

def save_learning_path(db: Session, learner_id: str, goal_id: str, target_role: str, total_estimated_hours: float, deadline_weeks: float) -> LearningPath:
    new_path = LearningPath(
        path_id=str(uuid.uuid4()),
        learner_id=learner_id,
        goal_id=goal_id,
        target_role=target_role,
        total_estimated_hours=total_estimated_hours,
        deadline_weeks=deadline_weeks,
        status="active",
        feasible_within_deadline=True
    )
    db.add(new_path)
    db.commit()
    db.refresh(new_path)
    return new_path

def save_path_items(db: Session, path_items_data: List[dict]) -> List[PathItem]:
    saved_items = []
    for item_data in path_items_data:
        new_item = PathItem(
            path_item_id=str(uuid.uuid4()),
            **item_data
        )
        db.add(new_item)
        saved_items.append(new_item)
    db.commit()
    for item in saved_items:
        db.refresh(item)
    return saved_items
