PYTHON ?= python
MODE ?= sample
.PHONY: setup data train evaluate serve demo test lint
setup:
	$(PYTHON) -m pip install -e ".[dev]"
data:
	$(PYTHON) scripts/build_data.py --mode $(MODE)
train:
	$(PYTHON) scripts/train.py
evaluate:
	$(PYTHON) scripts/evaluate.py
serve:
	$(PYTHON) -m uvicorn real_estate_ranking.serving.api:app --reload
demo:
	$(PYTHON) scripts/run_demo.py
test:
	$(PYTHON) -m pytest -q
lint:
	$(PYTHON) -m ruff check src tests scripts

