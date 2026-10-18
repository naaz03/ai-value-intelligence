"""Daily user login and access audit files."""

from __future__ import annotations

import fcntl
import re
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


def _clean(value: object, default: str = "-") -> str:
    text = " ".join(str(value or "").split())
    return text or default


def _header(headers, *names: str) -> str:
    if headers is None:
        return ""
    for name in names:
        try:
            value = headers.get(name)
        except Exception:
            value = None
        if value:
            return str(value)
    return ""


def _client_ip(context) -> str:
    try:
        ip = getattr(context, "ip_address", None)
        if ip:
            return str(ip)
    except Exception:
        pass
    headers = getattr(context, "headers", None)
    forwarded = _header(headers, "X-Forwarded-For", "x-forwarded-for")
    if forwarded:
        # First hop is typically the original client when proxies append.
        return forwarded.split(",")[0].strip()
    real_ip = _header(headers, "X-Real-IP", "x-real-ip", "CF-Connecting-IP", "cf-connecting-ip")
    return real_ip or "-"


def _parse_system(user_agent: str) -> str:
    ua = user_agent or ""
    if not ua or ua == "-":
        return "-"

    os_name = "Unknown OS"
    if "Windows NT" in ua:
        os_name = "Windows"
    elif "Android" in ua:
        os_name = "Android"
    elif "iPhone" in ua or "iPad" in ua or "iOS" in ua:
        os_name = "iOS"
    elif "Mac OS X" in ua or "Macintosh" in ua:
        os_name = "macOS"
    elif "CrOS" in ua:
        os_name = "ChromeOS"
    elif "Linux" in ua:
        os_name = "Linux"

    browser = "Unknown browser"
    if "Edg/" in ua:
        browser = "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        browser = "Opera"
    elif "Chrome/" in ua and "Chromium" not in ua:
        browser = "Chrome"
    elif "Firefox/" in ua:
        browser = "Firefox"
    elif "Safari/" in ua and "Chrome/" not in ua:
        browser = "Safari"

    device = "Desktop"
    if re.search(r"Mobile|Android|iPhone|iPad", ua, re.I):
        device = "Mobile"

    return f"{device}/{os_name}/{browser}"


def client_context() -> dict[str, str]:
    """Best-effort client metadata from Streamlit session context."""
    try:
        import streamlit as st

        context = st.context
    except Exception:
        return {
            "ip": "-",
            "system": "-",
            "user_agent": "-",
            "timezone": "-",
            "locale": "-",
        }

    headers = getattr(context, "headers", None)
    user_agent = _clean(_header(headers, "User-Agent", "user-agent"))
    try:
        timezone_name = _clean(getattr(context, "timezone", None))
    except Exception:
        timezone_name = "-"
    try:
        locale = _clean(getattr(context, "locale", None))
    except Exception:
        locale = "-"

    return {
        "ip": _clean(_client_ip(context)),
        "system": _parse_system(user_agent),
        "user_agent": user_agent,
        "timezone": timezone_name,
        "locale": locale,
    }


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
    client = client_context()
    safe_detail = _clean(detail, default="")
    line = (
        f"{now.strftime('%Y-%m-%d %H:%M:%S')} UTC | "
        f"action={action} | outcome={outcome} | "
        f"username={username or '-'} | role={role or '-'} | "
        f"ip={client['ip']} | system={client['system']} | "
        f"timezone={client['timezone']} | locale={client['locale']} | "
        f"user_agent={client['user_agent']} | "
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
