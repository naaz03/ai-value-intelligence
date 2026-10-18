from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auth.session import current_user
from auth.ui import log_page_view, render_sidebar_identity
from config.settings import SETTINGS
from config.theme import apply_theme
from components.filters import render_sidebar_filters
from services.data_service import ensure_data


def bootstrap_page(page_title: str, show_filters: bool = True) -> None:
    st.set_page_config(
        page_title=f"{page_title} · {SETTINGS.app_name}",
        layout="wide",
        initial_sidebar_state="auto",
    )
    apply_theme()
    if current_user() is None:
        st.error("Sign in is required to use this application.")
        st.stop()
    ensure_data()
    with st.sidebar:
        st.markdown(f'<div class="avi-brand">{SETTINGS.app_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="avi-subtitle">{SETTINGS.app_subtitle}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="avi-org">{SETTINGS.organization_name}</div>', unsafe_allow_html=True)
        render_sidebar_identity()
        st.divider()
        if show_filters:
            render_sidebar_filters()
    log_page_view(page_title)
    st.title(page_title)


def page_note(text: str) -> None:
    st.markdown(f'<p class="section-note">{text}</p>', unsafe_allow_html=True)
