from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import DATABASE_URL

# Create declarative base
Base = declarative_base()

# Global engine variable
engine = None

def initialize_database():
    """Initialize database connection with fallback logic"""
    global engine
    
    if engine is not None:
        return engine
    
    try:
        # Try PostgreSQL first with very short timeout
        engine = create_engine(
            DATABASE_URL, 
            connect_args={"connect_timeout": 2}, 
            pool_timeout=1, 
            pool_pre_ping=True
        )
        # Test the connection with timeout
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("PostgreSQL connection successful!")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        print("Falling back to SQLite for local development")
        # Fallback to SQLite
        engine = create_engine("sqlite:///./air_quality.db")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("SQLite fallback database connected successfully!")
    
    return engine

# Initialize engine on first import (but don't test connection yet)
engine = None

# Session-Fabrik: stellt Transaktionen zur Verfügung
def get_session_local():
    """Get SessionLocal factory, initializing database if needed"""
    if engine is None:
        initialize_database()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Funktion zur Session-Erstellung (z. B. für FastAPI dependency)
def get_db():
    if engine is None:
        initialize_database()
    
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Direct database session for non-dependency injection use"""
    if engine is None:
        initialize_database()
    
    SessionLocal = get_session_local()
    return SessionLocal()
