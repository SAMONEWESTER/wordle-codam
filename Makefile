.PHONY: install run clean

# Creates .venv (if needed) and installs the dependencies from
# pyproject.toml into it. uv reads .python-version and downloads
# that interpreter itself if it isn't installed yet, so this always
# lands on a Python version pygame ships a prebuilt wheel for.
install:
	uv python install
	uv sync

# Makes sure dependencies are installed, then runs the game inside
# that same .venv.
run: install
	uv run python -m wordle

clean:
	rm -rf .venv