# API Service

Primary AI chat and authentication interface powered by FastAPI, Ollama (Llama 3.2), and PostgreSQL.

## Features

- **Authentication**: User registration and login with session management
- **Chat Interface**: Streaming and non-streaming chat endpoints
- **Session Management**: Conversation history persisted in PostgreSQL
- **AI Integration**: Llama 3.2 via Ollama for chat completions

## Tech Stack

- **FastAPI**: Modern async web framework
- **Ollama**: Local LLM inference
- **PostgreSQL**: Session and user data storage
- **SQLAlchemy**: Async ORM
- **Passlib**: Password hashing
- **Pydantic**: Data validation

## Development

### Prerequisites

- Python 3.13+
- uv package manager
- Docker and Docker Compose (for full stack)

### Local Development

```bash
# Navigate to api directory
cd api

# Install dependencies
uv sync

# Run the development server
uv run uvicorn main:app --reload --port 8000

# Or use the make command from root
make api-dev
```

### With Docker Compose

From the root directory:

```bash
# Start all services including API
make start

# View API logs
make api-logs

# Stop all services
make stop
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get session token
- `POST /api/auth/logout` - Logout and invalidate session

### Chat
- `POST /api/chat` - Send chat message (non-streaming)
- `POST /api/chat/stream` - Send chat message (streaming)

### Health
- `GET /api/health` - Service health check

## Environment Variables

When running with Docker Compose, these are automatically configured:

- `OLLAMA_HOST`: Ollama service URL (default: `http://ollama:11434`)
- `MODEL_NAME`: LLM model name (default: `llama3.2`)
- `DATABASE_URL`: PostgreSQL connection string

## Project Structure

```
api/
├── main.py              # FastAPI application entry point
├── src/
│   ├── core/           # Core functionality (auth, sessions, dependencies)
│   ├── database/       # Database models and connection
│   ├── routers/        # API route handlers (auth, chat)
│   ├── services/       # External service integrations (Ollama)
│   ├── config.py       # Configuration management
│   └── schemas.py      # Pydantic models
├── pyproject.toml      # Project dependencies
├── Dockerfile          # Container image definition
└── README.md           # This file
```

## Dependencies

Key dependencies (see `pyproject.toml` for full list):
- fastapi>=0.115.0
- uvicorn[standard]>=0.32.0
- httpx>=0.27.0
- sqlalchemy>=2.0.0
- asyncpg>=0.30.0
- passlib[bcrypt]>=1.7.4
