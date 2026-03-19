from groq import Groq
from app.utils.logger import logger
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Classify a single email ────────────────────────────
def classify_email(subject: str, sender: str, body: str) -> dict:
    prompt = f"""You are an expert email classifier for job seekers.

Analyze this email and extract structured information.

EMAIL:
Subject: {subject}
From: {sender}
Body: {body[:2000]}

Respond ONLY with a valid JSON object — no explanation, no markdown:
{{
  "email_type": "job_advert|interview|offer|confirmed|rejection|followup|irrelevant",
  "company": "company name or null",
  "role_title": "job title or null",
  "location": "location or null",
  "salary": "salary range or null",
  "deadline": "deadline date or null",
  "action_required": true or false,
  "urgency": "high|medium|low",
  "body_preview": "first 200 chars of body"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()

        # Clean JSON if wrapped in markdown
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        logger.info(f"Classified: {subject[:50]} → {result.get('email_type')}")
        return result

    except Exception as e:
        logger.error(f"Classification failed for '{subject[:50]}': {e}")
        return {
            "email_type":     "irrelevant",
            "company":        None,
            "role_title":     None,
            "location":       None,
            "salary":         None,
            "deadline":       None,
            "action_required": False,
            "urgency":        "low",
            "body_preview":   body[:200] if body else "",
        }