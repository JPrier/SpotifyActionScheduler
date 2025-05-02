deps:
    bash scripts/setup.sh

lint:
    uvx ruff check --exit-zero .

format:
    uvx ruff format . 

test:
    uv run --frozen pytest -q

# All checks
build: deps lint test
