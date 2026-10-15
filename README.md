# AI Value Intelligence

**Measure Adoption. Prove Value. Optimize AI Investment.**

Enterprise platform for understanding whether spend on Generative AI, Microsoft Copilot, GitHub Copilot, enterprise LLMs, and AI agents is producing measurable business value.

The first release runs entirely on a high-quality **synthetic** dataset for a fictional GCC holding company, **Al Noor Holdings PJSC**. No API keys are required. The metric engine is source-agnostic so synthetic tables can later be replaced by enterprise systems.

**Shareable guide:** open [`docs/AI_Value_Intelligence_User_and_Business_Guide.html`](docs/AI_Value_Intelligence_User_and_Business_Guide.html) in a browser (Print → Save as PDF). It covers the product, pages, metrics, synthetic enterprise, and a demo walkthrough for business audiences.

## Business purpose

Leadership typically cannot answer:

- How much are we spending on AI?
- Who is licensed but unused?
- Which use cases create **realized** value rather than activity?
- What is portfolio ROI, payback, and value leakage (Potential → Demonstrated → Realized)?
- Which licenses should be reassigned and which initiatives should stop?

This application follows a strict value chain:

AI Investment → Availability → Adoption → Effective Usage → Operational Improvement → Demonstrated Benefit → Financial Realization → Realized AI Value → ROI

It never equates prompts with productivity, usage with value, hours saved with cash, or adoption with ROI.

## Personas

Use the sidebar persona selector. Calculations do not change; KPI emphasis and insight order do.

CEO / Executive Committee, CFO, CIO / CTO, Chief AI Officer, Business Unit Head, Finance, AI Program Office, Technology, Data & Analytics, Procurement / Vendor Management.

## Architecture

```
ai_audit/
  app.py                    Streamlit home (Executive Overview)
  pages/                    12 analytical pages
  views/                    Page renderers
  components/               Filters, KPI cards, charts, tables, insights
  services/                 Metric, ROI, optimization, forecast, insight engines
  services/adapters/        SourceAdapter protocol + synthetic implementation
  generators/               Story-driven synthetic enterprise
  models/                   Pydantic contracts
  config/                   Settings, reference data, theme
  data/generated/           Parquet + DuckDB (created on first run)
  tests/                    ROI, metrics, data-quality tests
```

**Stack:** Python 3.10+ (3.11 recommended), Streamlit, Pandas, NumPy, Plotly, DuckDB, PyArrow, Pydantic, scikit-learn (forecasting), pytest.

Facts are monthly. Large employee-level usage is stored in Parquet/DuckDB; pages query pre-aggregated marts.

## Installation

```bash
cd ai_audit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running locally

```bash
# Optional: generate data explicitly (also runs automatically on first app start)
python -m generators.generate_all

streamlit run app.py
```

Open the URL Streamlit prints (typically http://localhost:8501).

### View on a phone

The app is responsive: KPIs stack, charts stay full-width, tabs scroll sideways, and the sidebar starts collapsed on small screens.

1. Laptop and phone must be on the **same Wi-Fi**.
2. On the laptop: `streamlit run app.py`. Safari should open on the Mac; the server also listens on the LAN for a phone.
3. In the sidebar, open **Open on a phone** and copy the `http://192.168.x.x:8501` address.
4. On the phone, paste that URL in Safari or Chrome.

If the page does not load: allow incoming connections for Python in macOS **System Settings → Network → Firewall**, or run `streamlit run app.py --server.address 0.0.0.0 --server.port 8501`. `localhost` on the phone will not work — use the laptop’s LAN IP.

## Regenerating data

```bash
python -m generators.generate_all
```

Generation is deterministic (seed `42`). Output:

- `data/generated/*.parquet`
- `data/generated/ai_value.duckdb`
- `data/generated/manifest.json`

## Data model

| Table | Grain |
| --- | --- |
| organizations | 1 fictional group |
| business_units | 12 units |
| departments | 28 departments |
| employees | ~12,000 synthetic IDs (no real personal data) |
| ai_products | 6 platforms |
| licenses | employee × product |
| ai_usage | employee × product × month |
| ai_use_cases | 70–90 use cases |
| productivity_metrics | sampled employee × use case × month |
| financial_benefits | use case × month |
| ai_costs | use case × month |
| mart_* | pre-aggregates for the UI |

## Synthetic methodology

Al Noor Holdings PJSC is a UAE-headquartered diversified group with operations in the UAE, Saudi Arabia, Qatar, Bahrain, Oman, and Kuwait. Variables are **jointly** generated:

- Training increases adoption and session depth
- Job family drives product mix (engineering → GitHub Copilot; corporate functions → M365 Copilot; customer service → Noor Assist)
- High adoption does not imply high ROI
- Realization rates vary by department and benefit type
- Seasonality (summer dip), ramp-up, abandonment, and over-licensing are explicit

Hidden stories used for testing are documented in [`data/SYNTHETIC_STORIES.md`](data/SYNTHETIC_STORIES.md) and are not printed as a dashboard checklist.

## Metric definitions

| Metric | Definition |
| --- | --- |
| Potential value | Steady-state expected benefit × time in period × ramp |
| Demonstrated value | Potential × evidence factor from operational measurement |
| Realized value | Demonstrated × realization factor; subset flagged finance-validated |
| Hours saved | Operational minutes avoided. **Not cash.** |
| FTE capacity | Hours saved / 1,880 working hours |
| Adoption | Active licensed users / licensed users (latest month in filter) |
| User segments | Power, Regular, Occasional, Inactive, Never Activated, Abandoned |

## ROI methodology

Total AI cost = license + infrastructure + implementation + training + support + security + governance

```
ROI = (Realized financial benefit − Total AI cost) / Total AI cost
Net benefit = Realized − Cost
BCR = Realized / Cost
Payback (months) = Cost / average monthly realized value
```

Hours saved are converted to money **only** through an explicit realization factor (default 35% in the simulator).

## Application pages

1. **Executive Overview** — portfolio KPIs, trends, P→D→R, matrix, insights
2. **AI Investment** — spend by product, vendor, unit, department, use case, cost category
3. **Adoption Intelligence** — eligible / licensed / active, segments, training lift
4. **Use Case Portfolio** — registry and Scale / Optimize / Monitor / Reassess / Stop
5. **Productivity** — before/after task time, quality, rework, hours vs FTE vs cash
6. **Value Realization** — waterfall, leakage, finance validation, benefit types
7. **ROI Intelligence** — ROI, payback, BCR, unit economics
8. **License Optimization** — unused / idle / overlap, dynamic recommendations
9. **Department Benchmarking** — 0–100 AI Value Index
10. **Forecasting** — 12–36 month Conservative / Base / Accelerated scenarios
11. **AI Value Simulator** — interactive executive model
12. **Data Explorer** — table preview, quality checks, CSV export

Global filters (date, business unit, department, country, product, vendor, use case, status, risk, job level) apply across analytical pages.

## Testing

```bash
pytest -q
```

- `tests/test_roi.py` — ROI, payback, BCR, realization factor
- `tests/test_metrics.py` — KPI reconciliation, value hierarchy, hours ≠ cash
- `tests/test_data_quality.py` — keys, FKs, enums, P≥D≥R, scale bounds

## Future integrations

Do not treat the synthetic adapter as a live connector. Implement `services.adapters.base.SourceAdapter` for each source and map into the same logical tables.

| Source | Typical mapping |
| --- | --- |
| Microsoft Graph / M365 Copilot usage | licenses, usage, department |
| GitHub Copilot metrics | developer usage |
| Azure OpenAI / Foundry telemetry | tokens, infrastructure cost |
| Microsoft Fabric / Power BI / Databricks / Snowflake | warehouse facts |
| ServiceNow | use-case / demand register |
| SAP / Oracle finance | actuals, cost centers, validated benefits |
| Workday / HRIS | employees, jobs, cost rates |
| Procurement systems | vendor contracts, unit prices |
| Custom apps and agents | task telemetry, quality |

`services/adapters/synthetic.py` is the only implemented adapter.

## Limitations

- All figures are synthetic and directional, not advice or a real client residual.
- Monthly grain; no true daily telemetry.
- Productivity is sampled, not a census of every employee-task.
- Forecasts are trend scenarios, not predictions.
- No authentication, row-level security, or write-back.
- Currency is USD for vendor-comparable AI spend.

## License

Internal demonstration asset. Not for redistribution as a named-client deliverable.
