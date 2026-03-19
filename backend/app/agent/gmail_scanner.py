from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.utils.logger import logger
from datetime import datetime, timezone
import os
import json
import base64
import re

SCOPES     = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.json'

# ── Build Gmail service ────────────────────────────────
def get_gmail_service():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"token.json not found. Run get_gmail_token.py first."
        )

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        logger.info("Gmail token refreshed")

    return build('gmail', 'v1', credentials=creds)

# ── Extract email body ─────────────────────────────────
def extract_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                body += extract_body(part)
    else:
        data = payload['body'].get('data', '')
        if data:
            body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body

# ── Clean email text ───────────────────────────────────
def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:3000]

# ── Fetch emails ───────────────────────────────────────
def fetch_emails(days_back=7, max_results=50):
    logger.info(f"Fetching emails from last {days_back} days...")
    service  = get_gmail_service()
    emails   = []

    try:
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=f'newer_than:{days_back}d'
        ).execute()

        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} emails to process")

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

                subject = headers.get('Subject', '')
                sender  = headers.get('From',    '')
                date    = headers.get('Date',    '')
                body    = clean_text(extract_body(detail['payload']))

                # Parse received date
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
                logger.error(f"Error fetching email {msg['id']}: {e}")
                continue

        logger.info(f"Successfully fetched {len(emails)} emails")
        return emails

    except Exception as e:
        logger.error(f"Gmail fetch failed: {e}")
        raise