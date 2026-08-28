from typing import Dict, TypedDict, Any, List
from langgraph.graph import StateGraph, END

# Define the State Model as per SRS Section 11
class LearnerState(TypedDict):
    learner_id: str
    session_id: str
    user_message: str
    intent: Dict[str, Any]
    learner_profile: Dict[str, Any]
    goal: Dict[str, Any]
    skill_context: List[Any]
    skill_gaps: List[Any]
    retrieved_resources: List[Any]
    ranked_resources: List[Any]
    candidate_path: List[Any]
    validated_path: List[Any]
    explanation: Dict[str, Any]
    response: Dict[str, Any]
    confidence: float
    citations: List[Any]
    events: List[Any]

# Primary Graph Node Functions
def intent_detection(state: LearnerState) -> LearnerState:
    # Logic for intent detection
    return state

def goal_extraction(state: LearnerState) -> LearnerState:
    return state

def learner_context_load(state: LearnerState) -> LearnerState:
    return state

def skill_graph_retrieval(state: LearnerState) -> LearnerState:
    return state

def gap_analysis(state: LearnerState) -> LearnerState:
    return state

def candidate_retrieval(state: LearnerState) -> LearnerState:
    return state

def recommendation_ranking(state: LearnerState) -> LearnerState:
    return state

def path_planning(state: LearnerState) -> LearnerState:
    return state

def constraint_validation(state: LearnerState) -> LearnerState:
    return state

def explanation_generation(state: LearnerState) -> LearnerState:
    return state

def response_validation(state: LearnerState) -> LearnerState:
    return state

# Adaptive Graph Node Functions
def evidence_collection(state: LearnerState) -> LearnerState:
    return state

def assessment_interpretation(state: LearnerState) -> LearnerState:
    return state

def mastery_update(state: LearnerState) -> LearnerState:
    return state

def risk_analysis(state: LearnerState) -> LearnerState:
    return state

def replanning_decision(state: LearnerState) -> str:
    # Returns the next node in conditionally branching
    return "continue"

# Build Primary Workflow
primary_workflow = StateGraph(LearnerState)

primary_workflow.add_node("intent_detection", intent_detection)
primary_workflow.add_node("goal_extraction", goal_extraction)
primary_workflow.add_node("learner_context_load", learner_context_load)
primary_workflow.add_node("skill_graph_retrieval", skill_graph_retrieval)
primary_workflow.add_node("gap_analysis", gap_analysis)
primary_workflow.add_node("candidate_retrieval", candidate_retrieval)
primary_workflow.add_node("recommendation_ranking", recommendation_ranking)
primary_workflow.add_node("path_planning", path_planning)
primary_workflow.add_node("constraint_validation", constraint_validation)
primary_workflow.add_node("explanation_generation", explanation_generation)
primary_workflow.add_node("response_validation", response_validation)

primary_workflow.set_entry_point("intent_detection")
primary_workflow.add_edge("intent_detection", "goal_extraction")
primary_workflow.add_edge("goal_extraction", "learner_context_load")
primary_workflow.add_edge("learner_context_load", "skill_graph_retrieval")
primary_workflow.add_edge("skill_graph_retrieval", "gap_analysis")
primary_workflow.add_edge("gap_analysis", "candidate_retrieval")
primary_workflow.add_edge("candidate_retrieval", "recommendation_ranking")
primary_workflow.add_edge("recommendation_ranking", "path_planning")
primary_workflow.add_edge("path_planning", "constraint_validation")
primary_workflow.add_edge("constraint_validation", "explanation_generation")
primary_workflow.add_edge("explanation_generation", "response_validation")
primary_workflow.add_edge("response_validation", END)

primary_graph = primary_workflow.compile()


# Build Adaptive Workflow
adaptive_workflow = StateGraph(LearnerState)

adaptive_workflow.add_node("evidence_collection", evidence_collection)
adaptive_workflow.add_node("assessment_interpretation", assessment_interpretation)
adaptive_workflow.add_node("mastery_update", mastery_update)
adaptive_workflow.add_node("risk_analysis", risk_analysis)
adaptive_workflow.add_node("gap_analysis", gap_analysis) # re-using from primary
adaptive_workflow.add_node("new_path", path_planning) # re-using from primary
# using a dummy end node for 'continue' path
def continue_plan(state: LearnerState) -> LearnerState:
    return state
adaptive_workflow.add_node("continue_plan", continue_plan)

adaptive_workflow.set_entry_point("evidence_collection")
adaptive_workflow.add_edge("evidence_collection", "assessment_interpretation")
adaptive_workflow.add_edge("assessment_interpretation", "mastery_update")
adaptive_workflow.add_edge("mastery_update", "risk_analysis")

# conditional edge based on replanning_decision
adaptive_workflow.add_conditional_edges(
    "risk_analysis",
    replanning_decision,
    {
        "continue": "continue_plan",
        "replan": "gap_analysis"
    }
)
adaptive_workflow.add_edge("gap_analysis", "new_path")
adaptive_workflow.add_edge("new_path", END)
adaptive_workflow.add_edge("continue_plan", END)

adaptive_graph = adaptive_workflow.compile()
