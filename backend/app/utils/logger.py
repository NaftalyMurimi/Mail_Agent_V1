from loguru import logger
import os

# ── Create logs directory if it doesn't exist ────────
os.makedirs("logs", exist_ok=True)

# ── Configure Loguru ──────────────────────────────────
logger.add(
    "logs/app.log",
    rotation="10 MB",       # new file every 10MB
    retention="30 days",    # keep logs for 30 days
    compression="zip",      # compress old logs
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}",
)

logger.add(
    "logs/errors.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="ERROR",          # errors only
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module} | {message}",
)