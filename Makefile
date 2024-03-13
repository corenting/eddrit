PYTHON := poetry run
BIOME := npx @biomejs/biome@latest
SRC = eddrit
JS_SRC = static/js

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
format:
	$(PYTHON) ruff format $(SRC)
	$(PYTHON) ruff check --fix $(SRC)
	$(BIOME) format --write $(JS_SRC)
	$(BIOME) check --apply $(JS_SRC)


.PHONY: style
style:
	$(PYTHON) ruff format --check $(SRC)
	$(PYTHON) ruff check $(SRC)
	$(PYTHON) pyright -- $(SRC)
	$(BIOME) lint  $(JS_SRC)

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
