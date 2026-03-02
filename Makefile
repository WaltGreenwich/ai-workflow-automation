.PHONY: help setup up down logs logs-backend logs-n8n test test-watch clean rebuild \
        shell-backend shell-n8n shell-db ps restart health demo import-workflows

help: ## Show available commands
	@echo "=========================================="
	@echo "  AI Workflow Automation Platform"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## First-time setup (creates .env and builds containers)
	@echo "🔧 Setting up project..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ""; \
		echo "✅ .env created."; \
		echo ""; \
		echo "⚠️  ACTION REQUIRED: Edit .env and add your GOOGLE_API_KEY"; \
		echo "   Free key: https://makersuite.google.com/app/apikey"; \
		echo ""; \
	else \
		echo "ℹ️  .env already exists"; \
	fi
	@docker compose build
	@echo "✅ Setup complete! Run: make up"

up: ## Start all services
	@echo "🚀 Starting services..."
	@docker compose up -d
	@echo "⏳ Waiting for services..."
	@sleep 12
	@echo ""
	@echo "✅ Services running:"
	@echo "   🎨 Frontend:   http://localhost:3000"
	@echo "   📄 Backend:    http://localhost:8000"
	@echo "   📖 API Docs:   http://localhost:8000/docs"
	@echo "   🔄 n8n:        http://localhost:5678  (admin / admin123)"
	@echo "   🗄️  PostgreSQL: localhost:5432"
	@echo ""
	@echo "   Run: make health  to verify"

down: ## Stop all services
	@docker compose down
	@echo "✅ Services stopped"

logs: ## Live logs (all services)
	@docker compose logs -f

logs-backend: ## Live logs (backend only)
	@docker compose logs -f backend

logs-n8n: ## Live logs (n8n only)
	@docker compose logs -f n8n

test: ## Run backend test suite with coverage
	@echo "🧪 Running tests..."
	@docker compose exec backend pytest -v --cov=app --cov-report=term-missing
	@echo "📊 HTML coverage: backend/htmlcov/index.html"

test-watch: ## Tests in watch mode
	@docker compose exec backend pytest -v --cov=app -f

clean: ## Remove containers and volumes (WARNING: deletes all data)
	@echo "🧹 Cleaning up..."
	@docker compose down -v
	@docker system prune -f
	@echo "✅ Clean complete"

rebuild: ## Full rebuild from scratch
	@echo "🔨 Rebuilding..."
	@docker compose down -v
	@docker compose build --no-cache
	@docker compose up -d
	@echo "✅ Rebuild complete"

shell-backend: ## Shell into backend container
	@docker compose exec backend bash

shell-n8n: ## Shell into n8n container
	@docker compose exec n8n sh

shell-db: ## Open psql
	@docker compose exec postgres psql -U workflowuser -d workflowdb

ps: ## Container status
	@docker compose ps

restart: ## Restart all services
	@docker compose restart

health: ## Check all service health
	@echo "🏥 Health Check"
	@echo ""
	@echo "📄 Backend:"
	@curl -sf http://localhost:8000/api/v1/health | python3 -m json.tool 2>/dev/null || echo "   ❌ Not responding"
	@echo ""
	@echo "🔄 n8n:"
	@curl -sf http://localhost:5678/healthz && echo "   ✅ OK" || echo "   ❌ Not responding"
	@echo ""
	@echo "🎨 Frontend:"
	@curl -sf http://localhost:3000 > /dev/null && echo "   ✅ OK" || echo "   ❌ Not responding"

demo: ## Test the qualify-lead API
	@echo "🔬 Testing Lead Qualification API..."
	@curl -s -X POST http://localhost:8000/api/v1/langchain/qualify-lead \
		-H "Content-Type: application/json" \
		-d '{"name":"John Doe","company":"TechCorp","email":"john@techcorp.com","industry":"Technology","employees":500,"message":"Need AI automation ASAP, budget approved"}' \
		| python3 -m json.tool

import-workflows: ## Instructions for importing n8n workflows
	@echo ""
	@echo "📥 Import workflows into n8n:"
	@echo ""
	@echo "  1. Open: http://localhost:5678"
	@echo "  2. Login: admin / admin123"
	@echo "  3. Workflows -> + New -> ... -> Import from File"
	@echo "  4. Import each file from: ./n8n/workflows/"
	@echo "     - lead_qualification.json"
	@echo "     - email_routing.json"
	@echo "     - content_generation.json"
	@echo ""
	@echo "  ⚠️  Update Slack/Airtable credentials in each workflow"
