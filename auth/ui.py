"""Native Streamlit login, signup, and password-change screens."""

from __future__ import annotations

from typing import Any

import streamlit as st

from auth.audit import write_audit
from auth.session import begin_session, clear_session, current_user, is_admin
from auth.users import get_user_store
from config.settings import SETTINGS
from config.theme import apply_theme


def navigation_pages() -> list:
    """Return the pages the current visitor is allowed to open."""
    get_user_store().ensure_ready()
    user = current_user()
    if user is None:
        return [st.Page(_render_login_page, title="Sign in", default=True)]
    if user.get("must_change_password"):
        return [st.Page(_render_forced_password_page, title="Change password", default=True)]

    pages = [
        st.Page("pages/01_executive_overview.py", title="Executive Overview", default=True),
        st.Page("pages/02_ai_investment.py", title="AI Investment"),
        st.Page("pages/03_adoption_intelligence.py", title="Adoption Intelligence"),
        st.Page("pages/04_use_case_portfolio.py", title="Use Case Portfolio"),
        st.Page("pages/05_productivity.py", title="Productivity Intelligence"),
        st.Page("pages/06_value_realization.py", title="Value Realization"),
        st.Page("pages/07_roi_intelligence.py", title="ROI Intelligence"),
        st.Page("pages/13_ai_roi_methodology.py", title="AI ROI Methodology"),
        st.Page("pages/08_license_optimization.py", title="License Optimization"),
        st.Page("pages/09_department_benchmarking.py", title="Department Benchmarking"),
        st.Page("pages/10_forecasting.py", title="Forecasting"),
        st.Page("pages/11_ai_value_simulator.py", title="AI Value Simulator"),
        st.Page("pages/12_data_explorer.py", title="Data Explorer"),
        st.Page("pages/14_knowledge.py", title="Knowledge"),
        st.Page("pages/15_account.py", title="Account"),
    ]
    if is_admin(user):
        pages.append(st.Page("pages/16_admin_console.py", title="Admin Console"))
    return pages


def render_sidebar_identity() -> None:
    user = current_user()
    if user is None:
        return
    st.markdown(
        f'<div class="avi-user-name">{user["display_name"]}</div>'
        f'<div class="avi-user-meta">{user["username"]} · {user["role"]}</div>',
        unsafe_allow_html=True,
    )
    if st.button("Sign out", width="stretch"):
        write_audit("LOGOUT", username=user["username"], role=user["role"], detail="Signed out")
        clear_session()
        st.rerun()


def render_password_form(user: dict[str, Any], *, forced: bool = False) -> None:
    store = get_user_store()
    title = "Set a new password" if forced else "Change password"
    st.subheader(title)
    if forced:
        st.warning("Your first-time password matches the username. Replace it before continuing.")
    with st.form("change_password_form", clear_on_submit=True):
        current = st.text_input("Current password", type="password")
        new_password = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Update password")
    if not submitted:
        return
    error = store.change_password(user["username"], current, new_password, confirm)
    if error:
        write_audit(
            "PASSWORD_CHANGE",
            username=user["username"],
            role=user["role"],
            detail=error,
            outcome="denied",
        )
        st.error(error)
        return
    write_audit("PASSWORD_CHANGE", username=user["username"], role=user["role"], detail="Password updated")
    st.success("Password updated.")
    if forced:
        st.rerun()


def log_page_view(page_title: str) -> None:
    user = current_user()
    if user is None:
        return
    last = st.session_state.get("_audit_last_page")
    if last == page_title:
        return
    st.session_state._audit_last_page = page_title
    write_audit("PAGE_VIEW", username=user["username"], role=user["role"], detail=page_title)


def _setup_auth_screen(title: str) -> None:
    st.set_page_config(page_title=f"{title} · {SETTINGS.app_name}", layout="centered", initial_sidebar_state="collapsed")
    apply_theme()
    with st.sidebar:
        st.markdown(f'<div class="avi-brand">{SETTINGS.app_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="avi-subtitle">{SETTINGS.app_subtitle}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="avi-org">{SETTINGS.organization_name}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="avi-developer">Developed by {SETTINGS.developer_name} · {SETTINGS.developer_username}</div>',
            unsafe_allow_html=True,
        )


def _render_login_page() -> None:
    _setup_auth_screen("Sign in")
    st.title("Sign in")
    st.caption("Sign-up for first time use.")

    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])
    store = get_user_store()
    store.ensure_ready()

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")
        if submitted:
            user, error = store.authenticate(username, password)
            if error or user is None:
                write_audit("LOGIN_FAILURE", username=username.strip().lower(), detail=error or "Rejected", outcome="denied")
                st.error(error or "Invalid username or password.")
            else:
                begin_session(user)
                write_audit("LOGIN_SUCCESS", username=user["username"], role=user["role"], detail="Signed in")
                st.rerun()

    with signup_tab:
        with st.form("signup_form"):
            display_name = st.text_input("Full name")
            username = st.text_input("Username", help="3–32 characters. Letters, numbers, dot, underscore, or hyphen.")
            password = st.text_input("Password", type="password", help="At least 8 characters. Stored as a PBKDF2 hash.")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account")
        if submitted:
            user, error = store.signup(username, password, confirm, display_name)
            if error or user is None:
                write_audit("SIGNUP", username=username.strip().lower(), role="user", detail=error or "Rejected", outcome="denied")
                st.error(error)
            else:
                begin_session(user)
                write_audit("SIGNUP", username=user["username"], role=user["role"], detail="New tester registered")
                write_audit("LOGIN_SUCCESS", username=user["username"], role=user["role"], detail="Signed in after signup")
                st.rerun()


def _render_forced_password_page() -> None:
    _setup_auth_screen("Change password")
    user = current_user()
    if user is None:
        clear_session()
        st.rerun()
        return
    st.title("Change your password")
    st.caption(f"Signed in as {user['username']} ({user['role']}).")
    render_password_form(user, forced=True)
    if st.button("Sign out"):
        write_audit("LOGOUT", username=user["username"], role=user["role"], detail="Signed out from password prompt")
        clear_session()
        st.rerun()
