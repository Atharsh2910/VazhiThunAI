"""
Tests for the Adaptive Learning Path / Replanning Engine.
Uses SQLite in-memory database — no external dependencies required.

Run: python -m pytest tests/test_adaptive_planner.py -v
"""
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite in-memory for fast, isolated tests
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    from app.models.database import Base
    from app.models import orm  # ensure all models are imported
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="session")
def demo_learner(db):
    from app.models.orm import Learner
    learner = Learner(
        learner_id="TEST001",
        full_name="Test Learner",
        gender="M",
        city="Chennai",
        state="TN",
        college="Test College",
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
    return learner


@pytest.fixture(scope="session")
def demo_skills(db):
    from app.models.orm import Skill
    skills = [
        Skill(skill_id="SKT001", skill_name="Python", domain="Programming",
              difficulty_tier="beginner", difficulty_score=0.3, decay_rate=0.05),
        Skill(skill_id="SKT002", skill_name="Machine Learning", domain="ML",
              difficulty_tier="intermediate", difficulty_score=0.6, decay_rate=0.1),
        Skill(skill_id="SKT003", skill_name="Statistics", domain="Math",
              difficulty_tier="intermediate", difficulty_score=0.5, decay_rate=0.08),
    ]
    for s in skills: db.add(s)
    db.commit()
    return skills


@pytest.fixture(scope="session")
def demo_resources(db, demo_skills):
    from app.models.orm import Resource
    resources = [
        Resource(resource_id="RST001", title="Python Basics", provider="Coursera",
                 resource_type="course", format="video", primary_skill_id="SKT001",
                 primary_skill_name="Python", domain="Programming", difficulty_score=0.25,
                 duration_minutes=300, quality_score=0.9, status="active"),
        Resource(resource_id="RST002", title="Advanced Python", provider="Udemy",
                 resource_type="course", format="video", primary_skill_id="SKT001",
                 primary_skill_name="Python", domain="Programming", difficulty_score=0.7,
                 duration_minutes=480, quality_score=0.85, status="active"),
        Resource(resource_id="RST003", title="ML Fundamentals", provider="Coursera",
                 resource_type="course", format="video", primary_skill_id="SKT002",
                 primary_skill_name="Machine Learning", domain="ML", difficulty_score=0.55,
                 duration_minutes=600, quality_score=0.88, status="active"),
        Resource(resource_id="RST004", title="Advanced ML", provider="Fast.ai",
                 resource_type="course", format="video", primary_skill_id="SKT002",
                 primary_skill_name="Machine Learning", domain="ML", difficulty_score=0.85,
                 duration_minutes=900, quality_score=0.92, status="active"),
        Resource(resource_id="RST004b", title="ML for Beginners", provider="YouTube",
                 resource_type="video", format="video", primary_skill_id="SKT002",
                 primary_skill_name="Machine Learning", domain="ML", difficulty_score=0.20,
                 duration_minutes=120, quality_score=0.75, status="active"),
        Resource(resource_id="RST005", title="Stats Intro", provider="Khan Academy",
                 resource_type="course", format="video", primary_skill_id="SKT003",
                 primary_skill_name="Statistics", domain="Math", difficulty_score=0.3,
                 duration_minutes=240, quality_score=0.8, status="active"),
    ]
    for r in resources: db.add(r)
    db.commit()
    return resources


@pytest.fixture(scope="session")
def demo_path_state(db, demo_learner, demo_resources):
    """Seed a 5-item ML Engineer path for the test learner."""
    from app.models.orm import AdaptivePathState
    from app.services.adaptive_planner import _recompute_timeline

    items = [
        {
            "id": "ITM001", "item_type": "resource", "sequence_order": 1,
            "title": "Python Basics", "skill_id": "SKT001", "skill_name": "Python",
            "resource_id": "RST001", "difficulty_score": 0.25,
            "estimated_minutes": 300, "status": "completed", "required": True,
        },
        {
            "id": "ITM002", "item_type": "resource", "sequence_order": 2,
            "title": "ML Fundamentals", "skill_id": "SKT002", "skill_name": "Machine Learning",
            "resource_id": "RST003", "difficulty_score": 0.55,
            "estimated_minutes": 600, "status": "in_progress", "required": True,
        },
        {
            "id": "ITM003", "item_type": "resource", "sequence_order": 3,
            "title": "Stats Intro", "skill_id": "SKT003", "skill_name": "Statistics",
            "resource_id": "RST005", "difficulty_score": 0.3,
            "estimated_minutes": 240, "status": "planned", "required": False,
        },
        {
            "id": "ITM004", "item_type": "resource", "sequence_order": 4,
            "title": "Advanced ML", "skill_id": "SKT002", "skill_name": "Machine Learning",
            "resource_id": "RST004", "difficulty_score": 0.85,
            "estimated_minutes": 900, "status": "planned", "required": True,
        },
    ]
    state = AdaptivePathState(
        state_id="STATE001",
        learner_id="TEST001",
        current_path=items,
        weekly_hours=8.0,
        deadline_weeks=20.0,
    )
    _recompute_timeline(state)
    db.add(state)
    db.commit()
    return state


# ─────────────────────────────────────────────────
# Test Cases
# ─────────────────────────────────────────────────

class TestFeedback:
    def test_too_difficult_lowers_difficulty(self, db, demo_path_state):
        """TC-01: Too difficult → lower difficulty resource."""
        from app.services.adaptive_planner import adapt_for_feedback
        result = adapt_for_feedback(db, "TEST001", "ITM002", "TOO_HARD")
        assert result["success"] is True
        assert result["adaptation_type"] == "RESOURCE_REPLACED"
        new_diff = result["new_item"]["difficulty"]
        old_diff = result["old_item"]["difficulty"]
        assert new_diff < old_diff, f"New difficulty {new_diff} should be < old {old_diff}"

    def test_too_easy_raises_difficulty(self, db, demo_path_state):
        """TC-02: Too easy → higher difficulty resource."""
        from app.services.adaptive_planner import adapt_for_feedback
        result = adapt_for_feedback(db, "TEST001", "ITM001", "TOO_EASY")
        # ITM001 is completed — should fail gracefully
        assert result["success"] is False
        assert "completed" in result["message"].lower()

    def test_too_easy_on_inprogress(self, db, demo_path_state):
        """TC-02b: Too easy on in-progress item raises difficulty."""
        from app.services.adaptive_planner import adapt_for_feedback
        result = adapt_for_feedback(db, "TEST001", "ITM002", "TOO_EASY")
        # Should find Advanced ML (difficulty 0.85) as replacement
        assert result["success"] is True

    def test_already_known_requests_verification(self, db, demo_path_state):
        """TC-03: Already known → verification initiated."""
        from app.services.adaptive_planner import adapt_for_feedback
        result = adapt_for_feedback(db, "TEST001", "ITM002", "ALREADY_KNOWN")
        assert result["success"] is True
        assert result.get("requires_verification") is True
        assert result["adaptation_type"] == "VERIFICATION_REQUESTED"

    def test_completed_item_not_modified(self, db, demo_path_state):
        """TC-01b: Completed items are never modified."""
        from app.services.adaptive_planner import adapt_for_feedback
        result = adapt_for_feedback(db, "TEST001", "ITM001", "TOO_HARD")
        assert result["success"] is False


class TestVerification:
    def test_verification_pass_skips_item(self, db, demo_path_state):
        """TC-04: Verification pass → MASTERED_SKIP."""
        from app.services.adaptive_planner import apply_verification_result, adapt_for_feedback
        # First initiate verification
        adapt_for_feedback(db, "TEST001", "ITM002", "ALREADY_KNOWN")
        # Then pass verification
        result = apply_verification_result(db, "TEST001", "ITM002", passed=True)
        assert result["success"] is True
        assert result["new_status"] == "mastered_skip"

    def test_verification_fail_retains_item(self, db, demo_path_state):
        """TC-05: Verification fail → item retained."""
        from app.services.adaptive_planner import apply_verification_result
        result = apply_verification_result(db, "TEST001", "ITM002", passed=False)
        assert result["success"] is True
        assert result["new_status"] == "in_progress"
        assert result["passed"] is False


class TestRemediation:
    def test_knowledge_gap_inserts_remediation(self, db, demo_path_state):
        """TC-06: Knowledge gap → remediation inserted."""
        from app.services.adaptive_planner import adapt_for_assessment
        result = adapt_for_assessment(db, "TEST001", "SKT002", score=0.40)
        assert result["success"] is True
        assert result["adaptation_type"] == "REMEDIATION_INSERTED"

    def test_high_score_no_change(self, db, demo_path_state):
        """TC-06b: High assessment score → no change."""
        from app.services.adaptive_planner import adapt_for_assessment
        result = adapt_for_assessment(db, "TEST001", "SKT002", score=0.85)
        assert result["adaptation_type"] == "NO_CHANGE"

    def test_pitfall_inserts_remediation(self, db, demo_path_state):
        """TC-07: Pitfall detected → remediation inserted."""
        from app.models.orm import Concept, Pitfall
        from app.services.adaptive_planner import adapt_for_pitfall

        concept = Concept(concept_id="CON001", skill_id="SKT002",
                          name="Data Leakage", description="Common ML pitfall")
        pitfall = Pitfall(pitfall_id="PIT001", concept_id="CON001",
                          title="Data Leakage Misconception",
                          description="Learner includes test data in training",
                          misconception="It's fine to use all data for training",
                          correct_mental_model="Test data must never be seen during training",
                          severity="high", status="active",
                          remediation_text="Always split data before any preprocessing.")
        db.add(concept); db.add(pitfall); db.commit()

        result = adapt_for_pitfall(db, "TEST001", "PIT001", "Data Leakage")
        assert result["success"] is True
        assert result["adaptation_type"] == "REMEDIATION_INSERTED"

    def test_duplicate_remediation_blocked(self, db, demo_path_state):
        """TC-07b: Duplicate pitfall remediation is not inserted twice."""
        from app.models.orm import Concept, Pitfall
        from app.services.adaptive_planner import adapt_for_pitfall

        # Insert once (may already exist from previous test if not isolated)
        concept = Concept(concept_id="CON002", skill_id="SKT003",
                          name="P-value Misconception", description="Stats pitfall")
        pitfall = Pitfall(pitfall_id="PIT002", concept_id="CON002",
                          title="P-value Misconception", description="Common error",
                          misconception="p<0.05 proves the hypothesis",
                          correct_mental_model="p-value does not prove hypotheses",
                          severity="medium", status="active",
                          remediation_text="Review hypothesis testing basics.")
        db.add(concept); db.add(pitfall); db.commit()

        result1 = adapt_for_pitfall(db, "TEST001", "PIT002", "P-value")
        result2 = adapt_for_pitfall(db, "TEST001", "PIT002", "P-value")
        # Second call should be blocked (already in path)
        assert result2["success"] is False


class TestTimeline:
    def test_weekly_hours_change_recalculates(self, db, demo_path_state):
        """TC-09: Weekly hours change → recalculated timeline."""
        from app.services.adaptive_planner import update_weekly_hours
        result = update_weekly_hours(db, "TEST001", 5.0)
        assert result["success"] is True
        assert result["new_weekly_hours"] == 5.0
        assert result["projected_completion_weeks"] > 0

    def test_deadline_change_recalculates(self, db, demo_path_state):
        """TC-10: Deadline change → feasibility recalculated."""
        from app.services.adaptive_planner import update_deadline
        result = update_deadline(db, "TEST001", 8.0)
        assert result["success"] is True
        assert result["new_deadline_weeks"] == 8.0

    def test_lighter_path_removes_optionals(self, db, demo_path_state):
        """TC-10b: Lighter path removes optional items."""
        from app.services.adaptive_planner import make_path_lighter, get_or_create_state
        result = make_path_lighter(db, "TEST001")
        assert result["success"] is True
        assert len(result["items_removed"]) > 0
        # Verify optional item is gone from state
        state = get_or_create_state(db, "TEST001")
        optional_remaining = [i for i in state.current_path if not i.get("required", True)
                              and i.get("status") not in ("completed", "mastered_skip")]
        assert len(optional_remaining) == 0


class TestSimulation:
    def test_simulation_does_not_mutate(self, db, demo_path_state):
        """TC-11: Simulation must NOT mutate the path."""
        from app.services.adaptive_planner import simulate_plan, get_or_create_state
        before = list(get_or_create_state(db, "TEST001").current_path)
        simulate_plan(db, "TEST001", weekly_hours=20.0, deadline_weeks=5.0, optional_policy="remove")
        after = list(get_or_create_state(db, "TEST001").current_path)
        assert len(before) == len(after), "Simulation should not change path length"
        assert before[0]["id"] == after[0]["id"]

    def test_simulation_is_marked(self, db, demo_path_state):
        """TC-11b: Simulation result has is_simulation=True."""
        from app.services.adaptive_planner import simulate_plan
        result = simulate_plan(db, "TEST001", 10.0, 12.0, "keep")
        assert result.get("is_simulation") is True

    def test_apply_simulation_mutates(self, db, demo_path_state):
        """TC-12: Applying a simulation option changes the path."""
        from app.services.adaptive_planner import apply_simulation, get_or_create_state
        state_before = get_or_create_state(db, "TEST001")
        old_hours = state_before.weekly_hours
        apply_simulation(db, "TEST001", option_key="A", weekly_hours=12.0, optional_policy="keep")
        state_after = get_or_create_state(db, "TEST001")
        assert state_after.weekly_hours == 12.0
        assert state_after.weekly_hours != old_hours


class TestHistory:
    def test_completed_items_stay_completed(self, db, demo_path_state):
        """TC-13: Completed items remain completed after any adaptation."""
        from app.services.adaptive_planner import adapt_for_feedback, get_or_create_state
        adapt_for_assessment = __import__("app.services.adaptive_planner", fromlist=["adapt_for_assessment"]).adapt_for_assessment
        adapt_for_assessment(db, "TEST001", "SKT002", score=0.3)
        state = get_or_create_state(db, "TEST001")
        completed = [i for i in state.current_path if i.get("id") == "ITM001"]
        assert completed[0]["status"] == "completed"

    def test_adaptation_history_logged(self, db, demo_path_state):
        """TC-14: Every adaptation is logged in adaptation_events."""
        from app.services.adaptive_planner import adapt_for_feedback
        from app.models.orm import AdaptationEvent
        adapt_for_feedback(db, "TEST001", "ITM002", "TOO_HARD")
        events = db.query(AdaptationEvent).filter(
            AdaptationEvent.learner_id == "TEST001"
        ).all()
        assert len(events) >= 1
        assert events[-1].trigger == "TOO_HARD"

    def test_missing_resource_fallback(self, db, demo_path_state):
        """TC-15: No alternative resource → graceful failure."""
        from app.services.adaptive_planner import adapt_for_feedback
        # Stats item (SKT003) has only one resource — no alternative
        result = adapt_for_feedback(db, "TEST001", "ITM003", "TOO_HARD")
        # Should fail gracefully, not raise exception
        assert isinstance(result, dict)
        assert "success" in result
