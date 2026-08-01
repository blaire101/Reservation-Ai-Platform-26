from __future__ import annotations

import os, sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
WH = ROOT / "data" / "warehouse"
WH.mkdir(parents=True, exist_ok=True)

def build_with_pandas() -> pd.DataFrame:
    r=pd.read_csv(RAW/"fact_reservation.csv",parse_dates=["reservation_time","ingestion_time"])
    o=pd.read_csv(RAW/"fact_order.csv",parse_dates=["order_time","payment_time","ingestion_time"])
    c=pd.read_csv(RAW/"dim_campaign.csv",parse_dates=["reservation_start_time","reservation_end_time","sale_start_time","conversion_end_time"])
    p=pd.read_csv(RAW/"dim_product.csv",parse_dates=["launch_date"])
    r=r.sort_values("ingestion_time").drop_duplicates("reservation_id",keep="last")
    base=r.merge(c,on=["campaign_id","product_id","site"],how="left").merge(p,on="product_id",how="left")
    cand=base.merge(o,on=["user_id","product_id","site"],how="left",suffixes=("","_order"))
    valid=cand[(cand["order_time"].isna()) | ((cand["order_time"]>=cand["sale_start_time"]) & (cand["order_time"]<=cand["conversion_end_time"]))]
    valid=valid.sort_values("order_time").drop_duplicates("reservation_id",keep="first")
    valid["reserve_flag"]=1
    valid["order_flag"]=valid["order_id"].notna().astype(int)
    valid["paid_flag"]=(valid["payment_status"]=="SUCCESS").astype(int)
    valid["reserved_not_paid_flag"]=((valid["reserve_flag"]==1)&(valid["paid_flag"]==0)).astype(int)
    valid["partition_date"]=valid["reservation_time"].dt.strftime("%Y-%m-%d")
    cols=["user_id","campaign_id","campaign_name","product_id","product_name","product_category","site","reservation_time","order_id","order_time","payment_status","payment_time","order_amount","reserve_flag","order_flag","paid_flag","reserved_not_paid_flag","partition_date"]
    return valid[cols]

def build_with_spark() -> pd.DataFrame:
    try:
        from pyspark.sql import SparkSession, functions as F, Window
    except ImportError:
        print("PySpark is unavailable; falling back to pandas.")
        return build_with_pandas()
    spark=SparkSession.builder.master("local[*]").appName("reservation-mart").getOrCreate()
    r=spark.read.option("header",True).option("inferSchema",True).csv(str(RAW/"fact_reservation.csv"))
    o=spark.read.option("header",True).option("inferSchema",True).csv(str(RAW/"fact_order.csv"))
    c=spark.read.option("header",True).option("inferSchema",True).csv(str(RAW/"dim_campaign.csv"))
    p=spark.read.option("header",True).option("inferSchema",True).csv(str(RAW/"dim_product.csv"))
    for col in ["reservation_time","ingestion_time"]: r=r.withColumn(col,F.to_timestamp(col))
    for col in ["order_time","payment_time","ingestion_time"]: o=o.withColumn(col,F.to_timestamp(col))
    for col in ["reservation_start_time","reservation_end_time","sale_start_time","conversion_end_time"]: c=c.withColumn(col,F.to_timestamp(col))
    w=Window.partitionBy("reservation_id").orderBy(F.col("ingestion_time").desc())
    r=r.withColumn("rn",F.row_number().over(w)).filter("rn=1").drop("rn")
    base=r.join(c,["campaign_id","product_id","site"],"left").join(p,["product_id"],"left")
    joined=base.join(o,["user_id","product_id","site"],"left").filter(F.col("order_time").isNull()|((F.col("order_time")>=F.col("sale_start_time"))&(F.col("order_time")<=F.col("conversion_end_time"))))
    w2=Window.partitionBy("reservation_id").orderBy(F.col("order_time").asc_nulls_last())
    out=(joined.withColumn("rn",F.row_number().over(w2)).filter("rn=1").drop("rn")
         .withColumn("reserve_flag",F.lit(1)).withColumn("order_flag",F.when(F.col("order_id").isNotNull(),1).otherwise(0))
         .withColumn("paid_flag",F.when(F.col("payment_status")=="SUCCESS",1).otherwise(0))
         .withColumn("reserved_not_paid_flag",F.when(F.col("payment_status")=="SUCCESS",0).otherwise(1))
         .withColumn("partition_date",F.date_format("reservation_time","yyyy-MM-dd")))
    pdf=out.select("user_id","campaign_id","campaign_name","product_id","product_name","product_category","site","reservation_time","order_id","order_time","payment_status","payment_time","order_amount","reserve_flag","order_flag","paid_flag","reserved_not_paid_flag","partition_date").toPandas()
    spark.stop(); return pdf

def main():
    engine=os.getenv("PIPELINE_ENGINE","pandas").lower()
    mart=build_with_spark() if engine=="spark" else build_with_pandas()
    mart.to_csv(WH/"dm_reservation_conversion.csv",index=False)
    db=WH/"reservation.db"
    with sqlite3.connect(db) as con:
        mart.to_sql("dm_reservation_conversion",con,if_exists="replace",index=False)
    print(f"Built {len(mart)} mart rows using {engine}; output={WH}")

if __name__=="__main__": main()
