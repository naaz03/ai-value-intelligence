from __future__ import annotations

from collections import defaultdict

from config.constants import PERSONAS
from models.schemas import FilterState
from services.metric_service import (
    adoption_by_dimension,
    investment_value_trend,
    portfolio_kpis,
    spend_by_dimension,
    usecase_performance,
)
from services.optimization_service import optimization_summary, recommendations
from utils.formatting import format_currency, format_percent, safe_div


def generate_insights(filters: FilterState, persona: str) -> dict[str, list[str]]:
    k = portfolio_kpis(filters)
    trend = investment_value_trend(filters)
    perf = usecase_performance(filters)
    bu = spend_by_dimension(filters, "business_unit_name")
    opt = optimization_summary(filters)
    adopt_bu = adoption_by_dimension(filters, "business_unit_name")

    findings: list[str] = []
    value_ops: list[str] = []
    opt_ops: list[str] = recommendations(filters)
    attention: list[str] = []
    actions: list[str] = []

    findings.append(
        f"Portfolio realized value is {format_currency(k['realized_value'])} against "
        f"{format_currency(k['total_cost'])} total AI cost, for a net benefit of "
        f"{format_currency(k['net_benefit'])} and ROI of {format_percent(k['portfolio_roi'])}."
    )
    findings.append(
        f"Value conversion is {format_percent(k['pd_conversion'])} potential-to-demonstrated and "
        f"{format_percent(k['dr_conversion'])} demonstrated-to-realized "
        f"(overall realization {format_percent(k['value_realization_pct'])}). "
        "Hours saved are not treated as cash until realization is evidenced."
    )

    if len(trend) >= 6:
        last = trend.tail(3)
        prev = trend.iloc[-6:-3]
        adopt_delta = safe_div(last["adoption_rate"].mean() - prev["adoption_rate"].mean(), prev["adoption_rate"].mean() or 1)
        value_delta = safe_div(last["realized_value"].mean() - prev["realized_value"].mean(), prev["realized_value"].mean() or 1)
        findings.append(
            f"AI adoption changed {format_percent(adopt_delta)} over the last quarter while realized value "
            f"changed {format_percent(value_delta)}"
            + (
                ", suggesting adoption is growing faster than value realization."
                if adopt_delta > value_delta + 0.03
                else "."
            )
        )

    if not bu.empty and bu["total_cost"].sum() > 0:
        top = bu.sort_values("realized_value", ascending=False).iloc[0]
        spend_share = safe_div(top["total_cost"], bu["total_cost"].sum())
        value_share = safe_div(top["realized_value"], bu["realized_value"].sum())
        findings.append(
            f"{top['business_unit_name']} generates {format_percent(value_share)} of realized AI value "
            f"while accounting for {format_percent(spend_share)} of AI expenditure."
        )

    if not perf.empty:
        top5 = perf.head(5)
        share = safe_div(top5["realized_value"].sum(), perf["realized_value"].sum())
        findings.append(
            f"Five AI use cases account for {format_percent(share)} of total realized portfolio value."
        )
        weak = perf[perf["classification"].isin(["Reassess", "Stop"])]
        if not weak.empty:
            attention.append(
                f"{len(weak)} use cases are classified Reassess or Stop, with "
                f"{format_currency(weak['total_cost'].sum())} of associated cost and "
                f"{format_currency(weak['realized_value'].sum())} realized value."
            )

    if opt["annual_savings"] > 0:
        opt_ops.insert(
            0,
            f"Approximately {format_currency(opt['annual_savings'])} of annual license expenditure "
            f"is associated with unused, abandoned, or inactive licenses "
            f"({opt['unused'] + opt['underutilized']:,} licenses).",
        )

    if not adopt_bu.empty:
        low = adopt_bu.sort_values("adoption_rate").head(1)
        if not low.empty and low.iloc[0]["adoption_rate"] < 0.45:
            row = low.iloc[0]
            attention.append(
                f"{row.iloc[0]} adoption is {format_percent(row['adoption_rate'])} "
                f"across {int(row['licensed']):,} licensed employees."
            )

    leak = k["demonstrated_value"] - k["realized_value"]
    if leak > 0:
        value_ops.append(
            f"{format_currency(leak)} of demonstrated benefit has not been financially realized. "
            "Prioritize process redesign, demand backfill, or finance validation — do not book hours saved as cash."
        )
    if k["unvalidated_value"] > 0:
        value_ops.append(
            f"{format_currency(k['unvalidated_value'])} of realized value is not yet finance-validated."
        )

    if not bu.empty:
        bu = bu.copy()
        bu["roi"] = (bu["realized_value"] - bu["total_cost"]) / bu["total_cost"].replace(0, pd_nan())
        efficient = bu.sort_values("roi", ascending=False).iloc[0]
        if efficient["total_cost"] > 0:
            value_ops.append(
                f"{efficient['business_unit_name']} shows the strongest spend productivity in the filter "
                f"(realized {format_currency(efficient['realized_value'])} on "
                f"{format_currency(efficient['total_cost'])} cost)."
            )

    if k["underutilized_licenses"] > 0:
        actions.append(
            "Reassign or reclaim inactive licenses before purchasing additional seats."
        )
    if k["underperforming"] > 0:
        actions.append(
            "Run stage-gate reviews on Reassess/Stop use cases and halt further scale-up until evidence improves."
        )
    if k["dr_conversion"] < 0.45:
        actions.append(
            "Stand up a realization workstream (capacity redeployment, avoided spend capture, finance sign-off) "
            "so demonstrated productivity converts to realized value."
        )
    if k["high_performing"] > 0:
        actions.append(
            f"Prepare scale cases for {k['high_performing']} high-performing use cases with confirmed owners and benefits."
        )
    actions.append(
        "Keep Potential, Demonstrated, and Realized values distinct in investment committee materials."
    )

    buckets = {
        "key_findings": findings,
        "value_opportunities": value_ops,
        "optimization_opportunities": opt_ops,
        "management_attention": attention,
        "recommended_actions": actions,
    }
    order = PERSONAS.get(persona, PERSONAS["CEO / Executive Committee"])["insight_order"]
    return {key: buckets[key] for key in order if buckets[key]}


def pd_nan():
    import numpy as np

    return np.nan


def flatten_insights(grouped: dict[str, list[str]]) -> list[dict[str, str]]:
    rows = []
    labels = {
        "key_findings": "Key findings",
        "value_opportunities": "Value opportunities",
        "optimization_opportunities": "Optimization opportunities",
        "management_attention": "Management attention",
        "recommended_actions": "Recommended actions",
    }
    for key, items in grouped.items():
        for item in items:
            rows.append({"section": labels.get(key, key), "finding": item})
    return rows
