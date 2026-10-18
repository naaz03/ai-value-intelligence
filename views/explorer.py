from __future__ import annotations

import pandas as pd
import streamlit as st

from components.filters import current_filters
from components.layout import page_note
from components.tables import download_csv, styled_table
from generators.quality import run_quality_checks
from services.data_service import apply_filters, cached_tables, sample_usage_rows
from services.metric_service import usecase_mart


PRESETS = {
    "Use case monthly mart": ("mart_month_usecase", "month"),
    "Department monthly mart": ("mart_month_department", "month"),
    "Business unit monthly mart": ("mart_month_bu", "month"),
    "Product monthly mart": ("mart_month_product", "month"),
    "License snapshot": ("mart_license_status", None),
    "Benefit register": ("financial_benefits", "month"),
    "Cost register": ("ai_costs", "month"),
    "Use case master": ("ai_use_cases", None),
    "Employees (sample)": ("employees", None),
}


def render() -> None:
    filters = current_filters()
    page_note("Inspect the analytical tables that power every page. Employee-level usage is queried in samples to stay fast.")
    choice = st.selectbox("Table", list(PRESETS))
    name, date_col = PRESETS[choice]
    frame = cached_tables()[name]
    if date_col:
        frame = apply_filters(frame, filters, date_col)
    else:
        mapping = {
            "business_unit_name": filters.business_units,
            "department_name": filters.departments,
            "country": filters.countries,
            "product_name": filters.products,
            "vendor": filters.vendors,
            "job_level": filters.job_levels,
            "status": filters.statuses,
            "risk_rating": filters.risk_ratings,
        }
        for column, selected in mapping.items():
            if selected and column in frame.columns:
                frame = frame[frame[column].isin(selected)]
        if name == "ai_use_cases" and filters.use_cases:
            frame = frame[frame["use_case_name"].isin(filters.use_cases)]
        if name == "ai_use_cases" and filters.business_units and "business_unit" in frame.columns:
            frame = frame[frame["business_unit"].isin(filters.business_units)]

    st.caption(f"{len(frame):,} rows after filters")
    styled_table(frame.head(500), height=480)
    download_csv(frame, f"{name}.csv")

    if st.checkbox("Sample employee-level usage"):
        sample = sample_usage_rows(400)
        styled_table(sample)
        download_csv(sample, "usage_sample.csv")

    st.subheader("Data quality")
    tables = {k: cached_tables()[k] for k in [
        "organizations",
        "business_units",
        "departments",
        "employees",
        "ai_products",
        "licenses",
        "ai_usage",
        "ai_use_cases",
        "financial_benefits",
        "ai_costs",
    ] if k in cached_tables()}
    # usage may be large; quality on full parquet
    from services.data_service import read_table

    tables["ai_usage"] = read_table("ai_usage")
    results = run_quality_checks(tables)
    result_df = pd.DataFrame([{"check": r.name, "passed": r.passed, "detail": r.detail} for r in results])
    styled_table(result_df, height=360)
    if all(r.passed for r in results):
        st.success("All core integrity checks passed.")
    else:
        st.error("One or more integrity checks failed.")

    st.subheader("KPI reconciliation preview")
    uc = usecase_mart(filters)
    if not uc.empty:
        st.write(
            {
                "potential": float(uc["potential_value"].sum()),
                "demonstrated": float(uc["demonstrated_value"].sum()),
                "realized": float(uc["realized_value"].sum()),
                "cost": float(uc["total_cost"].sum()),
            }
        )
