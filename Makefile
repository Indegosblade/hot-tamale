.PHONY: lint format typecheck test coverage all

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

test:
	pytest

coverage:
	pytest --cov=hot_tamale --cov-report=term-missing

all: lint typecheck coverage
