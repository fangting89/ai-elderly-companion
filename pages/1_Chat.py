"""Chat page: talk with the companion."""

import streamlit as st

from backend import chat
from backend.strings import get_string
from ui import render_read_aloud_button, render_voice_input_widget

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_chat"))

chat.maybe_send_daily_checkin(profile.id)

if st.button(get_string(lang, "chat_share_memory_button")):
    opener = chat.add_reminiscence_message(profile.id, lang)
    if opener is None:
        st.info(get_string(lang, "chat_no_memories_message"))
    else:
        st.rerun()

for i, message in enumerate(chat.get_history(profile.id, lang)):
    sender = message["sender"]
    with st.chat_message("user" if sender == "elder" else "assistant"):
        st.write(message["content"])
        if sender == "ai":
            render_read_aloud_button(
                message["content"],
                key=f"chat-{i}",
                label=get_string(lang, "voice_read_aloud_button"),
            )

render_voice_input_widget(
    key="chat-input",
    not_supported_text=get_string(lang, "voice_not_supported_message"),
    label=get_string(lang, "voice_mic_button"),
)
user_text = st.chat_input(get_string(lang, "chat_input_placeholder"))
if user_text:
    with st.spinner(get_string(lang, "chat_thinking_spinner")):
        chat.send_message(profile.id, user_text)
    st.rerun()
