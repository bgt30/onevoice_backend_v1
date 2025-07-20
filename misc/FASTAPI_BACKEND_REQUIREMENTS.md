# FastAPI Backend Integration Requirements

## Overview
This document outlines all required files, libraries, and dependencies for integrating a FastAPI backend into the onevoice project. Always proceed in a virtual environment.

## Core FastAPI Dependencies

### Web Framework & Server
- **fastapi** - Modern, fast web framework for building APIs
- **uvicorn[standard]** - ASGI server for running FastAPI applications
- **gunicorn** - WSGI HTTP Server for production deployment
- **python-multipart** - For handling form data and file uploads

### Request/Response Handling
- **pydantic[email]** - Data validation and settings management
- **pydantic-settings** - Configuration management with Pydantic
- **typing-extensions** - Enhanced type hints support

## Database & ORM

### Database Drivers
- **psycopg2-binary** - PostgreSQL adapter for Python
- **asyncpg** - Async PostgreSQL driver
- **redis** - Redis client for caching and task queue

### ORM & Database Tools
- **sqlalchemy** - SQL toolkit and ORM
- **alembic** - Database migration tool
- **databases[postgresql]** - Async database support

## Authentication & Security

### JWT & Password Management
- **python-jose[cryptography]** - JWT token handling
- **passlib[bcrypt]** - Password hashing library

### Security Libraries
- **cryptography** - Cryptographic recipes and primitives
- **python-decouple** - Environment variable management

## Task Queue & Background Processing

### Task Queue
- **celery[redis]** - Distributed task queue
- **kombu** - Messaging library for Python
- **flower** - Web-based tool for monitoring Celery clusters

### Async Support
- **aioredis** - Async Redis client
- **asyncio** - Async I/O support (built-in Python 3.10)

## File Handling & Media Processing

### File Operations
- **aiofiles** - Async file operations
- **python-magic** - File type detection

### Media Processing (onevoice Integration)
- **ffmpeg-python** - FFmpeg wrapper for Python
- **pydub** - Audio manipulation library
- **Pillow** - Image processing library

## HTTP Client & External APIs

### HTTP Clients
- **httpx** - Async HTTP client
- **aiohttp** - Async HTTP client/server framework
- **requests** - Simple HTTP library (for sync operations)

## WebSocket Support

### Real-time Communication
- **websockets** - WebSocket implementation

## Testing & Development

### Testing Framework
- **pytest** - Testing framework
- **pytest-asyncio** - Async support for pytest
- **httpx** - For testing HTTP endpoints
- **pytest-cov** - Coverage reporting

## Monitoring & Logging

### Health Checks
- **healthcheck** - Health check endpoints

## Environment & Configuration

### Environment Management
- **python-dotenv** - Load environment variables from .env
- **environs** - Environment variable parsing

## Required Configuration Files

### `.env` (Environment Variables)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/onevoice
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_HOSTS=http://localhost:3000,http://localhost:8000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=2147483648  # 2GB

# External APIs
OPENAI_API_KEY=your-openai-key
AZURE_API_KEY=your-azure-key
WHISPER_API_KEY=your-whisper-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### `docker-compose.yml` (Development Environment)
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/onevoice
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./uploads:/app/uploads
      - ./output:/app/output

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: onevoice
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker:
    build: .
    command: celery -A app.core.celery worker --loglevel=info
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/onevoice
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./uploads:/app/uploads
      - ./output:/app/output

  flower:
    build: .
    command: celery -A app.core.celery flower
    ports:
      - "5555:5555"
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0

volumes:
  postgres_data:
```

### `Dockerfile`
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p uploads output

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `alembic.ini` (Database Migrations)
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost:5432/onevoice

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### `pyproject.toml` (Project Configuration)
```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.mypy]
python_version = "3.10"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_optional = true
```

## Project Structure

```
onevoice-backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── videos.py
│   │           └── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── celery.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── video.py
│   │   └── job.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── video.py
│   │   └── job.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── video.py
│   │   └── processing.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── video_processing.py
│   └── utils/
│       ├── __init__.py
│       ├── deps.py
│       └── helpers.py
├── alembic/
│   ├── versions/
│   └── env.py
├── uploads/
├── output/
├── main.py
├── requirements.txt
├── .env
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── pyproject.toml
```

## Installation & Setup Commands

### Database Setup
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Development Server
```bash
# Run FastAPI development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
celery -A app.core.celery worker --loglevel=info

# Run Flower monitoring
celery -A app.core.celery flower
```

### Production Deployment
```bash
# Build Docker image
docker build -t onevoice-backend .

# Run with Docker Compose
docker-compose up -d

# Scale workers
docker-compose up --scale worker=3
```

## Integration Notes

### onevoice Core Integration
- Import existing `core/` modules directly
- Wrap synchronous functions in async task queue
- Maintain existing configuration structure
- Preserve all processing quality and features

### Migration Strategy
- Gradual migration of features
- Maintain backward compatibility

This comprehensive requirements list ensures all necessary components are available for a successful FastAPI backend integration with the onevoice project. 