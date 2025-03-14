import os
from dotenv import load_dotenv

load_dotenv()  # Laad variabelen uit het .env-bestand

def get_db_password():
    db_pass = os.getenv('DATABASE_PASSWORD')
    if not db_pass:
        raise ValueError("DATABASE_PASSWORD ontbreekt in de .env file of omgeving!")
    return db_pass

def get_api_key():
    db_pass = os.getenv('API_KEY')
    if not db_pass:
        raise ValueError("DATABASE_PASSWORD missing in .env file or environment!")
    return db_pass
