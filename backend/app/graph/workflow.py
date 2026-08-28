from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.retrieval.rag import retrieve_relevant_content
from app.recommendation.recommender import get_hybrid_recommendations
from app.planning.planner import optimize_learning_path

class AgentState(TypedDict):
    learner_id: str
    session_id: str
    user_message: str
    intent: Dict[str, Any]
    goal: Dict[str, Any]
    skill_gaps: List[str]
    retrieved_content: List[Any]
    ranked_resources: List[Any]
    candidate_path: List[Dict[str, Any]]
    response: str

def get_llm():
    if not settings.GROQ_API_KEY:
        return None
    return ChatGroq(api_key=settings.GROQ_API_KEY, model_name="llama3-8b-8192")

def detect_intent(state: AgentState):
    llm = get_llm()
    if llm:
        messages = [
            SystemMessage(content="You are an intent detector for a learning app. Determine the intent of the user message. Return a simple json string like {'intent': 'plan_learning'}"),
            HumanMessage(content=state.get("user_message", ""))
        ]
        intent = {"intent": "plan_learning"}
    else:
        intent = {"intent": "plan_learning"}
    
    return {"intent": intent}

def extract_goal(state: AgentState):
    return {"goal": {"target_role": "Machine Learning Engineer"}}

def gap_analysis(state: AgentState):
    return {"skill_gaps": ["Deep Learning", "MLOps"]}

def retrieve_resources(state: AgentState):
    query = " ".join(state.get("skill_gaps", []))
    content = retrieve_relevant_content(query)
    return {"retrieved_content": content}

def rank_candidates(state: AgentState):
    ranked = get_hybrid_recommendations(state.get("skill_gaps", []), {})
    return {"ranked_resources": ranked}

def plan_path(state: AgentState):
    path = optimize_learning_path(state.get("ranked_resources", []), {})
    return {"candidate_path": path}

def generate_response(state: AgentState):
    llm = get_llm()
    if llm:
        messages = [
            SystemMessage(content="You are an AI learning navigator. Respond to the user concisely based on their goal and path."),
            HumanMessage(content=f"My goal is {state.get('goal', {}).get('target_role')}. My path is {state.get('candidate_path')}. Can you explain this?")
        ]
        try:
            res = llm.invoke(messages)
            response_text = res.content
        except Exception:
            response_text = "Here is your learning path based on your goals."
    else:
        titles = [p.get("title") for p in state.get('candidate_path', [])]
        response_text = f"I have planned a path for {state.get('goal', {}).get('target_role', 'your goal')}: {', '.join(titles)}."
        
    return {"response": response_text}

workflow = StateGraph(AgentState)

workflow.add_node("intent_detection", detect_intent)
workflow.add_node("goal_extraction", extract_goal)
workflow.add_node("gap_analysis", gap_analysis)
workflow.add_node("retrieve_resources", retrieve_resources)
workflow.add_node("rank_candidates", rank_candidates)
workflow.add_node("path_planning", plan_path)
workflow.add_node("response_generation", generate_response)

workflow.set_entry_point("intent_detection")
workflow.add_edge("intent_detection", "goal_extraction")
workflow.add_edge("goal_extraction", "gap_analysis")
workflow.add_edge("gap_analysis", "retrieve_resources")
workflow.add_edge("retrieve_resources", "rank_candidates")
workflow.add_edge("rank_candidates", "path_planning")
workflow.add_edge("path_planning", "response_generation")
workflow.add_edge("response_generation", END)

app_graph = workflow.compile()
