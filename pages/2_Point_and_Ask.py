"""Point & Ask page. Placeholder — full implementation lands in Phase 2."""

import streamlit as st

from ui import render_card

st.title("Point & Ask")
render_card(
    "Coming soon",
    "Take a photo of a letter or message to have it explained or checked for scams.",
    icon="📷",
)
