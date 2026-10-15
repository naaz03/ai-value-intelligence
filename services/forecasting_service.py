from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from models.schemas import FilterState
from services.metric_service import investment_value_trend


SCENARIOS = {
    "Conservative": {"spend": 0.96, "value": 0.92, "adoption": 0.97},
    "Base": {"spend": 1.02, "value": 1.06, "adoption": 1.03},
    "Accelerated": {"spend": 1.08, "value": 1.16, "adoption": 1.07},
}


def forecast_scenarios(filters: FilterState, horizon: int = 24) -> pd.DataFrame:
    history = investment_value_trend(filters)
    if history.empty or len(history) < 6:
        return pd.DataFrame()

    hist = history.sort_values("month").copy()
    hist["t"] = np.arange(len(hist))
    last_month = pd.Timestamp(hist["month"].max())
    future_idx = np.arange(len(hist), len(hist) + horizon)
    future_months = pd.date_range(last_month + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")

    rows: list[dict] = []
    for label, factors in SCENARIOS.items():
        spend = _project(hist, "total_cost", future_idx, factors["spend"])
        value = _project(hist, "realized_value", future_idx, factors["value"])
        adopt = _project(hist, "adoption_rate", future_idx, factors["adoption"])
        adopt = np.clip(adopt, 0.05, 0.98)
        for i in range(horizon):
            cost = max(0.0, float(spend[i]))
            realized = max(0.0, float(value[i]))
            rows.append(
                {
                    "scenario": label,
                    "month": future_months[i],
                    "forecast_spend": cost,
                    "forecast_realized_value": realized,
                    "forecast_roi": (realized - cost) / cost if cost else 0.0,
                    "forecast_adoption": float(adopt[i]),
                    "horizon_month": i + 1,
                }
            )
    return pd.DataFrame(rows)


def _project(hist: pd.DataFrame, column: str, future_idx: np.ndarray, drift: float) -> np.ndarray:
    model = LinearRegression()
    x = hist[["t"]].to_numpy()
    y = hist[column].fillna(0).to_numpy()
    model.fit(x, y)
    pred = model.predict(future_idx.reshape(-1, 1))
    # Blend last observed level with trend, then apply scenario drift compounding
    last = float(y[-1])
    blended = 0.65 * pred + 0.35 * last
    growth = np.array([drift ** (i + 1) / drift for i in range(len(future_idx))])
    return blended * growth


def scenario_totals(forecast: pd.DataFrame) -> pd.DataFrame:
    if forecast.empty:
        return forecast
    return (
        forecast.groupby("scenario", as_index=False)
        .agg(
            spend=("forecast_spend", "sum"),
            realized_value=("forecast_realized_value", "sum"),
            end_adoption=("forecast_adoption", "last"),
        )
        .assign(net_benefit=lambda d: d["realized_value"] - d["spend"])
        .assign(roi=lambda d: (d["realized_value"] - d["spend"]) / d["spend"].replace(0, np.nan))
    )
