#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

print("🛠️  SUPABASE SCHEMA RECREATION")
print("=" * 50)

try:
    print("📊 Importing modules...")
    from database import initialize_database, get_db_session
    from models import Base, StationData
    from sqlalchemy import text
    
    print("📊 Initializing database...")
    engine = initialize_database()
    print(f"✅ Engine created: {type(engine)}")
    
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    print("📊 Checking tables...")
    db = get_db_session()
    result = db.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """))
    tables = [row[0] for row in result]
    print(f"📋 Tables found: {tables}")
    
    # Test data insertion
    if 'station_data' in tables:
        print("📊 Testing data insertion...")
        test_count = db.execute(text("SELECT COUNT(*) FROM station_data")).scalar()
        print(f"   Current records: {test_count}")
    
    db.close()
    print("🎉 Supabase schema is ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
