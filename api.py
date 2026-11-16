
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import run_agent

# FastAPI application
app = FastAPI(
    title="TaskPilot AI API",
    description="Personal AI Assistant Backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class ChatRequest(BaseModel):
    message: str


# Response model
class ChatResponse(BaseModel):
    response: str


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to TaskPilot AI API",
        "status": "running"
    }


# Health endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# AI Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    try:
        response = run_agent(request.message)

        return {
            "response": response or ""
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
