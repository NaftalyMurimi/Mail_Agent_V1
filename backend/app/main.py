from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from app.utils.logger import logger
from app.api import auth, users, emails, jobs, cvs, scan, settings
import os

load_dotenv()

app = FastAPI(
    title="Email Manager Agent",
    description="AI-powered job search automation API",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(emails.router)
app.include_router(jobs.router)
app.include_router(cvs.router)
app.include_router(scan.router)
app.include_router(settings.router)

# ── Events ────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("Email Manager Agent API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Email Manager Agent API shutting down...")

# ── Health Check ──────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status":  "online",
        "app":     "Email Manager Agent",
        "version": "1.0.0",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}