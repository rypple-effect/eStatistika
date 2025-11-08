# Build Club x Meta - AI Chat API

AI-powered chat service built with FastAPI, Ollama (Llama 3.2), and PostgreSQL.

## Features

- **Authentication**: User registration and login with session management
- **Chat Interface**: Streaming and non-streaming chat endpoints
- **Session Management**: Conversation history persisted in PostgreSQL
- **AI Integration**: Llama 3.2 via Ollama for chat completions

## Architecture Overview

```
build-club-x-meta/
├── api/                    # AI chat + auth service
│   ├── main.py            # FastAPI application
│   ├── src/
│   │   ├── core/          # Auth, sessions, dependencies
│   │   ├── database/      # Database models and connection
│   │   ├── routers/       # API route handlers (auth, chat)
│   │   ├── services/      # External integrations (Ollama)
│   │   ├── config.py      # Configuration management
│   │   └── schemas.py     # Pydantic models
│   ├── Dockerfile         # Container definition
│   └── pyproject.toml     # Dependencies
├── compose.yml            # Docker Compose orchestration
└── Makefile               # Development commands
```

## Prerequisites

- **Python 3.13+** with uv package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Docker and Docker Compose** for containerized deployment
- At least 8GB of RAM (16GB recommended)
- ~5GB of disk space for the Llama model

## Quick Start

### Option 1: Docker Compose (Recommended)

Start all services (API, Ollama, PostgreSQL):

```bash
make start
```

This will:
1. Start Ollama service and pull Llama 3.2 model (~4.7GB)
2. Start PostgreSQL for session/user storage
3. Start API service on http://localhost:8081

**Note:** First run takes several minutes to download the Llama model.

### Option 2: Local Development

Run the API locally for development:

```bash
# Start Ollama and PostgreSQL
docker compose up ollama postgres -d

# In a new terminal: Start API service
make api-dev
```

The API will be available at http://localhost:8000

## Available Commands

### Global Commands

```bash
make start        # Start all services with Docker Compose
make logs         # Show logs for all services
make stop         # Stop all services
make destroy      # Remove all containers, volumes, and networks
make help         # Show all available commands
```

### API Commands

```bash
make api-dev      # Start API in development mode (local, port 8000)
make api-logs     # Show logs for API service
make api-shell    # Enter API container shell
make api-test     # Run API tests
```

## API Endpoints

AI chat and authentication interface powered by Llama 3.2 via Ollama (available at http://localhost:8081 when using Docker, or http://localhost:8000 for local development).

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get session token
- `POST /api/auth/logout` - Logout and invalidate session

**Chat:**
- `POST /api/chat` - Chat with AI (non-streaming)
- `POST /api/chat/stream` - Chat with AI (streaming)

**Health:**
- `GET /api/health` - Service health check
- `GET /` - API information and available endpoints

**Documentation:** http://localhost:8081/docs (or http://localhost:8000/docs for local development)

See [api/README.md](api/README.md) for detailed documentation.

## Example Usage

### Chat with AI

```bash
curl -X POST "http://localhost:8081/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "temperature": 0.7
  }'
```

### Streaming Chat

```bash
curl -X POST "http://localhost:8081/api/chat/stream" \
  -H "Content-Type: application/json" \
  -N \
  -d '{"message": "Tell me a joke"}'
```

### Register a User

```bash
curl -X POST "http://localhost:8081/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8081/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword"
  }'
```

## Configuration

### Environment Variables

Configured in `compose.yml`:

**API Service:**
- `OLLAMA_HOST`: Ollama service URL (default: `http://ollama:11434`)
- `MODEL_NAME`: LLM model name (default: `llama3.2`)
- `DATABASE_URL`: PostgreSQL connection string

**PostgreSQL:**
- `POSTGRES_USER`: Database user (default: `llama_user`)
- `POSTGRES_PASSWORD`: Database password (default: `llama_pass`)
- `POSTGRES_DB`: Database name (default: `llama_db`)

### Using Different Models

Edit `compose.yml` to use a different Llama model:

```yaml
environment:
  - MODEL_NAME=llama3.1  # or llama3, llama3.1:70b, etc.
```

Available models:
- `llama3.2` (default, ~4.7GB)
- `llama3.1` (~4.7GB)
- `llama3.1:70b` (larger, better quality, ~40GB)

### GPU Support (Optional)

Uncomment the GPU section in `compose.yml` under the ollama service:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Development Workflow

### Setting Up the API Service

```bash
# Navigate to API directory
cd api

# Install dependencies
uv sync

# Run in development mode with auto-reload
uv run uvicorn main:app --reload
```

### Adding Dependencies

```bash
cd api
uv add <package-name>
uv sync
```

## Troubleshooting

### Ollama Connection Issues

Check if Ollama is running:
```bash
docker compose ps
make logs
```

### Model Download Issues

The model downloads automatically. If it fails:
```bash
make destroy
make start
```

### Out of Memory

- Use a smaller model (llama3.2 is smallest)
- Close other applications
- Increase Docker's memory limit in Docker Desktop settings

### Port Conflicts

Modify ports in `compose.yml` if 8081 is in use:
```yaml
ports:
  - "8083:80"  # Change to any available port
```

### Database Connection Issues

Check PostgreSQL is healthy:
```bash
docker compose ps postgres
docker compose logs postgres
```

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Llama 3 Model Card](https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_2/)
- [uv Documentation](https://docs.astral.sh/uv/)

## License

This project is open source and available for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Check [api/README.md](api/README.md) for API-specific documentation
3. Review Ollama and FastAPI documentation
4. Open an issue in the repository
