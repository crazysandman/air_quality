"""
Database Configuration
=====================

Database connection and session management for the Air Quality API.
Supports PostgreSQL (primary) with SQLite fallback for development.

Author: Master's Student Project
Production DB: Supabase PostgreSQL
Development DB: SQLite
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Use relative imports for package structure
try:
    # When run as module (uvicorn backend.main:app)
    from .config import DATABASE_URL
except ImportError:
    # Fallback for direct execution (development)
    from config import DATABASE_URL

# SQLAlchemy declarative base for ORM models
Base = declarative_base()

# Global database engine instance
engine = None

def initialize_database():
    """
    Initialize database connection with intelligent fallback logic.
    
    Attempts to connect to PostgreSQL (Supabase) first, then falls back
    to SQLite for local development if PostgreSQL is unavailable.
    
    Returns:
        Engine: SQLAlchemy database engine instance
        
    Raises:
        Exception: If both PostgreSQL and SQLite connections fail
    """
    global engine
    
    if engine is not None:
        return engine
    
    try:
        # Primary: PostgreSQL connection (Supabase/Railway)
        print(f"🔗 Attempting PostgreSQL connection...")
        engine = create_engine(
            DATABASE_URL, 
            connect_args={
                "connect_timeout": 10,
                "sslmode": "require",
                "target_session_attrs": "read-write"
            }, 
            pool_timeout=5,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False  # Set to True for SQL debugging
        )
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connection successful!")
            print(f"Database version: {version[:50]}...")
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
