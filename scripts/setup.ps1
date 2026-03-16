# TTL-Aware Automated Archival Service Setup Script (PowerShell)
# This script sets up the development environment on Windows

Write-Host "🚀 Setting up TTL-Aware Automated Archival Service..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is required but not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check Python version
$versionMatch = $pythonVersion -match 'Python (\d+)\.(\d+)'
if ($versionMatch) {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "❌ Python $major.$minor is installed, but Python 3.8+ is required." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  Could not determine Python version. Proceeding anyway..." -ForegroundColor Yellow
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Install dependencies
if ($args[0] -eq "--dev") {
    Write-Host "🔧 Installing with development dependencies..." -ForegroundColor Blue
    pip install -e ".[dev,postgres,redis]"
} else {
    Write-Host "📚 Installing dependencies..." -ForegroundColor Blue
    pip install -e .
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "archives" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "temp" | Out-Null

# Copy environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating environment file..." -ForegroundColor Blue
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env file with your configuration" -ForegroundColor Yellow
}

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Blue
python -c @"
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database initialized successfully!')
"@

# Create default policies
Write-Host "📋 Creating default policies..." -ForegroundColor Blue
python -c @"
from app.database import SessionLocal
from app.services import PolicyService
from app.schemas import ArchivePolicyCreate

db = SessionLocal()
policy_service = PolicyService()

policies = [
    ArchivePolicyCreate(
        name='default_user_data',
        description='Default policy for user data (90 days)',
        ttl_days=90,
        compression_enabled=True,
        auto_cleanup=True
    ),
    ArchivePolicyCreate(
        name='default_logs',
        description='Default policy for logs (30 days)',
        ttl_days=30,
        compression_enabled=True,
        auto_cleanup=True
    ),
    ArchivePolicyCreate(
        name='default_temp',
        description='Default policy for temporary files (7 days)',
        ttl_days=7,
        compression_enabled=False,
        auto_cleanup=True
    ),
    ArchivePolicyCreate(
        name='backup_data',
        description='Policy for backup data (365 days)',
        ttl_days=365,
        compression_enabled=True,
        encryption_enabled=False,
        auto_cleanup=True
    )
]

created_count = 0
for policy_data in policies:
    try:
        policy = policy_service.create_policy(db, policy_data)
        print(f'✅ Created policy: {policy.name} (TTL: {policy.ttl_days} days)')
        created_count += 1
    except Exception as e:
        print(f'⚠️  Policy {policy_data.name} may already exist: {e}')

db.close()
print(f'📋 Created {created_count} default policies')
"@

# Run tests if development setup
if ($args[0] -eq "--dev") {
    Write-Host "🧪 Running tests..." -ForegroundColor Blue
    pytest tests/ -v
}

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Edit .env file with your configuration"
Write-Host "   2. Run the service: make run"
Write-Host "   3. Open API docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "🔧 Useful commands:" -ForegroundColor Cyan
Write-Host "   make run          - Run the service"
Write-Host "   make test         - Run tests"
Write-Host "   make lint         - Run linting"
Write-Host "   make format       - Format code"
Write-Host "   make docker-run   - Run with Docker"
Write-Host "   make health       - Check service health"
Write-Host "   make docs          - Show API documentation URLs"
Write-Host ""
Write-Host "📚 Documentation: README.md" -ForegroundColor Cyan
