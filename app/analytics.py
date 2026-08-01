from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from app.config import settings

ALLOWED_DIMENSIONS = {"site", "campaign_name", "product_name", "product_category"}
ALLOWED_METRICS = {
    "reservation_users", "order_users", "paid_users",
    "reservation_to_order_rate", "reservation_to_payment_rate", "reserved_not_paid_users"
}

def _connect() -> sqlite3.Connection:
    db = settings.warehouse_dir / "reservation.db"
    if not db.exists():
        raise FileNotFoundError("Warehouse database missing. Run `make bootstrap`.")
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con

def parse_query_plan(question: str) -> dict[str, Any]:
    q = question.lower()
    dimension = "site"
    if "campaign" in q:
        dimension = "campaign_name"
    elif "product category" in q or "category" in q:
        dimension = "product_category"
    elif "product" in q:
        dimension = "product_name"

    if "order rate" in q or "reservation-to-order" in q:
        metric = "reservation_to_order_rate"
    elif "paid conversion" in q or "payment rate" in q or "conversion rate" in q:
        metric = "reservation_to_payment_rate"
    elif "reserved but did not pay" in q or "reserved-not-paid" in q:
        metric = "reserved_not_paid_users"
    elif "paid user" in q:
        metric = "paid_users"
    elif "order user" in q:
        metric = "order_users"
    else:
        metric = "reservation_users"
    return {"metric": metric, "dimension": dimension}

def execute_plan(plan: dict[str, Any]) -> dict[str, Any]:
    metric = plan["metric"]
    dimension = plan["dimension"]
    if metric not in ALLOWED_METRICS or dimension not in ALLOWED_DIMENSIONS:
        raise ValueError("Unsupported metric or dimension")

    aggregate = {
        "reservation_users": "COUNT(DISTINCT user_id)",
        "order_users": "COUNT(DISTINCT CASE WHEN order_flag=1 THEN user_id END)",
        "paid_users": "COUNT(DISTINCT CASE WHEN paid_flag=1 THEN user_id END)",
        "reserved_not_paid_users": "COUNT(DISTINCT CASE WHEN reserved_not_paid_flag=1 THEN user_id END)",
        "reservation_to_order_rate": "ROUND(100.0 * COUNT(DISTINCT CASE WHEN order_flag=1 THEN user_id END) / NULLIF(COUNT(DISTINCT user_id),0), 2)",
        "reservation_to_payment_rate": "ROUND(100.0 * COUNT(DISTINCT CASE WHEN paid_flag=1 THEN user_id END) / NULLIF(COUNT(DISTINCT user_id),0), 2)",
    }[metric]
    sql = (f"SELECT {dimension}, {aggregate} AS {metric} "
           f"FROM dm_reservation_conversion GROUP BY {dimension} "
           f"ORDER BY {metric} DESC")
    with _connect() as con:
        rows = [dict(r) for r in con.execute(sql).fetchall()]
    return {"query_plan": plan, "sql": sql, "rows": rows}

def answer_analytics(question: str) -> tuple[str, dict[str, Any]]:
    plan = parse_query_plan(question)
    result = execute_plan(plan)
    rows = result["rows"]
    if not rows:
        return "No matching data was found.", result
    metric = plan["metric"]
    dimension = plan["dimension"]
    formatted = "; ".join(f"{r[dimension]}: {r[metric]}" for r in rows)
    answer = f"{metric} by {dimension}: {formatted}."
    if "lowest" in question.lower():
        lowest = min(rows, key=lambda r: r[metric])
        answer = f"The lowest {metric} is {lowest[dimension]} at {lowest[metric]}."
    return answer, result
