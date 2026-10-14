NAME = src
SGOINFRE := /sgoinfre/students/$(USER)/CMM

export VIRTUAL_ENV := $(SGOINFRE)/venv
export UV_PROJECT_ENVIRONMENT := $(VIRTUAL_ENV)
export UV_PYTHON_CACHE_DIR := $(SGOINFRE)/uv/cache
export UV_CACHE_DIR := $(SGOINFRE)/uv/python-cache
export HF_HOME := /sgoinfre/students/$(USER)/huggingface

all: install run

run:
	@uv run python -m src

install:
	@mkdir -p $(VIRTUAL_ENV) $(UV_CACHE_DIR) $(UV_PYTHON_CACHE_DIR) $(HF_HOME)
	@which uv > /dev/null 2>&1 || wget -qO- https://astral.sh/uv/install.sh | sh
	@uv sync


debug:
	uv run python -m pdb -m src

clean:
	rm -rf .mypy_cache
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf .pytest_cache

lint:
	flake8 --exclude=./venv .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 --exclude=./venv .
	mypy . --strict
