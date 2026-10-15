from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class FilterState(BaseModel):
    start_date: date
    end_date: date
    business_units: list[str] = Field(default_factory=list)
    departments: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    vendors: list[str] = Field(default_factory=list)
    use_cases: list[str] = Field(default_factory=list)
    statuses: list[str] = Field(default_factory=list)
    risk_ratings: list[str] = Field(default_factory=list)
    job_levels: list[str] = Field(default_factory=list)

    def is_unfiltered(self) -> bool:
        return not any(
            [
                self.business_units,
                self.departments,
                self.countries,
                self.products,
                self.vendors,
                self.use_cases,
                self.statuses,
                self.risk_ratings,
                self.job_levels,
            ]
        )


class Organization(BaseModel):
    organization_id: str
    organization_name: str
    country: str
    industry: str
    employee_count: int
    annual_revenue: float
    ai_strategy_maturity: str


class BusinessUnit(BaseModel):
    business_unit_id: str
    business_unit_name: str
    executive_owner: str
    annual_budget: float
    employee_count: int


class Department(BaseModel):
    department_id: str
    department_name: str
    business_unit_id: str
    cost_center: str
    employee_count: int


class Employee(BaseModel):
    employee_id: str
    department_id: str
    business_unit_id: str
    country: str
    job_level: str
    job_family: str
    annual_salary: float
    hourly_cost: float
    manager_flag: bool
    ai_training_completed: bool
    ai_training_date: date | None = None
    join_date: date


class AIProduct(BaseModel):
    product_id: str
    product_name: str
    vendor: str
    product_category: str
    pricing_model: str
    monthly_unit_cost: float


class License(BaseModel):
    license_id: str
    employee_id: str
    product_id: str
    assigned_date: date
    license_status: str
    monthly_cost: float


class AIUseCase(BaseModel):
    use_case_id: str
    use_case_name: str
    business_unit: str
    department: str
    business_owner: str
    technology_owner: str
    ai_product: str
    use_case_category: str
    implementation_cost: float
    annual_operating_cost: float
    start_date: date
    status: str
    risk_rating: str
    expected_value: float
    expected_hours_saved: float
    target_users: int
