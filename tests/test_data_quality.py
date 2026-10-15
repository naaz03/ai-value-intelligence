from __future__ import annotations

from generators.quality import run_quality_checks
from services.data_service import read_table


def test_core_quality_checks(tables):
    quality_tables = {
        "organizations": tables["organizations"],
        "business_units": tables["business_units"],
        "departments": tables["departments"],
        "employees": tables["employees"],
        "ai_products": tables["ai_products"],
        "licenses": tables["licenses"],
        "ai_usage": read_table("ai_usage"),
        "ai_use_cases": tables["ai_use_cases"],
        "financial_benefits": tables["financial_benefits"],
        "ai_costs": tables["ai_costs"],
    }
    results = run_quality_checks(quality_tables)
    failed = [r for r in results if not r.passed]
    assert not failed, "; ".join(f"{r.name}: {r.detail}" for r in failed)


def test_scale_and_reproducibility_bounds(tables):
    assert 11_000 <= len(tables["employees"]) <= 13_000
    assert 4_000 <= tables["licenses"]["employee_id"].nunique() <= 8_500
    assert 50 <= len(tables["ai_use_cases"]) <= 120
    assert len(tables["business_units"]) == 12
    assert tables["organizations"].iloc[0]["organization_name"] == "Al Noor Holdings PJSC"


def test_story_use_cases_present(tables):
    names = set(tables["ai_use_cases"]["use_case_name"])
    assert "Engineering code completion" in names
    assert "Executive briefing agent" in names
    assert "AP invoice exception triage" in names
    retired = tables["ai_use_cases"].loc[tables["ai_use_cases"]["use_case_name"] == "Executive briefing agent"]
    assert retired.iloc[0]["status"] == "Retired"
