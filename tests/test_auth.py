from __future__ import annotations

import json
from datetime import datetime, timezone

from auth.audit import daily_log_path, list_audit_dates, read_audit_log, write_audit
from auth.passwords import hash_password, validate_new_password, verify_password
from auth.users import ROLE_ADMIN, ROLE_USER, UserStore
from config.settings import SETTINGS


def test_password_is_hashed_not_reversible():
    secret = "tester-pass-123"
    record = hash_password(secret)
    assert record["password_hash"] != secret
    assert record["password_salt"] != secret
    assert secret not in json.dumps(record)
    assert verify_password(secret, record)
    assert not verify_password("wrong-pass-123", record)


def test_password_rules():
    assert validate_new_password("short", "short") is not None
    assert validate_new_password("long-enough", "different") is not None
    assert validate_new_password("naaz.afrin", "naaz.afrin", username="naaz.afrin") is not None
    assert validate_new_password("long-enough", "long-enough") is None


def test_admin_seeded_with_username_password(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "users_path", tmp_path / "users.json")
    store = UserStore()
    store.ensure_ready()
    raw = json.loads((tmp_path / "users.json").read_text(encoding="utf-8"))
    payload = json.dumps(raw)
    assert '"password":' not in payload
    assert SETTINGS.admin_username not in [user.get("password_hash") for user in raw["users"]]
    admin = store.get(SETTINGS.admin_username)
    assert admin is not None
    assert admin["role"] == ROLE_ADMIN
    assert admin["must_change_password"] is True
    assert verify_password(SETTINGS.admin_username, admin)
    user, error = store.authenticate(SETTINGS.admin_username, SETTINGS.admin_username)
    assert error is None
    assert user is not None
    assert user["role"] == ROLE_ADMIN


def test_signup_assigns_user_role_only(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "users_path", tmp_path / "users.json")
    store = UserStore()
    created, error = store.signup("tester.one", "secret-pass", "secret-pass", "Tester One")
    assert error is None
    assert created is not None
    assert created["role"] == ROLE_USER
    raw = (tmp_path / "users.json").read_text(encoding="utf-8")
    assert "secret-pass" not in raw
    duplicate, dup_error = store.signup("tester.one", "secret-pass", "secret-pass", "Tester One")
    assert duplicate is None
    assert dup_error is not None


def test_user_and_admin_can_change_password(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "users_path", tmp_path / "users.json")
    store = UserStore()
    store.signup("tester.two", "old-password", "old-password", "Tester Two")
    assert store.change_password("tester.two", "old-password", "new-password", "new-password") is None
    user, error = store.authenticate("tester.two", "new-password")
    assert error is None and user is not None
    assert store.authenticate("tester.two", "old-password")[0] is None

    assert store.change_password(SETTINGS.admin_username, SETTINGS.admin_username, "admin-new-1", "admin-new-1") is None
    admin, admin_error = store.authenticate(SETTINGS.admin_username, "admin-new-1")
    assert admin_error is None and admin is not None
    assert admin["must_change_password"] is False


def test_admin_can_reset_tester_password(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "users_path", tmp_path / "users.json")
    store = UserStore()
    store.signup("tester.three", "old-password", "old-password", "Tester Three")
    assert store.admin_reset_password(SETTINGS.admin_username, "tester.three", "reset-pass-1", "reset-pass-1") is None
    user, error = store.authenticate("tester.three", "reset-pass-1")
    assert error is None and user is not None
    assert store.get("tester.three")["must_change_password"] is True


def test_daily_audit_file(tmp_path, monkeypatch):
    monkeypatch.setattr(SETTINGS, "audit_dir", tmp_path / "user_login_audit")
    path = write_audit("LOGIN_SUCCESS", username="tester.one", role="user", detail="Signed in")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assert path.name == f"{today}.log"
    assert path.parent.name == "user_login_audit"
    assert daily_log_path().name == f"{today}.log"
    text = read_audit_log(today)
    assert "LOGIN_SUCCESS" in text
    assert "tester.one" in text
    assert "ip=" in text
    assert "system=" in text
    assert "timezone=" in text
    assert "locale=" in text
    assert "user_agent=" in text
    assert "secret" not in text
    assert today in list_audit_dates()


def test_system_parser_from_user_agent():
    from auth.audit import _parse_system

    assert "macOS" in _parse_system(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
    assert "Mobile" in _parse_system(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1"
    )
