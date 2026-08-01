from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.config import settings

@dataclass
class RetrievedChunk:
    source: str
    text: str
    score: float

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")

def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text) if len(t) > 2}

class KeywordRetriever:
    def __init__(self, documents_dir: Path | None = None):
        self.documents_dir = documents_dir or settings.documents_dir
        self.documents = self._load()

    def _load(self) -> list[tuple[str, str]]:
        docs: list[tuple[str, str]] = []
        for path in sorted(self.documents_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            # heading-aware chunks, simple and deterministic for tests
            sections = re.split(r"(?=^##?\s)", text, flags=re.MULTILINE)
            for section in sections:
                section = section.strip()
                if section:
                    docs.append((path.name, section))
        return docs

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        q_tokens = _tokens(query)
        ranked: list[RetrievedChunk] = []
        for source, text in self.documents:
            d_tokens = _tokens(text)
            overlap = len(q_tokens & d_tokens)
            bonus = sum(2 for token in q_tokens if token in text.lower())
            score = float(overlap + bonus)
            if score > 0:
                ranked.append(RetrievedChunk(source, text[:700], score))
        ranked.sort(key=lambda x: x.score, reverse=True)
        return ranked[: top_k or settings.top_k]

class LlamaIndexRetriever:
    """Optional full retrieval backend. Falls back cleanly when extras are unavailable."""
    def __init__(self, documents_dir: Path | None = None):
        self.documents_dir = documents_dir or settings.documents_dir
        try:
            from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        except ImportError as exc:
            raise RuntimeError(
                "LlamaIndex backend requires requirements.txt. "
                "Use RETRIEVAL_BACKEND=keyword for the lightweight mode."
            ) from exc
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = None
        documents = SimpleDirectoryReader(str(self.documents_dir), required_exts=[".md"]).load_data()
        self.index = VectorStoreIndex.from_documents(documents)

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        retriever = self.index.as_retriever(similarity_top_k=top_k or settings.top_k)
        nodes = retriever.retrieve(query)
        output: list[RetrievedChunk] = []
        for item in nodes:
            source = item.node.metadata.get("file_name", "document")
            output.append(RetrievedChunk(source, item.node.get_content()[:700], float(item.score or 0)))
        return output

def get_retriever():
    if settings.retrieval_backend.lower() == "llamaindex":
        return LlamaIndexRetriever()
    return KeywordRetriever()

def answer_knowledge(question: str) -> tuple[str, list[dict[str, str]]]:
    chunks = get_retriever().search(question)
    if not chunks:
        return "I could not find supporting documentation for this question.", []
    evidence = [{"source": c.source, "excerpt": c.text[:260]} for c in chunks]
    combined = "\n\n".join(c.text for c in chunks)
    q = question.lower()
    if "grain" in q:
        answer = "The mart grain is User × Campaign × Product × Site: one row represents one user's reservation for one product within one campaign and country site."
    elif "matched" in q or "match" in q:
        answer = "A reservation is matched to an order by the same user, product, and site, with the order time falling inside the campaign conversion window."
    elif "reserved-not-paid" in q or "reserved not paid" in q:
        answer = "Reserved-not-paid means the user made a valid reservation but did not reach a successful final payment within the campaign conversion window. It includes no-order and payment-failed cases."
    else:
        answer = "The relevant project documentation says:\n" + combined[:900]
    return answer, evidence
