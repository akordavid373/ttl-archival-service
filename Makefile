.PHONY: help install dev-install test lint format clean run docker-build docker-run

# Default target
help:
	@echo "TTL-Aware Automated Archival Service"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install      Install the package"
	@echo "  dev-install  Install with development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean build artifacts"
	@echo "  run          Run the service"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker Compose"
	@echo "  db-init      Initialize database"
	@echo "  db-migrate   Run database migrations"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev,postgres,redis]"
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 app/ tests/
	mypy app/
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	black app/ tests/
	isort app/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Running the service
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-build:
	docker build -t ttl-archival-service .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
db-init:
	alembic init alembic
	alembic revision --autogenerate -m "Initial migration"
	alembic upgrade head

db-migrate:
	alembic revision --autogenerate -m "New migration"
	alembic upgrade head

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

# Development helpers
shell:
	python -c "
from app.database import SessionLocal
from app.models import Base
Base.metadata.create_all(bind=SessionLocal().bind)
print('Database initialized!')
"

create-admin:
	python -c "
from app.database import SessionLocal
from app.services import PolicyService
from app.schemas import ArchivePolicyCreate

db = SessionLocal()
policy_service = PolicyService()

# Create default policies
policies = [
    ArchivePolicyCreate(
        name='default_user_data',
        description='Default policy for user data',
        ttl_days=90,
        compression_enabled=True,
        auto_cleanup=True
    ),
    ArchivePolicyCreate(
        name='default_logs',
        description='Default policy for logs',
        ttl_days=30,
        compression_enabled=True,
        auto_cleanup=True
    ),
    ArchivePolicyCreate(
        name='default_temp',
        description='Default policy for temporary files',
        ttl_days=7,
        compression_enabled=False,
        auto_cleanup=True
    )
]

for policy_data in policies:
    try:
        policy = policy_service.create_policy(db, policy_data)
        print(f'Created policy: {policy.name}')
    except Exception as e:
        print(f'Error creating policy: {e}')

db.close()
print('Default policies created!')
"

# Health check
health:
	curl -f http://localhost:8000/api/v1/health || echo "Service not running"

# API documentation
docs:
	@echo "API Documentation:"
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
