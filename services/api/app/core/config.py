from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from services.common.env_loader import load_repo_env


load_repo_env()


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    runtime_dir: Path
    db_path: Path
    storage_dir: Path
    manual_review_decisions_dir: Path
    approved_hybrid_inventory_report_path: Path
    template_spec_dir: Path
    worker_entry: Path
    auth_secret: str
    access_token_ttl_sec: int
    inline_worker: bool
    session_ttl_sec: int
    cookie_secure: bool
    token_encryption_key: str  # 32-byte hex — AES-256-GCM key for OAuth token storage


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    repo_root = Path(__file__).resolve().parents[4]
    runtime_dir = Path(os.getenv("APP_RUNTIME_DIR", repo_root / ".runtime"))
    storage_dir = Path(os.getenv("APP_STORAGE_DIR", runtime_dir / "storage"))
    db_path = Path(os.getenv("APP_DB_PATH", runtime_dir / "app.sqlite3"))
    return Settings(
        repo_root=repo_root,
        runtime_dir=runtime_dir,
        db_path=db_path,
        storage_dir=storage_dir,
        manual_review_decisions_dir=Path(
            os.getenv(
                "APP_MANUAL_REVIEW_DECISIONS_DIR",
                repo_root / "docs" / "experiments" / "artifacts" / "exp-249-manual-review-decision-log",
            )
        ),
        approved_hybrid_inventory_report_path=Path(
            os.getenv(
                "APP_APPROVED_HYBRID_INVENTORY_REPORT_PATH",
                repo_root / "docs" / "experiments" / "artifacts" / "exp-254-approved-hybrid-candidate-inventory" / "report.json",
            )
        ),
        template_spec_dir=repo_root / "packages" / "template-spec",
        worker_entry=repo_root / "services" / "worker" / "main.py",
        auth_secret=os.getenv("APP_AUTH_SECRET", "demo-secret-change-me"),
        access_token_ttl_sec=int(os.getenv("APP_ACCESS_TOKEN_TTL_SEC", "43200")),
        inline_worker=_to_bool(os.getenv("APP_INLINE_WORKER"), default=False),
        session_ttl_sec=int(os.getenv("APP_SESSION_TTL_SEC", str(14 * 24 * 3600))),
        cookie_secure=_to_bool(os.getenv("APP_COOKIE_SECURE"), default=False),
        # Dev default: fixed 32-byte hex key. Production MUST override via TOKEN_ENCRYPTION_KEY.
        token_encryption_key=os.getenv(
            "TOKEN_ENCRYPTION_KEY",
            "6465762d6b65792d6368616e67652d6d652d696e2d70726f64756374696f6e21",
        ),
    )
