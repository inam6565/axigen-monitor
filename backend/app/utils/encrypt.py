from cryptography.fernet import Fernet
import os

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    # you should generate and store FERNET_KEY in .env or secret manager
    raise RuntimeError("FERNET_KEY not set")

fernet = Fernet(FERNET_KEY.encode())

def encrypt_password(plaintext: str) -> str:
    return fernet.encrypt(plaintext.encode()).decode()

def decrypt_password(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
