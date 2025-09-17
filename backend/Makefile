PY=python

.PHONY: venv install dev run train-popularity

venv:
	$(PY) -m venv .venv

install:
	. .venv/Scripts/activate && pip install -r requirements.txt

dev:
	. .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000

train-popularity:
	. .venv/Scripts/activate && $(PY) scripts/train_popularity.py

