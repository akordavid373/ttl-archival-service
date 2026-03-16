# TTL-Aware Automated Archival Service Run Script (PowerShell)
# This script provides convenient ways to run the service

param(
    [Parameter(Position=0)]
    [ValidateSet("run", "dev", "test", "lint", "format", "clean", "health", "docs", "logs", "shell", "docker", "help")]
    [string]$Command = "run"
)

# Colors for output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Error "Virtual environment not found. Please run setup first:"
    Write-Host "  .\scripts\setup.ps1"
    exit 1
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Check if dependencies are installed
try {
    python -c "import fastapi" | Out-Null
} catch {
    Write-Error "Dependencies not found. Please run setup first:"
    Write-Host "  .\scripts\setup.ps1"
    exit 1
}

# Create necessary directories if they don't exist
New-Item -ItemType Directory -Force -Path "archives", "logs", "temp" | Out-Null

# Set default values
$env:HOST = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }
$env:PORT = if ($env:PORT) { $env:PORT } else { "8000" }
$env:WORKERS = if ($env:WORKERS) { $env:WORKERS } else { "1" }
$env:RELOAD = if ($env:RELOAD) { $env:RELOAD } else { "false" }
$env:LOG_LEVEL = if ($env:LOG_LEVEL) { $env:LOG_LEVEL } else { "info" }

switch ($Command) {
    "run" {
        Write-Status "Running in production mode..."
        Write-Status "Starting TTL-Aware Automated Archival Service..."
        Write-Status "Host: $env:HOST"
        Write-Status "Port: $env:PORT"
        Write-Status "Workers: $env:WORKERS"
        Write-Status "Log Level: $env:LOG_LEVEL"
        Write-Host ""
        
        uvicorn app.main:app --host $env:HOST --port $env:PORT --workers $env:WORKERS --log-level $env:LOG_LEVEL
    }
    
    "dev" {
        $env:RELOAD = "true"
        $env:LOG_LEVEL = "debug"
        Write-Status "Running in development mode with auto-reload..."
        Write-Status "Starting TTL-Aware Automated Archival Service..."
        Write-Status "Host: $env:HOST"
        Write-Status "Port: $env:PORT"
        Write-Status "Log Level: $env:LOG_LEVEL"
        Write-Host ""
        
        uvicorn app.main:app --host $env:HOST --port $env:PORT --reload --log-level $env:LOG_LEVEL
    }
    
    "test" {
        Write-Status "Running tests..."
        pytest tests/ -v
        Write-Success "Tests completed!"
    }
    
    "lint" {
        Write-Status "Running linting..."
        flake8 app/ tests/
        mypy app/
        black --check app/ tests/
        isort --check-only app/ tests/
        Write-Success "Linting completed!"
    }
    
    "format" {
        Write-Status "Formatting code..."
        black app/ tests/
        isort app/ tests/
        Write-Success "Code formatted!"
    }
    
    "clean" {
        Write-Status "Cleaning up..."
        Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
        Remove-Item -Path ".pytest_cache", ".coverage", "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Cleanup completed!"
    }
    
    "health" {
        Write-Status "Checking service health..."
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$env:PORT/api/v1/health" -Method Get -ErrorAction Stop
            Write-Success "Service is healthy!"
        } catch {
            Write-Error "Service is not running or not healthy"
            exit 1
        }
    }
    
    "docs" {
        Write-Status "API Documentation:"
        Write-Host "  Swagger UI: http://localhost:$env:PORT/docs"
        Write-Host "  ReDoc: http://localhost:$env:PORT/redoc"
        Write-Host ""
        Write-Status "Opening Swagger UI in browser..."
        try {
            Start-Process "http://localhost:$env:PORT/docs"
        } catch {
            Write-Warning "Could not open browser automatically"
        }
    }
    
    "logs" {
        Write-Status "Following service logs..."
        $logFiles = Get-ChildItem -Path "logs\*.log" -ErrorAction SilentlyContinue
        if ($logFiles) {
            Get-Content -Path $logFiles -Wait -Tail 10
        } else {
            Write-Warning "No log files found"
        }
    }
    
    "shell" {
        Write-Status "Opening interactive shell..."
        python -c @"
from app.database import SessionLocal
from app.models import *
from app.services import *

db = SessionLocal()
print('Database session available as: db')
print('Available models: ArchivePolicy, ArchiveRecord')
print('Available services: ArchiveService, PolicyService')
print('Use Ctrl+Z then Enter to exit')
import code
code.interact(local=dict(globals(), **locals()))
"@
    }
    
    "docker" {
        Write-Status "Running with Docker..."
        docker-compose up -d
        Write-Success "Service started with Docker!"
        Write-Status "Logs: docker-compose logs -f"
        Write-Status "Stop: docker-compose down"
    }
    
    "help" {
        Write-Host "TTL-Aware Automated Archival Service Run Script"
        Write-Host ""
        Write-Host "Usage: .\scripts\run.ps1 [command]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  run      Run the service (default)"
        Write-Host "  dev      Run in development mode with auto-reload"
        Write-Host "  test     Run tests"
        Write-Host "  lint     Run linting checks"
        Write-Host "  format   Format code"
        Write-Host "  clean    Clean up temporary files"
        Write-Host "  health   Check service health"
        Write-Host "  docs     Open API documentation"
        Write-Host "  logs     Follow service logs"
        Write-Host "  shell    Open interactive shell"
        Write-Host "  docker   Run with Docker"
        Write-Host "  help     Show this help message"
        Write-Host ""
        Write-Host "Environment Variables:"
        Write-Host "  HOST        Host to bind to (default: 0.0.0.0)"
        Write-Host "  PORT        Port to bind to (default: 8000)"
        Write-Host "  WORKERS     Number of worker processes (default: 1)"
        Write-Host "  RELOAD      Enable auto-reload (default: false)"
        Write-Host "  LOG_LEVEL   Log level (default: info)"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\scripts\run.ps1 dev                    # Development mode"
        Write-Host "  .\scripts\run.ps1 run                    # Production mode"
        Write-Host "  `$env:HOST='127.0.0.1'; `$env:PORT='5000'; .\scripts\run.ps1  # Custom host/port"
    }
    
    default {
        Write-Error "Unknown command: $Command"
        Write-Host "Use '.\scripts\run.ps1 help' for available commands"
        exit 1
    }
}
