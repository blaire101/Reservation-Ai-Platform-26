from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Settings:
    ai_mode: str = os.getenv("AI_MODE", "mock")
    retrieval_backend: str = os.getenv("RETRIEVAL_BACKEND", "keyword")
    pipeline_engine: str = os.getenv("PIPELINE_ENGINE", "pandas")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    top_k: int = int(os.getenv("TOP_K", "5"))
    documents_dir: Path = ROOT / "data" / "documents"
    raw_dir: Path = ROOT / "data" / "raw"
    warehouse_dir: Path = ROOT / "data" / "warehouse"
    index_dir: Path = ROOT / "data" / "index"

settings = Settings()
