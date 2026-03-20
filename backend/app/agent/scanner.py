from app.agent.gmail_scanner import fetch_emails
from app.agent.classifier    import classify_email
from app.agent.cv_matcher    import score_job_against_cv
from app.database            import get_supabase
from app.utils.logger        import logger
from datetime                import datetime, timezone
import uuid

# ── Run full scan for a user ───────────────────────────
def run_scan(user_id: str, days_back: int = 7, max_results: int = 50) -> dict:
    sb = get_supabase()
    logger.info(f"Starting scan for user {user_id}")

    scan_start      = datetime.now(timezone.utc)
    emails_found    = 0
    emails_classified = 0
    jobs_detected   = 0
    error_message   = None

    try:
        # ── Fetch user's active CV ─────────────────────
        cv_result = sb.table("cvs").select("parsed_text").eq(
            "user_id", user_id
        ).eq("is_active", True).limit(1).execute()

        cv_text = ""
        if cv_result.data:
            cv_text = cv_result.data[0].get("parsed_text", "")
            logger.info(f"CV loaded — {len(cv_text)} characters")
        else:
            logger.info("No CV found for user — scoring without CV")

        # ── Fetch emails from Gmail ────────────────────
        # emails = fetch_emails(days_back=days_back, max_results=max_results)
        emails = fetch_emails(user_id=user_id, days_back=days_back, max_results=max_results)
        emails_found = len(emails)

        # ── Get already processed gmail IDs ───────────
        existing = sb.table("emails").select("gmail_id").eq(
            "user_id", user_id
        ).execute()
        processed_ids = {e["gmail_id"] for e in existing.data}

        # ── Process each email ─────────────────────────
        for email in emails:

            # Skip already processed
            if email["gmail_id"] in processed_ids:
                continue

            # Classify with Groq AI
            classification = classify_email(
                subject=email["subject"],
                sender=email["sender"],
                body=email["body"],
            )
            emails_classified += 1

            # Save email to Supabase
            email_record = {
                "id":              str(uuid.uuid4()),
                "user_id":         user_id,
                "gmail_id":        email["gmail_id"],
                "subject":         email["subject"],
                "sender":          email["sender"],
                "body_preview":    classification.get("body_preview", email["body"][:200]),
                "email_type":      classification.get("email_type"),
                "company":         classification.get("company"),
                "role_title":      classification.get("role_title"),
                "location":        classification.get("location"),
                "salary":          classification.get("salary"),
                "deadline":        classification.get("deadline"),
                "action_required": classification.get("action_required", False),
                "urgency":         classification.get("urgency", "low"),
                "is_processed":    True,
                "received_at":     email["received_at"],
                "classified_at":   datetime.now(timezone.utc).isoformat(),
            }

            email_result = sb.table("emails").insert(email_record).execute()

            # ── If job advert — score against CV ──────
            if classification.get("email_type") == "job_advert":
                match = score_job_against_cv(
                    cv_text=cv_text,
                    job_title=classification.get("role_title", "Unknown Role"),
                    company=classification.get("company", "Unknown Company"),
                    job_body=email["body"],
                )

                job_record = {
                    "id":                   str(uuid.uuid4()),
                    "user_id":              user_id,
                    "email_id":             email_record["id"],
                    "company":              classification.get("company"),
                    "role_title":           classification.get("role_title"),
                    "location":             classification.get("location"),
                    "salary":               classification.get("salary"),
                    "deadline":             classification.get("deadline"),
                    "match_score":          match.get("match_score"),
                    "match_reasons":        match.get("match_reasons"),
                    "gaps":                 match.get("gaps"),
                    "apply_recommendation": match.get("apply_recommendation"),
                    "personalized_tip":     match.get("personalized_tip"),
                    "status":               "detected",
                    "created_at":           datetime.now(timezone.utc).isoformat(),
                    "updated_at":           datetime.now(timezone.utc).isoformat(),
                }

                sb.table("jobs").insert(job_record).execute()
                jobs_detected += 1
                logger.info(
                    f"Job detected: {classification.get('role_title')} "
                    f"at {classification.get('company')} — "
                    f"Score: {match.get('match_score')}/10"
                )

        # ── Save scan log ──────────────────────────────
        sb.table("scan_logs").insert({
            "id":                 str(uuid.uuid4()),
            "user_id":            user_id,
            "scanned_at":         scan_start.isoformat(),
            "emails_found":       emails_found,
            "emails_classified":  emails_classified,
            "jobs_detected":      jobs_detected,
            "status":             "success",
        }).execute()

        logger.info(
            f"Scan complete — "
            f"found: {emails_found}, "
            f"classified: {emails_classified}, "
            f"jobs: {jobs_detected}"
        )

        return {
            "status":            "success",
            "emails_found":      emails_found,
            "emails_classified": emails_classified,
            "jobs_detected":     jobs_detected,
        }

    except Exception as e:
        error_message = str(e)
        logger.error(f"Scan failed: {e}")

        sb.table("scan_logs").insert({
            "id":           str(uuid.uuid4()),
            "user_id":      user_id,
            "scanned_at":   scan_start.isoformat(),
            "emails_found": emails_found,
            "status":       "failed",
            "error_message": error_message[:500],
        }).execute()

        return {
            "status":        "failed",
            "error_message": error_message,
        }