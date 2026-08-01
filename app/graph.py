from __future__ import annotations

from app.analytics import answer_analytics
from app.quality import answer_quality
from app.retrieval import answer_knowledge
from app.router import classify_intent
from app.schemas import AgentResponse, AgentState, SourceEvidence


def route_node(state: AgentState) -> AgentState:
    return {"route": classify_intent(state["question"])}

def knowledge_node(state: AgentState) -> AgentState:
    answer, evidence = answer_knowledge(state["question"])
    return {"answer": answer, "evidence": evidence, "data": {}}

def analytics_node(state: AgentState) -> AgentState:
    answer, data = answer_analytics(state["question"])
    return {"answer": answer, "evidence": [], "data": data}

def quality_node(state: AgentState) -> AgentState:
    answer, data = answer_quality(state["question"])
    return {"answer": answer, "evidence": [], "data": data}

def choose_route(state: AgentState) -> str:
    return {"KNOWLEDGE": "knowledge", "ANALYTICS": "analytics", "QUALITY": "quality"}[state["route"]]

def build_graph():
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return None
    builder = StateGraph(AgentState)
    builder.add_node("route", route_node)
    builder.add_node("knowledge", knowledge_node)
    builder.add_node("analytics", analytics_node)
    builder.add_node("quality", quality_node)
    builder.add_edge(START, "route")
    builder.add_conditional_edges("route", choose_route, {
        "knowledge": "knowledge", "analytics": "analytics", "quality": "quality"
    })
    builder.add_edge("knowledge", END)
    builder.add_edge("analytics", END)
    builder.add_edge("quality", END)
    return builder.compile()

_GRAPH = build_graph()

def ask(question: str) -> AgentResponse:
    initial: AgentState = {"question": question, "warnings": []}
    if _GRAPH is not None:
        result = _GRAPH.invoke(initial)
    else:
        result = {**initial, **route_node(initial)}
        node = {"KNOWLEDGE": knowledge_node, "ANALYTICS": analytics_node, "QUALITY": quality_node}[result["route"]]
        result.update(node(result))
        result.setdefault("warnings", []).append("LangGraph is not installed; deterministic fallback workflow was used.")
    evidence = [SourceEvidence(**x) for x in result.get("evidence", [])]
    return AgentResponse(
        question=question,
        route=result["route"],
        answer=result.get("answer", ""),
        evidence=evidence,
        data=result.get("data", {}),
        warnings=result.get("warnings", []),
    )
