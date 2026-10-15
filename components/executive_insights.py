from __future__ import annotations

import streamlit as st

from components.tables import download_csv
from services.insight_service import flatten_insights, generate_insights
from models.schemas import FilterState


def render_insights(filters: FilterState, persona: str) -> None:
    grouped = generate_insights(filters, persona)
    labels = {
        "key_findings": ("Key findings", ""),
        "value_opportunities": ("Value opportunities", ""),
        "optimization_opportunities": ("Optimization opportunities", "insight-attn"),
        "management_attention": ("Management attention", "insight-attn"),
        "recommended_actions": ("Recommended actions", ""),
    }
    tabs = st.tabs([labels[k][0] for k in grouped])
    for tab, key in zip(tabs, grouped):
        with tab:
            css = labels[key][1]
            for item in grouped[key]:
                st.markdown(f'<div class="insight-box {css}">{item}</div>', unsafe_allow_html=True)
    download_csv(pd_frame(grouped), "executive_findings.csv", "Export executive findings")


def pd_frame(grouped: dict[str, list[str]]):
    import pandas as pd

    return pd.DataFrame(flatten_insights(grouped))
