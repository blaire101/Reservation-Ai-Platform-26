.PHONY: bootstrap data mart test eval api ui clean

bootstrap: data mart

data:
	python pipelines/generate_sample_data.py

mart:
	python pipelines/build_reservation_mart.py

test:
	pytest -q

eval:
	python evaluation/evaluate.py

api:
	uvicorn app.api:app --reload

ui:
	streamlit run streamlit_app.py

clean:
	rm -rf data/raw/*.csv data/warehouse/*.csv data/warehouse/*.db data/index/*
