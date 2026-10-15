from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import SETTINGS
from config.theme import apply_theme
from components.filters import render_sidebar_filters
from services.data_service import ensure_data


def bootstrap_page(page_title: str) -> None:
    st.set_page_config(
        page_title=f"{page_title} · {SETTINGS.app_name}",
        layout="wide",
        initial_sidebar_state="auto",
    )
    apply_theme()
    ensure_data()
    with st.sidebar:
        st.markdown(f'<div class="avi-brand">{SETTINGS.app_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="avi-subtitle">{SETTINGS.app_subtitle}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="avi-org">{SETTINGS.organization_name}</div>', unsafe_allow_html=True)
        st.divider()
        render_sidebar_filters()
        _phone_access()
    st.title(page_title)


def _phone_access() -> None:
    from utils.helpers import lan_url

    url = lan_url()
    with st.expander("Open on a phone"):
        st.caption("Same Wi-Fi as this computer. Tap the menu icon to open pages and filters.")
        st.code(url, language="text")
        st.caption("If it does not load, confirm the app was started with streamlit run app.py and that the Mac firewall allows incoming connections.")


def page_note(text: str) -> None:
    st.markdown(f'<p class="section-note">{text}</p>', unsafe_allow_html=True)
