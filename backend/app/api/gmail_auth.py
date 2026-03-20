from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app.utils.dependencies import get_current_user
from app.database import get_supabase
from app.utils.logger import logger
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import json
import requests
import secrets

load_dotenv()

router = APIRouter(prefix="/gmail", tags=["Gmail Auth"])

SCOPES        = 'https://www.googleapis.com/auth/gmail.readonly'
REDIRECT_URI  = 'http://127.0.0.1:8000/gmail/callback'
TOKEN_URL     = 'https://oauth2.googleapis.com/token'
AUTH_URL      = 'https://accounts.google.com/o/oauth2/v2/auth'

# ── Load client credentials from credentials.json ─────
def load_client_config():
    creds_file = 'credentials.json'
    if not os.path.exists(creds_file):
        raise HTTPException(status_code=500, detail="credentials.json not found")
    with open(creds_file) as f:
        data = json.load(f)
    # Web app credentials are under "web" key
    config = data.get('web') or data.get('installed')
    if not config:
        raise HTTPException(status_code=500, detail="Invalid credentials.json format")
    return config

# ── Temporary state store ──────────────────────────────
oauth_states = {}

# ── Step 1: Generate OAuth URL ─────────────────────────
@router.get("/connect")
async def gmail_connect(current_user: dict = Depends(get_current_user)):
    config = load_client_config()
    state  = secrets.token_urlsafe(32)

    oauth_states[state] = current_user["id"]

    params = {
        'client_id':     config['client_id'],
        'redirect_uri':  REDIRECT_URI,
        'response_type': 'code',
        'scope':         SCOPES,
        'access_type':   'offline',
        'prompt':        'consent',
        'state':         state,
    }

    query = '&'.join(f'{k}={requests.utils.quote(str(v))}' for k,v in params.items())
    auth_url = f"{AUTH_URL}?{query}"

    logger.info(f"Gmail OAuth URL generated for {current_user['email']}")
    return {"auth_url": auth_url}

# ── Step 2: Handle OAuth Callback ─────────────────────
@router.get("/callback")
async def gmail_callback(code: str, state: str):
    user_id = oauth_states.get(state)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    config = load_client_config()

    # Exchange code for tokens manually
    response = requests.post(TOKEN_URL, data={
        'code':          code,
        'client_id':     config['client_id'],
        'client_secret': config['client_secret'],
        'redirect_uri':  REDIRECT_URI,
        'grant_type':    'authorization_code',
    })

    if response.status_code != 200:
        logger.error(f"Token exchange failed: {response.text}")
        raise HTTPException(
            status_code=400,
            detail=f"Token exchange failed: {response.text}"
        )

    token_info = response.json()
    logger.info(f"Token exchange successful for user {user_id}")

    sb = get_supabase()

    token_data = {
        "user_id":       user_id,
        "access_token":  token_info['access_token'],
        "refresh_token": token_info.get('refresh_token', ''),
        "token_uri":     TOKEN_URL,
        "client_id":     config['client_id'],
        "client_secret": config['client_secret'],
        "scopes":        json.dumps([SCOPES]),
        "expiry":        None,
        "updated_at":    datetime.now(timezone.utc).isoformat(),
    }

    existing = sb.table("gmail_tokens").select("id").eq(
        "user_id", user_id
    ).execute()

    if existing.data:
        sb.table("gmail_tokens").update(token_data).eq(
            "user_id", user_id
        ).execute()
    else:
        sb.table("gmail_tokens").insert(token_data).execute()

    del oauth_states[state]
    logger.info(f"Gmail connected successfully for user {user_id}")

    return RedirectResponse(url="http://localhost:5173/settings?gmail=connected")

# ── Check Gmail connection status ──────────────────────
@router.get("/status")
async def gmail_status(current_user: dict = Depends(get_current_user)):
    sb     = get_supabase()
    result = sb.table("gmail_tokens").select("id, updated_at").eq(
        "user_id", current_user["id"]
    ).execute()

    return {
        "connected":  bool(result.data),
        "updated_at": result.data[0]["updated_at"] if result.data else None
    }

# ── Disconnect Gmail ───────────────────────────────────
@router.delete("/disconnect")
async def gmail_disconnect(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    sb.table("gmail_tokens").delete().eq(
        "user_id", current_user["id"]
    ).execute()
    logger.info(f"Gmail disconnected for {current_user['email']}")
    return {"message": "Gmail disconnected successfully"}