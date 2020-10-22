PYTHON=poetry run

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
.SILENT: format
format:
	$(PYTHON) black .
	$(PYTHON) isort .

.PHONY: style
.SILENT: style
style:
	$(PYTHON) pyflakes eddrit
	$(PYTHON) mypy --ignore-missing-imports --disallow-untyped-defs -- .
	$(PYTHON) black --check .
	$(PYTHON) isort --check-only  .

.PHONY: test
.SILENT: test
test:
	$(PYTHON) pytest --cov=eddrit

.PHONY: run
.SILENT: run
run:
	$(PYTHON) uvicorn --reload eddrit.app:app

.PHONY: build
.SILENT: build
build:
	docker build -t eddrit .