"""
Groq prompt templates for VazhiThunAI AI orchestration.
"""

INTENT_DETECTION_PROMPT = """
You are an AI learning navigator. Determine the learner's intent based on their message.
Analyze the message and return a JSON object with:
- intent_type: (e.g., 'goal_setting', 'question', 'feedback', 'skip_request')
- confidence: float between 0.0 and 1.0
- extracted_entities: any relevant entities (e.g., skills mentioned, deadlines)

Learner Message: {user_message}
"""

GOAL_EXTRACTION_PROMPT = """
Extract a structured learning goal from the user's natural language description.
Transform the high-level goal into a target role/outcome and a list of competencies/skills.

Learner Message: {user_message}
Current Profile: {learner_profile}

Return a JSON object with:
- target_objective: The overall objective
- target_role: The role or domain
- current_experience: Extracted experience level
- known_skills: List of skills they already have
- target_skills: List of skills they need to acquire
- constraints: Any time or format constraints
- deadline: Timeline if mentioned
"""

EXPLANATION_GENERATION_PROMPT = """
Generate a "Why this?" explanation for the recommended learning path.
Use the following context to explain why these resources and sequence were chosen.

Skill Gaps: {skill_gaps}
Recommended Path: {candidate_path}
Learner Goal: {goal}

The explanation should be empathetic, clear, and directly connect the path to their goal.
"""

DIAGNOSTIC_INTERVIEW_PROMPT = """
You are assessing a learner's proficiency in: {target_skill}.
Generate a diagnostic question to test their knowledge.
The question should be adaptive based on their previous responses.

Previous Context: {skill_context}
Question Type: {question_type} (e.g., conceptual, practical, scenario)

Output the question clearly.
"""

REPLANNING_DECISION_PROMPT = """
Analyze the recent learning events and decide if the current learning path needs replanning.

Recent Events: {events}
Current Mastery: {learner_profile}
Goal: {goal}

Return a JSON object with:
- decision: 'continue' or 'replan'
- reason: brief explanation for the decision
"""
