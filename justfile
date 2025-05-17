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
        uv run --frozen \
        coverage run --source=$PWD/spotifyActionService/src -m \
        pytest
    uv run --frozen coverage html || true
    uv run --frozen coverage report

build: deps format lint test
