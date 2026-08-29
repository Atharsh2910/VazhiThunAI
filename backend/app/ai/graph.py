import os
import json
from typing import Dict, TypedDict, Any, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.ai.prompts.templates import (
    INTENT_DETECTION_PROMPT,
    GOAL_EXTRACTION_PROMPT,
    EXPLANATION_GENERATION_PROMPT,
    REPLANNING_DECISION_PROMPT
)
from app.retrieval.pinecone_client import pinecone_client
from app.services.recommendation import recommendation_engine
from app.planning.planner import optimize_learning_path
from sentence_transformers import SentenceTransformer

# Initialize Embedding Model (used for Pinecone retrieval)
try:
    embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
except Exception:
    embedding_model = None

# Initialize Groq LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY", "mock_groq_key"),
    model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192"),
    temperature=0.0
)

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

def parse_json_from_llm(content: str) -> Dict[str, Any]:
    # Utility to extract JSON from LLM response
    try:
        # Simple extraction logic
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(content[start:end])
    except Exception:
        pass
    return {}

# Primary Graph Node Functions
def intent_detection(state: LearnerState) -> LearnerState:
    prompt = PromptTemplate.from_template(INTENT_DETECTION_PROMPT)
    chain = prompt | llm
    res = chain.invoke({"user_message": state.get("user_message", "")})
    state["intent"] = parse_json_from_llm(res.content)
    return state

def goal_extraction(state: LearnerState) -> LearnerState:
    prompt = PromptTemplate.from_template(GOAL_EXTRACTION_PROMPT)
    chain = prompt | llm
    res = chain.invoke({
        "user_message": state.get("user_message", ""),
        "learner_profile": json.dumps(state.get("learner_profile", {}))
    })
    state["goal"] = parse_json_from_llm(res.content)
    return state

def learner_context_load(state: LearnerState) -> LearnerState:
    # Here we would typically hit a database for learner profile. 
    # For now, if empty, init defaults.
    if not state.get("learner_profile"):
        state["learner_profile"] = {"known_skills": []}
    return state

def skill_graph_retrieval(state: LearnerState) -> LearnerState:
    # Use Pinecone client to retrieve skill contexts based on target skills in goal
    goal = state.get("goal", {})
    target_skills = goal.get("target_skills", [])
    skill_context = []
    
    if target_skills and embedding_model:
        # Use real embedding for target skills
        query_text = " ".join(target_skills)
        # e5 models require "query: " prefix for asymmetric search
        query_embedding = embedding_model.encode(f"query: {query_text}").tolist()
        
        docs = pinecone_client.query_vectors(vector=query_embedding, top_k=5, namespace="skills")
        if "matches" in docs:
            skill_context = [match.get("metadata", {}) for match in docs["matches"]]
            
    state["skill_context"] = skill_context
    return state

def gap_analysis(state: LearnerState) -> LearnerState:
    goal = state.get("goal", {})
    profile = state.get("learner_profile", {})
    
    target_skills = set(goal.get("target_skills", []))
    known_skills = set(profile.get("known_skills", []))
    
    missing_skills = list(target_skills - known_skills)
    state["skill_gaps"] = [{"missing_skills": missing_skills}]
    return state

def candidate_retrieval(state: LearnerState) -> LearnerState:
    gaps = state.get("skill_gaps", [])
    retrieved_resources = []
    
    if gaps and gaps[0].get("missing_skills") and embedding_model:
        # Use real embedding for missing skills
        query_text = " ".join(gaps[0]["missing_skills"])
        query_embedding = embedding_model.encode(f"query: {query_text}").tolist()
        
        docs = pinecone_client.query_vectors(vector=query_embedding, top_k=10, namespace="resources")
        if "matches" in docs:
            retrieved_resources = [match.get("metadata", {}) for match in docs["matches"]]
            
    state["retrieved_resources"] = retrieved_resources
    return state

def recommendation_ranking(state: LearnerState) -> LearnerState:
    candidates = state.get("retrieved_resources", [])
    learner_profile = state.get("learner_profile", {})
    skill_gaps = state.get("skill_gaps", [{}])[0]
    
    ranked = recommendation_engine.rank_candidates(candidates, learner_profile, skill_gaps)
    state["ranked_resources"] = ranked
    return state

def path_planning(state: LearnerState) -> LearnerState:
    ranked = state.get("ranked_resources", [])
    goal = state.get("goal", {})
    constraints = {
        "weekly_hours": state.get("learner_profile", {}).get("weekly_hours", 10),
        "target_deadline": goal.get("target_deadline", "None")
    }
    state["candidate_path"] = optimize_learning_path(ranked, constraints)
    return state

def constraint_validation(state: LearnerState) -> LearnerState:
    state["validated_path"] = state.get("candidate_path", [])
    return state

def explanation_generation(state: LearnerState) -> LearnerState:
    prompt = PromptTemplate.from_template(EXPLANATION_GENERATION_PROMPT)
    chain = prompt | llm
    res = chain.invoke({
        "skill_gaps": json.dumps(state.get("skill_gaps", [])),
        "candidate_path": json.dumps(state.get("validated_path", [])),
        "goal": json.dumps(state.get("goal", {}))
    })
    
    state["explanation"] = {"content": res.content}
    state["response"] = {"message": res.content, "path": state.get("validated_path", [])}
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
    prompt = PromptTemplate.from_template(REPLANNING_DECISION_PROMPT)
    chain = prompt | llm
    res = chain.invoke({
        "events": json.dumps(state.get("events", [])),
        "learner_profile": json.dumps(state.get("learner_profile", {})),
        "goal": json.dumps(state.get("goal", {}))
    })
    parsed = parse_json_from_llm(res.content)
    return parsed.get("decision", "continue")

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
