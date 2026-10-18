from __future__ import annotations

import streamlit as st

from auth.session import current_user
from auth.ui import render_password_form
from components.layout import page_note


def render() -> None:
    user = current_user()
    if user is None:
        st.error("Sign in to manage your account.")
        st.stop()

    page_note("Update the password used for this tester login. The stored value is a hash, not the password itself.")
    left, right = st.columns(2)
    with left:
        st.markdown(f"**Name:** {user['display_name']}")
        st.markdown(f"**Username:** `{user['username']}`")
        st.markdown(f"**Role:** {user['role']}")
    with right:
        st.markdown(f"**Last login:** {user.get('last_login_at') or '—'}")
        st.markdown(f"**Account created:** {user.get('created_at') or '—'}")

    st.divider()
    render_password_form(user, forced=False)
