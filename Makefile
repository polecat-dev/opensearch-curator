# Makefile for OpenSearch Curator development

.PHONY: help install test lint clean docker-up docker-down docker-logs

help:
	@echo "OpenSearch Curator - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies with uv (or pip)"
	@echo "  make install-dev      Install with development dependencies"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        Start OpenSearch test environment"
	@echo "  make docker-down      Stop OpenSearch test environment"
	@echo "  make docker-logs      View OpenSearch logs"
	@echo "  make docker-clean     Stop and remove all data"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-cov         Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters"
	@echo "  make format           Format code with black"
	@echo "  make mypy             Run type checking"
	@echo ""
	@echo "Build:"
	@echo "  make build            Build distribution packages"
	@echo "  make clean            Clean build artifacts"

install:
	@if command -v uv > /dev/null 2>&1; then \
		echo "Installing with uv..."; \
		uv pip install -e .; \
	else \
		echo "Installing with pip..."; \
		pip install -e .; \
	fi

install-dev:
	@if command -v uv > /dev/null 2>&1; then \
		echo "Installing with uv (dev mode)..."; \
		uv pip install -e ".[test]"; \
	else \
		echo "Installing with pip (dev mode)..."; \
		pip install -e ".[test]"; \
	fi

docker-up:
	docker-compose up -d
	@echo "Waiting for OpenSearch..."
	@sleep 5
	@curl -s http://localhost:9200/_cluster/health?pretty || echo "OpenSearch not ready yet"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f opensearch

docker-clean:
	docker-compose down -v

test:
	pytest

test-unit:
	pytest tests/unit

test-integration:
	pytest tests/integration

test-cov:
	pytest --cov=curator --cov-report=term-missing

test-opensearch-client:
	pytest opensearch_client/tests/unit -v

lint:
	ruff check .
	black --check .
	mypy .

format:
	black .
	ruff check --fix .

mypy:
	mypy curator

build:
	hatch build

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
