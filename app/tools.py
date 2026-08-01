from __future__ import annotations

from app.analytics import answer_analytics
from app.quality import answer_quality
from app.retrieval import answer_knowledge

try:
    from langchain.tools import tool
except ImportError:
    def tool(func):
        return func

@tool
def search_reservation_knowledge(question: str) -> dict:
    """Search reservation business, metric, table, and runbook documentation."""
    answer, evidence = answer_knowledge(question)
    return {"answer": answer, "evidence": evidence}

@tool
def query_reservation_metrics(question: str) -> dict:
    """Run an approved reservation metric query using a controlled query plan."""
    answer, data = answer_analytics(question)
    return {"answer": answer, "data": data}

@tool
def diagnose_reservation_quality(question: str) -> dict:
    """Run deterministic reservation freshness, completeness, null, and duplicate checks."""
    answer, data = answer_quality(question)
    return {"answer": answer, "data": data}
