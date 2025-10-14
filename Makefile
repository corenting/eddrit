PYTHON := poetry run
BIOME := npx @biomejs/biome@latest
SRC = eddrit
BIOME_FILES = static/js static/css

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
format:
	$(PYTHON) ruff format $(SRC)
	$(PYTHON) ruff check --fix $(SRC)
	$(BIOME) format --write $(BIOME_FILES)
	$(BIOME) check --write $(BIOME_FILES)


.PHONY: style
style:
	$(PYTHON) ruff format --check $(SRC)
	$(PYTHON) ruff check $(SRC)
	$(PYTHON) pyright -- $(SRC)
	$(BIOME) lint $(BIOME_FILES)

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
