NAME = src

run:
	uv run python -m src
	
install:
	wget -qO- https://astral.sh/uv/install.sh | sh
	uv pip install -r pyproject.toml
	uv sync


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
