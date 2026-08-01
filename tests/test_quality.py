from app.quality import run_quality_checks

def test_known_incomplete_partition():
    result=run_quality_checks("2026-07-31","SG")
    assert result["status"] == "FAILED"
    assert "partition_completeness" in result["failed_checks"]
