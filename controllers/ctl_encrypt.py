from cryptography.fernet import Fernet
from dotenv import load_dotenv

import os

load_dotenv()

fernet = Fernet(os.getenv("ENCRYPT"))

def encrypt(texto):
    return fernet.encrypt(texto.encode()).decode()

def decrypt(texto):
    return fernet.decrypt(texto.encode()).decode()
