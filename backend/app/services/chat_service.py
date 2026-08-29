import os
import json
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.retrieval.pinecone_client import pinecone_client
from sentence_transformers import SentenceTransformer

try:
    embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
except Exception:
    embedding_model = None

# Static knowledge about the VazhiThunAI website — injected into every prompt
WEBSITE_GUIDE = """
=== VAZHITHUNAI WEBSITE GUIDE (Navigation & Features) ===

VazhiThunAI is an AI-powered personalized learning path recommender.
Complete map of every page and what the user can do there:

1. **Dashboard** (URL: /dashboard or /)
   - Overview of overall learning progress, skill development chart, upcoming milestones, next recommended action.

2. **Learning Path** (URL: /path)
   - Full personalized roadmap in sequence order: skill name, status (pending/completed), estimated time, required/optional.

3. **AI Assistant / Chat** (URL: /chat)
   - Current page. Users ask anything about their path, goals, weaknesses, or the website.

4. **Pitfalls Page** (URL: /pitfalls)
   - Lists all detected misconceptions with status: DETECTED → REMEDIATION → VERIFICATION → RESOLVED.

5. **Pitfall Check / MCQ** (URL: /pitfalls/check/:skillId)
   - WHERE THE USER GOES TO TAKE MCQs / QUIZZES for a specific skill.
   - Presents multiple-choice questions to detect misconceptions in that skill.
   - After submitting, system evaluates the answer and explains the correct concept.
   - Example: to test Python → go to /pitfalls/check/{python-skill-id}

6. **Pitfall Detail** (URL: /pitfalls/:pitfallId)
   - Detailed view of a single pitfall: misconception, correct mental model, remediation steps.

7. **Pitfall Analytics** (URL: /pitfalls/analytics)
   - Population-level view of which misconceptions are most common across all learners.

8. **Onboarding** (URL: /onboarding)
   - Initial setup: user sets goals, experience level, learning preferences.

KEY USER ACTIONS:
- Take MCQ / Quiz for a skill → /pitfalls/check/{skillId}
- View full learning roadmap → /path
- See detected misconceptions → /pitfalls
- Check overall progress → /dashboard

When a user asks "where can I take an MCQ?", "where can I do a quiz?", or "how do I test my knowledge?",
ALWAYS direct them to /pitfalls/check/{relevant-skill-id}.
"""


class ChatService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY", "mock_groq_key"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")
        )

    def generate_embedding(self, text: str) -> List[float]:
        if embedding_model:
            # e5 models require "query: " prefix for asymmetric search
            return embedding_model.encode(f"query: {text}").tolist()
        return [0.1] * 1024

    def _fmt(self, data: Any, fallback: str = "None") -> str:
        """Safely format any data to a compact, readable string."""
        if data is None:
            return fallback
        if isinstance(data, list) and len(data) == 0:
            return fallback
        if isinstance(data, dict) and not data:
            return fallback
        return json.dumps(data, indent=2, default=str)

    def generate_chat_response(
        self,
        user_message: str,
        history: List[Dict[str, str]] = None,
        learner_data: Optional[dict] = None,
        learner_profile: Optional[dict] = None,
        active_goals: Optional[List[dict]] = None,
        pending_items: Optional[List[dict]] = None,
        completed_items: Optional[List[dict]] = None,
        mastered_skills: Optional[List[dict]] = None,
        weak_skills: Optional[List[dict]] = None,
        available_assessments: Optional[List[dict]] = None,
        recent_attempts: Optional[List[dict]] = None,
        pitfalls: Optional[List[dict]] = None,
        projects: Optional[List[dict]] = None,
    ) -> str:
        # --- Short-Term Memory Window (last 6 messages = 3 turns) ---
        history_str = ""
        if history:
            for msg in history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_str += f"{role.capitalize()}: {content}\n"

        # --- RAG: Retrieve relevant resources from Pinecone ---
        vector = self.generate_embedding(user_message)
        retrieved_docs = pinecone_client.query_vectors(vector=vector, top_k=3, namespace="resources")
        context_str = ""
        if "matches" in retrieved_docs:
            for match in retrieved_docs["matches"]:
                metadata = match.get("metadata", {})
                content = metadata.get("content", match.get("id", ""))
                context_str += f"- {content}\n"
        if not context_str:
            context_str = "No additional resources retrieved."

        # --- Build the context string safely (Python string, no LangChain parsing yet) ---
        system_context = (
            "You are **VazhiThun**, the AI learning guide inside the VazhiThunAI platform.\n\n"
            "## YOUR RULES\n"
            "- You are **READ-ONLY**. You guide, explain, and motivate. You CANNOT update the database or mark tasks complete.\n"
            "- Always base answers on the learner's actual state below. NEVER invent progress, courses, or skills.\n"
            "- Use **markdown** formatting in all responses (bold, bullets, headers) for clarity.\n"
            "- When answering navigation questions, ALWAYS provide the exact URL path.\n"
            "- If data is missing for a section, say 'No data available yet' — do not guess.\n\n"
            + WEBSITE_GUIDE
            + "\n\n=== LEARNER FULL STATE (Live from Database) ===\n\n"
            "**Full Learner Record:**\n" + self._fmt(learner_data, "Not found.") + "\n\n"
            "**Interests & Preferences:**\n" + self._fmt(learner_profile, "Not set.") + "\n\n"
            "**Active Goals:**\n" + self._fmt(active_goals, "No active goals.") + "\n\n"
            "**Completed Courses (last 5):**\n" + self._fmt(completed_items, "No completed items yet.") + "\n\n"
            "**Upcoming Pending Path Items (next 5):**\n" + self._fmt(pending_items, "No pending items.") + "\n\n"
            "**Mastered Skills (mastery >= 60%):**\n" + self._fmt(mastered_skills, "No mastered skills yet.") + "\n\n"
            "**Weak Skills (mastery < 60%):**\n" + self._fmt(weak_skills, "No weakness data.") + "\n\n"
            "**Available MCQ Assessments for Current Skills:**\n" + self._fmt(available_assessments, "No assessments found.") + "\n\n"
            "**Recent Assessment Attempts:**\n" + self._fmt(recent_attempts, "No attempts yet.") + "\n\n"
            "**Pitfalls / Misconceptions (all statuses):**\n" + self._fmt(pitfalls, "No pitfalls detected yet.") + "\n\n"
            "**Recommended Projects for Target Role:**\n" + self._fmt(projects, "No project recommendations.") + "\n\n"
            "**Retrieved Resources (RAG):**\n" + context_str + "\n\n"
            "**Recent Conversation:**\n" + (history_str if history_str else "Start of conversation.") + "\n\n"
        )

        # --- Build a safe prompt template ---
        # We pass system_context as an input variable so LangChain doesn't try to parse the JSON braces {} inside it.
        prompt_template = PromptTemplate(
            input_variables=["system_context", "user_message"],
            template="{system_context}\n---\nUser Query: {user_message}\n\nVazhiThun:"
        )

        chain = prompt_template | self.llm
        response = chain.invoke({
            "system_context": system_context, 
            "user_message": user_message
        })
        return response.content


chat_service = ChatService()
