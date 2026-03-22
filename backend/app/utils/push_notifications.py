from pywebpush import webpush, WebPushException
from app.utils.logger import logger
from app.database import get_supabase
from dotenv import load_dotenv
import os
import json

load_dotenv()

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY  = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL       = os.getenv("VAPID_EMAIL", "mailto:admin@emailagent.com")

# ── Send browser push notification ────────────────────
def send_push(subscription: dict, title: str, body: str, url: str = "/jobs") -> bool:
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        logger.warning("VAPID keys not configured — skipping push notification")
        return False
    try:
        webpush(
            subscription_info = subscription,
            data              = json.dumps({
                "title": title,
                "body":  body,
                "url":   url,
            }),
            vapid_private_key = VAPID_PRIVATE_KEY,
            vapid_claims      = {"sub": VAPID_EMAIL},
        )
        logger.info("Browser push notification sent")
        return True
    except WebPushException as e:
        logger.error(f"Push notification failed: {e}")
        return False

# ── Notify user via browser push ──────────────────────
def notify_push(user_id: str, title: str, body: str):
    sb = get_supabase()
    result = sb.table("push_subscriptions").select("subscription").eq(
        "user_id", user_id
    ).execute()

    if not result.data:
        return

    for row in result.data:
        sub = row["subscription"]
        if isinstance(sub, str):
            sub = json.loads(sub)
        send_push(sub, title, body)