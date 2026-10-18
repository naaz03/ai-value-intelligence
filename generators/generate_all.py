from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import SETTINGS
from generators.employee_generator import generate_employees
from generators.financial_generator import generate_financials
from generators.license_generator import generate_licenses, generate_products
from generators.organization_generator import generate_business_units, generate_departments, generate_organizations
from generators.productivity_generator import generate_productivity
from generators.quality import run_quality_checks
from generators.usage_generator import generate_usage
from generators.use_case_generator import generate_use_cases
from services.storage import duckdb_available, write_duckdb_if_available, write_manifest, write_table
from utils.helpers import ensure_generated_dir, month_starts


TABLES = (
    "organizations",
    "business_units",
    "departments",
    "employees",
    "ai_products",
    "licenses",
    "ai_usage",
    "ai_use_cases",
    "productivity_metrics",
    "financial_benefits",
    "ai_costs",
    "mart_month_enterprise",
    "mart_month_department",
    "mart_month_bu",
    "mart_month_product",
    "mart_month_usecase",
    "mart_license_status",
    "mart_employee_segment",
)


def build_datasets(seed: int | None = None) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed or SETTINGS.seed)
    end = date.today().replace(day=1)
    months = month_starts(end, SETTINGS.history_months)

    organizations = generate_organizations()
    business_units = generate_business_units()
    departments = generate_departments()
    employees = generate_employees(departments, months, rng)
    products = generate_products()
    licenses = generate_licenses(employees, products, months, rng)
    usage = generate_usage(employees, licenses, months, rng)
    use_cases = generate_use_cases(departments, months, rng)
    productivity = generate_productivity(employees, use_cases, usage, months, rng)
    costs, benefits = generate_financials(use_cases, licenses, usage, productivity, employees, months, rng)

    marts = build_marts(
        employees=employees,
        departments=departments,
        business_units=business_units,
        products=products,
        licenses=licenses,
        usage=usage,
        use_cases=use_cases,
        productivity=productivity,
        costs=costs,
        benefits=benefits,
        months=months,
    )
    return {
        "organizations": organizations,
        "business_units": business_units,
        "departments": departments,
        "employees": employees,
        "ai_products": products,
        "licenses": licenses,
        "ai_usage": usage,
        "ai_use_cases": use_cases,
        "productivity_metrics": productivity,
        "financial_benefits": benefits,
        "ai_costs": costs,
        **marts,
    }


def build_marts(
    employees: pd.DataFrame,
    departments: pd.DataFrame,
    business_units: pd.DataFrame,
    products: pd.DataFrame,
    licenses: pd.DataFrame,
    usage: pd.DataFrame,
    use_cases: pd.DataFrame,
    productivity: pd.DataFrame,
    costs: pd.DataFrame,
    benefits: pd.DataFrame,
    months: list[date],
) -> dict[str, pd.DataFrame]:
    as_of = months[-1]
    dept_names = departments.set_index("department_id")["department_name"]
    bu_names = business_units.set_index("business_unit_id")["business_unit_name"]
    product_names = products.set_index("product_id")["product_name"]
    vendors = products.set_index("product_id")["vendor"]

    usage = usage.copy()
    usage["date"] = pd.to_datetime(usage["date"]).dt.date
    costs = costs.copy()
    costs["month"] = pd.to_datetime(costs["month"]).dt.date
    benefits = benefits.copy()
    benefits["month"] = pd.to_datetime(benefits["month"]).dt.date

    uc_month = (
        benefits.merge(costs, on=["month", "use_case_id", "department_id", "business_unit_id"], how="outer")
        .merge(
            use_cases[
                [
                    "use_case_id",
                    "use_case_name",
                    "status",
                    "risk_rating",
                    "ai_product",
                    "expected_value",
                    "implementation_cost",
                    "story",
                ]
            ],
            on="use_case_id",
            how="left",
        )
        .fillna(
            {
                "potential_value": 0,
                "demonstrated_value": 0,
                "realized_value": 0,
                "total_cost": 0,
                "license_cost": 0,
                "infrastructure_cost": 0,
                "implementation_cost_y": 0,
                "hours_saved": 0,
            }
        )
    )
    if "implementation_cost_x" in uc_month.columns:
        uc_month["implementation_cost"] = uc_month["implementation_cost_x"]
    uc_month["department_name"] = uc_month["department_id"].map(dept_names)
    uc_month["business_unit_name"] = uc_month["business_unit_id"].map(bu_names)
    uc_month["product_name"] = uc_month["ai_product"].map(product_names)
    uc_month["vendor"] = uc_month["ai_product"].map(vendors)
    validated_flag = uc_month["finance_validated"] if "finance_validated" in uc_month.columns else False
    if isinstance(validated_flag, pd.Series):
        validated_flag = validated_flag.fillna(False).astype(bool)
    uc_month["finance_validated_value"] = np.where(validated_flag, uc_month["realized_value"], 0.0)

    hours = (
        productivity.groupby(["date", "use_case_id"], as_index=False)["hours_saved"].sum()
        if not productivity.empty
        else pd.DataFrame(columns=["date", "use_case_id", "hours_saved"])
    )
    if not hours.empty:
        hours["date"] = pd.to_datetime(hours["date"]).dt.date
        uc_month = uc_month.merge(
            hours.rename(columns={"date": "month", "hours_saved": "hours_saved_ops"}),
            on=["month", "use_case_id"],
            how="left",
        )
        uc_month["hours_saved"] = uc_month["hours_saved_ops"].fillna(uc_month.get("hours_saved", 0))

    mart_usecase = uc_month.copy()

    value_dept = mart_usecase.groupby(["month", "department_id", "business_unit_id"], as_index=False).agg(
        potential_value=("potential_value", "sum"),
        demonstrated_value=("demonstrated_value", "sum"),
        realized_value=("realized_value", "sum"),
        total_cost=("total_cost", "sum"),
        license_cost=("license_cost", "sum"),
        infrastructure_cost=("infrastructure_cost", "sum"),
        hours_saved=("hours_saved", "sum"),
        finance_validated_value=("finance_validated_value", "sum"),
    )
    usage_dept = usage.groupby(["date", "department_id", "business_unit_id"], as_index=False).agg(
        active_users=("employee_id", lambda s: s[usage.loc[s.index, "active_flag"]].nunique() if len(s) else 0),
        licensed_users=("employee_id", "nunique"),
        sessions=("sessions", "sum"),
        prompts=("prompts", "sum"),
        tasks_completed=("tasks_completed", "sum"),
        tokens_consumed=("tokens_consumed", "sum"),
    )
    # Fix active users properly
    active_users = (
        usage.loc[usage["active_flag"]]
        .groupby(["date", "department_id"], as_index=False)["employee_id"]
        .nunique()
        .rename(columns={"employee_id": "active_users", "date": "month"})
    )
    licensed_users = (
        usage.groupby(["date", "department_id"], as_index=False)["employee_id"]
        .nunique()
        .rename(columns={"employee_id": "licensed_users", "date": "month"})
    )
    usage_vol = usage.groupby(["date", "department_id", "business_unit_id"], as_index=False).agg(
        sessions=("sessions", "sum"),
        prompts=("prompts", "sum"),
        tasks_completed=("tasks_completed", "sum"),
        tokens_consumed=("tokens_consumed", "sum"),
        compute_cost=("estimated_compute_cost", "sum"),
    )
    usage_vol = usage_vol.rename(columns={"date": "month"})
    mart_dept = (
        value_dept.merge(active_users, on=["month", "department_id"], how="left")
        .merge(licensed_users, on=["month", "department_id"], how="left")
        .merge(usage_vol, on=["month", "department_id", "business_unit_id"], how="left")
        .fillna(0)
    )
    mart_dept["department_name"] = mart_dept["department_id"].map(dept_names)
    mart_dept["business_unit_name"] = mart_dept["business_unit_id"].map(bu_names)

    mart_bu = mart_dept.groupby(["month", "business_unit_id", "business_unit_name"], as_index=False).agg(
        potential_value=("potential_value", "sum"),
        demonstrated_value=("demonstrated_value", "sum"),
        realized_value=("realized_value", "sum"),
        total_cost=("total_cost", "sum"),
        license_cost=("license_cost", "sum"),
        infrastructure_cost=("infrastructure_cost", "sum"),
        hours_saved=("hours_saved", "sum"),
        finance_validated_value=("finance_validated_value", "sum"),
        active_users=("active_users", "sum"),
        licensed_users=("licensed_users", "sum"),
        sessions=("sessions", "sum"),
        tasks_completed=("tasks_completed", "sum"),
    )

    mart_ent = mart_bu.groupby("month", as_index=False).agg(
        potential_value=("potential_value", "sum"),
        demonstrated_value=("demonstrated_value", "sum"),
        realized_value=("realized_value", "sum"),
        total_cost=("total_cost", "sum"),
        license_cost=("license_cost", "sum"),
        infrastructure_cost=("infrastructure_cost", "sum"),
        hours_saved=("hours_saved", "sum"),
        finance_validated_value=("finance_validated_value", "sum"),
        active_users=("active_users", "sum"),
        licensed_users=("licensed_users", "sum"),
        sessions=("sessions", "sum"),
        tasks_completed=("tasks_completed", "sum"),
    )

    usage_product = usage.groupby(["date", "product_id"], as_index=False).agg(
        active_users=("employee_id", lambda s: usage.loc[s.index, "employee_id"][usage.loc[s.index, "active_flag"]].nunique()),
        licensed_users=("employee_id", "nunique"),
        sessions=("sessions", "sum"),
        tasks_completed=("tasks_completed", "sum"),
        tokens_consumed=("tokens_consumed", "sum"),
        compute_cost=("estimated_compute_cost", "sum"),
    )
    active_prod = (
        usage.loc[usage["active_flag"]]
        .groupby(["date", "product_id"], as_index=False)["employee_id"]
        .nunique()
        .rename(columns={"employee_id": "active_users", "date": "month"})
    )
    lic_prod = (
        usage.groupby(["date", "product_id"], as_index=False)["employee_id"]
        .nunique()
        .rename(columns={"employee_id": "licensed_users", "date": "month"})
    )
    vol_prod = usage.groupby(["date", "product_id"], as_index=False).agg(
        sessions=("sessions", "sum"),
        tasks_completed=("tasks_completed", "sum"),
        tokens_consumed=("tokens_consumed", "sum"),
        compute_cost=("estimated_compute_cost", "sum"),
    ).rename(columns={"date": "month"})
    value_prod = (
        mart_usecase.groupby(["month", "ai_product"], as_index=False)
        .agg(
            potential_value=("potential_value", "sum"),
            demonstrated_value=("demonstrated_value", "sum"),
            realized_value=("realized_value", "sum"),
            total_cost=("total_cost", "sum"),
        )
        .rename(columns={"ai_product": "product_id"})
    )
    mart_product = (
        vol_prod.merge(active_prod, on=["month", "product_id"], how="outer")
        .merge(lic_prod, on=["month", "product_id"], how="outer")
        .merge(value_prod, on=["month", "product_id"], how="outer")
        .fillna(0)
    )
    mart_product["product_name"] = mart_product["product_id"].map(product_names)
    mart_product["vendor"] = mart_product["product_id"].map(vendors)

    # License status snapshot from last 3 months of usage
    recent = [m for m in months if (pd.Timestamp(as_of) - pd.Timestamp(m)).days <= 93]
    usage_recent = usage[usage["date"].isin(recent)]
    last_active = (
        usage.loc[usage["active_flag"]]
        .groupby(["employee_id", "product_id"], as_index=False)["date"]
        .max()
        .rename(columns={"date": "last_active_date"})
    )
    ever_active = (
        usage.loc[usage["active_flag"]]
        .groupby(["employee_id", "product_id"], as_index=False)
        .size()
        .rename(columns={"size": "active_months"})
    )
    recent_sessions = usage_recent.groupby(["employee_id", "product_id"], as_index=False).agg(
        recent_sessions=("sessions", "sum"),
        recent_active_months=("active_flag", "sum"),
    )
    snapshot = licenses.merge(employees, on="employee_id", how="left")
    snapshot = snapshot.merge(last_active, on=["employee_id", "product_id"], how="left")
    snapshot = snapshot.merge(ever_active, on=["employee_id", "product_id"], how="left")
    snapshot = snapshot.merge(recent_sessions, on=["employee_id", "product_id"], how="left")
    snapshot["active_months"] = snapshot["active_months"].fillna(0)
    snapshot["recent_sessions"] = snapshot["recent_sessions"].fillna(0)
    snapshot["recent_active_months"] = snapshot["recent_active_months"].fillna(0)
    snapshot["days_inactive"] = snapshot["last_active_date"].apply(
        lambda d: (pd.Timestamp(as_of) - pd.Timestamp(d)).days if pd.notna(d) else 999
    )
    snapshot["segment"] = snapshot.apply(_segment_row, axis=1)
    snapshot["annual_cost"] = snapshot["monthly_cost"] * 12
    snapshot["product_name"] = snapshot["product_id"].map(product_names)
    snapshot["vendor"] = snapshot["product_id"].map(vendors)
    snapshot["department_name"] = snapshot["department_id"].map(dept_names)
    snapshot["business_unit_name"] = snapshot["business_unit_id"].map(bu_names)
    snapshot["as_of_date"] = as_of

    overlap = (
        snapshot.groupby("employee_id")["product_id"]
        .nunique()
        .reset_index(name="product_count")
    )
    snapshot = snapshot.merge(overlap, on="employee_id", how="left")

    # Employee segment from latest persona / activity
    latest_usage = usage[usage["date"] == as_of]
    if latest_usage.empty:
        latest_usage = usage[usage["date"] == usage["date"].max()]
    emp_seg = latest_usage.groupby("employee_id", as_index=False).agg(
        sessions=("sessions", "sum"),
        active_flag=("active_flag", "max"),
    )
    emp_seg = emp_seg.merge(
        snapshot.groupby("employee_id", as_index=False).agg(
            segment=("segment", "first"),
            department_id=("department_id", "first"),
            business_unit_id=("business_unit_id", "first"),
            job_level=("job_level", "first"),
            country=("country", "first"),
            ai_training_completed=("ai_training_completed", "first"),
        ),
        on="employee_id",
        how="outer",
    )
    emp_seg["department_name"] = emp_seg["department_id"].map(dept_names)
    emp_seg["business_unit_name"] = emp_seg["business_unit_id"].map(bu_names)

    # Drop unused local
    del usage_dept
    del usage_product

    return {
        "mart_month_enterprise": mart_ent,
        "mart_month_department": mart_dept,
        "mart_month_bu": mart_bu,
        "mart_month_product": mart_product,
        "mart_month_usecase": mart_usecase,
        "mart_license_status": snapshot,
        "mart_employee_segment": emp_seg,
    }


def _segment_row(row: pd.Series) -> str:
    if row["active_months"] == 0:
        return "Never Activated"
    if row["days_inactive"] >= 90 and row["active_months"] <= 3:
        return "Abandoned"
    if row["days_inactive"] >= 60:
        return "Inactive"
    if row["recent_sessions"] >= 45:
        return "Power User"
    if row["recent_sessions"] >= 16:
        return "Regular User"
    if row["recent_sessions"] >= 1:
        return "Occasional User"
    return "Inactive"


def persist(tables: dict[str, pd.DataFrame]) -> Path:
    out = ensure_generated_dir()
    for name, frame in tables.items():
        write_table(name, frame, out)

    db_path = write_duckdb_if_available(list(tables.keys()), out)
    write_manifest(
        tables,
        out,
        extra={"duckdb_written": bool(db_path), "duckdb_available": duckdb_available()},
    )
    return db_path or (out / "manifest.json")


def generate_and_save(seed: int | None = None) -> dict[str, pd.DataFrame]:
    tables = build_datasets(seed=seed)
    persist(tables)
    return tables


def main() -> None:
    print("Generating Al Noor Holdings synthetic enterprise...")
    tables = generate_and_save()
    results = run_quality_checks(tables)
    failed = [r for r in results if not r.passed]
    print("\nDataset summary")
    for name in TABLES:
        print(f"  {name:28s} {len(tables[name]):>9,} rows")
    print(f"\nQuality checks: {len(results) - len(failed)} passed / {len(results)} total")
    if failed:
        print("Failures:")
        for item in failed:
            print(f"  - {item.name}: {item.detail}")
        raise SystemExit(1)
    if duckdb_available() and SETTINGS.duckdb_path.exists():
        print(f"\nDuckDB written to {SETTINGS.duckdb_path}")
    else:
        print("\nDuckDB skipped (not installed). Portable JSON.gz + Parquet written under data/generated/.")


if __name__ == "__main__":
    main()
