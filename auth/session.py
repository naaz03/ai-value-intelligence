"""Streamlit session helpers for the signed-in tester."""

from __future__ import annotations

from typing import Any

import streamlit as st

from auth.users import ROLE_ADMIN, get_user_store, public_user

SESSION_KEY = "avi_auth"


def current_user() -> dict[str, Any] | None:
    payload = st.session_state.get(SESSION_KEY)
    if not isinstance(payload, dict) or not payload.get("username"):
        return None
    store = get_user_store()
    record = store.get(str(payload["username"]))
    if record is None or not record.get("is_active", True):
        clear_session()
        return None
    return public_user(record)


def is_authenticated() -> bool:
    return current_user() is not None


def is_admin(user: dict[str, Any] | None = None) -> bool:
    person = user if user is not None else current_user()
    return bool(person and person.get("role") == ROLE_ADMIN)


def begin_session(user: dict[str, Any]) -> None:
    st.session_state[SESSION_KEY] = {
        "username": user["username"],
        "role": user["role"],
        "display_name": user.get("display_name") or user["username"],
    }
    st.session_state.pop("_audit_last_page", None)


def clear_session() -> None:
    st.session_state.pop(SESSION_KEY, None)
    st.session_state.pop("_audit_last_page", None)
