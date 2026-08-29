import os
import json
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

PLANNER_PROMPT = """
You are an expert educational planner. Your task is to take a list of highly-ranked candidate learning resources and sequence them into an optimal learning path based on the user's constraints.

Candidate Resources (JSON):
{candidates}

Constraints (JSON):
{constraints}

Your goal is to select the best resources and arrange them in order.
Assign each item a sequential `sequence_order` starting at 1.
Assign a `phase` to each item (e.g., "Foundation", "Intermediate", "Advanced", "Specialization").
Ensure the total estimated time fits logically into a structured timeline.

Output ONLY a raw JSON array of objects with the following keys:
- `sequence_order` (int)
- `phase` (string)
- `resource_id` (string, MUST exactly match the id from Candidate Resources)
- `title` (string)
- `estimated_minutes` (int)

Do NOT include markdown formatting, backticks, or extra text. Only the raw JSON array.
"""

def optimize_learning_path(ranked_candidates: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Plan the sequence of learning items taking into account prerequisite ordering,
    time constraints, and maximum weekly hours using an LLM.
    """
    if not ranked_candidates:
        return []

    try:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY", "mock_groq_key"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192"),
            temperature=0.1
        )
        
        prompt = PromptTemplate.from_template(PLANNER_PROMPT)
        chain = prompt | llm
        
        # Pass top 10 candidates to avoid context overflow
        candidates_str = json.dumps(ranked_candidates[:10], indent=2)
        constraints_str = json.dumps(constraints, indent=2)
        
        res = chain.invoke({
            "candidates": candidates_str,
            "constraints": constraints_str
        })
        
        # Parse the JSON array from the LLM
        content = res.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        path_items = json.loads(content.strip())
        return path_items
    except Exception as e:
        print(f"Planner LLM failed: {e}")
        # Fallback to greedy sequencing if LLM fails
        fallback_path = []
        for i, candidate in enumerate(ranked_candidates[:5]):
            fallback_path.append({
                "sequence_order": i + 1,
                "phase": "Core Learning" if i > 0 else "Foundation",
                "resource_id": candidate.get("id") or candidate.get("resource_id", "unknown"),
                "title": candidate.get("title", "Untitled Resource"),
                "estimated_minutes": candidate.get("duration_minutes", 60)
            })
        return fallback_path
