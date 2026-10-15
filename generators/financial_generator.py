from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from config.constants import BENEFIT_REALIZATION
from generators.productivity_generator import department_realization


def generate_financials(
    use_cases: pd.DataFrame,
    licenses: pd.DataFrame,
    usage: pd.DataFrame,
    productivity: pd.DataFrame,
    employees: pd.DataFrame,
    months: list[date],
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    license_month = _license_cost_by_dept_month(licenses, employees, months)
    compute_month = (
        usage.groupby(["date", "department_id"], as_index=False)["estimated_compute_cost"]
        .sum()
        .rename(columns={"estimated_compute_cost": "compute_cost"})
    )
    hours_by_uc_month = (
        productivity.groupby(["date", "use_case_id"], as_index=False)
        .agg(hours_saved=("hours_saved", "sum"), tasks=("tasks_completed", "sum"))
        if not productivity.empty
        else pd.DataFrame(columns=["date", "use_case_id", "hours_saved", "tasks"])
    )

    cost_rows: list[dict] = []
    benefit_rows: list[dict] = []
    benefit_n = 1

    for uc in use_cases.itertuples(index=False):
        start = pd.Timestamp(uc.start_date)
        retire_after = uc.retire_after if pd.notna(uc.retire_after) else None
        realization = department_realization(uc.department_id, uc.realization_override)
        benefit_real = BENEFIT_REALIZATION.get(uc.benefit_type, 0.32)
        realization = float(np.clip(0.55 * realization + 0.45 * benefit_real, 0.02, 0.85))
        if uc.realization_override is not None and pd.notna(uc.realization_override):
            realization = float(uc.realization_override)

        monthly_expected = float(uc.expected_value) / 12.0
        impl_total = float(uc.implementation_cost)
        annual_op = float(uc.annual_operating_cost)

        for i, month in enumerate(months):
            ts = pd.Timestamp(month)
            if ts < start:
                continue
            months_live = (ts.year - start.year) * 12 + ts.month - start.month
            if retire_after is not None and months_live > int(retire_after):
                continue
            if uc.status in {"Idea"} and months_live > 2:
                continue

            ramp = _value_ramp(months_live, uc.status, uc.story)
            season = 0.86 if month.month in {7, 8} else 1.0
            noise = float(rng.normal(1.0, 0.06))
            potential = max(0.0, monthly_expected * ramp * season * noise)

            evidence = float(uc.evidence_factor) * ramp
            if uc.story == "finance_training_lift" and months_live >= 10:
                evidence = min(0.88, evidence + 0.18)
            demonstrated = min(potential, potential * evidence)
            realized = min(demonstrated, demonstrated * realization)
            # Story 15: realized trails demonstrated at portfolio level
            if uc.story is None:
                realized *= 0.92

            finance_share = 0.78 if uc.benefit_type in {"Cost Avoidance", "Cost Reduction"} else 0.36
            if uc.story == "marketing_usage_no_cash":
                finance_share = 0.08
            if uc.story == "procurement_roi":
                finance_share = 0.82
            if uc.story == "failed_agent_pilot":
                finance_share = 0.05
            finance_validated = bool(rng.random() < finance_share)

            hour_row = hours_by_uc_month[
                (hours_by_uc_month["use_case_id"] == uc.use_case_id) & (hours_by_uc_month["date"] == month)
            ]
            hours = float(hour_row["hours_saved"].sum()) if not hour_row.empty else 0.0

            dept_lic = license_month[
                (license_month["date"] == month) & (license_month["department_id"] == uc.department_id)
            ]
            dept_compute = compute_month[
                (compute_month["date"] == month) & (compute_month["department_id"] == uc.department_id)
            ]
            dept_uc_count = max(
                1,
                int(
                    (
                        (use_cases["department_id"] == uc.department_id)
                        & (pd.to_datetime(use_cases["start_date"]) <= ts)
                    ).sum()
                ),
            )
            license_cost = float(dept_lic["license_cost"].sum()) / dept_uc_count if not dept_lic.empty else 0.0
            infra = float(dept_compute["compute_cost"].sum()) / dept_uc_count if not dept_compute.empty else 0.0
            if uc.ai_product == "PRD-AZ-OAI":
                infra *= 2.4 * (1 + months_live / 20)
            impl = impl_total / 6.0 if months_live < 6 else 0.0
            support = annual_op / 12.0 * 0.35
            training = annual_op / 12.0 * (0.22 if months_live < 4 else 0.08)
            security = annual_op / 12.0 * 0.12
            governance = annual_op / 12.0 * 0.10
            if uc.story == "failed_agent_pilot":
                support *= 1.8
                governance *= 1.6
                impl = impl_total / 8.0 if months_live < 8 else impl_total / 20.0

            total_cost = license_cost + infra + impl + support + training + security + governance

            cost_rows.append(
                {
                    "month": month,
                    "use_case_id": uc.use_case_id,
                    "department_id": uc.department_id,
                    "business_unit_id": uc.business_unit_id,
                    "license_cost": round(license_cost, 2),
                    "infrastructure_cost": round(infra, 2),
                    "implementation_cost": round(impl, 2),
                    "support_cost": round(support, 2),
                    "training_cost": round(training, 2),
                    "security_cost": round(security, 2),
                    "governance_cost": round(governance, 2),
                    "total_cost": round(total_cost, 2),
                }
            )
            benefit_rows.append(
                {
                    "benefit_id": f"BEN-{benefit_n:07d}",
                    "use_case_id": uc.use_case_id,
                    "month": month,
                    "department_id": uc.department_id,
                    "business_unit_id": uc.business_unit_id,
                    "benefit_type": uc.benefit_type,
                    "potential_value": round(potential, 2),
                    "demonstrated_value": round(demonstrated, 2),
                    "realized_value": round(realized, 2),
                    "finance_validated": finance_validated,
                    "benefit_owner": uc.business_owner,
                    "hours_saved": round(hours, 2),
                }
            )
            benefit_n += 1

    costs = pd.DataFrame(cost_rows)
    benefits = pd.DataFrame(benefit_rows)
    if not benefits.empty:
        # Guardrail: Potential >= Demonstrated >= Realized
        benefits["demonstrated_value"] = benefits[["potential_value", "demonstrated_value"]].min(axis=1)
        benefits["realized_value"] = benefits[["demonstrated_value", "realized_value"]].min(axis=1)
    return costs, benefits


def _license_cost_by_dept_month(
    licenses: pd.DataFrame,
    employees: pd.DataFrame,
    months: list[date],
) -> pd.DataFrame:
    merged = licenses.merge(
        employees[["employee_id", "department_id"]],
        on="employee_id",
        how="left",
    )
    rows: list[dict] = []
    for month in months:
        ts = pd.Timestamp(month)
        active = merged[(pd.to_datetime(merged["assigned_date"]) <= ts) & (merged["license_status"] == "Active")]
        grouped = active.groupby("department_id", as_index=False)["monthly_cost"].sum()
        grouped["date"] = month
        grouped = grouped.rename(columns={"monthly_cost": "license_cost"})
        rows.append(grouped)
    if not rows:
        return pd.DataFrame(columns=["department_id", "license_cost", "date"])
    return pd.concat(rows, ignore_index=True)


def _value_ramp(months_live: int, status: str, story: str | None) -> float:
    if status in {"Idea", "Assessment"}:
        return 0.08 if months_live >= 0 else 0.0
    if status == "Paused":
        return 0.12
    if story == "failed_agent_pilot":
        return max(0.05, 0.35 - months_live * 0.03)
    if story == "scaling_winner":
        return min(1.15, 0.35 + months_live * 0.07)
    if status == "Pilot":
        return min(0.55, 0.20 + months_live * 0.04)
    if status == "Production":
        return min(1.0, 0.40 + months_live * 0.06)
    if status == "Scaling":
        return min(1.20, 0.50 + months_live * 0.07)
    if status == "Retired":
        return 0.05
    return min(0.9, 0.3 + months_live * 0.05)
