# TTL-Aware Automated Archival Service

A robust FastAPI-based service for automated data archival with Time-To-Live (TTL) based cleanup and management.

## Features

- **TTL-Based Archival**: Automatically manage data retention with configurable TTL policies
- **Automated Cleanup**: Scheduled cleanup of expired records
- **File Management**: Automatic file compression and storage management
- **Policy-Based**: Flexible archival policies with different configurations
- **RESTful API**: Complete REST API for integration
- **Monitoring**: Built-in health checks and statistics
- **Integrity Verification**: Checksum validation for archived data

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ttl-archival-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the service:
```bash
uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Core Concepts

### Archive Policies

Policies define how data should be archived and when it expires:

```python
{
    "name": "user_data_policy",
    "description": "Archive user data after 90 days",
    "ttl_days": 90,
    "compression_enabled": true,
    "encryption_enabled": false,
    "auto_cleanup": true
}
```

### Archive Records

Records represent individual archived items:

```python
{
    "policy_id": 1,
    "original_data_id": "user_123_data",
    "data_type": "user_data",
    "file_path": "/path/to/original/file",
    "metadata": "{\"user_id\": 123, \"category\": \"profile\"}"
}
```

## API Endpoints

### Policies
- `POST /api/v1/policies` - Create new archival policy
- `GET /api/v1/policies` - List all policies
- `GET /api/v1/policies/{id}` - Get specific policy

### Archives
- `POST /api/v1/archives` - Create archive record
- `GET /api/v1/archives` - List archive records
- `GET /api/v1/archives/{id}` - Get specific archive record
- `DELETE /api/v1/archives/{id}` - Delete archive record
- `POST /api/v1/archives/cleanup` - Trigger manual cleanup

### System
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Service statistics

## Usage Examples

### Create an Archive Policy

```bash
curl -X POST "http://localhost:8000/api/v1/policies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "logs_policy",
    "description": "Archive logs after 30 days",
    "ttl_days": 30,
    "compression_enabled": true,
    "auto_cleanup": true
  }'
```

### Archive Data

```bash
curl -X POST "http://localhost:8000/api/v1/archives" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": 1,
    "original_data_id": "log_file_20240101",
    "data_type": "logs",
    "file_path": "/var/log/app.log",
    "metadata": "{\"source\": \"web_server\", \"date\": \"2024-01-01\"}"
  }'
```

### Trigger Cleanup

```bash
curl -X POST "http://localhost:8000/api/v1/archives/cleanup"
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string
- `ARCHIVE_STORAGE_PATH`: Path for archived files (default: `./archives`)
- `REDIS_URL`: Redis connection for caching (optional)
- `SECRET_KEY`: JWT secret key
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `ENABLE_SCHEDULER`: Enable automated scheduler (default: `true`)

### Database Setup

#### SQLite (Default)
```bash
DATABASE_URL=sqlite:///./ttl_archival.db
```

#### PostgreSQL
```bash
DATABASE_URL=postgresql://user:password@localhost/ttl_archival
```

#### MySQL
```bash
DATABASE_URL=mysql://user:password@localhost/ttl_archival
```

## Architecture

### Components

1. **FastAPI Application**: Main web service
2. **Database Layer**: SQLAlchemy ORM with support for multiple databases
3. **Archive Service**: Core archival logic and file management
4. **Policy Service**: Policy management and enforcement
5. **Scheduler**: Automated cleanup and maintenance tasks

### Data Flow

1. Client creates archive record via API
2. Service applies policy and calculates expiry
3. Files are compressed and stored according to policy
4. Record is stored in database with metadata
5. Scheduler periodically cleans up expired records
6. Monitoring and statistics are maintained

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

```
app/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── services.py          # Business logic
├── scheduler.py         # Task scheduling
└── __init__.py          # Package initialization

tests/
├── test_services.py     # Service tests
└── test_api.py          # API tests
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Considerations

- Use PostgreSQL or MySQL for production
- Configure proper backup strategies
- Set up monitoring and alerting
- Implement proper access controls
- Configure log rotation

## Monitoring

### Health Checks

The service provides health check endpoints:
- `/api/v1/health` - Basic health status
- Database connectivity
- Scheduler status

### Metrics

- Total archive records
- Active/expired/deleted counts
- Storage usage
- Policy statistics
- Cleanup performance

## Security

- Input validation and sanitization
- File path traversal protection
- Checksum verification
- Optional encryption support
- Access control via JWT tokens

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation
- Review the test cases for usage examples
