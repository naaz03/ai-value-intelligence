from __future__ import annotations

from config.settings import SETTINGS

COUNTRIES = ("UAE", "Saudi Arabia", "Qatar", "Bahrain", "Oman", "Kuwait")

COUNTRY_WEIGHTS = {
    "UAE": 0.48,
    "Saudi Arabia": 0.22,
    "Qatar": 0.10,
    "Bahrain": 0.07,
    "Oman": 0.07,
    "Kuwait": 0.06,
}

JOB_LEVELS = (
    "Executive",
    "Senior Manager",
    "Manager",
    "Senior Specialist",
    "Specialist",
    "Analyst",
    "Associate",
)

JOB_FAMILIES = (
    "Executive Leadership",
    "Finance",
    "Accounting",
    "Human Resources",
    "People Operations",
    "Software Engineering",
    "Data & Analytics",
    "IT Operations",
    "Product",
    "Operations",
    "Supply Chain",
    "Procurement",
    "Legal",
    "Customer Service",
    "Sales",
    "Marketing",
    "Risk",
    "Compliance",
    "Internal Audit",
    "Strategy",
    "Administration",
)

USE_CASE_STATUSES = (
    "Idea",
    "Assessment",
    "Pilot",
    "Production",
    "Scaling",
    "Paused",
    "Retired",
)

BENEFIT_TYPES = (
    "Cost Avoidance",
    "Cost Reduction",
    "Revenue Increase",
    "Capacity Release",
    "Productivity",
    "Quality Improvement",
    "Risk Reduction",
)

RISK_RATINGS = ("Low", "Medium", "High", "Critical")

LICENSE_STATUSES = ("Active", "Suspended", "Revoked")

USER_SEGMENTS = (
    "Power User",
    "Regular User",
    "Occasional User",
    "Inactive",
    "Never Activated",
    "Abandoned",
)

PORTFOLIO_ACTIONS = ("Scale", "Optimize", "Monitor", "Reassess", "Stop")

COST_CATEGORIES = (
    "license_cost",
    "infrastructure_cost",
    "implementation_cost",
    "support_cost",
    "training_cost",
    "security_cost",
    "governance_cost",
)

PERSONAS = {
    "CEO / Executive Committee": {
        "focus": ["net_benefit", "portfolio_roi", "realized_value", "payback_months", "value_realization_pct"],
        "insight_order": ["key_findings", "management_attention", "recommended_actions", "value_opportunities"],
        "description": "Portfolio value, net benefit, and strategic investment decisions.",
    },
    "CFO": {
        "focus": ["realized_value", "finance_validated", "total_cost", "portfolio_roi", "payback_months"],
        "insight_order": ["value_opportunities", "key_findings", "recommended_actions", "optimization_opportunities"],
        "description": "Realized value, finance validation, payback, and cost control.",
    },
    "CIO / CTO": {
        "focus": ["total_cost", "active_users", "adoption_rate", "underutilized_licenses", "cost_per_active_user"],
        "insight_order": ["optimization_opportunities", "key_findings", "recommended_actions", "management_attention"],
        "description": "Platform spend, adoption, licenses, and technical unit economics.",
    },
    "Chief AI Officer": {
        "focus": ["potential_value", "demonstrated_value", "realized_value", "production_use_cases", "high_performing"],
        "insight_order": ["key_findings", "value_opportunities", "management_attention", "recommended_actions"],
        "description": "Use-case portfolio health and Potential → Demonstrated → Realized conversion.",
    },
    "Business Unit Head": {
        "focus": ["realized_value", "hours_saved", "adoption_rate", "portfolio_roi", "underperforming"],
        "insight_order": ["value_opportunities", "key_findings", "recommended_actions", "management_attention"],
        "description": "Business-unit value, adoption, and use-case performance.",
    },
    "Finance": {
        "focus": ["finance_validated", "realized_value", "total_cost", "net_benefit", "benefit_cost_ratio"],
        "insight_order": ["value_opportunities", "optimization_opportunities", "key_findings", "recommended_actions"],
        "description": "Benefit register integrity, validated value, and cost completeness.",
    },
    "AI Program Office": {
        "focus": ["production_use_cases", "high_performing", "underperforming", "adoption_rate", "value_realization_pct"],
        "insight_order": ["management_attention", "recommended_actions", "key_findings", "value_opportunities"],
        "description": "Portfolio governance, delivery status, and realization tracking.",
    },
    "Technology": {
        "focus": ["active_users", "cost_per_ai_task", "infrastructure_cost", "adoption_rate", "hours_saved"],
        "insight_order": ["optimization_opportunities", "key_findings", "recommended_actions", "management_attention"],
        "description": "Usage, infrastructure cost, and engineering productivity.",
    },
    "Data & Analytics": {
        "focus": ["demonstrated_value", "value_realization_pct", "hours_saved", "fte_capacity", "active_users"],
        "insight_order": ["key_findings", "value_opportunities", "management_attention", "recommended_actions"],
        "description": "Measurement quality, conversion leakage, and analytical integrity.",
    },
    "Procurement / Vendor Management": {
        "focus": ["total_cost", "underutilized_licenses", "optimization_opportunity", "cost_per_active_user", "portfolio_roi"],
        "insight_order": ["optimization_opportunities", "recommended_actions", "key_findings", "value_opportunities"],
        "description": "Vendor spend, license utilization, and commercial optimization.",
    },
}

BUSINESS_UNITS = (
    {
        "business_unit_id": "BU-CORP",
        "business_unit_name": "Corporate",
        "executive_owner": "Group Chief of Staff",
        "annual_budget": 48_000_000,
        "employee_count": 480,
    },
    {
        "business_unit_id": "BU-FIN",
        "business_unit_name": "Finance",
        "executive_owner": "Group Chief Financial Officer",
        "annual_budget": 62_000_000,
        "employee_count": 920,
    },
    {
        "business_unit_id": "BU-HR",
        "business_unit_name": "Human Resources",
        "executive_owner": "Group Chief People Officer",
        "annual_budget": 28_000_000,
        "employee_count": 520,
    },
    {
        "business_unit_id": "BU-TECH",
        "business_unit_name": "Technology",
        "executive_owner": "Group Chief Technology Officer",
        "annual_budget": 145_000_000,
        "employee_count": 1_680,
    },
    {
        "business_unit_id": "BU-OPS",
        "business_unit_name": "Operations",
        "executive_owner": "Group Chief Operating Officer",
        "annual_budget": 410_000_000,
        "employee_count": 3_600,
    },
    {
        "business_unit_id": "BU-PROC",
        "business_unit_name": "Procurement",
        "executive_owner": "Group Chief Procurement Officer",
        "annual_budget": 22_000_000,
        "employee_count": 400,
    },
    {
        "business_unit_id": "BU-LEG",
        "business_unit_name": "Legal",
        "executive_owner": "Group General Counsel",
        "annual_budget": 18_000_000,
        "employee_count": 220,
    },
    {
        "business_unit_id": "BU-CS",
        "business_unit_name": "Customer Service",
        "executive_owner": "Group Head of Customer Experience",
        "annual_budget": 54_000_000,
        "employee_count": 1_800,
    },
    {
        "business_unit_id": "BU-SALES",
        "business_unit_name": "Sales",
        "executive_owner": "Group Chief Commercial Officer",
        "annual_budget": 96_000_000,
        "employee_count": 1_520,
    },
    {
        "business_unit_id": "BU-MKT",
        "business_unit_name": "Marketing",
        "executive_owner": "Group Chief Marketing Officer",
        "annual_budget": 41_000_000,
        "employee_count": 480,
    },
    {
        "business_unit_id": "BU-RISK",
        "business_unit_name": "Risk & Compliance",
        "executive_owner": "Group Chief Risk Officer",
        "annual_budget": 24_000_000,
        "employee_count": 320,
    },
    {
        "business_unit_id": "BU-IA",
        "business_unit_name": "Internal Audit",
        "executive_owner": "Group Chief Audit Executive",
        "annual_budget": 9_500_000,
        "employee_count": 140,
    },
)

DEPARTMENTS = (
    ("DEP-CORP-STRAT", "Group Strategy", "BU-CORP", "CC-1001", 160, "Strategy"),
    ("DEP-CORP-GOV", "Corporate Governance", "BU-CORP", "CC-1002", 90, "Administration"),
    ("DEP-CORP-COMMS", "Corporate Communications", "BU-CORP", "CC-1003", 230, "Marketing"),
    ("DEP-FIN-FPNA", "Financial Planning & Analysis", "BU-FIN", "CC-2001", 280, "Finance"),
    ("DEP-FIN-ACC", "Group Accounting", "BU-FIN", "CC-2002", 360, "Accounting"),
    ("DEP-FIN-TRE", "Treasury", "BU-FIN", "CC-2003", 280, "Finance"),
    ("DEP-HR-BP", "HR Business Partners", "BU-HR", "CC-3001", 220, "Human Resources"),
    ("DEP-HR-TA", "Talent Acquisition", "BU-HR", "CC-3002", 160, "People Operations"),
    ("DEP-HR-OPS", "HR Operations", "BU-HR", "CC-3003", 140, "People Operations"),
    ("DEP-TECH-ENG", "Software Engineering", "BU-TECH", "CC-4001", 820, "Software Engineering"),
    ("DEP-TECH-DATA", "Data & Analytics", "BU-TECH", "CC-4002", 360, "Data & Analytics"),
    ("DEP-TECH-ITO", "IT Operations", "BU-TECH", "CC-4003", 500, "IT Operations"),
    ("DEP-OPS-PROD", "Production Operations", "BU-OPS", "CC-5001", 1_700, "Operations"),
    ("DEP-OPS-LOG", "Logistics", "BU-OPS", "CC-5002", 1_100, "Supply Chain"),
    ("DEP-OPS-QA", "Quality Assurance", "BU-OPS", "CC-5003", 800, "Operations"),
    ("DEP-PROC-SRC", "Strategic Sourcing", "BU-PROC", "CC-6001", 180, "Procurement"),
    ("DEP-PROC-P2P", "Procure-to-Pay", "BU-PROC", "CC-6002", 220, "Procurement"),
    ("DEP-LEG-CORP", "Corporate Legal", "BU-LEG", "CC-7001", 130, "Legal"),
    ("DEP-LEG-CON", "Contracts", "BU-LEG", "CC-7002", 90, "Legal"),
    ("DEP-CS-CNT", "Contact Center", "BU-CS", "CC-8001", 1_250, "Customer Service"),
    ("DEP-CS-RET", "Retention & Care", "BU-CS", "CC-8002", 550, "Customer Service"),
    ("DEP-SALES-ENT", "Enterprise Sales", "BU-SALES", "CC-9001", 820, "Sales"),
    ("DEP-SALES-SMB", "SMB Sales", "BU-SALES", "CC-9002", 700, "Sales"),
    ("DEP-MKT-BRAND", "Brand & Content", "BU-MKT", "CC-9101", 210, "Marketing"),
    ("DEP-MKT-GROW", "Growth Marketing", "BU-MKT", "CC-9102", 270, "Marketing"),
    ("DEP-RISK-ERM", "Enterprise Risk", "BU-RISK", "CC-9201", 150, "Risk"),
    ("DEP-RISK-CMP", "Compliance", "BU-RISK", "CC-9202", 170, "Compliance"),
    ("DEP-IA-ASS", "Assurance", "BU-IA", "CC-9301", 140, "Internal Audit"),
)

AI_PRODUCTS = (
    {
        "product_id": "PRD-M365-COP",
        "product_name": "Microsoft 365 Copilot",
        "vendor": "Microsoft",
        "product_category": "Productivity Copilot",
        "pricing_model": "Per user / month",
        "monthly_unit_cost": 30.0,
    },
    {
        "product_id": "PRD-GH-COP",
        "product_name": "GitHub Copilot",
        "vendor": "GitHub",
        "product_category": "Developer Copilot",
        "pricing_model": "Per user / month",
        "monthly_unit_cost": 19.0,
    },
    {
        "product_id": "PRD-CHATGPT",
        "product_name": "ChatGPT Enterprise",
        "vendor": "OpenAI",
        "product_category": "Enterprise LLM",
        "pricing_model": "Per user / month",
        "monthly_unit_cost": 60.0,
    },
    {
        "product_id": "PRD-AZ-OAI",
        "product_name": "Azure OpenAI",
        "vendor": "Microsoft",
        "product_category": "Model Platform",
        "pricing_model": "Consumption",
        "monthly_unit_cost": 0.0,
    },
    {
        "product_id": "PRD-NOOR-ASSIST",
        "product_name": "Noor Assist",
        "vendor": "Al Noor Digital",
        "product_category": "Enterprise AI Assistant",
        "pricing_model": "Per user / month",
        "monthly_unit_cost": 12.0,
    },
    {
        "product_id": "PRD-NOOR-AGENT",
        "product_name": "Noor Agent Platform",
        "vendor": "Al Noor Digital",
        "product_category": "Custom AI Agent",
        "pricing_model": "Platform + use case",
        "monthly_unit_cost": 25.0,
    },
)

# Department-level realization of demonstrated value into cash / validated benefit.
DEPARTMENT_REALIZATION = {
    "DEP-TECH-ENG": 0.58,
    "DEP-TECH-DATA": 0.52,
    "DEP-TECH-ITO": 0.40,
    "DEP-FIN-FPNA": 0.48,
    "DEP-FIN-ACC": 0.50,
    "DEP-FIN-TRE": 0.46,
    "DEP-PROC-SRC": 0.72,
    "DEP-PROC-P2P": 0.70,
    "DEP-CS-CNT": 0.42,
    "DEP-CS-RET": 0.40,
    "DEP-MKT-BRAND": 0.14,
    "DEP-MKT-GROW": 0.16,
    "DEP-LEG-CORP": 0.22,
    "DEP-LEG-CON": 0.20,
    "DEP-HR-BP": 0.24,
    "DEP-HR-TA": 0.26,
    "DEP-HR-OPS": 0.28,
    "DEP-SALES-ENT": 0.38,
    "DEP-SALES-SMB": 0.34,
    "DEP-OPS-PROD": 0.36,
    "DEP-OPS-LOG": 0.40,
    "DEP-OPS-QA": 0.33,
    "DEP-RISK-ERM": 0.30,
    "DEP-RISK-CMP": 0.28,
    "DEP-CORP-STRAT": 0.32,
    "DEP-CORP-GOV": 0.25,
    "DEP-CORP-COMMS": 0.18,
    "DEP-IA-ASS": 0.44,
}

BENEFIT_REALIZATION = {
    "Cost Avoidance": 0.70,
    "Cost Reduction": 0.75,
    "Revenue Increase": 0.45,
    "Capacity Release": 0.32,
    "Productivity": 0.30,
    "Quality Improvement": 0.28,
    "Risk Reduction": 0.22,
}

# Product affinity by job family (weights do not need to sum to 1).
PRODUCT_AFFINITY = {
    "Software Engineering": {"PRD-GH-COP": 0.85, "PRD-CHATGPT": 0.25, "PRD-AZ-OAI": 0.15},
    "Data & Analytics": {"PRD-CHATGPT": 0.55, "PRD-AZ-OAI": 0.35, "PRD-M365-COP": 0.30, "PRD-GH-COP": 0.20},
    "IT Operations": {"PRD-M365-COP": 0.45, "PRD-CHATGPT": 0.25, "PRD-GH-COP": 0.15},
    "Legal": {"PRD-M365-COP": 0.90, "PRD-CHATGPT": 0.20, "PRD-NOOR-AGENT": 0.10},
    "Finance": {"PRD-M365-COP": 0.70, "PRD-CHATGPT": 0.25, "PRD-NOOR-ASSIST": 0.10},
    "Accounting": {"PRD-M365-COP": 0.65, "PRD-NOOR-ASSIST": 0.20, "PRD-CHATGPT": 0.15},
    "Human Resources": {"PRD-M365-COP": 0.80, "PRD-NOOR-ASSIST": 0.15},
    "People Operations": {"PRD-M365-COP": 0.75, "PRD-NOOR-ASSIST": 0.20},
    "Customer Service": {"PRD-NOOR-ASSIST": 0.80, "PRD-M365-COP": 0.15, "PRD-NOOR-AGENT": 0.10},
    "Sales": {"PRD-M365-COP": 0.70, "PRD-CHATGPT": 0.20},
    "Marketing": {"PRD-CHATGPT": 0.55, "PRD-M365-COP": 0.50, "PRD-AZ-OAI": 0.20},
    "Procurement": {"PRD-M365-COP": 0.60, "PRD-NOOR-ASSIST": 0.25, "PRD-CHATGPT": 0.15},
    "Risk": {"PRD-M365-COP": 0.55, "PRD-CHATGPT": 0.25},
    "Compliance": {"PRD-M365-COP": 0.60, "PRD-CHATGPT": 0.20},
    "Internal Audit": {"PRD-M365-COP": 0.55, "PRD-CHATGPT": 0.25},
    "Operations": {"PRD-NOOR-ASSIST": 0.35, "PRD-M365-COP": 0.25},
    "Supply Chain": {"PRD-NOOR-ASSIST": 0.30, "PRD-M365-COP": 0.30},
    "Executive Leadership": {"PRD-M365-COP": 0.70, "PRD-CHATGPT": 0.15},
    "Strategy": {"PRD-M365-COP": 0.55, "PRD-CHATGPT": 0.40},
    "Product": {"PRD-CHATGPT": 0.45, "PRD-M365-COP": 0.40, "PRD-GH-COP": 0.15},
    "Administration": {"PRD-M365-COP": 0.50},
}

# Story-driven adoption multipliers by department.
ADOPTION_MULTIPLIER = {
    "DEP-TECH-ENG": 1.55,
    "DEP-TECH-DATA": 1.35,
    "DEP-TECH-ITO": 1.10,
    "DEP-FIN-FPNA": 1.05,
    "DEP-FIN-ACC": 1.00,
    "DEP-FIN-TRE": 0.95,
    "DEP-PROC-SRC": 0.85,
    "DEP-PROC-P2P": 0.90,
    "DEP-CS-CNT": 1.25,
    "DEP-CS-RET": 1.15,
    "DEP-MKT-BRAND": 1.30,
    "DEP-MKT-GROW": 1.40,
    "DEP-LEG-CORP": 0.42,
    "DEP-LEG-CON": 0.38,
    "DEP-HR-BP": 0.48,
    "DEP-HR-TA": 0.50,
    "DEP-HR-OPS": 0.45,
    "DEP-SALES-ENT": 1.05,
    "DEP-SALES-SMB": 0.95,
    "DEP-OPS-PROD": 0.70,
    "DEP-OPS-LOG": 0.75,
    "DEP-OPS-QA": 0.72,
    "DEP-RISK-ERM": 0.80,
    "DEP-RISK-CMP": 0.78,
    "DEP-CORP-STRAT": 0.90,
    "DEP-CORP-GOV": 0.55,
    "DEP-CORP-COMMS": 1.10,
    "DEP-IA-ASS": 0.88,
}

# Over-licensing: share of white-collar staff who receive a license (story 7, 12).
LICENSE_COVERAGE = {
    "DEP-LEG-CORP": 0.92,
    "DEP-LEG-CON": 0.94,
    "DEP-HR-BP": 0.88,
    "DEP-HR-TA": 0.86,
    "DEP-HR-OPS": 0.90,
    "DEP-TECH-ENG": 0.78,
    "DEP-TECH-DATA": 0.80,
    "DEP-TECH-ITO": 0.55,
    "DEP-FIN-FPNA": 0.62,
    "DEP-FIN-ACC": 0.48,
    "DEP-FIN-TRE": 0.50,
    "DEP-PROC-SRC": 0.55,
    "DEP-PROC-P2P": 0.42,
    "DEP-CS-CNT": 0.58,
    "DEP-CS-RET": 0.50,
    "DEP-MKT-BRAND": 0.70,
    "DEP-MKT-GROW": 0.72,
    "DEP-SALES-ENT": 0.60,
    "DEP-SALES-SMB": 0.45,
    "DEP-OPS-PROD": 0.12,
    "DEP-OPS-LOG": 0.18,
    "DEP-OPS-QA": 0.16,
    "DEP-RISK-ERM": 0.50,
    "DEP-RISK-CMP": 0.52,
    "DEP-CORP-STRAT": 0.65,
    "DEP-CORP-GOV": 0.40,
    "DEP-CORP-COMMS": 0.55,
    "DEP-IA-ASS": 0.60,
}

SALARY_BY_LEVEL = {
    "Executive": (210_000, 380_000),
    "Senior Manager": (140_000, 210_000),
    "Manager": (95_000, 145_000),
    "Senior Specialist": (75_000, 110_000),
    "Specialist": (52_000, 82_000),
    "Analyst": (42_000, 68_000),
    "Associate": (28_000, 46_000),
}

LEVEL_WEIGHTS = {
    "Executive": 0.015,
    "Senior Manager": 0.045,
    "Manager": 0.12,
    "Senior Specialist": 0.18,
    "Specialist": 0.27,
    "Analyst": 0.22,
    "Associate": 0.15,
}

TRAINING_CAMPAIGN_MONTHS = (8, 18, 27)

VALUE_CHAIN = (
    "AI Investment",
    "AI Availability",
    "AI Adoption",
    "Effective Usage",
    "Operational Improvement",
    "Demonstrated Business Benefit",
    "Financial Realization",
    "Realized AI Value",
    "ROI",
)

ORGANIZATION = {
    "organization_id": "ORG-ALNOOR",
    "organization_name": SETTINGS.organization_name,
    "country": "UAE",
    "industry": "Diversified Holdings",
    "employee_count": SETTINGS.employee_count,
    "annual_revenue": 4_850_000_000,
    "ai_strategy_maturity": "Scaling",
}
