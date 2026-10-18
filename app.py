import streamlit as st

from auth.ui import navigation_pages

st.navigation(navigation_pages()).run()
