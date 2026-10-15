from __future__ import annotations

from utils.formatting import safe_div


def roi_pct(realized_benefit: float, total_cost: float) -> float:
    """ROI = (Realized Financial Benefit - Total AI Cost) / Total AI Cost."""
    return safe_div(realized_benefit - total_cost, total_cost)


def net_benefit(realized_benefit: float, total_cost: float) -> float:
    return float(realized_benefit) - float(total_cost)


def benefit_cost_ratio(realized_benefit: float, total_cost: float) -> float:
    return safe_div(realized_benefit, total_cost)


def payback_months(total_cost: float, monthly_realized: float) -> float | None:
    if monthly_realized <= 0:
        return None
    return float(total_cost) / float(monthly_realized)


def fte_equivalent(hours_saved: float, working_hours_per_year: float) -> float:
    return safe_div(hours_saved, working_hours_per_year)


def realized_from_hours(
    hours_saved: float,
    hourly_cost: float,
    realization_factor: float,
) -> float:
    """Hours become money only through an explicit realization factor."""
    return max(0.0, hours_saved) * max(0.0, hourly_cost) * max(0.0, min(realization_factor, 1.5))


def conversion_rate(numerator: float, denominator: float) -> float:
    return safe_div(numerator, denominator)
