from app.utils.logger import logger
from app.database import get_supabase
from dotenv import load_dotenv
import os
import httpx

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL   = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ── Send Telegram message ──────────────────────────────
async def send_telegram(chat_id: str, message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        logger.warning("Telegram not configured — skipping notification")
        return False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={
                    "chat_id":    chat_id,
                    "text":       message,
                    "parse_mode": "HTML",
                }
            )
            if response.status_code == 200:
                logger.info(f"Telegram notification sent to {chat_id}")
                return True
            else:
                logger.error(f"Telegram failed: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

# ── Format job notification ────────────────────────────
def format_job_notification(job: dict) -> str:
    score     = job.get("match_score", 0)
    role      = job.get("role_title",  "Unknown Role")
    company   = job.get("company",     "Unknown Company")
    location  = job.get("location",    "")
    salary    = job.get("salary",      "")
    rec       = job.get("apply_recommendation", "")
    tip       = job.get("personalized_tip", "")
    deadline  = job.get("deadline",    "")

    # Score emoji
    if score >= 8:   emoji = "🔥"
    elif score >= 6: emoji = "✅"
    else:            emoji = "📋"

    lines = [
        f"{emoji} <b>New Job Match — {score}/10</b>",
        f"",
        f"💼 <b>{role}</b>",
        f"🏢 {company}",
    ]
    if location: lines.append(f"📍 {location}")
    if salary:   lines.append(f"💰 {salary}")
    if deadline: lines.append(f"⏰ Deadline: {deadline}")
    lines.append(f"")
    lines.append(f"📊 <b>{rec}</b>")
    if tip:
        lines.append(f"")
        lines.append(f"💡 {tip}")

    return "\n".join(lines)

# ── Format scan summary ────────────────────────────────
def format_scan_summary(result: dict) -> str:
    found      = result.get("emails_found",      0)
    classified = result.get("emails_classified", 0)
    jobs       = result.get("jobs_detected",     0)

    return (
        f"🔍 <b>Scan Complete</b>\n\n"
        f"📧 Emails scanned: {found}\n"
        f"🤖 Classified: {classified}\n"
        f"💼 Job adverts found: {jobs}\n\n"
        f"{'🎯 Check your jobs dashboard!' if jobs > 0 else '📭 No new jobs this scan'}"
    )

# ── Notify user after scan ─────────────────────────────
async def notify_scan_complete(user_id: str, result: dict):
    sb = get_supabase()

    # Get user telegram_chat_id
    user_result = sb.table("users").select(
        "telegram_chat_id"
    ).eq("id", user_id).execute()

    if not user_result.data:
        return

    chat_id = user_result.data[0].get("telegram_chat_id")
    if not chat_id:
        logger.info(f"No Telegram chat ID for user {user_id}")
        return

    # Get ONLY jobs with match_score > 7
    jobs_result = sb.table("jobs").select("*").eq(
        "user_id", user_id
    ).gt("match_score", 7.0).eq(
        "status", "detected"
    ).order("match_score", desc=True).limit(5).execute()

    high_match_jobs = jobs_result.data

    # Only notify if there are high match jobs
    if not high_match_jobs:
        logger.info(f"No jobs above 7/10 for user {user_id} — skipping notification")
        return

    # Send summary only if high match jobs found
    summary = (
        f"🎯 <b>High Match Jobs Found!</b>\n\n"
        f"📧 Emails scanned: {result.get('emails_found', 0)}\n"
        f"💼 Jobs above 7/10: {len(high_match_jobs)}\n"
    )
    await send_telegram(chat_id, summary)

    # Send one card per high match job
    for job in high_match_jobs:
        message = format_job_notification(job)
        await send_telegram(chat_id, message)

    logger.info(f"Sent {len(high_match_jobs)} high-match job notifications to {user_id}")
