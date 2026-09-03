.PHONY: help run test lint format lint-fix

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "%-10s %s\n", $$1, $$2}'

run: ## Run the API standalone (mock LLM, no Docker/frontend needed)
	LLM_MODE=mock poetry run uvicorn app.main:app --reload

test: ## Run tests with coverage
	poetry run pytest --cov=app --cov-report=term-missing

lint: ## Check code style
	poetry run ruff check .

lint-fix: ## Check code style and auto-fix what's fixable
	poetry run ruff check . --fix

format: ## Format code
	poetry run ruff format .

.DEFAULT_GOAL := help
