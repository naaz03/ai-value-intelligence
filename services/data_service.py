from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import duckdb
import pandas as pd

from config.settings import SETTINGS
from models.schemas import FilterState


def data_ready() -> bool:
    return SETTINGS.duckdb_path.exists() and (SETTINGS.generated_dir / "mart_month_enterprise.parquet").exists()


def ensure_data() -> None:
    if data_ready():
        return
    from generators.generate_all import generate_and_save

    generate_and_save()


def read_table(name: str) -> pd.DataFrame:
    ensure_data()
    path = SETTINGS.generated_dir / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing generated table {name}: {path}")
    frame = pd.read_parquet(path)
    return _normalize_dates(frame)


def _normalize_dates(frame: pd.DataFrame) -> pd.DataFrame:
    for col in ("date", "month", "assigned_date", "start_date", "join_date", "ai_training_date", "last_active_date", "as_of_date"):
        if col in frame.columns:
            frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frame


@lru_cache(maxsize=1)
def cached_tables() -> dict[str, pd.DataFrame]:
    ensure_data()
    names = [
        "organizations",
        "business_units",
        "departments",
        "employees",
        "ai_products",
        "licenses",
        "ai_use_cases",
        "financial_benefits",
        "ai_costs",
        "productivity_metrics",
        "mart_month_enterprise",
        "mart_month_department",
        "mart_month_bu",
        "mart_month_product",
        "mart_month_usecase",
        "mart_license_status",
        "mart_employee_segment",
    ]
    return {name: read_table(name) for name in names}


def duckdb_connect() -> duckdb.DuckDBPyConnection:
    ensure_data()
    return duckdb.connect(str(SETTINGS.duckdb_path), read_only=True)


def filter_options() -> dict[str, list]:
    tables = cached_tables()
    dept = tables["departments"]
    bu = tables["business_units"]
    products = tables["ai_products"]
    use_cases = tables["ai_use_cases"]
    employees = tables["employees"]
    dates = tables["mart_month_enterprise"]["month"].dropna().sort_values()
    return {
        "business_units": sorted(bu["business_unit_name"].tolist()),
        "departments": sorted(dept["department_name"].tolist()),
        "countries": sorted(employees["country"].dropna().unique().tolist()),
        "products": sorted(products["product_name"].tolist()),
        "vendors": sorted(products["vendor"].unique().tolist()),
        "use_cases": sorted(use_cases["use_case_name"].tolist()),
        "statuses": sorted(use_cases["status"].unique().tolist()),
        "risk_ratings": sorted(use_cases["risk_rating"].unique().tolist()),
        "job_levels": sorted(employees["job_level"].unique().tolist()),
        "min_date": dates.min().date(),
        "max_date": dates.max().date(),
    }


def apply_time(frame: pd.DataFrame, filters: FilterState, col: str = "month") -> pd.DataFrame:
    if col not in frame.columns or frame.empty:
        return frame
    start = pd.Timestamp(filters.start_date)
    end = pd.Timestamp(filters.end_date)
    series = pd.to_datetime(frame[col])
    return frame.loc[(series >= start) & (series <= end)].copy()


def apply_filters(frame: pd.DataFrame, filters: FilterState, date_col: str = "month") -> pd.DataFrame:
    out = apply_time(frame, filters, date_col)
    mapping = {
        "business_unit_name": filters.business_units,
        "department_name": filters.departments,
        "country": filters.countries,
        "product_name": filters.products,
        "vendor": filters.vendors,
        "use_case_name": filters.use_cases,
        "status": filters.statuses,
        "risk_rating": filters.risk_ratings,
        "job_level": filters.job_levels,
    }
    for column, selected in mapping.items():
        if selected and column in out.columns:
            out = out[out[column].isin(selected)]
    return out.reset_index(drop=True)


def lookup_maps() -> dict[str, dict]:
    tables = cached_tables()
    dept = tables["departments"]
    bu = tables["business_units"]
    products = tables["ai_products"]
    return {
        "dept_to_name": dict(zip(dept["department_id"], dept["department_name"])),
        "bu_to_name": dict(zip(bu["business_unit_id"], bu["business_unit_name"])),
        "product_to_name": dict(zip(products["product_id"], products["product_name"])),
        "product_to_vendor": dict(zip(products["product_id"], products["vendor"])),
        "dept_to_bu": dict(zip(dept["department_id"], dept["business_unit_id"])),
    }


def parquet_path(name: str) -> Path:
    return SETTINGS.generated_dir / f"{name}.parquet"
