"""Medication page. Placeholder — full implementation lands in Phase 3."""

import streamlit as st

from backend.strings import get_string
from ui import render_card

lang = st.session_state["profile"].preferred_language

st.title(get_string(lang, "nav_medication"))
render_card(
    get_string(lang, "coming_soon_title"),
    get_string(lang, "medication_coming_soon_body"),
    icon="💊",
)
