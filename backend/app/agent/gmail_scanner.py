from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.utils.logger import logger
from app.database import get_supabase
from datetime import datetime, timezone
import base64
import re
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ── Load credentials from Supabase for a user ─────────
def get_gmail_service_for_user(user_id: str):
    sb     = get_supabase()
    result = sb.table("gmail_tokens").select("*").eq(
        "user_id", user_id
    ).execute()

    if not result.data:
        raise ValueError(
            f"No Gmail connection found for user {user_id}. "
            "Please connect Gmail in Settings."
        )

    token_data = result.data[0]

    creds = Credentials(
        token         = token_data["access_token"],
        refresh_token = token_data["refresh_token"],
        token_uri     = token_data["token_uri"],
        client_id     = token_data["client_id"],
        client_secret = token_data["client_secret"],
        scopes        = json.loads(token_data["scopes"]),
    )

    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        logger.info(f"Gmail token refreshed for user {user_id}")

        # Save refreshed token back to Supabase
        sb.table("gmail_tokens").update({
            "access_token": creds.token,
            "expiry":       creds.expiry.isoformat() if creds.expiry else None,
            "updated_at":   datetime.now(timezone.utc).isoformat(),
        }).eq("user_id", user_id).execute()

    return build('gmail', 'v1', credentials=creds)

# ── Extract email body ─────────────────────────────────
def extract_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode(
                        'utf-8', errors='ignore'
                    )
            elif 'parts' in part:
                body += extract_body(part)
    else:
        data = payload['body'].get('data', '')
        if data:
            body += base64.urlsafe_b64decode(data).decode(
                'utf-8', errors='ignore'
            )
    return body

# ── Clean email text ───────────────────────────────────
def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:3000]

# ── Fetch emails for a specific user ──────────────────
def fetch_emails(user_id: str, days_back: int = 7, max_results: int = 50):
    logger.info(f"Fetching emails for user {user_id} — last {days_back} days")
    service = get_gmail_service_for_user(user_id)
    emails  = []

    try:
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=f'newer_than:{days_back}d'
        ).execute()

        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} emails")

        for msg in messages:
            try:
                detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = {
                    h['name']: h['value']
                    for h in detail['payload']['headers']
                }

                subject    = headers.get('Subject', '')
                sender     = headers.get('From',    '')
                date       = headers.get('Date',    '')
                body       = clean_text(extract_body(detail['payload']))

                received_at = None
                try:
                    from email.utils import parsedate_to_datetime
                    received_at = parsedate_to_datetime(date).isoformat()
                except Exception:
                    received_at = datetime.now(timezone.utc).isoformat()

                emails.append({
                    'gmail_id':    msg['id'],
                    'subject':     subject,
                    'sender':      sender,
                    'body':        body,
                    'received_at': received_at,
                })

            except Exception as e:
                logger.error(f"Error processing email {msg['id']}: {e}")
                continue

        logger.info(f"Fetched {len(emails)} emails for user {user_id}")
        return emails

    except Exception as e:
        logger.error(f"Gmail fetch failed for user {user_id}: {e}")
        raise