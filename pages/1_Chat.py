"""Chat page: talk with the companion."""

import streamlit as st

from backend import chat
from backend.strings import get_string

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_chat"))

chat.maybe_send_daily_checkin(profile.id)

for message in chat.get_history(profile.id, lang):
    with st.chat_message("user" if message["sender"] == "elder" else "assistant"):
        st.write(message["content"])

user_text = st.chat_input(get_string(lang, "chat_input_placeholder"))
if user_text:
    with st.spinner(get_string(lang, "chat_thinking_spinner")):
        chat.send_message(profile.id, user_text)
    st.rerun()
