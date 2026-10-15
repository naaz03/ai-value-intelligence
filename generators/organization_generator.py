from __future__ import annotations

import pandas as pd

from config.constants import BUSINESS_UNITS, DEPARTMENTS, ORGANIZATION


def generate_organizations() -> pd.DataFrame:
    return pd.DataFrame([ORGANIZATION])


def generate_business_units() -> pd.DataFrame:
    return pd.DataFrame(list(BUSINESS_UNITS))


def generate_departments() -> pd.DataFrame:
    rows = [
        {
            "department_id": dept_id,
            "department_name": name,
            "business_unit_id": bu_id,
            "cost_center": cost_center,
            "employee_count": count,
            "job_family": family,
        }
        for dept_id, name, bu_id, cost_center, count, family in DEPARTMENTS
    ]
    return pd.DataFrame(rows)
