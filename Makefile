PYTHON := poetry run
ROME := npx rome@latest
SRC = eddrit
JS_SRC = static/js

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
format:
	$(PYTHON) black $(SRC)
	$(PYTHON) ruff --fix $(SRC)
	$(ROME) check --apply $(JS_SRC)

.PHONY: style
style:
	$(PYTHON) black --check $(SRC)
	$(PYTHON) ruff $(SRC)
	$(PYTHON) mypy -- $(SRC)
	$(ROME) check $(JS_SRC)

.PHONY: test
.SILENT: test
test:
	$(PYTHON) pytest --cov=$(SRC)

.PHONY: run
.SILENT: run
run:
	$(PYTHON) uvicorn --reload $(SRC).app:app

.PHONY: build
.SILENT: build
build:
	docker build -t eddrit .
