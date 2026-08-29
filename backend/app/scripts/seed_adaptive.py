"""
seed_adaptive.py — Seeds an ML Engineer adaptive learning path for LRN0001.

Reads existing skills and resources from DB, maps them to the ML Engineer
journey stages, and creates an AdaptivePathState record.

Run from backend/ directory:
    python -m app.scripts.seed_adaptive
"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.models.database import SessionLocal, engine
from app.models.orm import Base, AdaptivePathState, Skill, Resource, ResourceSkill, Learner
from app.services.adaptive_planner import _recompute_timeline

# Create all tables (including new adaptive ones)
Base.metadata.create_all(bind=engine)

DEMO_LEARNER_ID = "LRN0001"

# ML Engineer journey stages in order
# Each stage has: title, skill_keywords, phase, required, estimated_minutes_fallback
ML_STAGES = [
    {
        "stage": "python",
        "title": "Python for ML",
        "keywords": ["python", "programming", "scripting"],
        "phase": "Foundation",
        "required": True,
        "fallback_minutes": 480,
        "difficulty_target": 0.3,
    },
    {
        "stage": "math_stats",
        "title": "Mathematics & Statistics",
        "keywords": ["statistics", "math", "linear algebra", "probability", "calculus"],
        "phase": "Foundation",
        "required": True,
        "fallback_minutes": 600,
        "difficulty_target": 0.4,
    },
    {
        "stage": "ml_fundamentals",
        "title": "Machine Learning Fundamentals",
        "keywords": ["machine learning", "ml fundamentals", "ml basics", "supervised", "unsupervised"],
        "phase": "Core ML",
        "required": True,
        "fallback_minutes": 720,
        "difficulty_target": 0.55,
    },
    {
        "stage": "data_processing",
        "title": "Data Processing & Feature Engineering",
        "keywords": ["data processing", "feature engineering", "pandas", "numpy", "data cleaning"],
        "phase": "Core ML",
        "required": True,
        "fallback_minutes": 480,
        "difficulty_target": 0.45,
    },
    {
        "stage": "supervised_learning",
        "title": "Supervised Learning",
        "keywords": ["supervised learning", "classification", "regression", "decision tree", "random forest"],
        "phase": "Advanced ML",
        "required": True,
        "fallback_minutes": 600,
        "difficulty_target": 0.6,
    },
    {
        "stage": "model_evaluation",
        "title": "Model Evaluation & Validation",
        "keywords": ["model evaluation", "cross validation", "metrics", "accuracy", "precision recall"],
        "phase": "Advanced ML",
        "required": True,
        "fallback_minutes": 360,
        "difficulty_target": 0.6,
    },
    {
        "stage": "deep_learning",
        "title": "Deep Learning",
        "keywords": ["deep learning", "neural network", "tensorflow", "pytorch", "keras"],
        "phase": "Specialization",
        "required": False,   # optional for core ML engineer
        "fallback_minutes": 900,
        "difficulty_target": 0.75,
    },
    {
        "stage": "deployment",
        "title": "Model Deployment",
        "keywords": ["deployment", "api", "flask", "fastapi", "docker", "serving", "production"],
        "phase": "ML Engineering",
        "required": True,
        "fallback_minutes": 480,
        "difficulty_target": 0.65,
    },
    {
        "stage": "mlops",
        "title": "MLOps",
        "keywords": ["mlops", "pipeline", "ci/cd", "monitoring", "mlflow", "kubeflow"],
        "phase": "ML Engineering",
        "required": True,
        "fallback_minutes": 540,
        "difficulty_target": 0.75,
    },
    {
        "stage": "project",
        "title": "ML Engineering Capstone Project",
        "keywords": ["project", "capstone", "portfolio"],
        "phase": "Capstone",
        "required": True,
        "fallback_minutes": 1200,
        "difficulty_target": 0.8,
    },
]


def find_best_skill(db, keywords):
    """Find the most relevant skill for a set of keywords."""
    skills = db.query(Skill).all()
    for kw in keywords:
        for skill in skills:
            name = (skill.skill_name or "").lower()
            if kw.lower() in name:
                return skill
    return None


def find_best_resource(db, skill_id, target_difficulty):
    """Find the best resource for a skill at target difficulty."""
    # Try direct primary skill match
    resources = db.query(Resource).filter(
        Resource.primary_skill_id == skill_id,
        Resource.status == "active",
    ).all()

    if not resources:
        rs_rows = db.query(ResourceSkill).filter(ResourceSkill.skill_id == skill_id).all()
        rids = [r.resource_id for r in rs_rows]
        resources = db.query(Resource).filter(
            Resource.resource_id.in_(rids),
            Resource.status == "active",
        ).all()

    if not resources:
        return None

    # Score by difficulty proximity + quality
    def score(r):
        diff_dist = abs((r.difficulty_score or 0.5) - target_difficulty)
        quality = r.quality_score or 0.5
        return quality - diff_dist

    resources.sort(key=score, reverse=True)
    return resources[0]


def seed():
    db = SessionLocal()
    try:
        # Check if learner exists
        learner = db.query(Learner).filter(Learner.learner_id == DEMO_LEARNER_ID).first()
        if not learner:
            print(f"⚠ Learner {DEMO_LEARNER_ID} not found in DB.")
            print("  Creating a minimal placeholder learner for demo purposes...")
            learner = Learner(
                learner_id=DEMO_LEARNER_ID,
                full_name="Demo Learner",
                gender="Not specified",
                city="Chennai",
                state="Tamil Nadu",
                college="Demo College",
                degree="B.Tech",
                graduation_year=2024,
                current_role="Student",
                experience_level="beginner",
                experience_years_numeric=0.0,
                weekly_study_hours=8.0,
                preferred_learning_format="video",
                target_goal="ML Engineer",
                goal_deadline_months=6.0,
                preferred_language="English",
                timezone="Asia/Kolkata",
            )
            db.add(learner)
            db.commit()
            print(f"  ✓ Created placeholder learner {DEMO_LEARNER_ID}")

        # Check if adaptive state already exists
        existing = db.query(AdaptivePathState).filter(
            AdaptivePathState.learner_id == DEMO_LEARNER_ID
        ).first()
        if existing:
            print(f"✓ Adaptive path for {DEMO_LEARNER_ID} already exists ({len(existing.current_path)} items).")
            print("  Delete from adaptive_path_states to re-seed.")
            return

        print(f"\nSeeding ML Engineer path for learner {DEMO_LEARNER_ID}...")
        path_items = []

        for i, stage in enumerate(ML_STAGES):
            skill = find_best_skill(db, stage["keywords"])
            skill_id = skill.skill_id if skill else None
            skill_name = skill.skill_name if skill else stage["title"]

            resource = None
            if skill_id:
                resource = find_best_resource(db, skill_id, stage["difficulty_target"])

            # Status: first two completed (demo), third in-progress, rest planned
            if i == 0:
                status = "completed"
            elif i == 1:
                status = "in_progress"
            else:
                status = "planned"

            item = {
                "id": str(uuid.uuid4()),
                "item_type": "resource",
                "sequence_order": i + 1,
                "title": resource.title if resource else stage["title"],
                "stage_title": stage["title"],
                "phase": stage["phase"],
                "skill_id": skill_id,
                "skill_name": skill_name,
                "resource_id": resource.resource_id if resource else None,
                "provider": resource.provider if resource else None,
                "format": resource.format if resource else "video",
                "resource_type": resource.resource_type if resource else "course",
                "difficulty_score": resource.difficulty_score if resource else stage["difficulty_target"],
                "quality_score": resource.quality_score if resource else 0.7,
                "estimated_minutes": resource.duration_minutes if resource else stage["fallback_minutes"],
                "status": status,
                "required": stage["required"],
                "has_pitfall_check": skill_id is not None,
            }
            path_items.append(item)
            print(f"  [{i+1}] {stage['title']} -> skill: {skill_name} | resource: {item['title'][:50]} | status: {status}")

        state = AdaptivePathState(
            state_id=str(uuid.uuid4()),
            learner_id=DEMO_LEARNER_ID,
            current_path=path_items,
            weekly_hours=8.0,
            deadline_weeks=24.0,
            total_hours_logged=0.0,
            current_item_index=1,
        )
        _recompute_timeline(state)
        db.add(state)
        db.commit()

        print(f"\n[Success] Seeded {len(path_items)}-item ML Engineer path for {DEMO_LEARNER_ID}")
        print(f"   Remaining hours: {state.remaining_hours:.1f}")
        print(f"   Projected completion: {state.projected_completion_weeks:.1f} weeks")
        print(f"   On track: {state.is_on_track}")

    except Exception as e:
        db.rollback()
        print(f"\n[Error] Seeding failed: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
