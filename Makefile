PYTHON=poetry run
SRC = eddrit

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
	$(PYTHON) pflake8 $(SRC)
	$(PYTHON) mypy --ignore-missing-imports --disallow-untyped-defs -- $(SRC)
	$(PYTHON) black --check $(SRC)
	$(PYTHON) isort --check-only  $(SRC)

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
