from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from config.constants import AI_PRODUCTS, LICENSE_COVERAGE, PRODUCT_AFFINITY
from config.settings import SETTINGS


def generate_products() -> pd.DataFrame:
    return pd.DataFrame(list(AI_PRODUCTS))


def generate_licenses(
    employees: pd.DataFrame,
    products: pd.DataFrame,
    months: list[date],
    rng: np.random.Generator,
) -> pd.DataFrame:
    product_cost = dict(zip(products["product_id"], products["monthly_unit_cost"]))
    rows: list[dict] = []
    license_n = 1
    licensed_employees: set[str] = set()

    for emp in employees.itertuples(index=False):
        coverage = LICENSE_COVERAGE.get(emp.department_id, 0.35)
        # Executives slightly more likely to be licensed even if unused
        if emp.job_level == "Executive":
            coverage = min(0.95, coverage + 0.15)
        if emp.job_level == "Associate" and emp.job_family in {"Operations", "Supply Chain"}:
            coverage *= 0.35
        if rng.random() > coverage:
            continue

        affinity = PRODUCT_AFFINITY.get(emp.job_family, {"PRD-M365-COP": 0.5})
        assigned: list[str] = []
        for product_id, probability in affinity.items():
            boost = 0.08 if emp.ai_training_completed else 0.0
            if rng.random() < min(0.97, probability + boost):
                assigned.append(product_id)

        if not assigned:
            assigned = [next(iter(affinity))]

        # Overlap story: some knowledge workers get Copilot + ChatGPT
        if emp.job_family in {"Marketing", "Strategy", "Finance", "Data & Analytics"} and rng.random() < 0.22:
            if "PRD-M365-COP" not in assigned:
                assigned.append("PRD-M365-COP")
            if "PRD-CHATGPT" not in assigned and rng.random() < 0.6:
                assigned.append("PRD-CHATGPT")

        join_ts = pd.Timestamp(emp.join_date)
        for product_id in assigned:
            delay = int(rng.integers(0, 18))
            assigned_idx = min(delay, len(months) - 8)
            assigned_date = months[assigned_idx]
            if pd.Timestamp(assigned_date) < join_ts:
                assigned_date = max(months[0], (join_ts + pd.offsets.MonthBegin(1)).date())
            status = "Active"
            if rng.random() < 0.015:
                status = "Suspended"
            rows.append(
                {
                    "license_id": f"LIC-{license_n:07d}",
                    "employee_id": emp.employee_id,
                    "product_id": product_id,
                    "assigned_date": assigned_date,
                    "license_status": status,
                    "monthly_cost": float(product_cost.get(product_id, 0.0)),
                }
            )
            license_n += 1
            licensed_employees.add(emp.employee_id)

    frame = pd.DataFrame(rows)

    # Nudge toward the target licensed-employee count
    unique = frame["employee_id"].nunique()
    target = SETTINGS.target_licensed_employees
    if unique > target * 1.12:
        keep_emps = (
            frame.groupby("employee_id")
            .size()
            .sample(n=target, random_state=int(SETTINGS.seed))
            .index
        )
        frame = frame[frame["employee_id"].isin(keep_emps)].reset_index(drop=True)
        frame["license_id"] = [f"LIC-{i:07d}" for i in range(1, len(frame) + 1)]
    return frame
