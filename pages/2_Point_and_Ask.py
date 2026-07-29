"""Point & Ask page: upload a photo to have it explained or checked for scams."""

import streamlit as st

from backend import point_and_ask
from backend.strings import get_string
from ui import render_card

st.title("Point & Ask")
st.write("Take or upload a photo of a letter, message, or document.")

uploaded = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png", "webp"])

if uploaded is not None:
    st.image(uploaded, width=300)
    profile = st.session_state["profile"]

    with st.spinner("Looking at this..."):
        result = point_and_ask.process_photo(profile.id, uploaded.getvalue())

    if result.classification == "scam":
        st.error(get_string(profile.preferred_language, "scam_warning_title"))
        st.write(get_string(profile.preferred_language, "scam_warning_body"))
    elif result.classification == "unclear":
        st.warning(get_string(profile.preferred_language, "blurry_photo_message"))
    else:
        render_card(
            "Here's what this says", result.explanation or result.content_summary, icon="📄"
        )
