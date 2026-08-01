from __future__ import annotations

from typing import Any, Literal, TypedDict
from pydantic import BaseModel, Field

Intent = Literal["KNOWLEDGE", "ANALYTICS", "QUALITY"]

class SourceEvidence(BaseModel):
    source: str
    excerpt: str

class AgentResponse(BaseModel):
    question: str
    route: Intent
    answer: str
    evidence: list[SourceEvidence] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

class AgentState(TypedDict, total=False):
    question: str
    route: Intent
    answer: str
    evidence: list[dict[str, str]]
    data: dict[str, Any]
    warnings: list[str]
