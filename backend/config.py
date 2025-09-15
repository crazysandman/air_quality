from dotenv import load_dotenv
import os
from pathlib import Path

# Get the directory where this config.py file is located
current_dir = Path(__file__).parent

# .env-Datei laden (explizit den Pfad angeben)
load_dotenv(current_dir / ".env")

# Token für WAQI API
WAQI_API_TOKEN = os.getenv("WAQI_API_TOKEN")

# Supabase / Railway Datenbank-URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Debug: Print values to check if they're loaded correctly
if DATABASE_URL is None:
    print("WARNING: DATABASE_URL is None!")
    print(f"Looking for .env file at: {current_dir / '.env'}")
    print(f".env file exists: {(current_dir / '.env').exists()}")
else:
    print("DATABASE_URL loaded successfully")