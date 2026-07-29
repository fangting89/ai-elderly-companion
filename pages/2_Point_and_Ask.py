"""Point & Ask page: upload a photo to have it explained or checked for scams."""

import streamlit as st

from backend import point_and_ask
from ui import render_card

st.title("Point & Ask")
st.write("Take or upload a photo of a letter, message, or document.")

uploaded = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png", "webp"])

if uploaded is not None:
    st.image(uploaded, width=300)
    elder_id = st.session_state["profile"].id

    with st.spinner("Looking at this..."):
        result = point_and_ask.process_photo(elder_id, uploaded.getvalue())

    if result.classification == "scam":
        st.error(f"This looks like it could be a scam (risk: {result.risk_level}).")
        st.write(result.content_summary)
        st.write(
            "Please don't reply, click any links, or send money or personal details. "
            "Ask a family member before doing anything else about this."
        )
    elif result.classification == "unclear":
        st.warning(
            "The photo isn't clear enough to read. Please try taking another "
            "photo with better lighting."
        )
    else:
        render_card(
            "Here's what this says", result.explanation or result.content_summary, icon="📄"
        )
        if result.translation:
            render_card("In Mandarin Chinese", result.translation, icon="🌐")
