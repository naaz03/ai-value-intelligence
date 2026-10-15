from __future__ import annotations

import pandas as pd

from config.settings import SETTINGS
from models.schemas import FilterState
from services.data_service import apply_filters, cached_tables
from utils.calculations import fte_equivalent
from utils.formatting import safe_div


def usecase_mart(filters: FilterState) -> pd.DataFrame:
    return apply_filters(cached_tables()["mart_month_usecase"], filters, "month")


def department_mart(filters: FilterState) -> pd.DataFrame:
    return apply_filters(cached_tables()["mart_month_department"], filters, "month")


def bu_mart(filters: FilterState) -> pd.DataFrame:
    return apply_filters(cached_tables()["mart_month_bu"], filters, "month")


def product_mart(filters: FilterState) -> pd.DataFrame:
    return apply_filters(cached_tables()["mart_month_product"], filters, "month")


def enterprise_mart(filters: FilterState) -> pd.DataFrame:
    frame = apply_filters(cached_tables()["mart_month_enterprise"], filters, "month")
    if filters.is_unfiltered():
        return frame
    # Rebuild enterprise totals from the filtered use-case mart so KPIs reconcile.
    uc = usecase_mart(filters)
    if uc.empty:
        return frame.iloc[0:0]
    grouped = uc.groupby("month", as_index=False).agg(
        potential_value=("potential_value", "sum"),
        demonstrated_value=("demonstrated_value", "sum"),
        realized_value=("realized_value", "sum"),
        total_cost=("total_cost", "sum"),
        license_cost=("license_cost", "sum"),
        infrastructure_cost=("infrastructure_cost", "sum"),
        hours_saved=("hours_saved", "sum"),
        finance_validated_value=("finance_validated_value", "sum"),
    )
    dept = department_mart(filters)
    if not dept.empty:
        usage = dept.groupby("month", as_index=False).agg(
            active_users=("active_users", "sum"),
            licensed_users=("licensed_users", "sum"),
            sessions=("sessions", "sum"),
            tasks_completed=("tasks_completed", "sum"),
        )
        grouped = grouped.merge(usage, on="month", how="left")
    return grouped.fillna(0)


def license_snapshot(filters: FilterState) -> pd.DataFrame:
    frame = cached_tables()["mart_license_status"]
    mapping = {
        "business_unit_name": filters.business_units,
        "department_name": filters.departments,
        "country": filters.countries,
        "product_name": filters.products,
        "vendor": filters.vendors,
        "job_level": filters.job_levels,
    }
    out = frame
    for column, selected in mapping.items():
        if selected and column in out.columns:
            out = out[out[column].isin(selected)]
    return out.reset_index(drop=True)


def use_case_master(filters: FilterState) -> pd.DataFrame:
    uc = cached_tables()["ai_use_cases"].copy()
    maps = {
        "business_unit": filters.business_units,
        "department": filters.departments,
        "use_case_name": filters.use_cases,
        "status": filters.statuses,
        "risk_rating": filters.risk_ratings,
    }
    products = cached_tables()["ai_products"]
    uc["product_name"] = uc["ai_product"].map(dict(zip(products["product_id"], products["product_name"])))
    uc["vendor"] = uc["ai_product"].map(dict(zip(products["product_id"], products["vendor"])))
    if filters.products:
        uc = uc[uc["product_name"].isin(filters.products)]
    if filters.vendors:
        uc = uc[uc["vendor"].isin(filters.vendors)]
    for column, selected in maps.items():
        if selected and column in uc.columns:
            uc = uc[uc[column].isin(selected)]
    return uc.reset_index(drop=True)


def portfolio_kpis(filters: FilterState) -> dict[str, float]:
    uc = usecase_mart(filters)
    licenses = license_snapshot(filters)
    master = use_case_master(filters)

    potential = float(uc["potential_value"].sum()) if not uc.empty else 0.0
    demonstrated = float(uc["demonstrated_value"].sum()) if not uc.empty else 0.0
    realized = float(uc["realized_value"].sum()) if not uc.empty else 0.0
    cost = float(uc["total_cost"].sum()) if not uc.empty else 0.0
    hours = float(uc["hours_saved"].sum()) if not uc.empty else 0.0
    finance_validated = float(uc["finance_validated_value"].sum()) if not uc.empty else 0.0
    infra = float(uc["infrastructure_cost"].sum()) if not uc.empty else 0.0

    licensed = int(licenses["employee_id"].nunique()) if not licenses.empty else 0
    inactive = licenses[licenses["segment"].isin(["Inactive", "Never Activated", "Abandoned"])] if not licenses.empty else licenses
    underutilized = int(inactive["license_id"].nunique()) if not inactive.empty else 0
    opt_opp = float(inactive["annual_cost"].sum()) if not inactive.empty else 0.0
    active_latest = 0
    if not licenses.empty:
        active_latest = int(
            licenses.loc[
                ~licenses["segment"].isin(["Inactive", "Never Activated", "Abandoned"]),
                "employee_id",
            ].nunique()
        )
    licensed_latest = licensed
    prod = product_mart(filters)

    employees = cached_tables()["employees"]
    if filters.business_units or filters.departments or filters.countries or filters.job_levels:
        emp = employees
        if filters.departments:
            dept = cached_tables()["departments"]
            ids = dept[dept["department_name"].isin(filters.departments)]["department_id"]
            emp = emp[emp["department_id"].isin(ids)]
        if filters.business_units:
            bu = cached_tables()["business_units"]
            ids = bu[bu["business_unit_name"].isin(filters.business_units)]["business_unit_id"]
            emp = emp[emp["business_unit_id"].isin(ids)]
        if filters.countries:
            emp = emp[emp["country"].isin(filters.countries)]
        if filters.job_levels:
            emp = emp[emp["job_level"].isin(filters.job_levels)]
        eligible = int(len(emp))
    else:
        eligible = int(len(employees))

    performance = usecase_performance(filters)
    high = int((performance["classification"] == "Scale").sum()) if not performance.empty else 0
    low = int(performance["classification"].isin(["Reassess", "Stop"]).sum()) if not performance.empty else 0
    production = int(master["status"].isin(["Production", "Scaling"]).sum()) if not master.empty else 0

    net = realized - cost
    roi = safe_div(net, cost)
    months = max(1, uc["month"].nunique()) if not uc.empty else 1
    payback = safe_div(cost, realized / months) if realized > 0 else None
    tasks = float(prod["tasks_completed"].sum()) if not prod.empty else 0.0

    return {
        "potential_value": potential,
        "demonstrated_value": demonstrated,
        "realized_value": realized,
        "total_cost": cost,
        "net_benefit": net,
        "portfolio_roi": roi,
        "payback_months": payback if payback not in {float("inf")} else None,
        "benefit_cost_ratio": safe_div(realized, cost),
        "hours_saved": hours,
        "fte_capacity": fte_equivalent(hours, SETTINGS.working_hours_per_year),
        "finance_validated": finance_validated,
        "unvalidated_value": max(0.0, realized - finance_validated),
        "pd_conversion": safe_div(demonstrated, potential),
        "dr_conversion": safe_div(realized, demonstrated),
        "value_realization_pct": safe_div(realized, potential),
        "eligible_users": eligible,
        "licensed_users": licensed_latest,
        "active_users": active_latest,
        "adoption_rate": safe_div(active_latest, licensed_latest),
        "activation_rate": safe_div(licensed, eligible) if eligible else 0.0,
        "underutilized_licenses": underutilized,
        "optimization_opportunity": opt_opp,
        "production_use_cases": production,
        "high_performing": high,
        "underperforming": low,
        "infrastructure_cost": infra,
        "cost_per_active_user": safe_div(cost, active_latest),
        "cost_per_ai_task": safe_div(cost, tasks),
        "cost_per_hour_saved": safe_div(cost, hours),
        "realized_per_user": safe_div(realized, active_latest),
        "realized_per_dollar": safe_div(realized, cost),
        "tasks_completed": tasks,
    }


def value_bridge(filters: FilterState) -> pd.DataFrame:
    k = portfolio_kpis(filters)
    return pd.DataFrame(
        [
            {"step": "Potential value", "value": k["potential_value"]},
            {"step": "Evidence adjustment", "value": k["demonstrated_value"] - k["potential_value"]},
            {"step": "Demonstrated value", "value": k["demonstrated_value"]},
            {"step": "Realization adjustment", "value": k["realized_value"] - k["demonstrated_value"]},
            {"step": "Realized value", "value": k["realized_value"]},
            {"step": "AI costs", "value": -k["total_cost"]},
            {"step": "Net AI value", "value": k["net_benefit"]},
        ]
    )


def investment_value_trend(filters: FilterState) -> pd.DataFrame:
    frame = enterprise_mart(filters)
    if frame.empty:
        return frame
    out = frame[
        [
            "month",
            "total_cost",
            "realized_value",
            "demonstrated_value",
            "potential_value",
            "active_users",
            "licensed_users",
        ]
    ].copy()
    out["net_benefit"] = out["realized_value"] - out["total_cost"]
    out["roi"] = out.apply(lambda r: safe_div(r["realized_value"] - r["total_cost"], r["total_cost"]), axis=1)
    out["adoption_rate"] = out.apply(lambda r: safe_div(r["active_users"], r["licensed_users"]), axis=1)
    return out.sort_values("month")


def spend_by_dimension(filters: FilterState, dimension: str) -> pd.DataFrame:
    uc = usecase_mart(filters)
    if uc.empty or dimension not in uc.columns:
        return pd.DataFrame(columns=[dimension, "total_cost", "realized_value"])
    return (
        uc.groupby(dimension, as_index=False)
        .agg(
            total_cost=("total_cost", "sum"),
            realized_value=("realized_value", "sum"),
            potential_value=("potential_value", "sum"),
            demonstrated_value=("demonstrated_value", "sum"),
            hours_saved=("hours_saved", "sum"),
        )
        .sort_values("total_cost", ascending=False)
    )


def cost_category_breakdown(filters: FilterState) -> pd.DataFrame:
    uc = usecase_mart(filters)
    cols = [
        "license_cost",
        "infrastructure_cost",
        "implementation_cost",
        "support_cost",
        "training_cost",
        "security_cost",
        "governance_cost",
    ]
    present = [c for c in cols if c in uc.columns]
    if uc.empty or not present:
        return pd.DataFrame(columns=["cost_category", "amount"])
    series = uc[present].sum().rename("amount")
    out = series.reset_index().rename(columns={"index": "cost_category"})
    out["cost_category"] = out["cost_category"].str.replace("_", " ").str.title()
    return out.sort_values("amount", ascending=False)


def usecase_performance(filters: FilterState) -> pd.DataFrame:
    uc = usecase_mart(filters)
    master = use_case_master(filters)
    if uc.empty:
        return pd.DataFrame()
    grouped = uc.groupby("use_case_id", as_index=False).agg(
        potential_value=("potential_value", "sum"),
        demonstrated_value=("demonstrated_value", "sum"),
        realized_value=("realized_value", "sum"),
        total_cost=("total_cost", "sum"),
        hours_saved=("hours_saved", "sum"),
        months=("month", "nunique"),
    )
    meta_cols = [
        "use_case_id",
        "use_case_name",
        "business_unit",
        "department",
        "status",
        "risk_rating",
        "product_name",
        "vendor",
        "implementation_cost",
        "expected_value",
        "target_users",
        "business_owner",
    ]
    meta_cols = [c for c in meta_cols if c in master.columns]
    grouped = grouped.merge(master[meta_cols], on="use_case_id", how="left")
    grouped["roi"] = grouped.apply(lambda r: safe_div(r["realized_value"] - r["total_cost"], r["total_cost"]), axis=1)
    grouped["payback_months"] = grouped.apply(
        lambda r: safe_div(r["total_cost"], r["realized_value"] / max(r["months"], 1)) if r["realized_value"] > 0 else None,
        axis=1,
    )
    grouped["value_realization_pct"] = grouped.apply(lambda r: safe_div(r["realized_value"], r["potential_value"]), axis=1)
    grouped["classification"] = grouped.apply(_classify_use_case, axis=1)
    return grouped.sort_values("realized_value", ascending=False)


def _classify_use_case(row: pd.Series) -> str:
    if row.get("status") in {"Retired", "Paused"} or (row["roi"] < -0.4 and row["realized_value"] < 50_000):
        return "Stop"
    if row.get("status") in {"Idea", "Assessment"}:
        return "Monitor"
    if row["roi"] >= 0.8 and row["realized_value"] >= 200_000:
        return "Scale"
    if row["roi"] >= 0.15 and row["value_realization_pct"] < 0.35:
        return "Optimize"
    if row["roi"] < 0 and row.get("status") in {"Pilot", "Production"}:
        return "Reassess"
    if row["realized_value"] < 40_000 and row["total_cost"] > 80_000:
        return "Reassess"
    return "Monitor"


def adoption_by_dimension(filters: FilterState, dimension: str) -> pd.DataFrame:
    licenses = license_snapshot(filters)
    if licenses.empty or dimension not in licenses.columns:
        return pd.DataFrame()
    grouped = licenses.groupby(dimension, as_index=False).agg(
        licensed=("employee_id", "nunique"),
        licenses=("license_id", "nunique"),
        annual_cost=("annual_cost", "sum"),
    )
    active = (
        licenses[~licenses["segment"].isin(["Inactive", "Never Activated", "Abandoned"])]
        .groupby(dimension, as_index=False)["employee_id"]
        .nunique()
        .rename(columns={"employee_id": "active"})
    )
    out = grouped.merge(active, on=dimension, how="left").fillna({"active": 0})
    out["adoption_rate"] = out.apply(lambda r: safe_div(r["active"], r["licensed"]), axis=1)
    return out.sort_values("licensed", ascending=False)


def segment_breakdown(filters: FilterState) -> pd.DataFrame:
    licenses = license_snapshot(filters)
    if licenses.empty:
        return pd.DataFrame()
    return (
        licenses.groupby("segment", as_index=False)
        .agg(
            licenses=("license_id", "nunique"),
            employees=("employee_id", "nunique"),
            annual_cost=("annual_cost", "sum"),
        )
        .sort_values("licenses", ascending=False)
    )


def productivity_summary(filters: FilterState) -> pd.DataFrame:
    prod = cached_tables()["productivity_metrics"].copy()
    uc = cached_tables()["ai_use_cases"]
    dept = cached_tables()["departments"]
    products = cached_tables()["ai_products"]
    meta = uc[
        [
            "use_case_id",
            "use_case_name",
            "business_unit",
            "department",
            "ai_product",
            "status",
            "risk_rating",
        ]
    ].rename(columns={"department": "department_name"})
    frame = prod.merge(meta, on="use_case_id", how="left")
    if "department_name" not in frame.columns:
        frame = frame.merge(dept[["department_id", "department_name"]], on="department_id", how="left")
    frame["product_name"] = frame["ai_product"].map(dict(zip(products["product_id"], products["product_name"])))
    frame["vendor"] = frame["ai_product"].map(dict(zip(products["product_id"], products["vendor"])))
    frame = apply_filters(frame, filters, "date")
    if filters.use_cases and "use_case_name" in frame.columns:
        frame = frame[frame["use_case_name"].isin(filters.use_cases)]
    return frame


def department_value_index(filters: FilterState) -> pd.DataFrame:
    dept = department_mart(filters)
    perf = usecase_performance(filters)
    if dept.empty:
        return pd.DataFrame()
    agg = dept.groupby(["department_id", "department_name", "business_unit_name"], as_index=False).agg(
        realized_value=("realized_value", "sum"),
        demonstrated_value=("demonstrated_value", "sum"),
        potential_value=("potential_value", "sum"),
        total_cost=("total_cost", "sum"),
        hours_saved=("hours_saved", "sum"),
        active_users=("active_users", "mean"),
        licensed_users=("licensed_users", "mean"),
        sessions=("sessions", "sum"),
    )
    trained = cached_tables()["employees"].groupby("department_id", as_index=False)["ai_training_completed"].mean()
    agg = agg.merge(trained, on="department_id", how="left")
    agg["adoption"] = agg.apply(lambda r: safe_div(r["active_users"], r["licensed_users"]), axis=1)
    agg["usage"] = agg.apply(lambda r: safe_div(r["sessions"], r["licensed_users"]), axis=1)
    agg["productivity"] = agg.apply(lambda r: safe_div(r["hours_saved"], r["licensed_users"]), axis=1)
    agg["value"] = agg["realized_value"]
    agg["roi"] = agg.apply(lambda r: safe_div(r["realized_value"] - r["total_cost"], r["total_cost"]), axis=1)
    agg["training"] = agg["ai_training_completed"].fillna(0)
    if not perf.empty:
        success = (
            perf.groupby("department")
            .apply(lambda g: safe_div((g["classification"] == "Scale").sum() + (g["roi"] > 0).sum(), max(len(g) * 2, 1)), include_groups=False)
            .rename("use_case_success")
            .reset_index()
            .rename(columns={"department": "department_name"})
        )
        agg = agg.merge(success, on="department_name", how="left")
    else:
        agg["use_case_success"] = 0.0
    agg["use_case_success"] = agg["use_case_success"].fillna(0)

    dimensions = ["adoption", "usage", "productivity", "value", "roi", "training", "use_case_success"]
    for col in dimensions:
        series = agg[col].astype(float)
        lo, hi = series.min(), series.max()
        agg[f"{col}_idx"] = 0.0 if hi == lo else (series - lo) / (hi - lo) * 100
    agg["ai_value_index"] = agg[[f"{c}_idx" for c in dimensions]].mean(axis=1)
    return agg.sort_values("ai_value_index", ascending=False)


def training_lift(filters: FilterState) -> pd.DataFrame:
    seg = cached_tables()["mart_employee_segment"]
    mapping = {
        "business_unit_name": filters.business_units,
        "department_name": filters.departments,
        "country": filters.countries,
        "job_level": filters.job_levels,
    }
    out = seg
    for column, selected in mapping.items():
        if selected and column in out.columns:
            out = out[out[column].isin(selected)]
    if out.empty:
        return pd.DataFrame()
    grouped = out.groupby("ai_training_completed", as_index=False).agg(
        employees=("employee_id", "nunique"),
        sessions=("sessions", "mean"),
    )
    grouped["ai_training_completed"] = grouped["ai_training_completed"].map({True: "Trained", False: "Not trained"})
    return grouped
