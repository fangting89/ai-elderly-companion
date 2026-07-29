"""Point & Ask page: upload a photo to have it explained or checked for scams."""

import streamlit as st

from backend import point_and_ask
from backend.strings import get_string
from ui import render_card

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_point_and_ask"))
st.write(get_string(lang, "point_and_ask_intro"))

uploaded = st.file_uploader(
    get_string(lang, "point_and_ask_uploader_label"), type=["jpg", "jpeg", "png", "webp"]
)

if uploaded is not None:
    st.image(uploaded, width=300)

    with st.spinner(get_string(lang, "point_and_ask_spinner")):
        result = point_and_ask.process_photo(profile.id, uploaded.getvalue())

    if result.classification == "scam":
        st.error(get_string(lang, "scam_warning_title"))
        st.write(get_string(lang, "scam_warning_body"))
    elif result.classification == "unclear":
        st.warning(get_string(lang, "blurry_photo_message"))
    else:
        render_card(
            get_string(lang, "point_and_ask_result_title"),
            result.explanation or result.content_summary,
            icon="📄",
        )
