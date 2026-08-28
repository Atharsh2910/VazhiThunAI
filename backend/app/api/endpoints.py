from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session

from app.schemas.base import APIResponse, MetaResponse
from app.core.config import supabase
from app.models.database import SessionLocal
from app.models.orm import User, LearnerProfile, Goal, LearningPath
from app.services.db_services import get_learner_profile, create_goal, get_goal, save_learning_path
from app.services.chat_service import chat_service
from app.ai.graph import primary_graph

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

# 17.1 Authentication
@router.post("/auth/register", response_model=APIResponse[Dict[str, Any]])
def auth_register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Supabase sign up
        auth_response = supabase.auth.sign_up({
            "email": request.email, 
            "password": request.password, 
            "options": {"data": {"display_name": request.display_name}}
        })
        user_id = auth_response.user.id
        
        # Insert into users table
        new_user = User(
            id=user_id,
            email=request.email,
            display_name=request.display_name,
            status="active"
        )
        db.add(new_user)
        
        # Insert into learner_profiles table
        new_profile = LearnerProfile(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        db.add(new_profile)
        db.commit()
        
        return APIResponse(
            success=True, 
            data={"user_id": user_id, "message": "User registered successfully"}, 
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/login", response_model=APIResponse[Dict[str, Any]])
def auth_login(request: LoginRequest):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        return APIResponse(
            success=True, 
            data={
                "access_token": auth_response.session.access_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                }
            }, 
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/auth/logout", response_model=APIResponse[Dict[str, Any]])
def auth_logout():
    return APIResponse(success=True, data={"status": "logged_out"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/auth/me", response_model=APIResponse[Dict[str, Any]])
def auth_me():
    return APIResponse(success=True, data={"id": "user1", "email": "test@test.com"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.2 Learner
@router.get("/learners/me", response_model=APIResponse[Dict[str, Any]])
def get_learner_profile_endpoint(db: Session = Depends(get_db)):
    # Assuming user_id is extracted from a verified token, for now hardcoding to "user1"
    profile = get_learner_profile(db, "user1")
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return APIResponse(success=True, data={"id": profile.id, "user_id": profile.user_id}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.patch("/learners/me", response_model=APIResponse[Dict[str, Any]])
def update_learner_profile_endpoint(db: Session = Depends(get_db)):
    return APIResponse(success=True, data={"status": "updated"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/learners/me/skills", response_model=APIResponse[Dict[str, Any]])
def get_learner_skills():
    return APIResponse(success=True, data={"skills": []}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.3 Goals
class GoalRequest(BaseModel):
    learner_id: str
    goal_title: str
    goal_type: str
    target_role: str
    deadline_months: float
    weekly_hours_committed: float

@router.post("/goals", response_model=APIResponse[Dict[str, Any]])
def create_goal_endpoint(request: GoalRequest, db: Session = Depends(get_db)):
    goal = create_goal(
        db=db,
        learner_id=request.learner_id,
        goal_title=request.goal_title,
        goal_type=request.goal_type,
        target_role=request.target_role,
        deadline_months=request.deadline_months,
        weekly_hours_committed=request.weekly_hours_committed
    )
    return APIResponse(success=True, data={"id": goal.goal_id, "title": goal.goal_title}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/goals", response_model=APIResponse[Dict[str, Any]])
def get_goals():
    # Placeholder for getting multiple goals
    return APIResponse(success=True, data={"goals": []}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/goals/{goal_id}", response_model=APIResponse[Dict[str, Any]])
def get_goal_endpoint(goal_id: str, db: Session = Depends(get_db)):
    goal = get_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return APIResponse(success=True, data={"id": goal.goal_id, "title": goal.goal_title}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.patch("/goals/{goal_id}", response_model=APIResponse[Dict[str, Any]])
def update_goal(goal_id: str):
    return APIResponse(success=True, data={"status": "updated"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.4 AI Chat
class ChatRequest(BaseModel):
    user_message: str
    session_id: str = "default_session"
    learner_id: str = "default_learner"
    history: List[Dict[str, str]] = []

@router.post("/chat", response_model=APIResponse[Dict[str, Any]])
def chat_endpoint(request: ChatRequest):
    response_content = chat_service.generate_chat_response(
        user_message=request.user_message,
        history=request.history
    )
    return APIResponse(success=True, data={"response": response_content}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/chat/stream", response_model=APIResponse[Dict[str, Any]])
def chat_stream(request: ChatRequest):
    return APIResponse(success=True, data={"response": "mock stream"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.5 Diagnostics
@router.post("/diagnostics/start", response_model=APIResponse[Dict[str, Any]])
def diagnostics_start():
    return APIResponse(success=True, data={"session_id": "diag1"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/diagnostics/{session_id}/answer", response_model=APIResponse[Dict[str, Any]])
def diagnostics_answer(session_id: str):
    return APIResponse(success=True, data={"status": "answered"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/diagnostics/{session_id}", response_model=APIResponse[Dict[str, Any]])
def diagnostics_get(session_id: str):
    return APIResponse(success=True, data={"id": session_id}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.6 Learning Paths
class GeneratePathRequest(BaseModel):
    learner_id: str
    goal_id: str
    target_role: str
    deadline_weeks: float
    user_message: str = "Generate my path"

@router.post("/paths/generate", response_model=APIResponse[Dict[str, Any]])
def paths_generate(request: GeneratePathRequest, db: Session = Depends(get_db)):
    initial_state = {
        "learner_id": request.learner_id,
        "session_id": str(uuid.uuid4()),
        "user_message": request.user_message,
        "intent": {},
        "learner_profile": {},
        "goal": {},
        "skill_context": [],
        "skill_gaps": [],
        "retrieved_resources": [],
        "ranked_resources": [],
        "candidate_path": [],
        "validated_path": [],
        "explanation": {},
        "response": {},
        "confidence": 0.0,
        "citations": [],
        "events": []
    }
    final_state = primary_graph.invoke(initial_state)
    
    # Save the resulting path to DB
    path = save_learning_path(
        db=db,
        learner_id=request.learner_id,
        goal_id=request.goal_id,
        target_role=request.target_role,
        total_estimated_hours=40.0, # Placeholder
        deadline_weeks=request.deadline_weeks
    )
    
    return APIResponse(success=True, data={"path_id": path.path_id, "state": final_state}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/paths", response_model=APIResponse[Dict[str, Any]])
def get_paths(db: Session = Depends(get_db)):
    return APIResponse(success=True, data={"paths": []}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/paths/{path_id}", response_model=APIResponse[Dict[str, Any]])
def get_path_endpoint(path_id: str, db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter(LearningPath.path_id == path_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    return APIResponse(success=True, data={"id": path.path_id, "target_role": path.target_role}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/paths/{path_id}/replan", response_model=APIResponse[Dict[str, Any]])
def path_replan(path_id: str):
    return APIResponse(success=True, data={"status": "replanned"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/paths/{path_id}/simulate", response_model=APIResponse[Dict[str, Any]])
def path_simulate(path_id: str):
    return APIResponse(success=True, data={"status": "simulated"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.7 Recommendations
@router.get("/recommendations", response_model=APIResponse[Dict[str, Any]])
def get_recommendations():
    return APIResponse(success=True, data={"recommendations": []}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/recommendations/next", response_model=APIResponse[Dict[str, Any]])
def get_next_recommendation():
    return APIResponse(success=True, data={"action": "next_action"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/recommendations/{id}/feedback", response_model=APIResponse[Dict[str, Any]])
def recommendation_feedback(id: str):
    return APIResponse(success=True, data={"status": "feedback_received"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.8 Progress
@router.get("/progress", response_model=APIResponse[Dict[str, Any]])
def get_progress():
    return APIResponse(success=True, data={"progress": "data"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/progress/events", response_model=APIResponse[Dict[str, Any]])
def progress_events():
    return APIResponse(success=True, data={"status": "event_recorded"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/progress/skills", response_model=APIResponse[Dict[str, Any]])
def progress_skills():
    return APIResponse(success=True, data={"skills": []}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/progress/milestones", response_model=APIResponse[Dict[str, Any]])
def progress_milestones():
    return APIResponse(success=True, data={"milestones": []}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.9 Assessments
@router.get("/assessments/{id}", response_model=APIResponse[Dict[str, Any]])
def get_assessment(id: str):
    return APIResponse(success=True, data={"id": id}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.post("/assessments/{id}/attempts", response_model=APIResponse[Dict[str, Any]])
def assessment_attempts(id: str):
    return APIResponse(success=True, data={"status": "attempted"}, meta=MetaResponse(request_id=str(uuid.uuid4())))
