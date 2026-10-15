from __future__ import annotations

import pandas as pd

from models.schemas import FilterState
from services.metric_service import license_snapshot
from utils.formatting import format_currency, safe_div


def optimization_summary(filters: FilterState) -> dict[str, float]:
    licenses = license_snapshot(filters)
    if licenses.empty:
        return {
            "current_spend": 0.0,
            "optimized_spend": 0.0,
            "annual_savings": 0.0,
            "optimization_pct": 0.0,
            "unused": 0,
            "underutilized": 0,
            "overlap_users": 0,
        }
    current = float(licenses["annual_cost"].sum())
    unused = licenses[licenses["segment"].isin(["Never Activated", "Abandoned"])]
    under = licenses[licenses["segment"] == "Inactive"]
    reclaim = pd.concat([unused, under], ignore_index=True)
    savings = float(reclaim["annual_cost"].sum())
    overlap_users = int((licenses.groupby("employee_id")["product_id"].nunique() >= 2).sum())
    return {
        "current_spend": current,
        "optimized_spend": max(0.0, current - savings),
        "annual_savings": savings,
        "optimization_pct": safe_div(savings, current),
        "unused": int(len(unused)),
        "underutilized": int(len(under)),
        "overlap_users": overlap_users,
    }


def opportunity_table(filters: FilterState) -> pd.DataFrame:
    licenses = license_snapshot(filters)
    if licenses.empty:
        return pd.DataFrame()
    mask = licenses["segment"].isin(["Never Activated", "Abandoned", "Inactive"]) | (licenses["product_count"] >= 2)
    out = licenses.loc[mask].copy()
    out["opportunity_type"] = out.apply(_opportunity_type, axis=1)
    cols = [
        "license_id",
        "employee_id",
        "department_name",
        "business_unit_name",
        "product_name",
        "vendor",
        "segment",
        "days_inactive",
        "recent_sessions",
        "product_count",
        "monthly_cost",
        "annual_cost",
        "opportunity_type",
        "job_level",
        "country",
    ]
    return out[cols].sort_values(["annual_cost", "days_inactive"], ascending=[False, False])


def _opportunity_type(row: pd.Series) -> str:
    if row["segment"] == "Never Activated":
        return "Never activated"
    if row["segment"] == "Abandoned":
        return "Abandoned after experimentation"
    if row["days_inactive"] >= 90:
        return "Inactive 90+ days"
    if row["days_inactive"] >= 60:
        return "Inactive 60+ days"
    if row["days_inactive"] >= 30:
        return "Inactive 30+ days"
    if row["product_count"] >= 2:
        return "Overlapping products"
    return "Underutilized"


def recommendations(filters: FilterState) -> list[str]:
    licenses = license_snapshot(filters)
    recs: list[str] = []
    if licenses.empty:
        return ["No license records in the current filter."]

    for dept, group in licenses.groupby("department_name"):
        stale = group[group["days_inactive"] >= 60]
        if len(stale) >= 8:
            recs.append(
                f"{dept} has {len(stale):,} licenses with no activity for 60+ days, "
                f"representing approximately {format_currency(stale['annual_cost'].sum())} "
                "in annual optimization opportunity."
            )
    overlap = licenses[licenses["product_count"] >= 2]
    if not overlap.empty:
        recs.append(
            f"{overlap['employee_id'].nunique():,} employees hold overlapping AI products "
            f"({overlap['license_id'].nunique():,} licenses), with "
            f"{format_currency(overlap['annual_cost'].sum())} annual spend in the overlap set."
        )
    never = licenses[licenses["segment"] == "Never Activated"]
    if not never.empty:
        top_prod = never.groupby("product_name")["annual_cost"].sum().sort_values(ascending=False)
        name = top_prod.index[0]
        recs.append(
            f"{len(never):,} licenses were never activated. {name} accounts for "
            f"{format_currency(float(top_prod.iloc[0]))} of that unused annual spend."
        )
    legal = licenses[licenses["business_unit_name"] == "Legal"]
    if not legal.empty:
        inactive_share = safe_div(
            len(legal[legal["segment"].isin(["Inactive", "Never Activated", "Abandoned"])]),
            len(legal),
        )
        if inactive_share >= 0.45:
            recs.append(
                f"Legal license inactivity is {inactive_share:.0%}. Reassignment or reduction "
                f"would release {format_currency(legal.loc[legal['segment'].isin(['Inactive','Never Activated','Abandoned']),'annual_cost'].sum())} annually."
            )
    hr = licenses[licenses["business_unit_name"] == "Human Resources"]
    if not hr.empty:
        unused = hr[hr["segment"].isin(["Inactive", "Never Activated", "Abandoned"])]
        if len(unused) >= 10:
            recs.append(
                f"Human Resources has {len(unused):,} inactive or never-activated licenses "
                f"({format_currency(unused['annual_cost'].sum())} annual spend)."
            )
    return recs[:8] or ["License utilization is broadly healthy in the current filter."]
