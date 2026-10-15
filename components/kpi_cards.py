from __future__ import annotations

import streamlit as st

from utils.formatting import format_currency, format_hours, format_months, format_number, format_percent


def kpi_grid(items: list[dict], columns: int = 4) -> None:
    for i in range(0, len(items), columns):
        cols = st.columns(columns)
        for col, item in zip(cols, items[i : i + columns]):
            with col:
                _card(item)


def _card(item: dict) -> None:
    value = item.get("display")
    if value is None:
        raw = item.get("value")
        kind = item.get("kind", "number")
        if kind == "currency":
            value = format_currency(raw)
        elif kind == "percent":
            value = format_percent(raw)
        elif kind == "hours":
            value = format_hours(raw)
        elif kind == "months":
            value = format_months(raw)
        elif kind == "int":
            value = format_number(raw, 0)
        else:
            value = format_number(raw, item.get("decimals", 1))
    help_txt = item.get("help", "")
    delta = item.get("delta", "")
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">{item["label"]}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-delta">{delta}</div>
          <div class="kpi-help">{help_txt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
