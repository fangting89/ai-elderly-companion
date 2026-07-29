"""Family settings page: set the elder's preferred language."""

import streamlit as st

from backend.db import get_profile, update_preferred_language

SUPPORTED_LANGUAGES = ["English", "Mandarin Chinese", "Malay", "Tamil"]

st.title("Settings")

family_profile = st.session_state["profile"]
elder = get_profile(family_profile.elder_id) if family_profile.elder_id else None

if elder is None:
    st.error("No linked elder profile found.")
    st.stop()

st.write(f"Language settings for **{elder.display_name}**")
st.caption(
    "The companion's chat replies and Point & Ask explanations are generated "
    "directly in this language, so it matters more than any other setting here."
)

selected = st.selectbox(
    "Preferred language",
    SUPPORTED_LANGUAGES,
    index=SUPPORTED_LANGUAGES.index(elder.preferred_language),
)

if st.button("Save"):
    update_preferred_language(elder.id, selected)
    st.success(f"Saved. {elder.display_name}'s preferred language is now {selected}.")
