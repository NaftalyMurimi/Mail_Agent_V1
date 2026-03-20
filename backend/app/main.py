from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.utils.logger import logger
from app.api import auth, users, emails, jobs, cvs, scan, settings
from app.api import gmail_auth
import os

load_dotenv()

app = FastAPI(
    title="Email Manager Agent",
    description="AI-powered job search automation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(emails.router)
app.include_router(jobs.router)
app.include_router(cvs.router)
app.include_router(scan.router)
app.include_router(settings.router)
app.include_router(gmail_auth.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Email Manager Agent API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Email Manager Agent API shutting down...")

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "app": "Email Manager Agent", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}