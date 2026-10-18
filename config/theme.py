from __future__ import annotations

import streamlit as st

TEAL = "#0F6E6B"
TEAL_DARK = "#0A4F4D"
CHARCOAL = "#1F2A33"
SLATE = "#4A5560"
MUTED = "#6B7280"
LINE = "#E5E7EB"
SURFACE = "#F7F5F2"
CARD = "#FFFFFF"
AMBER = "#C9842A"
CRIMSON = "#9B3A3A"
FOREST = "#2F6B4F"

THEME_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
  font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
  color: {CHARCOAL};
}}

.stApp {{
  background: {SURFACE};
}}

[data-testid="stHeader"] {{
  background: {SURFACE};
}}

[data-testid="stSidebar"] {{
  background: #F1EEE8;
  border-right: 1px solid {LINE};
}}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
  font-family: "Source Serif 4", Georgia, serif;
}}

h1, h2, h3 {{
  font-family: "Source Serif 4", Georgia, serif;
  color: {CHARCOAL};
  letter-spacing: -0.02em;
}}

h1 {{ font-size: 1.85rem !important; }}
h2 {{ font-size: 1.35rem !important; margin-top: 0.4rem; }}
h3 {{ font-size: 1.05rem !important; color: {SLATE}; }}

.avi-brand {{
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.35rem;
  font-weight: 650;
  color: {CHARCOAL};
  line-height: 1.2;
}}
.avi-subtitle {{
  font-size: 0.78rem;
  color: {MUTED};
  margin-top: 0.15rem;
  letter-spacing: 0.01em;
}}
.avi-org {{
  font-size: 0.72rem;
  color: {TEAL};
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 0.55rem;
}}
.avi-developer {{
  font-size: 0.7rem;
  color: {MUTED};
  margin-top: 0.35rem;
}}
.avi-user-name {{
  font-size: 0.88rem;
  font-weight: 600;
  color: {CHARCOAL};
  margin-top: 0.75rem;
}}
.avi-user-meta {{
  font-size: 0.72rem;
  color: {MUTED};
  margin: 0.15rem 0 0.55rem 0;
}}

.kpi-card {{
  background: {CARD};
  border: 1px solid {LINE};
  border-top: 3px solid {TEAL};
  padding: 0.85rem 0.95rem 0.75rem 0.95rem;
  min-height: 108px;
}}
.kpi-label {{
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: {MUTED};
  font-weight: 600;
}}
.kpi-value {{
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.55rem;
  font-weight: 650;
  color: {CHARCOAL};
  line-height: 1.2;
  margin-top: 0.25rem;
}}
.kpi-delta {{
  font-size: 0.75rem;
  color: {SLATE};
  margin-top: 0.2rem;
}}
.kpi-help {{
  font-size: 0.7rem;
  color: {MUTED};
}}

.insight-box {{
  background: {CARD};
  border: 1px solid {LINE};
  border-left: 3px solid {TEAL};
  padding: 0.75rem 0.9rem;
  margin-bottom: 0.55rem;
  font-size: 0.9rem;
  line-height: 1.45;
}}
.exec-hero {{
  background: {CARD};
  border: 1px solid {LINE};
  border-left: 4px solid {TEAL};
  padding: 1rem 1.15rem;
  margin: 0.2rem 0 1rem 0;
}}
.exec-hero-label {{
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
  color: {CRIMSON};
}}
.exec-hero-solution {{
  color: {TEAL};
  margin-top: 0.7rem;
}}
.exec-hero-approach {{
  color: {AMBER};
  margin-top: 0.7rem;
}}
.exec-hero-text {{
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 1.05rem;
  line-height: 1.5;
  color: {CHARCOAL};
  margin-top: 0.2rem;
}}
.insight-attn {{
  border-left-color: {AMBER};
}}
.insight-risk {{
  border-left-color: {CRIMSON};
}}

.section-note {{
  color: {MUTED};
  font-size: 0.85rem;
  margin-bottom: 0.8rem;
}}

.chain-step {{
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: {TEAL_DARK};
  font-weight: 600;
  display: block;
  white-space: normal;
  line-height: 1.7;
}}

div[data-testid="stMetric"] {{
  background: {CARD};
  border: 1px solid {LINE};
  padding: 0.6rem 0.75rem;
}}

.stTabs [data-baseweb="tab-list"] {{
  gap: 0.25rem;
}}
.stTabs [data-baseweb="tab"] {{
  font-size: 0.85rem;
}}

[data-testid="stPlotlyChart"] {{
  padding: 0.35rem 0 0.85rem 0;
}}

footer {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}

.block-container {{
  padding-top: 1.6rem;
  padding-bottom: 2.5rem;
  max-width: 1400px;
}}

[data-testid="stDataFrame"] {{
  overflow-x: auto;
}}

.stTabs [data-baseweb="tab-list"] {{
  flex-wrap: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
}}

@media (max-width: 900px) {{
  h1 {{
    font-size: 1.4rem !important;
    line-height: 1.3 !important;
    padding-top: 0.35rem;
  }}
  h2 {{ font-size: 1.15rem !important; }}
  .block-container {{
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 3.5rem !important;
  }}
  [data-testid="stHeader"] {{
    min-height: 3rem;
  }}
  .kpi-card {{
    min-height: 0;
    margin-bottom: 0.35rem;
  }}
  .kpi-value {{ font-size: 1.28rem; }}
  [data-testid="stHorizontalBlock"] {{
    flex-wrap: wrap !important;
    gap: 0.35rem 0.5rem;
  }}
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    min-width: calc(50% - 0.4rem) !important;
    flex: 1 1 calc(50% - 0.4rem) !important;
  }}
  [data-testid="stPlotlyChart"] {{
    max-width: 100%;
  }}
  .stTabs [data-baseweb="tab"] {{
    font-size: 0.78rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }}
}}

@media (max-width: 560px) {{
  h1 {{
    font-size: 1.22rem !important;
    margin-top: 0.2rem !important;
    padding-top: 0.45rem;
  }}
  .block-container {{
    padding-top: calc(4rem + env(safe-area-inset-top, 0px)) !important;
    padding-left: 1rem;
    padding-right: 1rem;
  }}
  .avi-brand {{ font-size: 1.15rem; }}
  .exec-hero {{ padding: 0.85rem 0.9rem; }}
  .exec-hero-text {{ font-size: 0.95rem; }}
  .kpi-card {{ padding: 0.7rem 0.75rem; }}
  .kpi-label {{ font-size: 0.66rem; }}
  .kpi-value {{ font-size: 1.15rem; }}
  .section-note {{ font-size: 0.8rem; }}
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }}
  [data-testid="stSidebar"] {{
    width: min(92vw, 340px) !important;
  }}
}}
</style>
"""


def apply_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
