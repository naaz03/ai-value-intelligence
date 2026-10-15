from __future__ import annotations

import pandas as pd

from config.settings import SETTINGS
from services.data_service import read_table


class SyntheticAdapter:
    """Reads locally generated Parquet / DuckDB tables."""

    name = "synthetic_al_noor"

    def load_organizations(self) -> pd.DataFrame:
        return read_table("organizations")

    def load_business_units(self) -> pd.DataFrame:
        return read_table("business_units")

    def load_departments(self) -> pd.DataFrame:
        return read_table("departments")

    def load_employees(self) -> pd.DataFrame:
        return read_table("employees")

    def load_products(self) -> pd.DataFrame:
        return read_table("ai_products")

    def load_licenses(self) -> pd.DataFrame:
        return read_table("licenses")

    def load_usage(self) -> pd.DataFrame:
        return read_table("ai_usage")

    def load_use_cases(self) -> pd.DataFrame:
        return read_table("ai_use_cases")

    def load_productivity(self) -> pd.DataFrame:
        return read_table("productivity_metrics")

    def load_benefits(self) -> pd.DataFrame:
        return read_table("financial_benefits")

    def load_costs(self) -> pd.DataFrame:
        return read_table("ai_costs")

    @property
    def source_path(self):
        return SETTINGS.duckdb_path
