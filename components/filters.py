from __future__ import annotations

from datetime import date

import streamlit as st

from config.constants import PERSONAS
from models.schemas import FilterState
from services.data_service import filter_options


def render_sidebar_filters() -> FilterState:
    options = filter_options()
    persona = st.selectbox(
        "Persona",
        list(PERSONAS.keys()),
        index=0,
        help="Changes KPI emphasis and insight order. Data and calculations stay the same.",
    )
    st.caption(PERSONAS[persona]["description"])
    st.session_state["persona"] = persona

    date_range = st.date_input(
        "Date range",
        value=(options["min_date"], options["max_date"]),
        min_value=options["min_date"],
        max_value=options["max_date"],
    )
    if isinstance(date_range, date):
        start, end = date_range, date_range
    else:
        start, end = date_range[0], date_range[-1]

    with st.expander("Organization", expanded=False):
        business_units = st.multiselect("Business unit", options["business_units"])
        departments = st.multiselect("Department", options["departments"])
        countries = st.multiselect("Country", options["countries"])
        job_levels = st.multiselect("Job level", options["job_levels"])
    with st.expander("AI portfolio", expanded=False):
        products = st.multiselect("AI product", options["products"])
        vendors = st.multiselect("Vendor", options["vendors"])
        use_cases = st.multiselect("Use case", options["use_cases"])
        statuses = st.multiselect("Use case status", options["statuses"])
        risk_ratings = st.multiselect("Risk rating", options["risk_ratings"])

    filters = FilterState(
        start_date=start,
        end_date=end,
        business_units=business_units,
        departments=departments,
        countries=countries,
        products=products,
        vendors=vendors,
        use_cases=use_cases,
        statuses=statuses,
        risk_ratings=risk_ratings,
        job_levels=job_levels,
    )
    st.session_state["filters"] = filters
    return filters


def current_filters() -> FilterState:
    if "filters" in st.session_state:
        return st.session_state["filters"]
    options = filter_options()
    return FilterState(start_date=options["min_date"], end_date=options["max_date"])


def current_persona() -> str:
    return st.session_state.get("persona", "CEO / Executive Committee")
