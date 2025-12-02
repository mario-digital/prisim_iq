.PHONY: setup dev dev-backend dev-frontend test test-backend test-frontend lint lint-backend lint-frontend clean help

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

##@ Setup

setup: ## Initial project setup
	@echo "$(CYAN)Setting up PrismIQ...$(RESET)"
	./scripts/setup.sh

##@ Development

dev: ## Start both frontend and backend development servers
	./scripts/dev.sh

dev-backend: ## Start backend development server only
	@echo "$(CYAN)Starting backend...$(RESET)"
	cd backend && source .venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server only
	@echo "$(CYAN)Starting frontend...$(RESET)"
	cd frontend && bun run dev

##@ Testing

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(CYAN)Running backend tests...$(RESET)"
	cd backend && source .venv/bin/activate && pytest -v

test-frontend: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(RESET)"
	cd frontend && bun test

##@ Linting

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	@echo "$(CYAN)Linting backend...$(RESET)"
	cd backend && source .venv/bin/activate && ruff check src/ tests/

lint-frontend: ## Lint frontend code
	@echo "$(CYAN)Linting frontend...$(RESET)"
	cd frontend && bun run lint

##@ Build

build-frontend: ## Build frontend for production
	@echo "$(CYAN)Building frontend...$(RESET)"
	cd frontend && bun run build

##@ Utilities

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf backend/__pycache__ backend/.pytest_cache backend/.mypy_cache
	rm -rf frontend/.next frontend/out frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(RESET)"

install-backend: ## Install backend dependencies
	@echo "$(CYAN)Installing backend dependencies...$(RESET)"
	cd backend && source .venv/bin/activate && uv pip sync requirements.lock

install-frontend: ## Install frontend dependencies
	@echo "$(CYAN)Installing frontend dependencies...$(RESET)"
	cd frontend && bun install

##@ Help

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(CYAN)PrismIQ$(RESET) - Dynamic Pricing Copilot\n\nUsage:\n  make $(GREEN)<target>$(RESET)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

