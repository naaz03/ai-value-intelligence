from __future__ import annotations

import pandas as pd
import streamlit as st

from components.layout import page_note
from components.tables import download_csv, styled_table
from config.knowledge_catalog import CATEGORIES, KNOWLEDGE


def render() -> None:
    page_note(
        "Search the metric dictionary. Every KPI on the dashboards is defined here — "
        "including what is bookable and what is only illustrative."
    )

    query = st.text_input(
        "Search metrics and formulas",
        placeholder="Try realized, payback, adoption, hours, reclaimed, FTE…",
        key="knowledge_search",
    )
    selected = st.multiselect("Category", list(CATEGORIES), default=[], key="knowledge_cats")

    matches = _search(query, selected)
    st.caption(f"{len(matches)} of {len(KNOWLEDGE)} topics")

    if not matches:
        st.info("No matching topics. Clear the search or choose another category.")
        return

    by_cat: dict[str, list[dict]] = {}
    for item in matches:
        by_cat.setdefault(item["category"], []).append(item)

    for category in CATEGORIES:
        items = by_cat.get(category)
        if not items:
            continue
        st.subheader(category)
        for item in items:
            with st.expander(item["title"], expanded=bool(query.strip()) and len(matches) <= 6):
                st.markdown(f"**{item['meaning']}**")
                st.code(item["formula"], language="text")
                if item.get("notes"):
                    st.caption(item["notes"])

    export = pd.DataFrame(matches)[["category", "title", "formula", "meaning", "notes"]]
    download_csv(export, "knowledge_metrics.csv", "Export visible topics")
    with st.expander("Table view"):
        styled_table(export, height=420)


def _search(query: str, categories: list[str]) -> list[dict]:
    rows = KNOWLEDGE
    if categories:
        rows = [row for row in rows if row["category"] in categories]
    needle = query.strip().lower()
    if not needle:
        return rows
    tokens = [part for part in needle.replace(",", " ").split() if part]
    out = []
    for row in rows:
        hay = " ".join(
            [
                row["title"],
                row["category"],
                row.get("keywords", ""),
                row["formula"],
                row["meaning"],
                row.get("notes", ""),
            ]
        ).lower()
        if all(token in hay for token in tokens):
            out.append(row)
    return out
