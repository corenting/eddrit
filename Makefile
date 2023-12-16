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
	$(PYTHON) black $(SRC)
	$(PYTHON) ruff --fix $(SRC)
	$(BIOME) format --write $(JS_SRC)
	$(BIOME) check --apply $(JS_SRC)


.PHONY: style
style:
	$(PYTHON) black --check $(SRC)
	$(PYTHON) ruff $(SRC)
	$(PYTHON) mypy -- $(SRC)
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
