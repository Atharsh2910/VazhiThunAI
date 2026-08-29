import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

ASSESSMENT_PROMPT = """
You are an expert AI grader. Evaluate the learner's assessment attempt.

Attempt Data:
{attempt_data}

Based on the provided question, correct answer (if any), and the learner's answer, determine:
1. `score`: A float from 0.0 to 1.0 indicating correctness.
2. `passed`: A boolean (true if score >= 0.7).
3. `skill_id`: The ID of the skill being tested.
4. `new_mastery`: A float from 0.0 to 1.0 representing the estimated new mastery level of this skill based on this answer.
5. `confidence`: A float from 0.0 to 1.0 indicating how confident you are in this evaluation (e.g., higher if it was a detailed open-ended response vs a guess).

Output ONLY a raw JSON object with this exact structure:
{{
    "score": 0.0,
    "passed": false,
    "mastery_update": {{
        "skill_id": "string",
        "new_mastery": 0.0,
        "confidence": 0.0
    }}
}}
Do NOT include markdown formatting, backticks, or extra text. Only the raw JSON object.
"""

def evaluate_assessment(attempt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate assessment answers against rubric and update learner model using LLM.
    """
    try:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY", "mock_groq_key"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192"),
            temperature=0.0
        )
        
        prompt = PromptTemplate.from_template(ASSESSMENT_PROMPT)
        chain = prompt | llm
        
        res = chain.invoke({
            "attempt_data": json.dumps(attempt_data, indent=2)
        })
        
        # Parse the JSON object from the LLM
        content = res.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        evaluation = json.loads(content.strip())
        
        # Ensure the skill_id is passed correctly if missing
        if "mastery_update" in evaluation and not evaluation["mastery_update"].get("skill_id"):
            evaluation["mastery_update"]["skill_id"] = attempt_data.get("skill_id", "unknown")
            
        return evaluation
    except Exception as e:
        print(f"Assessment LLM failed: {e}")
        # Fallback to conservative evaluation if LLM fails
        return {
            "score": 0.5,
            "passed": False,
            "mastery_update": {
                "skill_id": attempt_data.get("skill_id", "unknown"),
                "new_mastery": 0.5,
                "confidence": 0.3
            }
        }
