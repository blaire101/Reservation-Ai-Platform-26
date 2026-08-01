from app.router import classify_intent

def test_routes():
    assert classify_intent("What is reserved-not-paid?") == "KNOWLEDGE"
    assert classify_intent("Show conversion rate by site") == "ANALYTICS"
    assert classify_intent("Why is the dashboard incomplete?") == "QUALITY"
