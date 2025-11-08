from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.database.database import init_db
from src.routers import auth, chats, statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Llama Chat API - Starter Kit",
    description="Authentication and chat management boilerplate for Llama 3.2 workshop",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(chats.router)
api_router.include_router(statistics.router)

app.include_router(api_router)

# Serve static files (HTML page for browser access)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the HTML interface for browser access or API info"""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file)
    else:
        # Fallback to JSON response if HTML file doesn't exist
        return {
            "message": "Welcome to Llama Chat API - Starter Kit!",
            "docs": "/docs",
            "web_interface": "Visit /static/index.html after creating the static directory",
            "endpoints": {
                "auth": {
                    "register": "/api/auth/register",
                    "login": "/api/auth/login",
                },
                "chats": {
                    "create": "/api/chats",
                    "list": "/api/chats",
                    "delete": "/api/chats/{chat_id}",
                    "messages": "/api/chats/{chat_id}/messages",
                },
                "statistics": {
                    "create": "/api/statistics",
                    "list": "/api/statistics",
                    "get": "/api/statistics/{request_id}",
                },
            },
        }


@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Welcome to Llama Chat API - Starter Kit!",
        "docs": "/docs",
        "web_interface": "/",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
            },
            "chats": {
                "create": "/api/chats",
                "list": "/api/chats",
                "delete": "/api/chats/{chat_id}",
                "messages": "/api/chats/{chat_id}/messages",
            },
            "statistics": {
                "create": "/api/statistics",
                "list": "/api/statistics",
                "get": "/api/statistics/{request_id}",
            },
        },
    }


@app.get("/reload-test")
async def reload_test():
    return {"status": "hot reload is working!", "version": 1}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
