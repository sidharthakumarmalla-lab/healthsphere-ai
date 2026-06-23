import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database Config
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/healthsphere.db")

# Vector Memory Config
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", f"{BASE_DIR}/chroma_db")

# Gemini API Config
# Note: GEMINI_API_KEY might be in the environment already.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# App configs
APP_HOST = "127.0.0.1"
APP_PORT = 8000
STREAMLIT_PORT = 8501
