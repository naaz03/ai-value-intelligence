from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class QualityResult:
    name: str
    passed: bool
    detail: str


def run_quality_checks(tables: dict[str, pd.DataFrame]) -> list[QualityResult]:
    results: list[QualityResult] = []
    results.extend(_uniqueness(tables))
    results.extend(_orphans(tables))
    results.extend(_value_hierarchy(tables["financial_benefits"]))
    results.extend(_non_negative(tables))
    results.extend(_status_values(tables))
    results.extend(_date_validity(tables))
    return results


def _uniqueness(tables: dict[str, pd.DataFrame]) -> list[QualityResult]:
    keys = {
        "organizations": "organization_id",
        "business_units": "business_unit_id",
        "departments": "department_id",
        "employees": "employee_id",
        "ai_products": "product_id",
        "licenses": "license_id",
        "ai_use_cases": "use_case_id",
        "financial_benefits": "benefit_id",
        "ai_usage": "usage_id",
    }
    out: list[QualityResult] = []
    for table, key in keys.items():
        frame = tables[table]
        dup = int(frame[key].duplicated().sum())
        out.append(QualityResult(f"{table}.{key} unique", dup == 0, f"{dup} duplicates"))
        nulls = int(frame[key].isna().sum())
        out.append(QualityResult(f"{table}.{key} not null", nulls == 0, f"{nulls} nulls"))
    return out


def _orphans(tables: dict[str, pd.DataFrame]) -> list[QualityResult]:
    emp_ids = set(tables["employees"]["employee_id"])
    dept_ids = set(tables["departments"]["department_id"])
    bu_ids = set(tables["business_units"]["business_unit_id"])
    product_ids = set(tables["ai_products"]["product_id"])
    uc_ids = set(tables["ai_use_cases"]["use_case_id"])

    checks = [
        ("licenses.employee_id", tables["licenses"]["employee_id"], emp_ids),
        ("licenses.product_id", tables["licenses"]["product_id"], product_ids),
        ("employees.department_id", tables["employees"]["department_id"], dept_ids),
        ("employees.business_unit_id", tables["employees"]["business_unit_id"], bu_ids),
        ("ai_usage.employee_id", tables["ai_usage"]["employee_id"], emp_ids),
        ("financial_benefits.use_case_id", tables["financial_benefits"]["use_case_id"], uc_ids),
        ("ai_costs.use_case_id", tables["ai_costs"]["use_case_id"], uc_ids),
    ]
    results = []
    for name, series, parent in checks:
        missing = int((~series.isin(parent)).sum())
        results.append(QualityResult(f"{name} FK", missing == 0, f"{missing} orphans"))
    return results


def _value_hierarchy(benefits: pd.DataFrame) -> list[QualityResult]:
    pd_violation = int((benefits["potential_value"] + 1e-6 < benefits["demonstrated_value"]).sum())
    dr_violation = int((benefits["demonstrated_value"] + 1e-6 < benefits["realized_value"]).sum())
    return [
        QualityResult("potential >= demonstrated", pd_violation == 0, f"{pd_violation} rows"),
        QualityResult("demonstrated >= realized", dr_violation == 0, f"{dr_violation} rows"),
    ]


def _non_negative(tables: dict[str, pd.DataFrame]) -> list[QualityResult]:
    results = []
    money_cols = {
        "ai_costs": [
            "license_cost",
            "infrastructure_cost",
            "implementation_cost",
            "support_cost",
            "training_cost",
            "security_cost",
            "governance_cost",
            "total_cost",
        ],
        "financial_benefits": ["potential_value", "demonstrated_value", "realized_value"],
        "licenses": ["monthly_cost"],
    }
    for table, cols in money_cols.items():
        frame = tables[table]
        for col in cols:
            neg = int((frame[col] < -0.01).sum())
            results.append(QualityResult(f"{table}.{col} >= 0", neg == 0, f"{neg} negatives"))
    return results


def _status_values(tables: dict[str, pd.DataFrame]) -> list[QualityResult]:
    allowed = {"Idea", "Assessment", "Pilot", "Production", "Scaling", "Paused", "Retired"}
    bad = int((~tables["ai_use_cases"]["status"].isin(allowed)).sum())
    return [QualityResult("use_case.status enum", bad == 0, f"{bad} invalid")]


def _date_validity(tables: dict[str, pd.DataFrame]) -> list[QualityResult]:
    results = []
    licenses = tables["licenses"]
    invalid = int(pd.to_datetime(licenses["assigned_date"], errors="coerce").isna().sum())
    results.append(QualityResult("licenses.assigned_date parseable", invalid == 0, f"{invalid} invalid"))
    return results
