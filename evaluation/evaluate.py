from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.graph import ask

items=json.loads((ROOT/"evaluation"/"questions.json").read_text())
routing=0; retrieval_total=0; retrieval_hit=0; analytics_total=0; analytics_ok=0
for item in items:
    result=ask(item["question"])
    routing += result.route == item["expected_route"]
    if "expected_source" in item:
        retrieval_total += 1
        retrieval_hit += any(e.source == item["expected_source"] for e in result.evidence)
    if item["expected_route"] == "ANALYTICS":
        analytics_total += 1
        analytics_ok += bool(result.data.get("rows"))
print(json.dumps({
    "routing_accuracy": f"{routing}/{len(items)}",
    "retrieval_hit_rate": f"{retrieval_hit}/{retrieval_total}",
    "analytics_execution_accuracy": f"{analytics_ok}/{analytics_total}",
}, indent=2))
