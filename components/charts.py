from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.theme import AMBER, CHARCOAL, CRIMSON, FOREST, MUTED, TEAL, TEAL_DARK

PALETTE = [TEAL, CHARCOAL, AMBER, FOREST, "#5B7C99", CRIMSON, "#8A6A4F", "#3D5A80"]


def _title_style(text: str | None = None) -> dict:
    style = dict(
        font=dict(size=16, color=CHARCOAL, family="Source Serif 4, Georgia, serif"),
        x=0.0,
        xanchor="left",
        y=0.98,
        yanchor="top",
        pad=dict(t=4, b=18),
    )
    if text:
        style["text"] = text
    return style


def _layout(fig: go.Figure, height: int = 400, legend: str = "bottom") -> go.Figure:
    if legend == "right":
        legend_cfg = dict(
            orientation="v",
            yanchor="middle",
            y=0.45,
            x=1.04,
            xanchor="left",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
            itemclick="toggle",
        )
        margin = dict(l=36, r=168, t=78, b=48)
    elif legend == "none":
        legend_cfg = dict()
        margin = dict(l=48, r=28, t=78, b=56)
    else:
        legend_cfg = dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            x=0.0,
            xanchor="left",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
            itemwidth=40,
            traceorder="normal",
        )
        margin = dict(l=36, r=20, t=78, b=110)

    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=CHARCOAL, family="IBM Plex Sans"),
        title=_title_style(fig.layout.title.text),
        legend=legend_cfg,
        showlegend=legend != "none",
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, automargin=True, title_standoff=12)
    fig.update_yaxes(gridcolor="#EEEAE3", zerolinecolor="#DAD4C8", automargin=True, title_standoff=12)
    return fig


def line_trend(frame: pd.DataFrame, x: str, y: list[str], title: str, height: int = 360) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y):
        fig.add_trace(
            go.Scatter(
                x=frame[x],
                y=frame[col],
                mode="lines",
                name=col.replace("_", " ").title(),
                line=dict(color=PALETTE[i % len(PALETTE)], width=2.2),
            )
        )
    fig.update_layout(title=_title_style(title))
    return _layout(fig, max(height, 420))


def bar_rank(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.bar(
        frame,
        x=x,
        y=y,
        title=title,
        color=color,
        color_discrete_sequence=PALETTE if color else None,
    )
    if color is None:
        fig.update_traces(marker_color=TEAL)
    return _layout(fig, legend="none" if color is None else "bottom")


def horizontal_bar(frame: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    ordered = frame.sort_values(x)
    fig = px.bar(ordered, x=x, y=y, orientation="h", title=title, color_discrete_sequence=[TEAL])
    return _layout(fig, height=max(400, 28 * len(ordered) + 160), legend="none")


def waterfall(frame: pd.DataFrame, title: str) -> go.Figure:
    measures = []
    for step in frame["step"]:
        if step in {"Potential value", "Demonstrated value", "Realized value", "Net AI value"}:
            measures.append("absolute")
        else:
            measures.append("relative")
    fig = go.Figure(
        go.Waterfall(
            x=frame["step"],
            y=frame["value"],
            measure=measures,
            connector={"line": {"color": MUTED}},
            decreasing={"marker": {"color": CRIMSON}},
            increasing={"marker": {"color": FOREST}},
            totals={"marker": {"color": TEAL_DARK}},
        )
    )
    fig.update_layout(title=_title_style(title), showlegend=False)
    return _layout(fig, 420, legend="none")


def funnel(values: list[tuple[str, float]], title: str) -> go.Figure:
    fig = go.Figure(
        go.Funnel(
            y=[v[0] for v in values],
            x=[v[1] for v in values],
            textinfo="value+percent initial",
            marker={"color": [TEAL, "#4C8F8C", TEAL_DARK]},
        )
    )
    fig.update_layout(title=_title_style(title), showlegend=False)
    return _layout(fig, 380, legend="none")


def bubble(frame: pd.DataFrame, x: str, y: str, size: str, color: str, hover: str, title: str) -> go.Figure:
    fig = px.scatter(
        frame,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover,
        title=title,
        color_discrete_sequence=PALETTE,
        size_max=48,
    )
    return _layout(fig, 480)


def heatmap(frame: pd.DataFrame, title: str) -> go.Figure:
    fig = px.imshow(frame, aspect="auto", color_continuous_scale=["#F7F5F2", TEAL], title=title)
    return _layout(fig, 380)


def radar(row: pd.Series, dimensions: list[str], title: str) -> go.Figure:
    fig = go.Figure(
        go.Scatterpolar(
            r=[float(row[d]) for d in dimensions] + [float(row[dimensions[0]])],
            theta=dimensions + [dimensions[0]],
            fill="toself",
            line=dict(color=TEAL),
        )
    )
    fig.update_layout(title=_title_style(title), polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    return _layout(fig, 400, legend="none")


def pie(frame: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    source = frame.copy()
    source[names] = source[names].astype(str).str.replace("_", " ", regex=False)
    fig = px.pie(source, names=names, values=values, color_discrete_sequence=PALETTE)
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=12),
        hovertemplate="%{label}<br>%{percent}<br>%{value:,.0f}<extra></extra>",
    )
    fig.update_layout(title=_title_style(title), uniformtext_minsize=10, uniformtext_mode="hide")
    return _layout(fig, 440, legend="right")
