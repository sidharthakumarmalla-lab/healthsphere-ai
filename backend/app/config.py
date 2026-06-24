import os
from pathlib import Path
from dotenv import load_dotenv
import base64
import hashlib

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database Config
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/healthsphere.db")

# Vector Memory Config
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", f"{BASE_DIR}/chroma_db")

# Gemini API Config
# Note: GEMINI_API_KEY might be in the environment already.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Security Config
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "healthsphere_secure_api_token_2026")

# Derive stable database encryption key from GEMINI_API_KEY if not explicitly set
db_encrypt_key_raw = os.getenv("DB_ENCRYPTION_KEY")
if not db_encrypt_key_raw:
    base_key = GEMINI_API_KEY or "healthsphere_default_secure_salt_12345"
    key_hash = hashlib.sha256(base_key.encode()).digest()
    DB_ENCRYPTION_KEY = base64.urlsafe_b64encode(key_hash).decode()
else:
    DB_ENCRYPTION_KEY = db_encrypt_key_raw

# App configs
APP_HOST = "127.0.0.1"
APP_PORT = 8000
STREAMLIT_PORT = 8501

