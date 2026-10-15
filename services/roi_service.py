from __future__ import annotations

import pandas as pd

from models.schemas import FilterState
from services.metric_service import portfolio_kpis, usecase_performance
from utils.calculations import benefit_cost_ratio, net_benefit, payback_months, roi_pct
from utils.formatting import safe_div


def portfolio_roi(filters: FilterState) -> dict[str, float]:
    k = portfolio_kpis(filters)
    months = max(1, int(round(k.get("payback_months") or 0)) or 1)
    monthly_realized = safe_div(k["realized_value"], max(months, 1))
    # Prefer implied months from payback formula already in KPIs
    return {
        "gross_benefit": k["realized_value"],
        "total_cost": k["total_cost"],
        "net_benefit": net_benefit(k["realized_value"], k["total_cost"]),
        "roi": roi_pct(k["realized_value"], k["total_cost"]),
        "benefit_cost_ratio": benefit_cost_ratio(k["realized_value"], k["total_cost"]),
        "payback_months": k["payback_months"],
        "cost_per_active_user": k["cost_per_active_user"],
        "cost_per_ai_task": k["cost_per_ai_task"],
        "cost_per_hour_saved": k["cost_per_hour_saved"],
        "realized_per_user": k["realized_per_user"],
        "realized_per_dollar": k["realized_per_dollar"],
        "monthly_realized": monthly_realized,
    }


def methodology_kpis(filters: FilterState) -> dict[str, float]:
    """Recommended AI ROI pack. Headline cash ROI is only one layer."""
    from services.data_service import cached_tables
    from services.metric_service import usecase_mart
    from config.settings import SETTINGS

    k = portfolio_kpis(filters)
    uc = usecase_mart(filters)
    license_cost = float(uc["license_cost"].sum()) if not uc.empty and "license_cost" in uc.columns else 0.0
    months = max(1, int(uc["month"].nunique()) if not uc.empty else 1)
    hourly = float(cached_tables()["employees"]["hourly_cost"].mean())
    gross_prod = k["hours_saved"] * hourly
    idle_annual = k["optimization_opportunity"]
    idle_in_period = idle_annual * (months / 12.0)
    optimized_cost = max(0.0, k["total_cost"] - idle_in_period)

    potential = k["potential_value"]
    demonstrated = k["demonstrated_value"]
    realized = k["realized_value"]
    cost = k["total_cost"]
    active = max(k["active_users"], 0)
    licensed = max(k["licensed_users"], 0)

    return {
        "cash_roi": roi_pct(realized, cost),
        "evidence_roi": roi_pct(demonstrated, cost),
        "planning_roi": roi_pct(potential, cost),
        "net_benefit": net_benefit(realized, cost),
        "benefit_cost_ratio": benefit_cost_ratio(realized, cost),
        "payback_months": k["payback_months"],
        "potential_value": potential,
        "demonstrated_value": demonstrated,
        "realized_value": realized,
        "total_cost": cost,
        "license_cost": license_cost,
        "evidence_conversion": safe_div(demonstrated, potential),
        "cash_conversion": safe_div(realized, demonstrated),
        "realization_rate": safe_div(realized, potential),
        "finance_validation_rate": safe_div(k["finance_validated"], realized),
        "value_yield": safe_div(realized, cost),
        "license_only_roi": roi_pct(realized, license_cost),
        "realized_per_active_user": safe_div(realized, active),
        "realized_per_licensed_user": safe_div(realized, licensed),
        "license_dilution": 1.0 - safe_div(active, licensed),
        "cost_per_active_user": k["cost_per_active_user"],
        "cost_per_hour_saved": k["cost_per_hour_saved"],
        "hours_saved": k["hours_saved"],
        "fte_capacity": k["fte_capacity"],
        "avg_hourly_cost": hourly,
        "gross_productivity_value": gross_prod,
        "productivity_capture_rate": safe_div(realized, gross_prod),
        "idle_license_drag": safe_div(idle_in_period, cost),
        "optimized_cost": optimized_cost,
        "reclaimed_seat_roi": roi_pct(realized, optimized_cost),
        "roi_uplift_if_reclaimed": roi_pct(realized, optimized_cost) - roi_pct(realized, cost),
        "working_hours_per_year": float(SETTINGS.working_hours_per_year),
        "months": float(months),
    }


def usecase_roi_table(filters: FilterState) -> pd.DataFrame:
    frame = usecase_performance(filters)
    if frame.empty:
        return frame
    frame = frame.copy()
    frame["net_benefit"] = frame["realized_value"] - frame["total_cost"]
    frame["bcr"] = frame.apply(lambda r: safe_div(r["realized_value"], r["total_cost"]), axis=1)
    return frame.sort_values("roi", ascending=False)


def simulate(
    licenses: int,
    license_price: float,
    adoption_rate: float,
    hours_saved_per_user_year: float,
    hourly_cost: float,
    realization_factor: float,
    infrastructure_cost: float,
    training_cost: float,
    implementation_cost: float,
    success_rate: float,
    support_cost: float = 0.0,
    security_cost: float = 0.0,
    governance_cost: float = 0.0,
    years: float = 1.0,
) -> dict[str, float]:
    active_users = licenses * adoption_rate
    license_cost = licenses * license_price * 12 * years
    total_cost = (
        license_cost
        + infrastructure_cost
        + training_cost
        + implementation_cost
        + support_cost
        + security_cost
        + governance_cost
    )
    gross_hours = active_users * hours_saved_per_user_year * years
    gross_productivity = gross_hours * hourly_cost
    demonstrated = gross_productivity * success_rate
    realized = demonstrated * realization_factor
    net = realized - total_cost
    monthly_realized = realized / max(years * 12, 1)
    return {
        "active_users": active_users,
        "projected_cost": total_cost,
        "license_cost": license_cost,
        "gross_hours": gross_hours,
        "gross_productivity_value": gross_productivity,
        "demonstrated_value": demonstrated,
        "realized_value": realized,
        "net_benefit": net,
        "roi": roi_pct(realized, total_cost),
        "payback_months": payback_months(total_cost, monthly_realized),
        "break_even_users": safe_div(total_cost, hours_saved_per_user_year * hourly_cost * realization_factor * success_rate * years)
        if hours_saved_per_user_year * hourly_cost * realization_factor * success_rate > 0
        else None,
        "benefit_cost_ratio": benefit_cost_ratio(realized, total_cost),
    }
