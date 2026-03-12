from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

# ── Only create engine if DATABASE_URL is set ─────────
engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Dependency — use this in every route that needs DB ──
def get_db():
    if not SessionLocal:
        raise RuntimeError("DATABASE_URL is not set. Please configure your .env file.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()