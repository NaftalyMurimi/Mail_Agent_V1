from supabase import create_client, Client
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv()

SUPABASE_URL     = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

Base = declarative_base()

# ── Supabase client ────────────────────────────────────
supabase: Client = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_supabase() -> Client:
    if not supabase:
        raise RuntimeError("Supabase is not configured. Check your .env file.")
    return supabase