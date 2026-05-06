.PHONY: help docker-up docker-down docker-restart docker-logs docker-clean run install lint format check

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker commands

docker-up: ## Start all services (db + bot)
	docker compose up -d

docker-down: ## Stop all containers
	docker compose down

docker-restart: ## Restart all containers
	docker compose restart

docker-logs: ## View container logs
	docker compose logs -f

docker-logs-db: ## View PostgreSQL logs
	docker compose logs -f db

docker-logs-bot: ## View bot logs
	docker compose logs -f bot

docker-clean: ## Stop containers and remove volumes
	docker compose down -v

docker-ps: ## Show running containers
	docker compose ps

docker-build: ## Rebuild bot image
	docker compose build

# Development commands

sync: ## Sync dependencies with uv
	uv sync

install: ## Add a new dependency (usage: make install pkg=aiogram)
	uv add $(pkg)

install-dev: ## Add a new dev dependency (usage: make install-dev pkg=ruff)
	uv add --dev $(pkg)

lint: ## Run ruff linter
	ruff check .

format: ## Format code with ruff
	ruff format .

check: ## Run linting and formatting checks
	ruff format --check .
	ruff check .
