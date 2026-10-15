from __future__ import annotations

from services.roi_service import methodology_kpis, simulate
from utils.calculations import benefit_cost_ratio, fte_equivalent, net_benefit, payback_months, roi_pct, realized_from_hours


def test_roi_formula():
    assert roi_pct(150, 100) == 0.5
    assert roi_pct(80, 100) == -0.2
    assert roi_pct(10, 0) == 0.0


def test_net_benefit_and_bcr():
    assert net_benefit(250, 100) == 150
    assert benefit_cost_ratio(250, 100) == 2.5
    assert benefit_cost_ratio(10, 0) == 0.0


def test_payback():
    assert payback_months(120, 10) == 12
    assert payback_months(120, 0) is None


def test_hours_are_not_automatically_cash():
    hours = 100_000
    hourly = 50
    assert realized_from_hours(hours, hourly, 1.0) == 5_000_000
    assert realized_from_hours(hours, hourly, 0.35) == 1_750_000
    assert realized_from_hours(hours, hourly, 0.0) == 0


def test_fte_equivalent():
    assert fte_equivalent(1_880, 1_880) == 1
    assert fte_equivalent(0, 1_880) == 0


def test_simulator_respects_realization_and_success():
    full = simulate(1000, 30, 0.5, 40, 50, 1.0, 0, 0, 0, 1.0, years=1)
    half = simulate(1000, 30, 0.5, 40, 50, 0.5, 0, 0, 0, 1.0, years=1)
    fail = simulate(1000, 30, 0.5, 40, 50, 1.0, 0, 0, 0, 0.0, years=1)
    assert half["realized_value"] == pytest_approx(full["realized_value"] * 0.5)
    assert fail["realized_value"] == 0
    assert full["projected_cost"] == 1000 * 30 * 12


def test_methodology_kpis_keep_cash_below_planning(tables):
    from models.schemas import FilterState

    months = tables["mart_month_enterprise"]["month"]
    kpis = methodology_kpis(FilterState(start_date=months.min().date(), end_date=months.max().date()))
    assert kpis["planning_roi"] >= kpis["evidence_roi"] - 1e-9
    assert kpis["evidence_roi"] >= kpis["cash_roi"] - 1e-9
    assert 0 <= kpis["realization_rate"] <= 1
    assert kpis["reclaimed_seat_roi"] >= kpis["cash_roi"] - 1e-9


def pytest_approx(value):
    import pytest

    return pytest.approx(value)
