NAME = src

install:
	wget -qO- https://astral.sh/uv/install.sh | sh
	uv sync

run:
	uv run python -m src

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
