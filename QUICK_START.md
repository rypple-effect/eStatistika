# 🚀 Quick Start Guide - How to Open the Application

## Step 1: Start the Services

Open your terminal in the project root directory and run:

```bash
make start
```

**OR** if you're on Windows PowerShell:

```bash
docker compose up -d
```

This will start:
- ✅ Ollama (AI model server)
- ✅ PostgreSQL (database)
- ✅ API server (your web application)

**⏱️ First time setup:** This may take 5-10 minutes to download the Llama 3.2 model (~4.7GB).

## Step 2: Wait for Services to Start

Check if services are running:

```bash
docker compose ps
```

Wait until all services show as "healthy" or "running".

## Step 3: Open in Browser

Once services are running, open your web browser and go to:

### 🌐 Web Interface (HTML)
**http://localhost:8083/**

This is the beautiful web interface where you can:
- Register/Login
- Ask statistics questions
- Get AI-powered responses

### 📚 API Documentation (Interactive)
**http://localhost:8083/docs**

This is the FastAPI interactive documentation where you can test all endpoints.

## Step 4: Use the Application

1. **Register a new user:**
   - Enter a username and password
   - Click "Register"

2. **Login:**
   - Enter your username and password
   - Click "Login"
   - Your session token will be saved

3. **Ask a statistics question:**
   - Type your question (e.g., "What are the latest statistics on global internet usage?")
   - Optionally set a source
   - Click "Get Statistics"
   - Wait for the AI to generate a response!

## Alternative: Local Development Mode

If you want to run the API locally (not in Docker):

```bash
# 1. Start Ollama and PostgreSQL in Docker
docker compose up ollama postgres -d

# 2. Install dependencies (if not done)
cd api
uv sync

# 3. Run the API locally
cd api
uv run uvicorn main:app --reload --port 8000
```

Then open: **http://localhost:8000/**

## 🔍 Check if Everything is Working

### Check logs:
```bash
make logs
# OR
docker compose logs -f
```

### Check API health:
Visit: http://localhost:8083/api/info

### Check if Ollama is ready:
```bash
docker compose exec ollama ollama list
```

## 🛑 Stop the Application

When you're done:

```bash
make stop
# OR
docker compose stop
```

## 🗑️ Clean Up (Remove Everything)

To remove all containers, volumes, and data:

```bash
make destroy
# OR
docker compose down -v
```

## ⚠️ Troubleshooting

### Port Already in Use?
If port 8083 is already in use, you can change it in `compose.yml`:
```yaml
ports:
  - "8084:80"  # Change 8083 to any available port
```

### Services Not Starting?
```bash
# Check logs
docker compose logs

# Restart services
docker compose restart
```

### Ollama Model Not Loading?
```bash
# Check Ollama logs
docker compose logs ollama

# Manually pull the model
docker compose exec ollama ollama pull llama3.2
```

## 📝 Example Questions to Try

- "What are the latest statistics on global internet usage?"
- "Tell me statistics about renewable energy adoption"
- "What are the current statistics on AI adoption in businesses?"
- "Show me statistics about remote work trends"

---

**🎉 That's it! You're ready to use your AI Statistics API!**

For more details, see:
- `api/BROWSER_ACCESS.md` - Detailed browser access guide
- `README.md` - Full project documentation

