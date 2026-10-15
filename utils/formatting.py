from __future__ import annotations

from typing import Any


def format_currency(value: float | None, compact: bool = True, symbol: str = "$") -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "—"
    sign = "-" if value < 0 else ""
    amount = abs(float(value))
    if not compact:
        return f"{sign}{symbol}{amount:,.0f}"
    if amount >= 1_000_000_000:
        return f"{sign}{symbol}{amount / 1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"{sign}{symbol}{amount / 1_000_000:.2f}M"
    if amount >= 1_000:
        return f"{sign}{symbol}{amount / 1_000:.1f}K"
    return f"{sign}{symbol}{amount:,.0f}"


def format_percent(value: float | None, decimals: int = 1, already_ratio: bool = True) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "—"
    pct = value * 100 if already_ratio else value
    return f"{pct:,.{decimals}f}%"


def format_number(value: float | None, decimals: int = 0) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "—"
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"


def format_hours(value: float | None) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "—"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K hrs"
    return f"{value:,.0f} hrs"


def format_months(value: float | None) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "—"
    if value < 0:
        return "n/m"
    if value > 120:
        return ">10 yrs"
    return f"{value:.1f} mo"


def safe_div(numerator: Any, denominator: Any, default: float = 0.0) -> float:
    try:
        denom = float(denominator)
        if denom == 0:
            return default
        return float(numerator) / denom
    except (TypeError, ValueError):
        return default
