"""Chat page: talk with the companion."""

import streamlit as st

from backend import chat

st.title("Chat")

elder_id = st.session_state["profile"].id
chat.maybe_send_daily_checkin(elder_id)

for message in chat.get_history(elder_id):
    with st.chat_message("user" if message["sender"] == "elder" else "assistant"):
        st.write(message["content"])

user_text = st.chat_input("Type a message...")
if user_text:
    with st.spinner("Thinking..."):
        chat.send_message(elder_id, user_text)
    st.rerun()
