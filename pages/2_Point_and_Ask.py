"""Point & Ask page: take or upload a photo to have it explained or checked for scams."""

import streamlit as st

from backend import point_and_ask
from backend.strings import get_string
from ui import render_card

EXAMPLE_IMAGE_PATH = "eval/point_and_ask_images/case_10_legit_community.png"

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_point_and_ask"))
st.write(get_string(lang, "point_and_ask_intro"))
st.caption(get_string(lang, "point_and_ask_tips"))

with st.expander(get_string(lang, "point_and_ask_example_label")):
    st.image(
        EXAMPLE_IMAGE_PATH, caption=get_string(lang, "point_and_ask_example_caption"), width=300
    )

camera_tab, upload_tab = st.tabs(
    [
        get_string(lang, "point_and_ask_camera_button"),
        get_string(lang, "point_and_ask_uploader_label"),
    ]
)
with camera_tab:
    camera_photo = st.camera_input(
        get_string(lang, "point_and_ask_camera_button"), label_visibility="collapsed"
    )
with upload_tab:
    uploaded_file = st.file_uploader(
        get_string(lang, "point_and_ask_uploader_label"),
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

uploaded = camera_photo or uploaded_file

if uploaded is not None:
    st.image(uploaded, width=300)

    # Streamlit reruns this whole block on any page interaction (e.g. the
    # "notify family now" button below) as long as the widget still holds
    # this file -- without this guard, every rerun would reprocess the same
    # photo and write a second identical alert.
    if st.session_state.get("point_and_ask_processed_id") != uploaded.file_id:
        with st.spinner(get_string(lang, "point_and_ask_spinner")):
            result = point_and_ask.process_photo(profile.id, uploaded.getvalue())
        st.session_state["point_and_ask_processed_id"] = uploaded.file_id
        st.session_state["point_and_ask_result"] = result
    else:
        result = st.session_state["point_and_ask_result"]

    if result.classification == "scam":
        st.error(get_string(lang, "scam_warning_title"))
        st.write(get_string(lang, "scam_warning_body"))
        # The alert was already raised automatically in process_photo -- this
        # button gives the elder a felt, immediate action in the moment,
        # rather than only passive advisory text.
        if st.button(get_string(lang, "point_and_ask_notify_family_button")):
            st.success(get_string(lang, "point_and_ask_family_notified_message"))
    elif result.classification == "unclear":
        st.warning(get_string(lang, "blurry_photo_message"))
    else:
        render_card(
            get_string(lang, "point_and_ask_result_title"),
            result.explanation or result.content_summary,
            icon="📄",
        )
