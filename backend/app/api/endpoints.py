from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session

from app.schemas.base import APIResponse, MetaResponse
from app.core.config import supabase
from app.models.database import SessionLocal
from app.models.orm import User, LearnerProfile, Goal, LearningPath, PathItem, LearnerSkill, LearnerPitfall, Pitfall as PitfallModel
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

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    if authorization and authorization.startswith("Bearer hackathon_token_"):
        return authorization.replace("Bearer hackathon_token_", "").strip()
    return "user1"

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    career_goal: Optional[str] = None
    career_path: Optional[str] = None
    current_level: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    skills: Optional[List[str]] = None
    avatar: Optional[str] = None

# 17.1 Authentication
@router.post("/auth/register", response_model=APIResponse[Dict[str, Any]])
def auth_register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Check if email exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")

        user_id = str(uuid.uuid4())
        
        # Insert into users table
        new_user = User(
            id=user_id,
            email=request.email,
            password_hash=request.password,
            display_name=request.display_name,
            status="active"
        )
        db.add(new_user)
        db.flush()
        
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/login", response_model=APIResponse[Dict[str, Any]])
def auth_login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        if user.password_hash != request.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        # Generate a simple mock token for hackathon
        mock_token = f"hackathon_token_{user.id}"
        
        return APIResponse(
            success=True, 
            data={
                "access_token": mock_token,
                "user": {
                    "id": user.id,
                    "email": user.email
                }
            }, 
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/logout", response_model=APIResponse[Dict[str, Any]])
def auth_logout():
    return APIResponse(success=True, data={"status": "logged_out"}, meta=MetaResponse(request_id=str(uuid.uuid4())))

@router.get("/auth/me", response_model=APIResponse[Dict[str, Any]])
def auth_me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    user_id = get_current_user_id(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse(success=True, data={"id": "user1", "email": "test@test.com"}, meta=MetaResponse(request_id=str(uuid.uuid4())))
    return APIResponse(success=True, data={"id": user.id, "email": user.email, "display_name": user.display_name}, meta=MetaResponse(request_id=str(uuid.uuid4())))

# 17.2 Learner
@router.get("/learners/me", response_model=APIResponse[Dict[str, Any]])
def get_learner_profile_endpoint(db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization)
    profile = get_learner_profile(db, user_id)
    
    if not profile:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create a new profile on-the-fly for newly registered users
        profile = LearnerProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            learning_preferences={}
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    user = db.query(User).filter(User.id == user_id).first()
    display_name = user.display_name if user else "Learner"
    email = user.email if user else ""
    
    prefs = profile.learning_preferences or {}
    if not isinstance(prefs, dict):
        prefs = {}

    return APIResponse(
        success=True, 
        data={
            "id": profile.id, 
            "user_id": profile.user_id,
            "display_name": display_name,
            "email": email,
            "education": profile.education,
            "current_role": profile.current_role,
            "experience_years": profile.experience_years,
            "weekly_hours": profile.weekly_hours,
            "bio": prefs.get("bio", ""),
            "career_goal": prefs.get("career_goal", ""),
            "career_path": prefs.get("career_path", ""),
            "current_level": prefs.get("current_level", ""),
            "github_url": prefs.get("github_url", ""),
            "linkedin_url": prefs.get("linkedin_url", ""),
            "leetcode_url": prefs.get("leetcode_url", ""),
            "skills": prefs.get("skills", []),
            "avatar": prefs.get("avatar", ""),
        }, 
        meta=MetaResponse(request_id=str(uuid.uuid4()))
    )

@router.patch("/learners/me", response_model=APIResponse[Dict[str, Any]])
def update_learner_profile_endpoint(
    request: ProfileUpdateRequest, 
    db: Session = Depends(get_db), 
    authorization: Optional[str] = Header(None)
):
    user_id = get_current_user_id(authorization)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    profile = get_learner_profile(db, user_id)
    if not profile:
        profile = LearnerProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            learning_preferences={}
        )
        db.add(profile)
        db.flush()

    if request.display_name is not None:
        user.display_name = request.display_name

    prefs = dict(profile.learning_preferences) if profile.learning_preferences else {}

    if request.bio is not None:
        prefs["bio"] = request.bio
    if request.career_goal is not None:
        prefs["career_goal"] = request.career_goal
    if request.career_path is not None:
        prefs["career_path"] = request.career_path
    if request.current_level is not None:
        prefs["current_level"] = request.current_level
    if request.github_url is not None:
        prefs["github_url"] = request.github_url
    if request.linkedin_url is not None:
        prefs["linkedin_url"] = request.linkedin_url
    if request.leetcode_url is not None:
        prefs["leetcode_url"] = request.leetcode_url
    if request.skills is not None:
        prefs["skills"] = request.skills
    if request.avatar is not None:
        prefs["avatar"] = request.avatar

    profile.learning_preferences = prefs
    
    if request.career_path is not None:
        profile.current_role = request.career_path

    db.commit()
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
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    from app.models.orm import Learner, LearnerSkill, Assessment, AssessmentAttempt, Project, Resource

    # 1. Full Learner record (no password)
    learner = db.query(Learner).filter(Learner.learner_id == request.learner_id).first()
    learner_data = {
        "name": learner.full_name,
        "degree": learner.degree,
        "college": learner.college,
        "current_role": learner.current_role,
        "experience_level": learner.experience_level,
        "experience_years": learner.experience_years_numeric,
        "weekly_study_hours": learner.weekly_study_hours,
        "preferred_format": learner.preferred_learning_format,
        "target_goal": learner.target_goal,
        "deadline_months": learner.goal_deadline_months,
    } if learner else None

    # 2. LearnerProfile (interests, preferences)
    profile = get_learner_profile(db, request.learner_id)
    profile_data = {
        "interests": profile.interests,
        "learning_preferences": profile.learning_preferences,
        "preferred_formats": profile.preferred_formats,
        "education": profile.education,
    } if profile else None

    # 3. Active Goals
    active_goals = db.query(Goal).filter(Goal.learner_id == request.learner_id, Goal.status == "active").all()
    goals_data = [{"title": g.goal_title, "target_role": g.target_role, "core_skills": g.core_target_skills, "deadline_months": g.deadline_months, "weekly_hours": g.weekly_hours_committed} for g in active_goals]

    # 4. Active Learning Path + ALL path items (pending & completed)
    active_path = db.query(LearningPath).filter(LearningPath.learner_id == request.learner_id, LearningPath.status == "active").first()
    pending_items_data, completed_items_data = [], []
    if active_path:
        all_items = db.query(PathItem).filter(PathItem.path_id == active_path.path_id).order_by(PathItem.sequence_order).all()
        for item in all_items:
            entry = {"order": item.sequence_order, "skill": item.skill_name, "status": item.status, "estimated_minutes": item.estimated_minutes, "required": item.required}
            if item.status == "completed":
                completed_items_data.append(entry)
            else:
                pending_items_data.append(entry)
        # Limit to keep prompt focused: last 5 completed, next 5 pending
        completed_items_data = completed_items_data[-5:]
        pending_items_data = pending_items_data[:5]

    # 5. ALL Learner Skills (mastered + weak)
    all_skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == request.learner_id).all()
    mastered_skills = [{"skill": s.skill_name, "mastery": s.mastery_score, "band": s.mastery_band} for s in all_skills if s.mastery_score and s.mastery_score >= 60]
    weak_skills = [{"skill": s.skill_name, "mastery": s.mastery_score, "band": s.mastery_band} for s in all_skills if not s.mastery_score or s.mastery_score < 60]

    # 6. Available Assessments (matching skills in path)
    path_skill_names = list({item.skill_name for item in (db.query(PathItem).filter(PathItem.path_id == active_path.path_id).all() if active_path else [])})
    available_assessments = db.query(Assessment).filter(Assessment.skill_name.in_(path_skill_names)).limit(10).all() if path_skill_names else []
    assessments_data = [{"title": a.title, "type": a.assessment_type, "skill": a.skill_name, "difficulty": a.difficulty_score, "pass_threshold": a.pass_threshold} for a in available_assessments]

    # 7. Recent Assessment Attempts (last 5)
    recent_attempts = db.query(AssessmentAttempt).filter(AssessmentAttempt.learner_id == request.learner_id).order_by(AssessmentAttempt.attempt_id.desc()).limit(5).all()
    attempts_data = [{"skill": a.skill_name, "score": a.score, "passed": a.passed, "confidence": a.self_reported_confidence} for a in recent_attempts]

    # 8. ALL Learner Pitfalls (all statuses)
    all_pitfalls = db.query(LearnerPitfall).filter(LearnerPitfall.learner_id == request.learner_id).all()
    pitfalls_data = []
    for lp in all_pitfalls:
        if lp.pitfall:
            pitfalls_data.append({"title": lp.pitfall.title, "status": lp.status, "misconception": lp.pitfall.misconception, "correct_model": lp.pitfall.correct_mental_model, "severity": lp.pitfall.severity})

    # 9. Matching Projects for target role
    target_role = goals_data[0]["target_role"] if goals_data else ""
    projects = db.query(Project).filter(Project.target_role == target_role).limit(5).all() if target_role else []
    projects_data = [{"title": p.title, "difficulty": p.difficulty_tier, "hours": p.estimated_hours, "skills": p.primary_skills} for p in projects]

    response_content = chat_service.generate_chat_response(
        user_message=request.user_message,
        history=request.history,
        learner_data=learner_data,
        learner_profile=profile_data,
        active_goals=goals_data,
        pending_items=pending_items_data,
        completed_items=completed_items_data,
        mastered_skills=mastered_skills,
        weak_skills=weak_skills,
        available_assessments=assessments_data,
        recent_attempts=attempts_data,
        pitfalls=pitfalls_data,
        projects=projects_data,
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


# ─────────────────────────────────────────────────────────────────────────────
# 17.10  Pitfall & Misconception Detection Endpoints
# ─────────────────────────────────────────────────────────────────────────────

from app.services.pitfall_service import (
    get_pitfall_check_for_skill,
    submit_pitfall_answer,
    get_learner_pitfall_dashboard,
    start_remediation,
    submit_verification,
)
from app.services.pitfall_analytics import get_all_pitfall_analytics, compute_pitfall_analytics
from app.models.orm import Concept, Pitfall as PitfallModel, PitfallQuestion as PQModel


class PitfallSubmitRequest(BaseModel):
    learner_id: str
    question_id: str
    selected_option: str
    confidence: int  # 1-5


class PitfallRemediateRequest(BaseModel):
    learner_id: str


class PitfallVerifyRequest(BaseModel):
    learner_id: str
    question_id: str
    selected_option: str
    confidence: int  # 1-5


@router.get("/pitfalls/check/{skill_id}", response_model=APIResponse[Dict[str, Any]])
def get_pitfall_check(skill_id: str, learner_id: str = None, db: Session = Depends(get_db)):
    """Get a pitfall check question for a given skill."""
    result = get_pitfall_check_for_skill(db, skill_id, learner_id)
    if not result:
        return APIResponse(
            success=True,
            data={"available": False, "message": "No pitfall check available for this skill."},
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    return APIResponse(
        success=True,
        data={"available": True, **result},
        meta=MetaResponse(request_id=str(uuid.uuid4()))
    )


@router.post("/pitfalls/submit", response_model=APIResponse[Dict[str, Any]])
def submit_pitfall_check(request: PitfallSubmitRequest, db: Session = Depends(get_db)):
    """Submit an answer to a pitfall check question and receive evaluation + explanation."""
    try:
        result = submit_pitfall_answer(
            db=db,
            learner_id=request.learner_id,
            question_id=request.question_id,
            selected_option=request.selected_option,
            confidence=request.confidence,
        )
        return APIResponse(
            success=True,
            data=result,
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pitfalls/learner/{learner_id}", response_model=APIResponse[Dict[str, Any]])
def get_learner_pitfalls(learner_id: str, db: Session = Depends(get_db)):
    """Get dashboard data for a learner's active and resolved pitfalls."""
    data = get_learner_pitfall_dashboard(db, learner_id)
    return APIResponse(
        success=True,
        data=data,
        meta=MetaResponse(request_id=str(uuid.uuid4()))
    )


@router.post("/pitfalls/{pitfall_id}/remediate", response_model=APIResponse[Dict[str, Any]])
def remediate_pitfall(pitfall_id: str, request: PitfallRemediateRequest, db: Session = Depends(get_db)):
    """Start remediation for a detected pitfall — returns explanation + recommended resource."""
    try:
        result = start_remediation(db, request.learner_id, pitfall_id)
        return APIResponse(
            success=True,
            data=result,
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pitfalls/{pitfall_id}/verify", response_model=APIResponse[Dict[str, Any]])
def verify_pitfall(pitfall_id: str, request: PitfallVerifyRequest, db: Session = Depends(get_db)):
    """Submit verification answer after remediation. Returns RESOLVED or UNRESOLVED."""
    try:
        result = submit_verification(
            db=db,
            learner_id=request.learner_id,
            pitfall_id=pitfall_id,
            question_id=request.question_id,
            selected_option=request.selected_option,
            confidence=request.confidence,
        )
        return APIResponse(
            success=True,
            data=result,
            meta=MetaResponse(request_id=str(uuid.uuid4()))
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pitfalls/analytics", response_model=APIResponse[Dict[str, Any]])
def get_pitfall_analytics(db: Session = Depends(get_db)):
    """Population-level analytics across all pitfalls (admin/debug view)."""
    analytics = get_all_pitfall_analytics(db)
    return APIResponse(
        success=True,
        data={"pitfalls": analytics, "total": len(analytics)},
        meta=MetaResponse(request_id=str(uuid.uuid4()))
    )


@router.get("/pitfalls/analytics/{pitfall_id}", response_model=APIResponse[Dict[str, Any]])
def get_single_pitfall_analytics(pitfall_id: str, db: Session = Depends(get_db)):
    """Detailed population-level analytics for a single pitfall."""
    analytics = compute_pitfall_analytics(db, pitfall_id)
    return APIResponse(
        success=True,
        data=analytics,
        meta=MetaResponse(request_id=str(uuid.uuid4()))
    )


@router.get("/pitfalls/skill/{skill_id}", response_model=APIResponse[Dict[str, Any]])
def get_pitfalls_for_skill(skill_id: str, db: Session = Depends(get_db)):
    """Get all pitfalls associated with a skill (via its concepts)."""
    concepts = db.query(Concept).filter(Concept.skill_id == skill_id).all()
    concept_ids = [c.concept_id for c in concepts]
    pitfalls = db.query(PitfallModel).filter(
        PitfallModel.concept_id.in_(concept_ids),
        PitfallModel.status == "active"
    ).all()
    data = [
        {
            "pitfall_id": p.pitfall_id,
            "title": p.title,
            "severity": p.severity,
            "concept_id": p.concept_id,
        }
        for p in pitfalls
    ]
    return APIResponse(
        success=True,
        data={"skill_id": skill_id, "pitfalls": data},
        meta=MetaResponse(request_id=str(uuid.uuid4()))
    )

