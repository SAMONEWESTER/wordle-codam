run:
	uv run python wordle.py

clean:
	rm -rf .venv

lint:
	uv run ruff check .

fix:
	uv run ruff check . --fix

format:
	uv run ruff format .

typecheck:
	uv run pyright

.PHONY: run clean lint fix format typecheck

.DEFAULT_GOAL := run