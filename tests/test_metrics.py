from __future__ import annotations

from datetime import date

from models.schemas import FilterState
from services.metric_service import portfolio_kpis, usecase_mart
from utils.calculations import roi_pct


def _filters(tables) -> FilterState:
    months = tables["mart_month_enterprise"]["month"]
    return FilterState(start_date=months.min().date(), end_date=months.max().date())


def test_kpis_reconcile_to_usecase_mart(tables):
    filters = _filters(tables)
    k = portfolio_kpis(filters)
    uc = usecase_mart(filters)
    assert k["potential_value"] == pytest_approx(float(uc["potential_value"].sum()), rel=1e-6)
    assert k["demonstrated_value"] == pytest_approx(float(uc["demonstrated_value"].sum()), rel=1e-6)
    assert k["realized_value"] == pytest_approx(float(uc["realized_value"].sum()), rel=1e-6)
    assert k["total_cost"] == pytest_approx(float(uc["total_cost"].sum()), rel=1e-6)
    assert k["net_benefit"] == pytest_approx(k["realized_value"] - k["total_cost"], rel=1e-6)
    assert k["portfolio_roi"] == pytest_approx(roi_pct(k["realized_value"], k["total_cost"]))


def test_value_hierarchy_in_kpis(tables):
    k = portfolio_kpis(_filters(tables))
    assert k["potential_value"] >= k["demonstrated_value"] - 1e-6
    assert k["demonstrated_value"] >= k["realized_value"] - 1e-6


def test_hours_not_equal_realized(tables):
    k = portfolio_kpis(_filters(tables))
    naive_cash = k["hours_saved"] * 45
    assert k["realized_value"] != pytest_approx(naive_cash, rel=0.02)
    assert k["hours_saved"] > 0


def test_adoption_between_zero_and_one(tables):
    k = portfolio_kpis(_filters(tables))
    assert 0 <= k["adoption_rate"] <= 1
    assert k["licensed_users"] >= k["active_users"]


def pytest_approx(value, rel=1e-6):
    import pytest

    return pytest.approx(value, rel=rel)
