from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.utils.logger import logger
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
    logger.info("Root endpoint hit")
    return {
        "status": "online",
        "app": "Email Manager Agent",
        "version": "1.0.0",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}