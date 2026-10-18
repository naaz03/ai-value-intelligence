from __future__ import annotations

import streamlit as st

from auth.audit import list_audit_dates, read_audit_log, write_audit
from auth.session import current_user, is_admin
from auth.users import ROLE_ADMIN, get_user_store
from components.layout import page_note


def render() -> None:
    actor = current_user()
    if actor is None or not is_admin(actor):
        if actor:
            write_audit(
                "ACCESS_DENIED",
                username=actor["username"],
                role=actor["role"],
                detail="Admin Console",
                outcome="denied",
            )
        st.error("Admin access is required.")
        st.stop()

    page_note(
        "Review tester accounts and daily login audit files. New signups always receive the user role. "
        "Passwords are never stored or displayed. Audit lines include IP, system/browser, timezone, and locale when available."
    )
    store = get_user_store()
    users = store.list_users()

    users_tab, audit_tab = st.tabs(["Users", "Login audit"])
    with users_tab:
        st.subheader("Registered testers")
        st.dataframe(
            [
                {
                    "Username": item["username"],
                    "Name": item["display_name"],
                    "Role": item["role"],
                    "Must change password": item["must_change_password"],
                    "Last login": item.get("last_login_at") or "—",
                    "Created": item.get("created_at") or "—",
                }
                for item in users
            ],
            hide_index=True,
            width="stretch",
        )
        st.subheader("Reset a password")
        reset_targets = [item["username"] for item in users]
        if not reset_targets:
            st.info("No users are registered yet.")
        else:
            _render_password_reset(actor, store, reset_targets)

    with audit_tab:
        st.subheader("Daily login audit")
        dates = list_audit_dates()
        if not dates:
            st.info("No audit files have been written yet.")
            return
        day = st.selectbox("Log date (UTC)", dates)
        content = read_audit_log(day)
        st.code(content or "No entries for this date.", language="text")
        st.download_button(
            "Download this day's log",
            data=content,
            file_name=f"{day}.log",
            mime="text/plain",
        )


def _render_password_reset(actor: dict, store, reset_targets: list[str]) -> None:
    with st.form("admin_reset_password"):
        target = st.selectbox("User", reset_targets)
        new_password = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Reset password")
    if not submitted:
        return
    error = store.admin_reset_password(actor["username"], target, new_password, confirm)
    if error:
        write_audit(
            "ADMIN_PASSWORD_RESET",
            username=actor["username"],
            role=ROLE_ADMIN,
            detail=f"{target}: {error}",
            outcome="denied",
        )
        st.error(error)
        return
    write_audit(
        "ADMIN_PASSWORD_RESET",
        username=actor["username"],
        role=ROLE_ADMIN,
        detail=f"Reset password for {target}",
    )
    st.success(f"Password reset for `{target}`. They must change it on next sign-in.")
