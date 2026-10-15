import streamlit as st

pages = [
    st.Page("pages/01_executive_overview.py", title="Executive Overview", default=True),
    st.Page("pages/02_ai_investment.py", title="AI Investment"),
    st.Page("pages/03_adoption_intelligence.py", title="Adoption Intelligence"),
    st.Page("pages/04_use_case_portfolio.py", title="Use Case Portfolio"),
    st.Page("pages/05_productivity.py", title="Productivity Intelligence"),
    st.Page("pages/06_value_realization.py", title="Value Realization"),
    st.Page("pages/07_roi_intelligence.py", title="ROI Intelligence"),
    st.Page("pages/13_ai_roi_methodology.py", title="AI ROI Methodology"),
    st.Page("pages/08_license_optimization.py", title="License Optimization"),
    st.Page("pages/09_department_benchmarking.py", title="Department Benchmarking"),
    st.Page("pages/10_forecasting.py", title="Forecasting"),
    st.Page("pages/11_ai_value_simulator.py", title="AI Value Simulator"),
    st.Page("pages/12_data_explorer.py", title="Data Explorer"),
    st.Page("pages/14_knowledge.py", title="Knowledge"),
]

st.navigation(pages).run()
