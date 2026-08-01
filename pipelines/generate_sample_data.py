from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
RNG = random.Random(42)

products = pd.DataFrame([
    ["P001", "Smartphone Pro", "Smartphone", "2026-07-10"],
    ["P002", "Robot Vacuum X20", "Smart Home", "2026-07-12"],
    ["P003", "Tablet Pro", "Tablet", "2026-07-18"],
    ["P004", "Smart Watch S5", "Wearable", "2026-07-20"],
], columns=["product_id", "product_name", "product_category", "launch_date"])

campaigns = pd.DataFrame([
    ["C001", "SG Smartphone Launch", "P001", "SG", "2026-07-01", "2026-07-09", "2026-07-10", "2026-07-20"],
    ["C002", "MY Smart Home Launch", "P002", "MY", "2026-07-02", "2026-07-11", "2026-07-12", "2026-07-22"],
    ["C003", "SG Tablet Launch", "P003", "SG", "2026-07-08", "2026-07-17", "2026-07-18", "2026-07-28"],
    ["C004", "MY Wearable Launch", "P004", "MY", "2026-07-10", "2026-07-19", "2026-07-20", "2026-07-30"],
], columns=["campaign_id", "campaign_name", "product_id", "site", "reservation_start_time", "reservation_end_time", "sale_start_time", "conversion_end_time"])

reservations=[]
orders=[]
user_num=1
for c in campaigns.itertuples(index=False):
    start=datetime.fromisoformat(c.reservation_start_time)
    for i in range(45):
        user=f"U{user_num:04d}"; user_num += 1
        t=start + timedelta(hours=RNG.randint(0, 24*7), minutes=RNG.randint(0,59))
        reservations.append([f"R{len(reservations)+1:05d}",user,c.campaign_id,c.product_id,c.site,t.isoformat(sep=' '),(t+timedelta(minutes=RNG.randint(5,45))).isoformat(sep=' ')])
        # conversion differs by campaign
        conversion_prob={"C001":0.72,"C002":0.55,"C003":0.64,"C004":0.48}[c.campaign_id]
        if RNG.random() < conversion_prob:
            order_time=datetime.fromisoformat(c.sale_start_time)+timedelta(hours=RNG.randint(0,24*8),minutes=RNG.randint(0,59))
            paid=RNG.random() < 0.88
            orders.append([f"O{len(orders)+1:05d}",user,c.product_id,c.site,order_time.isoformat(sep=' '),"COMPLETED" if paid else "CREATED","SUCCESS" if paid else "FAILED",(order_time+timedelta(minutes=RNG.randint(1,10))).isoformat(sep=' '),round(RNG.uniform(199,1299),2),(order_time+timedelta(minutes=20)).isoformat(sep=' ')])

# Deliberately incomplete SG partition used by the DQ demo.
anomaly_date=datetime(2026,7,31,9,0)
for i in range(5):
    reservations.append([f"R{len(reservations)+1:05d}",f"UA{i:03d}","C003","P003","SG",(anomaly_date+timedelta(minutes=i)).isoformat(sep=' '),(anomaly_date+timedelta(hours=4,minutes=i)).isoformat(sep=' ')])

pd.DataFrame(reservations,columns=["reservation_id","user_id","campaign_id","product_id","site","reservation_time","ingestion_time"]).to_csv(RAW/"fact_reservation.csv",index=False)
pd.DataFrame(orders,columns=["order_id","user_id","product_id","site","order_time","order_status","payment_status","payment_time","order_amount","ingestion_time"]).to_csv(RAW/"fact_order.csv",index=False)
products.to_csv(RAW/"dim_product.csv",index=False)
campaigns.to_csv(RAW/"dim_campaign.csv",index=False)
print(f"Generated {len(reservations)} reservations and {len(orders)} orders in {RAW}")
