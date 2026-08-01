# AWS Reference Architecture

The repository runs locally, while this document maps the same interfaces to AWS.

| Local implementation | AWS reference |
|---|---|
| `data/raw` | Amazon S3 raw zone |
| pandas / local PySpark | AWS Glue PySpark job |
| CSV mart | S3 Parquet mart |
| SQLite analytics | Athena + Glue Data Catalog |
| local document folder | S3 knowledge bucket |
| LlamaIndex local index | OpenSearch Serverless or Aurora PostgreSQL pgvector |
| optional OpenAI adapter | Amazon Bedrock adapter |
| FastAPI / Streamlit Docker | ECS Fargate |
| local logs | CloudWatch |
| environment variables | Secrets Manager / Parameter Store |

Suggested S3 layout:

```text
s3://reservation-intelligence/raw/fact_reservation/dt=YYYY-MM-DD/
s3://reservation-intelligence/raw/fact_order/dt=YYYY-MM-DD/
s3://reservation-intelligence/reference/dim_campaign/
s3://reservation-intelligence/reference/dim_product/
s3://reservation-intelligence/mart/dm_reservation_conversion/dt=YYYY-MM-DD/
s3://reservation-intelligence/knowledge/documents/
```

The source-system CDC/event SDK is intentionally out of scope. Existing ingestion jobs are assumed to land files in the raw zone.
