.PHONY: help start logs stop destroy api-dev api-logs api-shell api-test

help:
	@echo "Available commands:"
	@echo ""
	@echo "Global commands:"
	@echo "  make start        - Start all services with Docker Compose"
	@echo "  make logs         - Show logs for all services"
	@echo "  make stop         - Stop all services"
	@echo "  make destroy      - Stop and remove all containers, volumes, and networks"
	@echo ""
	@echo "API commands:"
	@echo "  make api-dev      - Start API in development mode (local)"
	@echo "  make api-logs     - Show logs for API service"
	@echo "  make api-shell    - Enter API container shell"
	@echo "  make api-test     - Run API tests"

# Global commands
start:
	chmod +x quick-start.sh
	./quick-start.sh

logs:
	docker compose logs -f

stop:
	docker compose stop

destroy:
	docker compose down -v --remove-orphans

# API commands
api-dev:
	docker compose up api -d

api-logs:
	docker compose logs -f api

api-shell:
	docker compose exec api /bin/sh

api-test:
	cd api && uv run pytest
