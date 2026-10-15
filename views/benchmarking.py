from __future__ import annotations

import streamlit as st

from components.charts import horizontal_bar, radar
from components.filters import current_filters
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.metric_service import department_value_index


def render() -> None:
    filters = current_filters()
    page_note(
        "The AI Value Index is a 0–100 min-max normalization of adoption, usage, productivity, realized value, "
        "ROI, training completion, and use-case success. It is a relative ranking, not an absolute grade."
    )
    frame = department_value_index(filters)
    if frame.empty:
        st.warning("No department metrics in the current filter.")
        return
    show = frame[["department_name", "business_unit_name", "ai_value_index", "adoption", "roi", "realized_value", "hours_saved"]].copy()
    st.plotly_chart(horizontal_bar(show, "ai_value_index", "department_name", "AI Value Index by department"), width="stretch")

    dims = ["adoption_idx", "usage_idx", "productivity_idx", "value_idx", "roi_idx", "training_idx", "use_case_success_idx"]
    labels = ["Adoption", "Usage", "Productivity", "Value", "ROI", "Training", "Use case success"]
    selected = st.selectbox("Radar comparison", show["department_name"].tolist())
    row = frame[frame["department_name"] == selected].iloc[0]
    radar_row = row.copy()
    for src, label in zip(dims, labels):
        radar_row[label] = row[src]
    st.plotly_chart(radar(radar_row, labels, f"{selected} profile"), width="stretch")

    with st.expander("Index methodology"):
        st.markdown(
            """
            Each dimension is scaled to 0–100 using min-max normalization across departments in the current filter.

            - **Adoption** — active / licensed users
            - **Usage** — sessions per licensed user
            - **Productivity** — hours saved per licensed user (operational, not cash)
            - **Value** — realized financial benefit
            - **ROI** — (realized − cost) / cost
            - **Training** — share of employees with completed AI training
            - **Use-case success** — mix of Scale classifications and positive-ROI use cases

            The index is the unweighted mean of the seven scaled scores.
            """
        )
    styled_table(show)
    download_csv(frame, "department_benchmarking.csv", "Export benchmarking")
