FROM python:3.11-slim
WORKDIR /app
COPY requirements-lite.txt .
RUN pip install --no-cache-dir -r requirements-lite.txt
COPY . .
RUN python pipelines/generate_sample_data.py && python pipelines/build_reservation_mart.py
EXPOSE 8000 8501
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
