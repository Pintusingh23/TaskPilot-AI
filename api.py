import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.chat import router as chat_router
from app.api.calendar import router as calendar_router
from app.api.gmail import router as gmail_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("taskpilot")

# FastAPI Application
app = FastAPI(
    title="TaskPilot AI API",
    description="Full-Stack Personal AI Productivity Assistant Backend",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular API Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(calendar_router, prefix=settings.API_V1_STR)
app.include_router(gmail_router, prefix=settings.API_V1_STR)

# Root Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to TaskPilot AI API",
        "status": "running",
        "docs": "/docs",
        "version": settings.VERSION
    }

# Health Check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TaskPilot AI API",
        "version": settings.VERSION
    }

# Legacy CLI/fallback ChatRequest and ChatResponse models
class LegacyChatRequest(BaseModel):
    message: str

class LegacyChatResponse(BaseModel):
    response: str

# Legacy fallback endpoint preserved for direct backward compatibility
@app.post("/chat", response_model=LegacyChatResponse)
def legacy_chat(request: LegacyChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    try:
        from main import run_agent
        response = run_agent(request.message)
        return {"response": response or ""}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
