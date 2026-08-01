from pathlib import Path
import pandas as pd
from pipelines.build_reservation_mart import build_with_pandas

def test_mart_grain_and_flags():
    mart=build_with_pandas()
    assert not mart.duplicated(["user_id","campaign_id","product_id","site"]).any()
    assert set(mart["paid_flag"].unique()) <= {0,1}
    assert ((mart["paid_flag"]==1) & (mart["reserved_not_paid_flag"]==1)).sum() == 0
