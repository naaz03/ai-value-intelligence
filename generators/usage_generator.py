from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from config.constants import ADOPTION_MULTIPLIER, TRAINING_CAMPAIGN_MONTHS


def generate_usage(
    employees: pd.DataFrame,
    licenses: pd.DataFrame,
    months: list[date],
    rng: np.random.Generator,
) -> pd.DataFrame:
    emp = employees.set_index("employee_id")
    month_index = {m: i for i, m in enumerate(months)}
    rows: list[dict] = []
    usage_n = 1

    license_records = licenses.to_dict("records")
    for lic in license_records:
        employee = emp.loc[lic["employee_id"]]
        assigned = lic["assigned_date"]
        if isinstance(assigned, pd.Timestamp):
            assigned = assigned.date()
        start_i = month_index.get(assigned, 0)
        dept_mult = ADOPTION_MULTIPLIER.get(employee["department_id"], 0.8)
        trained = bool(employee["ai_training_completed"])
        train_date = employee["ai_training_date"]
        level = employee["job_level"]
        family = employee["job_family"]

        persona = _usage_persona(rng, employee["department_id"], trained, level)
        abandoned = persona == "Abandoned"
        never = persona == "Never Activated"
        abandon_after = int(rng.integers(1, 3)) if abandoned else 99

        for i, month in enumerate(months):
            if i < start_i:
                continue
            months_since = i - start_i
            if never:
                rows.append(
                    _empty_usage(
                        usage_n,
                        month,
                        lic,
                        employee,
                    )
                )
                usage_n += 1
                continue
            if abandoned and months_since > abandon_after:
                rows.append(_empty_usage(usage_n, month, lic, employee))
                usage_n += 1
                continue

            base_p = {
                "Power User": 0.96,
                "Regular User": 0.82,
                "Occasional User": 0.48,
                "Inactive": 0.08,
                "Abandoned": 0.70,
            }[persona]
            p = min(0.98, base_p * dept_mult * _ramp(months_since) * _summer_factor(month))
            if trained and train_date is not None:
                train_ts = pd.Timestamp(train_date)
                if pd.Timestamp(month) >= train_ts:
                    p = min(0.99, p + 0.14)
                    # Finance-specific training lift (story 3)
                    if employee["department_id"].startswith("DEP-FIN") and pd.Timestamp(month) >= train_ts:
                        p = min(0.99, p + 0.10)
            # Campaign months lift everyone slightly (story 11)
            if i in TRAINING_CAMPAIGN_MONTHS or i - 1 in TRAINING_CAMPAIGN_MONTHS:
                p = min(0.99, p + 0.06)

            active = rng.random() < p
            if not active:
                rows.append(_empty_usage(usage_n, month, lic, employee))
                usage_n += 1
                continue

            sessions = _sessions(rng, persona, level, family, lic["product_id"])
            prompts = max(sessions, int(sessions * rng.uniform(2.2, 6.5)))
            tasks = max(1, int(sessions * rng.uniform(0.45, 1.1)))
            tokens = int(prompts * rng.uniform(900, 4_200))
            if lic["product_id"] == "PRD-AZ-OAI":
                tokens = int(tokens * rng.uniform(3.5, 8.0) * (1 + i / 36 * 1.6))  # story 14
            minutes = float(np.clip(rng.normal(18 if level != "Executive" else 28, 6), 6, 75))
            compute = tokens * (0.0000024 if lic["product_id"] != "PRD-AZ-OAI" else 0.0000048)
            if lic["product_id"] == "PRD-AZ-OAI":
                compute *= 1.0 + i / 24

            rows.append(
                {
                    "usage_id": f"USG-{usage_n:08d}",
                    "date": month,
                    "employee_id": lic["employee_id"],
                    "product_id": lic["product_id"],
                    "department_id": employee["department_id"],
                    "business_unit_id": employee["business_unit_id"],
                    "country": employee["country"],
                    "job_level": level,
                    "active_flag": True,
                    "sessions": sessions,
                    "prompts": prompts,
                    "tasks_completed": tasks,
                    "tokens_consumed": tokens,
                    "estimated_compute_cost": round(float(compute), 2),
                    "average_session_minutes": round(minutes, 1),
                    "user_persona": persona,
                }
            )
            usage_n += 1

    return pd.DataFrame(rows)


def _empty_usage(usage_n: int, month: date, lic: dict, employee: pd.Series) -> dict:
    return {
        "usage_id": f"USG-{usage_n:08d}",
        "date": month,
        "employee_id": lic["employee_id"],
        "product_id": lic["product_id"],
        "department_id": employee["department_id"],
        "business_unit_id": employee["business_unit_id"],
        "country": employee["country"],
        "job_level": employee["job_level"],
        "active_flag": False,
        "sessions": 0,
        "prompts": 0,
        "tasks_completed": 0,
        "tokens_consumed": 0,
        "estimated_compute_cost": 0.0,
        "average_session_minutes": 0.0,
        "user_persona": "Inactive",
    }


def _usage_persona(rng: np.random.Generator, department_id: str, trained: bool, level: str) -> str:
    # Legal / HR: many never activated or inactive (stories 2, 7)
    if department_id.startswith("DEP-LEG"):
        return str(rng.choice(
            ["Power User", "Regular User", "Occasional User", "Inactive", "Never Activated", "Abandoned"],
            p=[0.04, 0.10, 0.14, 0.28, 0.30, 0.14],
        ))
    if department_id.startswith("DEP-HR"):
        return str(rng.choice(
            ["Power User", "Regular User", "Occasional User", "Inactive", "Never Activated", "Abandoned"],
            p=[0.05, 0.12, 0.16, 0.30, 0.24, 0.13],
        ))
    if department_id.startswith("DEP-TECH-ENG"):
        return str(rng.choice(
            ["Power User", "Regular User", "Occasional User", "Inactive", "Never Activated", "Abandoned"],
            p=[0.32, 0.38, 0.16, 0.06, 0.04, 0.04],
        ))
    if department_id.startswith("DEP-MKT"):
        return str(rng.choice(
            ["Power User", "Regular User", "Occasional User", "Inactive", "Never Activated", "Abandoned"],
            p=[0.28, 0.36, 0.20, 0.08, 0.04, 0.04],
        ))
    if department_id.startswith("DEP-CS"):
        return str(rng.choice(
            ["Power User", "Regular User", "Occasional User", "Inactive", "Never Activated", "Abandoned"],
            p=[0.22, 0.40, 0.22, 0.08, 0.04, 0.04],
        ))
    weights = [0.12, 0.30, 0.26, 0.16, 0.08, 0.08]
    if trained:
        weights = [0.18, 0.36, 0.24, 0.12, 0.05, 0.05]
    if level == "Executive":
        weights = [0.06, 0.18, 0.28, 0.22, 0.16, 0.10]
    return str(rng.choice(
        ["Power User", "Regular User", "Occasional User", "Inactive", "Never Activated", "Abandoned"],
        p=weights,
    ))


def _ramp(months_since: int) -> float:
    if months_since <= 0:
        return 0.55
    if months_since == 1:
        return 0.75
    return 1.0


def _summer_factor(month: date) -> float:
    if month.month in {7, 8}:
        return 0.78
    return 1.0


def _sessions(rng: np.random.Generator, persona: str, level: str, family: str, product_id: str) -> int:
    base = {
        "Power User": (18, 36),
        "Regular User": (8, 18),
        "Occasional User": (2, 7),
        "Abandoned": (3, 8),
        "Inactive": (1, 3),
        "Never Activated": (1, 2),
    }.get(persona, (2, 6))
    lo, hi = base
    if level == "Executive":
        hi = min(hi, 10)
        lo = min(lo, 4)
    if family == "Software Engineering" and product_id == "PRD-GH-COP":
        lo += 6
        hi += 10
    if family == "Marketing":
        lo += 3
        hi += 8
    return int(rng.integers(lo, hi + 1))
