from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from config.constants import (
    COUNTRIES,
    COUNTRY_WEIGHTS,
    JOB_LEVELS,
    LEVEL_WEIGHTS,
    SALARY_BY_LEVEL,
    TRAINING_CAMPAIGN_MONTHS,
)
from config.settings import SETTINGS
from utils.helpers import month_starts, weighted_choice


def generate_employees(departments: pd.DataFrame, months: list[date], rng: np.random.Generator) -> pd.DataFrame:
    country_items = list(COUNTRIES)
    country_weights = [COUNTRY_WEIGHTS[c] for c in country_items]
    level_items = list(JOB_LEVELS)
    level_weights = [LEVEL_WEIGHTS[level] for level in level_items]

    history_start = months[0]
    rows: list[dict] = []
    emp_n = 1

    for dept in departments.itertuples(index=False):
        n = int(dept.employee_count)
        for _ in range(n):
            level = weighted_choice(rng, level_items, level_weights)
            if dept.job_family == "Executive Leadership":
                level = "Executive"
            lo, hi = SALARY_BY_LEVEL[level]
            salary = float(rng.integers(lo, hi + 1))
            hourly = salary / SETTINGS.working_hours_per_year
            tenure_months = int(rng.integers(4, 140))
            join_date = pd.Timestamp(history_start) - pd.DateOffset(months=max(0, tenure_months - 6))
            join_date = max(join_date, pd.Timestamp("2014-01-01")).date()

            trained = False
            training_date = None
            # Training more common in Finance, Tech, CS; rarer in Legal/HR/Ops floor
            train_p = {
                "DEP-FIN-FPNA": 0.72,
                "DEP-FIN-ACC": 0.68,
                "DEP-FIN-TRE": 0.60,
                "DEP-TECH-ENG": 0.55,
                "DEP-TECH-DATA": 0.62,
                "DEP-CS-CNT": 0.50,
                "DEP-PROC-SRC": 0.48,
                "DEP-LEG-CORP": 0.22,
                "DEP-LEG-CON": 0.18,
                "DEP-HR-BP": 0.28,
                "DEP-HR-TA": 0.30,
                "DEP-HR-OPS": 0.26,
            }.get(dept.department_id, 0.38)
            if rng.random() < train_p:
                trained = True
                campaign = int(rng.choice(TRAINING_CAMPAIGN_MONTHS))
                jitter = int(rng.integers(-1, 2))
                idx = min(max(campaign + jitter, 0), len(months) - 1)
                training_date = months[idx]

            manager = level in {"Executive", "Senior Manager", "Manager"} and rng.random() < 0.85
            country = weighted_choice(rng, country_items, country_weights)
            if rng.random() < 0.55:
                country = "UAE"

            rows.append(
                {
                    "employee_id": f"EMP-{emp_n:06d}",
                    "department_id": dept.department_id,
                    "business_unit_id": dept.business_unit_id,
                    "country": country,
                    "job_level": level,
                    "job_family": dept.job_family,
                    "annual_salary": salary,
                    "hourly_cost": round(hourly, 2),
                    "manager_flag": bool(manager),
                    "ai_training_completed": bool(trained),
                    "ai_training_date": training_date,
                    "join_date": join_date,
                }
            )
            emp_n += 1

    # Scale to configured employee_count if department rollup drifted
    frame = pd.DataFrame(rows)
    target = SETTINGS.employee_count
    if len(frame) > target:
        frame = frame.sample(n=target, random_state=int(SETTINGS.seed)).reset_index(drop=True)
        frame["employee_id"] = [f"EMP-{i:06d}" for i in range(1, len(frame) + 1)]
    return frame
