from __future__ import annotations

"""
Daily hard-delete batch job (spec section 8, step 10-11).

Run once per day via cron or a management command:
    python -m app.services.hard_delete

Deletes users rows where hard_delete_at <= now(), cascading to all PII.
audit_logs rows are kept (1-year legal obligation) with user_id set to NULL.
"""

import logging
from datetime import datetime, timezone

from app.core.database import get_connection, utc_now

log = logging.getLogger(__name__)


def run_hard_delete_batch() -> int:
    """Delete all users due for hard deletion. Returns the number of rows deleted."""
    now_iso = datetime.now(timezone.utc).isoformat()
    deleted = 0

    with get_connection() as conn:
        due = conn.execute(
            "SELECT id FROM users WHERE hard_delete_at IS NOT NULL AND hard_delete_at <= ?",
            (now_iso,),
        ).fetchall()

        for row in due:
            user_id = row["id"]
            # Anonymise audit logs before the user row is gone (FK would cascade to NULL anyway,
            # but being explicit avoids relying on ON DELETE SET NULL being configured)
            conn.execute(
                "UPDATE audit_logs SET user_id = NULL WHERE user_id = ?",
                (user_id,),
            )
            # Hard-delete the user row; FK cascades will remove all related PII tables
            # (sessions, consents, verification_tokens, social_accounts, store_profiles, etc.)
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            deleted += 1
            log.info("hard_delete: purged user_id=%s", user_id)

    return deleted


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    count = run_hard_delete_batch()
    log.info("hard_delete batch complete: %d user(s) purged", count)
