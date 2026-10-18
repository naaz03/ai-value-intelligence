"""JSON user store. Passwords are stored only as PBKDF2 hashes."""

from __future__ import annotations

import fcntl
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

from auth.passwords import hash_password, validate_new_password, verify_password
from config.settings import SETTINGS

ROLE_ADMIN = "admin"
ROLE_USER = "user"
VALID_ROLES = {ROLE_ADMIN, ROLE_USER}
USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,31}$")
STORE_VERSION = 1

T = TypeVar("T")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def validate_username(username: str) -> str | None:
    if not USERNAME_RE.match(username):
        return "Username must be 3–32 characters: letters, numbers, dot, underscore, or hyphen."
    return None


def public_user(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "username": record.get("username"),
        "display_name": record.get("display_name") or record.get("username"),
        "role": record.get("role") or ROLE_USER,
        "must_change_password": bool(record.get("must_change_password")),
        "is_active": bool(record.get("is_active", True)),
        "created_at": record.get("created_at"),
        "updated_at": record.get("updated_at"),
        "last_login_at": record.get("last_login_at"),
        "created_by": record.get("created_by"),
    }


class UserStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or SETTINGS.users_path

    def ensure_ready(self) -> dict[str, Any]:
        def op(data: dict[str, Any]) -> dict[str, Any]:
            self._seed_admin(data)
            return data

        return self._locked(op)

    def list_users(self) -> list[dict[str, Any]]:
        users = [public_user(item) for item in self.ensure_ready().get("users", [])]
        return sorted(users, key=lambda item: (item["role"] != ROLE_ADMIN, item["username"] or ""))

    def get(self, username: str) -> dict[str, Any] | None:
        key = normalize_username(username)
        for item in self.ensure_ready().get("users", []):
            if item.get("username") == key:
                return item
        return None

    def authenticate(self, username: str, password: str) -> tuple[dict[str, Any] | None, str | None]:
        record = self.get(username)
        if record is None or not record.get("is_active", True):
            return None, "Invalid username or password."
        if not verify_password(password, record):
            return None, "Invalid username or password."

        def op(data: dict[str, Any]) -> dict[str, Any] | None:
            now = utc_now()
            found = self._find(data, record["username"])
            if found is None:
                return None
            found["last_login_at"] = now
            found["updated_at"] = now
            return found

        updated = self._locked(op)
        if updated is None:
            return None, "Invalid username or password."
        return public_user(updated), None

    def signup(
        self,
        username: str,
        password: str,
        confirm: str,
        display_name: str,
    ) -> tuple[dict[str, Any] | None, str | None]:
        key = normalize_username(username)
        name = (display_name or "").strip() or key
        if error := validate_username(key):
            return None, error
        if error := validate_new_password(password, confirm):
            return None, error

        def op(data: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
            self._seed_admin(data)
            if self._find(data, key) is not None:
                return None, "That username is already registered."
            now = utc_now()
            record = {
                "username": key,
                "display_name": name,
                "role": ROLE_USER,
                "must_change_password": False,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "last_login_at": now,
                "created_by": "signup",
                **hash_password(password),
            }
            data["users"].append(record)
            return record, None

        return self._locked(op)

    def change_password(
        self,
        username: str,
        current_password: str,
        new_password: str,
        confirm: str,
    ) -> str | None:
        record = self.get(username)
        if record is None:
            return "User was not found."
        if not verify_password(current_password, record):
            return "Current password is incorrect."
        if error := validate_new_password(new_password, confirm, username=record["username"]):
            return error
        if verify_password(new_password, record):
            return "New password must be different from the current password."

        def op(data: dict[str, Any]) -> str | None:
            found = self._find(data, record["username"])
            if found is None:
                return "User was not found."
            found.update(hash_password(new_password))
            found["must_change_password"] = False
            found["updated_at"] = utc_now()
            return None

        return self._locked(op)

    def admin_reset_password(self, actor: str, username: str, new_password: str, confirm: str) -> str | None:
        target = normalize_username(username)
        if error := validate_new_password(new_password, confirm, username=target):
            return error

        def op(data: dict[str, Any]) -> str | None:
            found = self._find(data, target)
            if found is None:
                return "User was not found."
            found.update(hash_password(new_password))
            found["must_change_password"] = True
            found["updated_at"] = utc_now()
            found["reset_by"] = actor
            return None

        return self._locked(op)

    def _seed_admin(self, data: dict[str, Any]) -> bool:
        admin_username = normalize_username(SETTINGS.admin_username)
        if self._find(data, admin_username) is not None:
            return False
        now = utc_now()
        data.setdefault("users", []).append(
            {
                "username": admin_username,
                "display_name": SETTINGS.admin_display_name,
                "role": ROLE_ADMIN,
                "must_change_password": True,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "last_login_at": None,
                "created_by": "system",
                **hash_password(admin_username),
            }
        )
        return True

    def _find(self, data: dict[str, Any], username: str) -> dict[str, Any] | None:
        for item in data.get("users", []):
            if item.get("username") == username:
                return item
        return None

    def _empty(self) -> dict[str, Any]:
        return {"version": STORE_VERSION, "users": []}

    def _locked(self, fn: Callable[[dict[str, Any]], T]) -> T:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")
        with self.path.open("r+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            raw = handle.read()
            data = json.loads(raw) if raw.strip() else self._empty()
            data.setdefault("version", STORE_VERSION)
            data.setdefault("users", [])
            result = fn(data)
            handle.seek(0)
            handle.truncate()
            handle.write(json.dumps(data, indent=2) + "\n")
            handle.flush()
            return result


def get_user_store() -> UserStore:
    return UserStore()
