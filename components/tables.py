from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.formatting import format_currency, format_percent


def styled_table(frame: pd.DataFrame, height: int = 420) -> None:
    st.dataframe(frame, width="stretch", height=height, hide_index=True)


def download_csv(frame: pd.DataFrame, filename: str, label: str = "Export CSV") -> None:
    if frame is None or frame.empty:
        return
    st.download_button(
        label,
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def format_money_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].apply(lambda v: format_currency(v) if pd.notna(v) else "—")
    return out


def format_pct_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].apply(lambda v: format_percent(v) if pd.notna(v) else "—")
    return out
