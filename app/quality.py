from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd

from app.config import settings

def run_quality_checks(date: str, site: str) -> dict[str, Any]:
    reservations = pd.read_csv(settings.raw_dir / "fact_reservation.csv", parse_dates=["reservation_time", "ingestion_time"])
    orders = pd.read_csv(settings.raw_dir / "fact_order.csv", parse_dates=["order_time", "payment_time", "ingestion_time"])
    target_date = pd.Timestamp(date).date()
    site = site.upper()
    r = reservations[(reservations["reservation_time"].dt.date == target_date) & (reservations["site"] == site)]
    o = orders[(orders["order_time"].dt.date == target_date) & (orders["site"] == site)]

    duplicate_count = int(r.duplicated(subset=["reservation_id"]).sum())
    null_rate = float(r[["user_id", "campaign_id", "product_id", "site"]].isna().mean().mean()) if len(r) else 1.0
    historical_median = reservations[(reservations["site"] == site) & (reservations["reservation_time"].dt.date != target_date)].groupby(reservations["reservation_time"].dt.date).size().median()
    expected_rows = max(int(historical_median or 0), 20)
    actual_rows = int(len(r))
    completeness = round(actual_rows / expected_rows, 4) if expected_rows else 0.0
    max_ingestion = r["ingestion_time"].max() if len(r) else pd.NaT
    freshness_delay_minutes = None
    if pd.notna(max_ingestion) and len(r):
        source_max = r["reservation_time"].max()
        freshness_delay_minutes = int((max_ingestion - source_max).total_seconds() / 60)

    failed = []
    if completeness < 0.8: failed.append("partition_completeness")
    if duplicate_count > 0: failed.append("duplicate_rate")
    if null_rate > 0.01: failed.append("null_rate")
    if freshness_delay_minutes is None or freshness_delay_minutes > 120: failed.append("freshness")

    return {
        "date": date,
        "site": site,
        "status": "FAILED" if failed else "PASSED",
        "failed_checks": failed,
        "evidence": {
            "expected_rows": expected_rows,
            "actual_rows": actual_rows,
            "completeness_ratio": completeness,
            "duplicate_count": duplicate_count,
            "null_rate": round(null_rate, 4),
            "freshness_delay_minutes": freshness_delay_minutes,
            "same_day_orders": int(len(o)),
        },
        "affected_metrics": ["reservation_users", "reservation_to_order_rate", "reservation_to_payment_rate"] if failed else [],
        "recommended_action": "Wait for source completion, correct invalid records, and rerun the affected partition." if failed else "No action required."
    }

def extract_date_site(question: str) -> tuple[str, str]:
    import re
    date_match = re.search(r"20\d{2}-\d{2}-\d{2}", question)
    date = date_match.group(0) if date_match else "2026-07-31"
    q = question.lower()
    site = "SG" if "singapore" in q or " sg" in q else "MY" if "malaysia" in q or " my" in q else "SG"
    return date, site

def answer_quality(question: str) -> tuple[str, dict[str, Any]]:
    date, site = extract_date_site(question)
    result = run_quality_checks(date, site)
    e = result["evidence"]
    if result["status"] == "FAILED":
        answer = (
            f"The {site} reservation data for {date} failed quality checks. "
            f"Actual rows were {e['actual_rows']} versus an expected baseline of {e['expected_rows']} "
            f"(completeness {e['completeness_ratio']:.1%}). "
            f"Failed checks: {', '.join(result['failed_checks'])}. "
            f"Recommended action: {result['recommended_action']}"
        )
    else:
        answer = f"The {site} reservation data for {date} passed the configured quality checks."
    return answer, result
