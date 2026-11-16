import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the TaskPilot-AI project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

def get_cleaned_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        return f"sqlite:///{BASE_DIR / 'taskpilot.db'}"

    # Handle Postgres URL and special characters in password
    if raw_url.startswith("postgresql://") or raw_url.startswith("postgres://"):
        try:
            prefix, rest = raw_url.split("://", 1)
            if "@" in rest:
                user_pass, host_db = rest.rsplit("@", 1)
                if ":" in user_pass:
                    user, password = user_pass.split(":", 1)
                    encoded_password = urllib.parse.quote_plus(password)
                    return f"postgresql+psycopg2://{user}:{encoded_password}@{host_db}"
            return raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        except Exception:
            return raw_url
    return raw_url

class Settings:
    PROJECT_NAME: str = "TaskPilot AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "taskpilot_super_secret_jwt_key_2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    DATABASE_URL: str = get_cleaned_database_url()
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR / 'taskpilot.db'}"
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    # Also support existing model or fallbacks
    FALLBACK_GROQ_MODELS: list = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b"]
    
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

settings = Settings()

