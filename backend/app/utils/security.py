import re
from cryptography.fernet import Fernet
from backend.app.config import DB_ENCRYPTION_KEY

# Initialize Fernet cipher using the derived encryption key
cipher = Fernet(DB_ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    """Encrypt a string using Fernet symmetric encryption."""
    if data is None:
        return None
    return cipher.encrypt(str(data).encode()).decode()

def decrypt_data(token: str) -> str:
    """Decrypt a Fernet encrypted token."""
    if token is None:
        return None
    try:
        return cipher.decrypt(token.encode()).decode()
    except Exception:
        # Fallback if the data is not encrypted (e.g. legacy data)
        return token

def sanitize_text(text: str) -> str:
    """Sanitize input text by stripping HTML tags, script tags, and pseudo-protocols."""
    if text is None:
        return None
    if not isinstance(text, str):
        return text
    # Remove HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    # Remove inline scripting handlers like onload, onerror, onclick
    clean = re.sub(r'(?i)on\w+\s*=\s*["\'][^"\']*["\']', '', clean)
    clean = re.sub(r'(?i)on\w+\s*=\s*[^\s>]+', '', clean)
    # Remove javascript: pseudo-protocols
    clean = re.sub(r'(?i)javascript:', '', clean)
    # Remove style blocks/link elements
    clean = re.sub(r'(?i)<style.*?>.*?</style>', '', clean, flags=re.DOTALL)
    clean = re.sub(r'(?i)<script.*?>.*?</script>', '', clean, flags=re.DOTALL)
    return clean.strip()
