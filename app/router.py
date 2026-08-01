from __future__ import annotations

from app.schemas import Intent

QUALITY_WORDS = {
    "incomplete", "missing", "late", "freshness", "duplicate", "null", "quality",
    "delay", "dashboard incomplete", "why is yesterday", "partition"
}
ANALYTICS_WORDS = {
    "show", "how many", "rate", "conversion", "lowest", "highest", "by site",
    "by campaign", "by product", "users reserved", "count"
}

def classify_intent(question: str) -> Intent:
    q = question.lower()
    if any(term in q for term in {"grain", "what does", "definition", "matched to", "how is a reservation matched"}):
        return "KNOWLEDGE"
    if any(term in q for term in QUALITY_WORDS):
        return "QUALITY"
    if any(term in q for term in ANALYTICS_WORDS):
        return "ANALYTICS"
    return "KNOWLEDGE"
