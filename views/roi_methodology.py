from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import bar_rank
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.roi_service import methodology_kpis
from utils.formatting import format_currency, format_percent


def render() -> None:
    filters = current_filters()
    m = methodology_kpis(filters)
    page_note(
        "A single ROI percentage is not enough to govern AI spend. This page shows how headline cash ROI "
        "is calculated, then the KPI pack that should sit beside it in an investment committee pack."
    )

    st.subheader("How headline ROI is calculated")
    st.markdown(
        """
The platform books **only realized financial benefit** in the ROI formula. Potential value and
demonstrated (operational) value are shown for integrity, but they are not treated as cash.
        """
    )
    st.code(
        "Total AI Cost = License + Infrastructure + Implementation + Training\n"
        "              + Support + Security + Governance\n\n"
        "Cash ROI      = (Realized Value − Total AI Cost) / Total AI Cost\n"
        "Net benefit   = Realized Value − Total AI Cost\n"
        "BCR           = Realized Value / Total AI Cost\n"
        "Payback (mo)  = Total AI Cost / Average monthly realized value",
        language="text",
    )
    kpi_grid(
        [
            {"label": "Realized value", "value": m["realized_value"], "kind": "currency", "help": "Numerator input — captured benefit only"},
            {"label": "Total AI cost", "value": m["total_cost"], "kind": "currency", "help": "Full cost stack, not licenses alone"},
            {"label": "Cash ROI", "value": m["cash_roi"], "kind": "percent", "help": "(Realized − Cost) / Cost"},
            {"label": "Net benefit", "value": m["net_benefit"], "kind": "currency"},
            {"label": "Benefit-cost ratio", "value": m["benefit_cost_ratio"], "kind": "number", "decimals": 2},
            {"label": "Payback", "value": m["payback_months"], "kind": "months"},
        ],
        columns=3,
    )

    st.subheader("Do not use these as booked ROI")
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"""
- **Planning ROI** {format_percent(m['planning_roi'])} uses Potential value. That is the business-case number, not a residual.
- **Evidence ROI** {format_percent(m['evidence_roi'])} uses Demonstrated value. It supports the operational case before cash is captured.
- **Hours × wage** {format_currency(m['gross_productivity_value'])} is illustrative capacity, not a P&L line.
            """
        )
    with right:
        compare = pd.DataFrame(
            [
                {"ROI view": "Planning ROI (Potential)", "value": m["planning_roi"], "bookable": "No"},
                {"ROI view": "Evidence ROI (Demonstrated)", "value": m["evidence_roi"], "bookable": "No"},
                {"ROI view": "Cash ROI (Realized)", "value": m["cash_roi"], "bookable": "Yes — headline"},
            ]
        )
        chart = compare.copy()
        chart["ROI %"] = chart["value"]
        st.plotly_chart(bar_rank(chart, "ROI view", "ROI %", "Three ROI views — only cash ROI is bookable"), width="stretch")

    st.subheader("Recommended AI ROI KPI pack")
    st.caption("Use this set together. Cash ROI without conversion, utilization, and capture rates can be gamed by inflating potential or ignoring idle licenses.")

    tabs = st.tabs(
        [
            "Integrity and leakage",
            "Unit economics",
            "Productivity capture",
            "License drag",
            "Definitions",
        ]
    )

    with tabs[0]:
        kpi_grid(
            [
                {"label": "Evidence conversion", "value": m["evidence_conversion"], "kind": "percent", "help": "Demonstrated / Potential"},
                {"label": "Cash conversion", "value": m["cash_conversion"], "kind": "percent", "help": "Realized / Demonstrated"},
                {"label": "Realization rate", "value": m["realization_rate"], "kind": "percent", "help": "Realized / Potential"},
                {"label": "Finance validation rate", "value": m["finance_validation_rate"], "kind": "percent", "help": "Finance-validated / Realized"},
            ]
        )
        st.markdown(
            f"Of {format_currency(m['potential_value'])} potential, "
            f"{format_currency(m['demonstrated_value'])} is evidenced and "
            f"{format_currency(m['realized_value'])} is realized. "
            "A healthy program raises cash conversion without quietly redefining potential."
        )

    with tabs[1]:
        kpi_grid(
            [
                {"label": "Value yield", "value": m["value_yield"], "kind": "number", "decimals": 2, "help": "Realized / $1 total spend"},
                {"label": "License-only ROI", "value": m["license_only_roi"], "kind": "percent", "help": "(Realized − License cost) / License cost — incomplete, for vendor talks only"},
                {"label": "Realized / active user", "value": m["realized_per_active_user"], "kind": "currency"},
                {"label": "Realized / licensed user", "value": m["realized_per_licensed_user"], "kind": "currency", "help": "Falls when seats sit idle"},
                {"label": "License dilution", "value": m["license_dilution"], "kind": "percent", "help": "1 − Active / Licensed"},
                {"label": "Cost / active user", "value": m["cost_per_active_user"], "kind": "currency"},
            ]
        )
        st.markdown(
            "Report **realized per active user** and **realized per licensed user** as a pair. "
            "The gap is unused-seat dilution, not a productivity failure."
        )

    with tabs[2]:
        kpi_grid(
            [
                {"label": "Hours saved", "value": m["hours_saved"], "kind": "hours", "help": "Operational capacity"},
                {"label": "FTE capacity", "value": m["fte_capacity"], "kind": "number", "decimals": 1, "help": f"Hours / {m['working_hours_per_year']:,.0f} working hours"},
                {"label": "Gross productivity value", "value": m["gross_productivity_value"], "kind": "currency", "help": f"Hours × ${m['avg_hourly_cost']:.0f} average hourly cost — not booked"},
                {"label": "Productivity capture rate", "value": m["productivity_capture_rate"], "kind": "percent", "help": "Realized / (Hours × wage)"},
                {"label": "Cost / hour saved", "value": m["cost_per_hour_saved"], "kind": "currency"},
            ]
        )
        st.markdown(
            "Productivity capture answers: of the time we freed, how much became an economic outcome "
            "(avoided spend, released capacity that was redeployed, or finance-recognized benefit)?"
        )

    with tabs[3]:
        kpi_grid(
            [
                {"label": "Idle license drag", "value": m["idle_license_drag"], "kind": "percent", "help": "Idle seat cost in period / Total AI cost"},
                {"label": "Optimized cost", "value": m["optimized_cost"], "kind": "currency", "help": "Total cost minus idle licenses in the period"},
                {"label": "Reclaimed-seat ROI", "value": m["reclaimed_seat_roi"], "kind": "percent", "help": "Cash ROI if idle seats are removed and realized value holds"},
                {"label": "ROI uplift if reclaimed", "value": m["roi_uplift_if_reclaimed"], "kind": "percent", "help": "Reclaimed-seat ROI − current cash ROI"},
            ]
        )
        st.markdown(
            "Before buying more licenses, compute **reclaimed-seat ROI**. If reclaiming idle seats lifts ROI, "
            "the next dollar should go to utilization, not additional seats."
        )

    with tabs[4]:
        styled_table(_definition_table(), height=560)
        download_csv(_definition_table(), "ai_roi_kpi_definitions.csv", "Export KPI definitions")

    st.subheader("Worked numbers in the current filter")
    pack = _kpi_pack_frame(m)
    styled_table(pack, height=420)
    download_csv(pack, "ai_roi_kpi_pack.csv", "Export KPI pack")

    st.subheader("How an investment committee should use these KPIs")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "**Approve or continue** when cash ROI and BCR are acceptable, "
            "finance validation is rising, and idle-license drag is contained."
        )
    with c2:
        st.markdown(
            "**Optimize** when evidence ROI is strong but cash conversion or productivity capture is weak. "
            "Fix realization, not more adoption spend."
        )
    with c3:
        st.markdown(
            "**Do not scale seats** when license dilution is high or reclaimed-seat ROI is materially above cash ROI. "
            "Reassign first."
        )


def _kpi_pack_frame(m: dict) -> pd.DataFrame:
    rows = [
        ("Cash ROI", m["cash_roi"], "percent", "Headline bookable ROI"),
        ("Evidence ROI", m["evidence_roi"], "percent", "Operational case only"),
        ("Planning ROI", m["planning_roi"], "percent", "Business case only"),
        ("Net benefit", m["net_benefit"], "currency", "Realized − cost"),
        ("Benefit-cost ratio", m["benefit_cost_ratio"], "number", "Realized / cost"),
        ("Payback (months)", m["payback_months"], "months", "Cost / monthly realized"),
        ("Evidence conversion", m["evidence_conversion"], "percent", "Demonstrated / potential"),
        ("Cash conversion", m["cash_conversion"], "percent", "Realized / demonstrated"),
        ("Realization rate", m["realization_rate"], "percent", "Realized / potential"),
        ("Finance validation rate", m["finance_validation_rate"], "percent", "Validated / realized"),
        ("Value yield", m["value_yield"], "number", "Realized per $1 spend"),
        ("License-only ROI", m["license_only_roi"], "percent", "Vendor conversation, not residual"),
        ("Realized / active user", m["realized_per_active_user"], "currency", "Value among users who engage"),
        ("Realized / licensed user", m["realized_per_licensed_user"], "currency", "Includes idle seats"),
        ("License dilution", m["license_dilution"], "percent", "Unused licensed population"),
        ("Productivity capture rate", m["productivity_capture_rate"], "percent", "Realized / hours × wage"),
        ("Idle license drag", m["idle_license_drag"], "percent", "Idle seat cost share"),
        ("Reclaimed-seat ROI", m["reclaimed_seat_roi"], "percent", "ROI after removing idle seats"),
        ("ROI uplift if reclaimed", m["roi_uplift_if_reclaimed"], "percent", "Improvement from hygiene"),
    ]
    out = []
    for name, value, kind, meaning in rows:
        if kind == "percent":
            display = format_percent(value)
        elif kind == "currency":
            display = format_currency(value)
        elif kind == "months":
            display = "—" if value is None else f"{value:.1f}"
        else:
            display = f"{value:,.2f}" if value is not None else "—"
        out.append({"KPI": name, "Result": display, "Meaning": meaning})
    return pd.DataFrame(out)


def _definition_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"KPI": "Cash ROI", "Formula": "(Realized − Total AI Cost) / Total AI Cost", "Use": "Headline residual. Only realized benefit."},
            {"KPI": "Evidence ROI", "Formula": "(Demonstrated − Total AI Cost) / Total AI Cost", "Use": "Operational case. Not bookable."},
            {"KPI": "Planning ROI", "Formula": "(Potential − Total AI Cost) / Total AI Cost", "Use": "Original business case. Not bookable."},
            {"KPI": "Net benefit", "Formula": "Realized − Total AI Cost", "Use": "Absolute value created."},
            {"KPI": "Benefit-cost ratio", "Formula": "Realized / Total AI Cost", "Use": ">1 means benefits exceed cost."},
            {"KPI": "Payback", "Formula": "Total AI Cost / Average monthly realized", "Use": "Time to recover spend."},
            {"KPI": "Evidence conversion", "Formula": "Demonstrated / Potential", "Use": "How much of the case is evidenced."},
            {"KPI": "Cash conversion", "Formula": "Realized / Demonstrated", "Use": "How much evidence became money."},
            {"KPI": "Realization rate", "Formula": "Realized / Potential", "Use": "End-to-end leakage."},
            {"KPI": "Finance validation rate", "Formula": "Finance-validated / Realized", "Use": "Share signed off by Finance."},
            {"KPI": "Value yield", "Formula": "Realized / Total AI Cost", "Use": "Dollars returned per dollar spent."},
            {"KPI": "License-only ROI", "Formula": "(Realized − License cost) / License cost", "Use": "Vendor price talks. Incomplete cost."},
            {"KPI": "Realized / active user", "Formula": "Realized / Active users", "Use": "Yield among people who use AI."},
            {"KPI": "Realized / licensed user", "Formula": "Realized / Licensed users", "Use": "Yield including idle seats."},
            {"KPI": "License dilution", "Formula": "1 − Active / Licensed", "Use": "Seat waste."},
            {"KPI": "Gross productivity value", "Formula": "Hours saved × average hourly cost", "Use": "Capacity illustration. Not cash."},
            {"KPI": "Productivity capture rate", "Formula": "Realized / (Hours × wage)", "Use": "Share of freed time converted to value."},
            {"KPI": "Idle license drag", "Formula": "Idle seat cost in period / Total AI Cost", "Use": "How much cost is non-productive seats."},
            {"KPI": "Reclaimed-seat ROI", "Formula": "(Realized − Optimized cost) / Optimized cost", "Use": "ROI after reclaiming idle licenses."},
            {"KPI": "Total AI Cost", "Formula": "License + Infra + Implementation + Training + Support + Security + Governance", "Use": "Always fully loaded."},
        ]
    )
