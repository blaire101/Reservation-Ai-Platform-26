from app.analytics import execute_plan

def test_approved_metric_query():
    result=execute_plan({"metric":"reservation_to_payment_rate","dimension":"site"})
    assert result["rows"]
    assert {r["site"] for r in result["rows"]} >= {"SG","MY"}
