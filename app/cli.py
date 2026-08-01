from __future__ import annotations
import json, sys
from app.graph import ask

def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit('Usage: python -m app.cli "your question"')
    print(json.dumps(ask(question).model_dump(), indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
