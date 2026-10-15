from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseModel):
    app_name: str = "AI Value Intelligence"
    app_subtitle: str = "Measure Adoption. Prove Value. Optimize AI Investment."
    organization_name: str = "Al Noor Holdings PJSC"
    currency: str = "USD"
    currency_symbol: str = "$"
    seed: int = 42
    history_months: int = 36
    employee_count: int = 12_000
    target_licensed_employees: int = 5_600
    working_hours_per_year: int = 1_880
    default_realization_factor: float = 0.35
    generated_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "data" / "generated")
    reference_dir: Path = Field(default_factory=lambda: PROJECT_ROOT / "data" / "reference")
    duckdb_path: Path = Field(default_factory=lambda: PROJECT_ROOT / "data" / "generated" / "ai_value.duckdb")
    forecast_horizon_months: int = 24
    inactive_thresholds_days: tuple[int, int, int] = (30, 60, 90)


SETTINGS = Settings()
