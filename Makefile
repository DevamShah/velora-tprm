# ═══════════════════════════════════════════════════════════════
# Velora TPRM — Makefile
# ═══════════════════════════════════════════════════════════════

.PHONY: help install dev infra core all down clean lint test fmt

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────

install: ## Install all packages with uv
	uv sync --all-packages

dev: ## Install in development mode
	uv sync --all-packages --dev

# ── Docker Compose ────────────────────────────────────────────

infra: ## Start infrastructure only (postgres, redis, minio)
	docker compose up -d postgres redis minio

core: ## Start infra + core services
	docker compose --profile core up -d

comms: ## Start communication services
	docker compose --profile comms up -d

reporting: ## Start reporting services
	docker compose --profile reporting up -d

admin: ## Start admin services
	docker compose --profile admin up -d

ai: ## Start AI services
	docker compose --profile ai up -d

frontend: ## Start frontend services (BFF + web app)
	docker compose --profile frontend up -d

all: ## Start everything
	docker compose --profile core --profile comms --profile reporting --profile admin --profile ai --profile workflow --profile frontend up -d

down: ## Stop all containers
	docker compose --profile core --profile comms --profile reporting --profile admin --profile ai --profile workflow --profile frontend down

clean: ## Stop all and remove volumes
	docker compose --profile core --profile comms --profile reporting --profile admin --profile ai --profile workflow --profile frontend down -v

# ── Development ───────────────────────────────────────────────

lint: ## Run linter on all services
	uv run ruff check .

fmt: ## Format all code
	uv run ruff format .

test: ## Run all tests
	uv run pytest

# ── Individual Services ───────────────────────────────────────

run-auth: ## Run auth service locally
	cd services/auth && uv run uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

run-vendor: ## Run vendor service locally
	cd services/vendor && uv run uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload

run-assessment: ## Run assessment service locally
	cd services/assessment && uv run uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload

run-framework: ## Run framework service locally
	cd services/framework && uv run uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload

run-scoring: ## Run scoring service locally
	cd services/scoring && uv run uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload

run-evidence: ## Run evidence service locally
	cd services/evidence && uv run uvicorn src.main:app --host 0.0.0.0 --port 8006 --reload

run-monitoring: ## Run monitoring service locally
	cd services/monitoring && uv run uvicorn src.main:app --host 0.0.0.0 --port 8007 --reload

run-finding: ## Run finding service locally
	cd services/finding && uv run uvicorn src.main:app --host 0.0.0.0 --port 8008 --reload

run-communication: ## Run communication service locally
	cd services/communication && uv run uvicorn src.main:app --host 0.0.0.0 --port 8009 --reload

run-reporting: ## Run reporting service locally
	cd services/reporting && uv run uvicorn src.main:app --host 0.0.0.0 --port 8010 --reload

run-admin: ## Run admin service locally
	cd services/admin && uv run uvicorn src.main:app --host 0.0.0.0 --port 8011 --reload

run-ai: ## Run AI service locally
	cd services/ai && uv run uvicorn src.main:app --host 0.0.0.0 --port 8012 --reload

# ── Database ──────────────────────────────────────────────────

db-migrate: ## Run alembic migrations (monolith — shared DB for Phase 1)
	cd src/backend && uv run alembic upgrade head

db-seed: ## Seed database with test data
	cd src/backend && uv run python -c "import asyncio; from app.core.seed import run_seed; from app.core.database import init_engine, get_db; asyncio.run(run_seed())"
