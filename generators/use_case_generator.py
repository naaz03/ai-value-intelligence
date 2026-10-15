from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from config.constants import BUSINESS_UNITS
from generators.use_case_catalog import USE_CASES


def generate_use_cases(
    departments: pd.DataFrame,
    months: list[date],
    rng: np.random.Generator,
) -> pd.DataFrame:
    dept_lookup = departments.set_index("department_id")
    bu_lookup = {row["business_unit_id"]: row["business_unit_name"] for row in BUSINESS_UNITS}
    bu_owner = {row["business_unit_id"]: row["executive_owner"] for row in BUSINESS_UNITS}

    rows: list[dict] = []
    for spec in USE_CASES:
        dept = dept_lookup.loc[spec["department"]]
        start_idx = min(max(int(spec["start_offset"]), 0), len(months) - 1)
        rows.append(
            {
                "use_case_id": spec["use_case_id"],
                "use_case_name": spec["use_case_name"],
                "business_unit": bu_lookup[dept["business_unit_id"]],
                "business_unit_id": dept["business_unit_id"],
                "department": dept["department_name"],
                "department_id": spec["department"],
                "business_owner": bu_owner[dept["business_unit_id"]],
                "technology_owner": "AI Program Office",
                "ai_product": spec["ai_product"],
                "use_case_category": spec["use_case_category"],
                "implementation_cost": spec["implementation_cost"],
                "annual_operating_cost": spec["annual_operating_cost"],
                "start_date": months[start_idx],
                "status": spec["status"],
                "risk_rating": spec["risk_rating"],
                "expected_value": spec["expected_value"],
                "expected_hours_saved": spec["expected_hours_saved"],
                "target_users": spec["target_users"],
                "benefit_type": spec["benefit_type"],
                "evidence_factor": spec["evidence_factor"],
                "realization_override": spec.get("realization_override"),
                "story": spec.get("story"),
                "retire_after": spec.get("retire_after"),
                "start_offset": spec["start_offset"],
            }
        )

    extra = _expand_portfolio(departments, months, rng, existing_ids={r["use_case_id"] for r in rows})
    rows.extend(extra)
    return pd.DataFrame(rows)


def _expand_portfolio(
    departments: pd.DataFrame,
    months: list[date],
    rng: np.random.Generator,
    existing_ids: set[str],
) -> list[dict]:
    """Add additional realistic use cases so the registry reaches ~80 items."""
    templates = [
        ("Meeting recap automation", "Productivity", "PRD-M365-COP", "Productivity", 0.50, 0.28),
        ("Inbox triage assist", "Productivity", "PRD-M365-COP", "Productivity", 0.48, 0.24),
        ("Policy FAQ drafting", "Knowledge", "PRD-CHATGPT", "Productivity", 0.45, 0.22),
        ("Report commentary assist", "Analytics Enablement", "PRD-M365-COP", "Productivity", 0.52, 0.30),
        ("Process SOP rewrite", "Knowledge", "PRD-CHATGPT", "Productivity", 0.42, 0.20),
        ("Vendor email drafting", "Operations", "PRD-M365-COP", "Productivity", 0.46, 0.26),
        ("Training content outline", "Learning", "PRD-CHATGPT", "Productivity", 0.40, 0.18),
        ("Exception narrative assist", "Operations", "PRD-NOOR-ASSIST", "Capacity Release", 0.55, 0.32),
    ]
    statuses = ["Idea", "Assessment", "Pilot", "Production", "Paused"]
    risks = ["Low", "Medium", "High"]
    bu_lookup = {row["business_unit_id"]: row["business_unit_name"] for row in BUSINESS_UNITS}
    bu_owner = {row["business_unit_id"]: row["executive_owner"] for row in BUSINESS_UNITS}

    extras: list[dict] = []
    seq = 200
    # One extra per department keeps the registry near 80 without crowding the hero stories.
    for dept in departments.itertuples(index=False):
        for _ in range(1):
            template = templates[int(rng.integers(0, len(templates)))]
            name, category, product, benefit, evidence, realization = template
            use_id = f"UC-{seq}"
            seq += 1
            if use_id in existing_ids:
                continue
            start_offset = int(rng.integers(6, 30))
            status = str(rng.choice(statuses, p=[0.10, 0.14, 0.28, 0.40, 0.08]))
            expected = float(rng.integers(80, 420) * 1000)
            extras.append(
                {
                    "use_case_id": use_id,
                    "use_case_name": f"{dept.department_name} {name.lower()}",
                    "business_unit": bu_lookup[dept.business_unit_id],
                    "business_unit_id": dept.business_unit_id,
                    "department": dept.department_name,
                    "department_id": dept.department_id,
                    "business_owner": bu_owner[dept.business_unit_id],
                    "technology_owner": "AI Program Office",
                    "ai_product": product,
                    "use_case_category": category,
                    "implementation_cost": float(rng.integers(12, 90) * 1000),
                    "annual_operating_cost": float(rng.integers(15, 70) * 1000),
                    "start_date": months[min(start_offset, len(months) - 1)],
                    "status": status,
                    "risk_rating": str(rng.choice(risks, p=[0.45, 0.40, 0.15])),
                    "expected_value": expected,
                    "expected_hours_saved": float(rng.integers(800, 8_000)),
                    "target_users": int(rng.integers(12, 90)),
                    "benefit_type": benefit,
                    "evidence_factor": evidence * (0.2 if status in {"Idea", "Assessment"} else 1.0),
                    "realization_override": realization * (0.2 if status in {"Idea", "Assessment"} else 1.0),
                    "story": None,
                    "retire_after": None,
                    "start_offset": start_offset,
                }
            )
    return extras
