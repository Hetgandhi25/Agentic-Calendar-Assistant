import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("POSTGRES_URL")

try:
    engine = create_engine(db_url, connect_args={"connect_timeout": 5})
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1")).fetchone()
        print("SELECT 1 Result:", res[0])
        
        tables = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'ai' OR table_schema = 'public'
        """)).fetchall()
        
        print("Found Tables:")
        for t in tables:
            print("-", t[0])
except Exception as e:
    print("Database connection failed:", e)
