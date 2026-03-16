#!/bin/bash

# TTL-Aware Automated Archival Service Run Script
# This script provides convenient ways to run the service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup first:"
    echo "  ./scripts/setup.sh"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    print_error "Dependencies not found. Please run setup first:"
    echo "  ./scripts/setup.sh"
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p archives logs temp

# Set default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
RELOAD=${RELOAD:-false}
LOG_LEVEL=${LOG_LEVEL:-info}

# Parse command line arguments
case "${1:-run}" in
    "run"|"dev")
        if [ "$1" = "dev" ]; then
            RELOAD=true
            LOG_LEVEL=debug
            print_status "Running in development mode with auto-reload..."
        else
            print_status "Running in production mode..."
        fi
        
        print_status "Starting TTL-Aware Automated Archival Service..."
        print_status "Host: $HOST"
        print_status "Port: $PORT"
        print_status "Workers: $WORKERS"
        print_status "Reload: $RELOAD"
        print_status "Log Level: $LOG_LEVEL"
        echo ""
        
        # Start the service
        if [ "$RELOAD" = "true" ]; then
            uvicorn app.main:app --host $HOST --port $PORT --reload --log-level $LOG_LEVEL
        else
            uvicorn app.main:app --host $HOST --port $PORT --workers $WORKERS --log-level $LOG_LEVEL
        fi
        ;;
    
    "test")
        print_status "Running tests..."
        pytest tests/ -v
        print_success "Tests completed!"
        ;;
    
    "lint")
        print_status "Running linting..."
        flake8 app/ tests/
        mypy app/
        black --check app/ tests/
        isort --check-only app/ tests/
        print_success "Linting completed!"
        ;;
    
    "format")
        print_status "Formatting code..."
        black app/ tests/
        isort app/ tests/
        print_success "Code formatted!"
        ;;
    
    "clean")
        print_status "Cleaning up..."
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        rm -rf .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
        print_success "Cleanup completed!"
        ;;
    
    "health")
        print_status "Checking service health..."
        if curl -f http://localhost:$PORT/api/v1/health 2>/dev/null; then
            print_success "Service is healthy!"
        else
            print_error "Service is not running or not healthy"
            exit 1
        fi
        ;;
    
    "docs")
        print_status "API Documentation:"
        echo "  Swagger UI: http://localhost:$PORT/docs"
        echo "  ReDoc: http://localhost:$PORT/redoc"
        echo ""
        print_status "Opening Swagger UI in browser..."
        if command -v xdg-open > /dev/null; then
            xdg-open http://localhost:$PORT/docs
        elif command -v open > /dev/null; then
            open http://localhost:$PORT/docs
        else
            print_warning "Could not open browser automatically"
        fi
        ;;
    
    "logs")
        print_status "Following service logs..."
        tail -f logs/*.log 2>/dev/null || print_warning "No log files found"
        ;;
    
    "shell")
        print_status "Opening interactive shell..."
        python -c "
from app.database import SessionLocal
from app.models import *
from app.services import *

db = SessionLocal()
print('Database session available as: db')
print('Available models: ArchivePolicy, ArchiveRecord')
print('Available services: ArchiveService, PolicyService')
print('Use Ctrl+D to exit')
import code
code.interact(local=dict(globals(), **locals()))
"
        ;;
    
    "docker")
        print_status "Running with Docker..."
        docker-compose up -d
        print_success "Service started with Docker!"
        print_status "Logs: docker-compose logs -f"
        print_status "Stop: docker-compose down"
        ;;
    
    "help"|"-h"|"--help")
        echo "TTL-Aware Automated Archival Service Run Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  run      Run the service (default)"
        echo "  dev      Run in development mode with auto-reload"
        echo "  test     Run tests"
        echo "  lint     Run linting checks"
        echo "  format   Format code"
        echo "  clean    Clean up temporary files"
        echo "  health   Check service health"
        echo "  docs     Open API documentation"
        echo "  logs     Follow service logs"
        echo "  shell    Open interactive shell"
        echo "  docker   Run with Docker"
        echo "  help     Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  HOST        Host to bind to (default: 0.0.0.0)"
        echo "  PORT        Port to bind to (default: 8000)"
        echo "  WORKERS     Number of worker processes (default: 1)"
        echo "  RELOAD      Enable auto-reload (default: false)"
        echo "  LOG_LEVEL   Log level (default: info)"
        echo ""
        echo "Examples:"
        echo "  $0 dev                    # Development mode"
        echo "  $0 run                    # Production mode"
        echo "  HOST=127.0.0.1 PORT=5000 $0  # Custom host/port"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac
