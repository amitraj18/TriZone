import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "exam_reporter.db"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-exam-reporter-key-2026")
    DATABASE = str(DATABASE_PATH)
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    CORS_HEADERS = "Content-Type"

