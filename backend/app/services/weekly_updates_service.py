"""
Weekly Career Updates Service
==============================
Isolated module — does NOT modify any existing service.

Responsibilities:
  1. Build a keyword search query from an arbitrary career path string.
  2. Fetch recent articles from GNews API (last 7 days).
  3. Filter & rank articles for relevance (deprioritise clickbait/celeb news).
  4. Use Groq (llama3-8b-8192) to generate a concise summary + "why it matters"
     for each article.
  5. Return structured update objects.
  6. Cache results per career path for 6 hours to avoid hammering the news API.

Environment variables:
  WEEKLY_UPDATES_API_KEY  — GNews API key (https://gnews.io)
  GROQ_API_KEY            — reused from existing config (already in env file)
"""

import os
import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from app.core.config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Simple in-memory cache:  { career_path_lower: {"expires_at": float, "data": [...]} }
# ──────────────────────────────────────────────────────────────────────────────
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours

# ──────────────────────────────────────────────────────────────────────────────
# Career → keyword query mapping
# Works for the listed examples; also falls back generically for any career.
# ──────────────────────────────────────────────────────────────────────────────
CAREER_QUERY_MAP: Dict[str, str] = {
    "data scientist": "data science OR machine learning OR artificial intelligence OR LLM",
    "data engineer": "data engineering OR Apache Spark OR Databricks OR data pipeline OR ETL",
    "ml engineer": "machine learning engineering OR MLOps OR model deployment OR LLM",
    "machine learning engineer": "machine learning engineering OR MLOps OR model deployment OR LLM",
    "cloud engineer": "cloud computing OR AWS OR Azure OR Google Cloud OR Kubernetes OR DevOps",
    "devops engineer": "DevOps OR Kubernetes OR CI/CD OR infrastructure as code OR cloud",
    "cybersecurity": "cybersecurity OR information security OR zero trust OR vulnerability OR data breach",
    "cybersecurity engineer": "cybersecurity OR information security OR zero trust OR vulnerability OR data breach",
    "frontend developer": "frontend development OR React OR JavaScript OR TypeScript OR web development",
    "backend developer": "backend development OR API design OR Node.js OR Python OR microservices",
    "full stack developer": "full stack development OR React OR Node.js OR web development OR API",
    "product manager": "product management OR product strategy OR agile OR roadmap OR user research",
    "ui/ux designer": "UX design OR UI design OR Figma OR user experience OR design systems",
    "blockchain developer": "blockchain OR Web3 OR Ethereum OR smart contracts OR DeFi",
    "game developer": "game development OR Unity OR Unreal Engine OR gaming industry",
    "embedded systems engineer": "embedded systems OR IoT OR RTOS OR microcontroller OR firmware",
    "data analyst": "data analytics OR business intelligence OR SQL OR Power BI OR Tableau",
    "mobile developer": "mobile development OR iOS OR Android OR React Native OR Flutter",
}

# Words that signal low-quality/irrelevant articles — used to deprioritise
NOISE_KEYWORDS = [
    "celebrity", "kardashian", "gossip", "entertainment",
    "sports", "hollywood", "movie", "music album", "fashion",
    "diet", "weight loss", "horoscope",
]

# Words that signal high-value tech/career news
SIGNAL_KEYWORDS = [
    "release", "launch", "framework", "tool", "library", "model",
    "certification", "open source", "breakthrough", "raises", "funding",
    "acquisition", "security", "vulnerability", "update", "version",
    "career", "job", "hiring", "salary", "trend", "report", "benchmark",
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "AI / Technology":       ["ai", "artificial intelligence", "machine learning", "llm", "gpt", "neural", "model"],
    "Tools & Frameworks":    ["framework", "library", "sdk", "tool", "release", "version", "open source", "github"],
    "Security":              ["security", "vulnerability", "breach", "exploit", "patch", "cve"],
    "Career":                ["career", "job", "hiring", "salary", "layoff", "workforce", "skill"],
    "Research":              ["research", "paper", "study", "benchmark", "experiment", "findings"],
    "Industry":              ["company", "startup", "funding", "ipo", "acquisition", "partnership"],
    "Learning":              ["course", "certification", "bootcamp", "tutorial", "learn", "training"],
}


# ──────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────────────────────────────────────

def _build_query(career_path: str) -> str:
    """Return a GNews keyword query for the given career path."""
    key = career_path.strip().lower()
    if key in CAREER_QUERY_MAP:
        return CAREER_QUERY_MAP[key]
    # Generic fallback: use the career path itself plus related terms
    words = career_path.strip().title()
    return f"{words} OR {words} technology OR {words} tools OR {words} trends OR {words} career"


def _score_article(article: Dict[str, Any]) -> int:
    """
    Score an article 0-100 for relevance/quality.
    Higher = more important to show.
    """
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    score = 50  # baseline

    # Reward signal keywords
    for kw in SIGNAL_KEYWORDS:
        if kw in text:
            score += 5

    # Penalise noise keywords
    for kw in NOISE_KEYWORDS:
        if kw in text:
            score -= 20

    # Reward recency (published within last 3 days)
    try:
        pub_str = article.get("publishedAt", "")
        pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - pub_dt).days
        if age_days == 0:
            score += 20
        elif age_days == 1:
            score += 12
        elif age_days <= 3:
            score += 6
    except Exception:
        pass

    return max(0, min(100, score))


def _detect_category(article: Dict[str, Any]) -> str:
    """Detect a display category label from article text."""
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "Industry"


def _format_date(iso_str: str) -> str:
    """Format ISO date string to human-readable 'Aug 29, 2026'."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str


def _week_range_label() -> str:
    """Return e.g. 'Aug 24 – Aug 30, 2026'."""
    today = datetime.now(timezone.utc)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"


# ──────────────────────────────────────────────────────────────────────────────
# GNews fetch
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_gnews_articles(query: str, api_key: str, max_results: int = 15) -> List[Dict[str, Any]]:
    """
    Call GNews API and return raw article list.
    Raises RuntimeError if the call fails.
    """
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "sortby": "publishedAt",
        "max": max_results,
        "apikey": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])
    except requests.exceptions.Timeout:
        raise RuntimeError("GNews API timed out.")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        raise RuntimeError(f"GNews API returned HTTP {status}.")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch from GNews: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Groq AI summarisation
# ──────────────────────────────────────────────────────────────────────────────

_llm: Optional[ChatGroq] = None

def _get_llm() -> Optional[ChatGroq]:
    """Lazy-load ChatGroq. Returns None if GROQ_API_KEY is missing."""
    global _llm
    if _llm is not None:
        return _llm
    groq_key = settings.GROQ_API_KEY
    if not groq_key or groq_key.startswith("mock"):
        return None
    try:
        _llm = ChatGroq(api_key=groq_key, model_name="llama3-8b-8192")
        return _llm
    except Exception as e:
        logger.warning(f"Could not initialise Groq LLM: {e}")
        return None


_SUMMARY_PROMPT = PromptTemplate(
    input_variables=["title", "description", "career_path"],
    template=(
        "You are a career intelligence assistant for learners pursuing a career as a {career_path}.\n\n"
        "Given the following news article:\n"
        "Title: {title}\n"
        "Description: {description}\n\n"
        "Provide a JSON object with exactly these fields (no markdown, pure JSON):\n"
        "{{\n"
        '  "summary": "<2-3 sentence plain-English summary of the article>",\n'
        '  "why_it_matters": "<1-2 sentences explaining why this matters for someone '
        "pursuing a career as a {career_path}>\"\n"
        "}}\n\n"
        "Return only valid JSON. No extra text."
    )
)


def _summarise_article(article: Dict[str, Any], career_path: str, llm: ChatGroq) -> Dict[str, str]:
    """
    Use Groq to generate summary + why_it_matters.
    Falls back to raw description if AI fails.
    """
    import json as _json

    title = article.get("title", "")
    description = article.get("description", "")

    # Truncate to avoid token limits
    description = description[:800] if description else ""

    try:
        chain = _SUMMARY_PROMPT | llm
        result = chain.invoke({
            "title": title,
            "description": description,
            "career_path": career_path,
        })
        raw = result.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = _json.loads(raw)
        return {
            "summary": parsed.get("summary", description),
            "why_it_matters": parsed.get("why_it_matters", ""),
        }
    except Exception as e:
        logger.warning(f"Groq summarisation failed for '{title}': {e}")
        return {
            "summary": description or title,
            "why_it_matters": "",
        }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_weekly_updates(career_path: str, max_updates: int = 7) -> Dict[str, Any]:
    """
    Main entry point called by the router.

    Returns:
        {
            "career_path": str,
            "period": str,
            "updates": List[UpdateDict],
        }

    Raises RuntimeError with a user-friendly message if the external API is
    unavailable. The router catches this and returns a graceful error response.
    """
    cache_key = career_path.strip().lower()

    # ── Cache hit ──────────────────────────────────────────────────────────
    if cache_key in _cache:
        entry = _cache[cache_key]
        if time.time() < entry["expires_at"]:
            logger.info(f"Cache hit for career '{career_path}'")
            return entry["data"]

    # ── Validate API key ───────────────────────────────────────────────────
    api_key = settings.WEEKLY_UPDATES_API_KEY
    if not api_key or api_key.startswith("mock"):
        raise RuntimeError(
            "WEEKLY_UPDATES_API_KEY is not configured. "
            "Weekly updates are temporarily unavailable."
        )

    # ── Build query & fetch ────────────────────────────────────────────────
    query = _build_query(career_path)
    logger.info(f"Fetching GNews for career='{career_path}', query='{query}'")
    raw_articles = _fetch_gnews_articles(query, api_key, max_results=20)

    if not raw_articles:
        result = {
            "career_path": career_path,
            "period": _week_range_label(),
            "updates": [],
        }
        # Cache briefly even for empty to avoid hammering API
        _cache[cache_key] = {"expires_at": time.time() + 1800, "data": result}
        return result

    # ── Score & rank ───────────────────────────────────────────────────────
    scored = [
        (article, _score_article(article))
        for article in raw_articles
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Deduplicate by title similarity (simple prefix check)
    seen_titles: set = set()
    ranked: List[Dict[str, Any]] = []
    for article, score in scored:
        title_key = article.get("title", "")[:60].lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        ranked.append(article)
        if len(ranked) >= max_updates:
            break

    # ── AI summarisation ───────────────────────────────────────────────────
    llm = _get_llm()
    updates: List[Dict[str, Any]] = []

    for article in ranked:
        if llm:
            ai = _summarise_article(article, career_path, llm)
        else:
            # No Groq key — use raw description
            description = article.get("description") or article.get("title", "")
            ai = {"summary": description, "why_it_matters": ""}

        source_info = article.get("source", {})
        source_name = (
            source_info.get("name")
            if isinstance(source_info, dict)
            else str(source_info)
        ) or "Unknown Source"

        updates.append({
            "title": article.get("title", ""),
            "summary": ai["summary"],
            "why_it_matters": ai["why_it_matters"],
            "category": _detect_category(article),
            "source": source_name,
            "published_at": _format_date(article.get("publishedAt", "")),
            "url": article.get("url", "#"),
        })

    result = {
        "career_path": career_path,
        "period": _week_range_label(),
        "updates": updates,
    }

    # ── Cache for 6 hours ──────────────────────────────────────────────────
    _cache[cache_key] = {
        "expires_at": time.time() + CACHE_TTL_SECONDS,
        "data": result,
    }

    return result
