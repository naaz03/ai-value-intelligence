from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from config.constants import DEPARTMENT_REALIZATION
from config.settings import SETTINGS


def generate_productivity(
    employees: pd.DataFrame,
    use_cases: pd.DataFrame,
    usage: pd.DataFrame,
    months: list[date],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Employee-month productivity sample for measured users of each use case."""
    active = usage.loc[usage["active_flag"], ["date", "employee_id", "product_id", "department_id"]]
    emp = employees.set_index("employee_id")
    rows: list[dict] = []

    for uc in use_cases.itertuples(index=False):
        start = pd.Timestamp(uc.start_date)
        candidates = active[
            (active["department_id"] == uc.department_id)
            & (pd.to_datetime(active["date"]) >= start)
        ]
        if uc.ai_product:
            product_match = candidates[candidates["product_id"] == uc.ai_product]
            if not product_match.empty:
                candidates = product_match
        if candidates.empty:
            continue

        user_ids = candidates["employee_id"].drop_duplicates()
        sample_n = min(int(max(8, uc.target_users * 0.18)), 80, len(user_ids))
        stable = int(SETTINGS.seed) + int("".join(ch for ch in uc.use_case_id if ch.isdigit()) or 0)
        sampled = user_ids.sample(n=sample_n, random_state=stable)
        baseline = float(np.clip(rng.normal(48, 18), 12, 180))
        if "contract" in uc.use_case_name.lower():
            baseline = 120.0
        improvement = float(np.clip(rng.normal(0.38, 0.10), 0.08, 0.72))
        if uc.story == "cs_automation":
            improvement = float(np.clip(rng.normal(0.55, 0.05), 0.42, 0.70))
        if uc.story == "tech_github_roi":
            improvement = float(np.clip(rng.normal(0.46, 0.06), 0.32, 0.62))
        if uc.story == "legal_low_adoption":
            improvement = float(np.clip(rng.normal(0.18, 0.05), 0.05, 0.30))
        if uc.story == "failed_agent_pilot":
            improvement = float(np.clip(rng.normal(0.08, 0.03), 0.02, 0.14))

        quality_before = float(np.clip(rng.normal(3.4, 0.3), 2.2, 4.2))
        quality_gain = float(np.clip(rng.normal(0.45, 0.15), 0.0, 1.2))
        rework_before = float(np.clip(rng.normal(0.18, 0.05), 0.05, 0.35))

        for employee_id in sampled:
            hourly = float(emp.loc[employee_id, "hourly_cost"])
            trained = bool(emp.loc[employee_id, "ai_training_completed"])
            user_rows = candidates[candidates["employee_id"] == employee_id]
            for rec in user_rows.itertuples(index=False):
                month = rec.date
                if isinstance(month, pd.Timestamp):
                    month = month.date()
                if pd.Timestamp(month) < start:
                    continue
                months_live = max(0, (pd.Timestamp(month).year - start.year) * 12 + pd.Timestamp(month).month - start.month)
                ramp = min(1.0, 0.45 + months_live * 0.08)
                if month.month in {7, 8}:
                    ramp *= 0.85
                task_n = int(max(1, rng.integers(6, 28) * ramp * (1.15 if trained else 1.0)))
                assisted = baseline * (1 - improvement * ramp * (1.08 if trained else 1.0))
                assisted = max(4.0, assisted)
                hours = task_n * (baseline - assisted) / 60.0
                rows.append(
                    {
                        "date": month,
                        "employee_id": employee_id,
                        "use_case_id": uc.use_case_id,
                        "department_id": uc.department_id,
                        "baseline_task_minutes": round(baseline, 1),
                        "ai_assisted_task_minutes": round(assisted, 1),
                        "tasks_completed": task_n,
                        "hours_saved": round(hours, 2),
                        "quality_before": round(quality_before, 2),
                        "quality_after": round(min(5.0, quality_before + quality_gain * ramp), 2),
                        "rework_before": round(rework_before, 3),
                        "rework_after": round(max(0.02, rework_before * (1 - improvement * 0.6 * ramp)), 3),
                        "hourly_cost": hourly,
                    }
                )
    return pd.DataFrame(rows)


def department_realization(department_id: str, override: float | None) -> float:
    if override is not None and not (isinstance(override, float) and np.isnan(override)):
        return float(override)
    return float(DEPARTMENT_REALIZATION.get(department_id, 0.32))
