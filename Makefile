PYTHON := poetry run
EXEC_WRAPPER := mise exec --
SRC = eddrit

.PHONY: init
.SILENT: init
init:
	poetry install

.PHONY: format
format:
	$(EXEC_WRAPPER) $(PYTHON) ruff format $(SRC)
	$(EXEC_WRAPPER) $(PYTHON) ruff check --fix $(SRC)
	$(EXEC_WRAPPER) biome format --write .
	$(EXEC_WRAPPER) biome check --write .


.PHONY: style
style:
	$(EXEC_WRAPPER) $(PYTHON) ruff format --check $(SRC)
	$(EXEC_WRAPPER) $(PYTHON) ruff check $(SRC)
	$(EXEC_WRAPPER) $(PYTHON) pyright -- $(SRC)
	$(EXEC_WRAPPER) biome lint .

.PHONY: test
.SILENT: test
test:
	$(EXEC_WRAPPER) $(PYTHON) pytest --cov=$(SRC)

.PHONY: run
.SILENT: run
run:
	$(EXEC_WRAPPER) $(PYTHON) uvicorn --reload $(SRC).app:app

.PHONY: build
.SILENT: build
build:
	docker build -t eddrit .
