PYTHON := poetry run
SRC = eddrit
BIOME_FILES = static/js static/css/main.css static/css/nojs.css

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
format:
	$(PYTHON) ruff format $(SRC)
	$(PYTHON) ruff check --fix $(SRC)
	biome format --write $(BIOME_FILES)
	biome check --write $(BIOME_FILES)


.PHONY: style
style:
	$(PYTHON) ruff format --check $(SRC)
	$(PYTHON) ruff check $(SRC)
	$(PYTHON) pyright -- $(SRC)
	biome lint $(BIOME_FILES)

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
