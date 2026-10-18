"""Daily user login and access audit files."""

from __future__ import annotations

import fcntl
from datetime import datetime, timezone
from pathlib import Path

from config.settings import SETTINGS

AUDIT_FOLDER_NAME = "user_login_audit"


def audit_dir() -> Path:
    path = SETTINGS.audit_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def daily_log_path(when: datetime | None = None) -> Path:
    moment = when or datetime.now(timezone.utc)
    return audit_dir() / f"{moment.strftime('%Y-%m-%d')}.log"


def write_audit(
    action: str,
    username: str = "-",
    role: str = "-",
    detail: str = "",
    outcome: str = "ok",
) -> Path:
    """Append one line to today's log. Never writes passwords or hashes."""
    now = datetime.now(timezone.utc)
    path = daily_log_path(now)
    safe_detail = " ".join(str(detail or "").split())
    line = (
        f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
        f"action={action} | outcome={outcome} | "
        f"username={username or '-'} | role={role or '-'} | "
        f"detail={safe_detail}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(line)
        handle.flush()
    return path


def list_audit_dates() -> list[str]:
    files = sorted(audit_dir().glob("*.log"), reverse=True)
    return [item.stem for item in files]


def read_audit_log(day: str) -> str:
    path = audit_dir() / f"{day}.log"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
