setup:
    bash scripts/setup.sh

deps:
    uv sync

lint:
    uvx ruff check --exit-zero .

format:
    uvx ruff format . 

test:
    PYTHONPATH=$PWD/spotifyActionService/src \
      uv run --extra dev \
        python -m coverage run --source=$PWD/spotifyActionService/src -m pytest
    uv run --extra dev coverage html || true
    uv run --extra dev coverage report

build: deps format lint test
