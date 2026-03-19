from groq import Groq
from app.utils.logger import logger
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Score a job against a CV ───────────────────────────
def score_job_against_cv(
    cv_text:   str,
    job_title: str,
    company:   str,
    job_body:  str,
) -> dict:

    if not cv_text or len(cv_text.strip()) < 50:
        return {
            "match_score":          5.0,
            "match_reasons":        "No CV uploaded yet",
            "gaps":                 "Upload a CV for personalised scoring",
            "apply_recommendation": "Consider",
            "personalized_tip":     "Upload your CV to get accurate job matching",
        }

    prompt = f"""You are an expert career coach and recruiter.

Score how well this candidate's CV matches this job advert.

CANDIDATE CV:
{cv_text[:3000]}

JOB ADVERT:
Title:   {job_title}
Company: {company}
Details: {job_body[:1500]}

Respond ONLY with a valid JSON object — no explanation, no markdown:
{{
  "match_score": 7.5,
  "match_reasons": "Strong Python skills match requirement. 3 years experience aligns well.",
  "gaps": "Missing AWS certification mentioned in job spec.",
  "apply_recommendation": "Strongly Apply|Consider|Skip",
  "personalized_tip": "Specific actionable advice for this candidate for this role"
}}

match_score must be a number from 1.0 to 10.0"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        score  = float(result.get("match_score", 5.0))
        result["match_score"] = round(min(max(score, 1.0), 10.0), 1)

        logger.info(f"Job scored: {job_title} at {company} → {result['match_score']}/10")
        return result

    except Exception as e:
        logger.error(f"CV matching failed: {e}")
        return {
            "match_score":          5.0,
            "match_reasons":        "Scoring unavailable",
            "gaps":                 "Try again later",
            "apply_recommendation": "Consider",
            "personalized_tip":     "Review the job requirements manually",
        }