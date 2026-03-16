PYTHON := poetry run
SRC = eddrit

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
format:
	$(PYTHON) ruff format $(SRC)
	$(PYTHON) ruff check --fix $(SRC)
	biome format --write .
	biome check --write .


.PHONY: style
style:
	$(PYTHON) ruff format --check $(SRC)
	$(PYTHON) ruff check $(SRC)
	$(PYTHON) pyright -- $(SRC)
	biome lint .

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
