"""
Rule-based intent classifier for adaptive learning chat commands.
No LLM used for routing — all decisions are keyword/pattern-based.
"""
import re
from typing import Dict, Any

# Intent constants
INTENT_TOO_HARD = "TOO_HARD"
INTENT_TOO_EASY = "TOO_EASY"
INTENT_ALREADY_KNOWN = "ALREADY_KNOWN"
INTENT_REQUEST_FASTER = "REQUEST_FASTER"
INTENT_REQUEST_LIGHTER = "REQUEST_LIGHTER"
INTENT_CHANGE_HOURS = "CHANGE_HOURS"
INTENT_CHANGE_DEADLINE = "CHANGE_DEADLINE"
INTENT_WHY_CHANGED = "WHY_CHANGED"
INTENT_WHAT_IF = "WHAT_IF"
INTENT_GENERAL_CHAT = "GENERAL_CHAT"

# Pattern lists — order matters, more specific first
_PATTERNS = [
    # Already known / skip
    (INTENT_ALREADY_KNOWN, [
        r"i\s+(already|already\s+know|know\s+this|know\s+it)",
        r"(skip|skipping)\s+(this|it|the)",
        r"i.{0,10}(familiar|mastered|done this)",
        r"know\s+(python|statistics|ml|this)",
    ]),
    # Too hard / difficult
    (INTENT_TOO_HARD, [
        r"too\s+(hard|difficult|complex|advanced|tough|overwhelming)",
        r"(can't|cannot|struggle|struggling|confused|confusing)",
        r"this\s+is\s+(hard|difficult|tough|complex)",
        r"(make|something)\s+(easier|simpler|beginner)",
        r"simplif",
        r"slow\s+down",
        r"easier\s+(path|version|material|resource)",
    ]),
    # Too easy
    (INTENT_TOO_EASY, [
        r"too\s+(easy|simple|basic|trivial|beginner)",
        r"(boring|bored|unchallenging)",
        r"(advanced|harder|more\s+challenging)",
        r"need\s+(more|harder|advanced)\s+(challenge|material|content)",
    ]),
    # Faster path
    (INTENT_REQUEST_FASTER, [
        r"(finish|complete|done)\s+(faster|quicker|sooner|in\s+less\s+time)",
        r"(faster|quicker|shorter)\s+(path|plan|roadmap|schedule)",
        r"can\s+i\s+(finish|complete)\s+(faster|sooner|quicker)",
        r"speed\s+up",
        r"what\s+if\s+i\s+(study|learn)\s+more",
        r"finish\s+(earlier|early|in\s+\d+\s+months?)",
    ]),
    # Lighter path
    (INTENT_REQUEST_LIGHTER, [
        r"(lighter|simpler|minimal|minimum)\s+(path|plan|roadmap)",
        r"(less|fewer)\s+(resources|courses|materials)",
        r"(reduce|cut|trim|shorten)\s+(my\s+)?(path|roadmap|course)",
        r"only\s+(essential|necessary|required|core)\s+(stuff|things|material|content)",
        r"remove\s+(optional|extra|unnecessary)",
        r"bare\s+minimum",
    ]),
    # Hours change
    (INTENT_CHANGE_HOURS, [
        r"(only|just)\s+(\d+)\s+hours?\s+(a\s+week|per\s+week|weekly)",
        r"(\d+)\s+hours?\s+(a\s+week|per\s+week|weekly|a\s+day|per\s+day)",
        r"(change|update|set)\s+(my\s+)?(weekly\s+)?(study\s+)?hours",
        r"(can|could)\s+only\s+study\s+(\d+)\s+hours?",
        r"study\s+(\d+)\s+hours?",
        r"i\s+have\s+(\d+)\s+hours?",
    ]),
    # Deadline change
    (INTENT_CHANGE_DEADLINE, [
        r"(finish|complete|done)\s+in\s+(\d+)\s+(weeks?|months?)",
        r"(need|want|have)\s+to\s+(finish|complete)\s+in\s+(\d+)\s+(weeks?|months?)",
        r"(change|update|set|extend)\s+(my\s+)?deadline",
        r"deadline\s+is\s+(\d+)\s+(weeks?|months?)",
        r"by\s+(\d+)\s+(weeks?|months?)",
        r"in\s+(\d+)\s+months?",
    ]),
    # Why changed / explanation
    (INTENT_WHY_CHANGED, [
        r"why\s+(did|was|has)\s+(my\s+)?(path|roadmap|plan)\s+change",
        r"what\s+changed",
        r"(explain|tell\s+me)\s+(why|what)\s+(changed|happened|was\s+updated)",
        r"why\s+(is|was)\s+(this|the)\s+(resource|course)\s+(changed|replaced|different)",
        r"adaptation\s+history",
        r"what\s+happened\s+to\s+my\s+(path|plan)",
    ]),
    # What-if / simulation
    (INTENT_WHAT_IF, [
        r"what\s+if\s+i",
        r"(simulate|simulation)",
        r"what\s+would\s+happen\s+if",
        r"can\s+i\s+still\s+(finish|complete)",
    ]),
]


def _extract_number(text: str) -> float | None:
    """Extract the first number from text."""
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def classify_adaptive_intent(user_message: str) -> Dict[str, Any]:
    """
    Classify a user message into an adaptive intent.
    Returns:
        {
            "intent": str,
            "confidence": float,
            "extracted": dict  # any extracted parameters (hours, deadline, etc.)
        }
    """
    text = user_message.lower().strip()
    extracted: Dict[str, Any] = {}

    for intent, patterns in _PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text):
                # Extract parameters based on intent
                if intent == INTENT_CHANGE_HOURS:
                    hours = _extract_number(text)
                    if hours:
                        extracted["new_hours"] = hours
                elif intent == INTENT_CHANGE_DEADLINE:
                    num = _extract_number(text)
                    if num:
                        if "month" in text:
                            extracted["deadline_weeks"] = num * 4.33
                            extracted["deadline_months"] = num
                        else:
                            extracted["deadline_weeks"] = num
                return {
                    "intent": intent,
                    "confidence": 0.85,
                    "extracted": extracted,
                    "matched_pattern": pattern,
                }

    return {
        "intent": INTENT_GENERAL_CHAT,
        "confidence": 0.5,
        "extracted": {},
    }
