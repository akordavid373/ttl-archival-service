#!/bin/bash

# TTL-Aware Automated Archival Service Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up TTL-Aware Automated Archival Service..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is installed, but Python $required_version+ is required."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
if [ "$1" = "--dev" ]; then
    echo "🔧 Installing with development dependencies..."
    pip install -e ".[dev,postgres,redis]"
else
    pip install -e .
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p archives
mkdir -p logs
mkdir -p temp

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
python -c "
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database initialized successfully!')
"

# Create default policies
echo "📋 Creating default policies..."
python -c "
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
"

# Run tests if development setup
if [ "$1" = "--dev" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. Run the service: make run"
echo "   3. Open API docs: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   make run          - Run the service"
echo "   make test         - Run tests"
echo "   make lint         - Run linting"
echo "   make format       - Format code"
echo "   make docker-run   - Run with Docker"
echo "   make health       - Check service health"
echo "   make docs          - Show API documentation URLs"
echo ""
echo "📚 Documentation: README.md"
