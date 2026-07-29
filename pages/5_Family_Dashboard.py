"""Family dashboard page. Memory bank is built here; adherence/sentiment/alerts
still land in a later phase, hence the placeholder card alongside it."""

import streamlit as st

from backend import memory_bank
from ui import render_card

profile = st.session_state["profile"]
elder_id = profile.elder_id

st.title("Family Dashboard")
render_card(
    "Coming soon",
    "Adherence, sentiment trend, and alerts for your family member.",
    icon="👨‍👩‍👧",
)

st.divider()
st.subheader("Memory Bank")
st.caption(
    "Facts and photos you add here help the companion talk naturally about "
    "your family member's life. It never invents details beyond what you provide."
)

with st.expander("Add a fact"):
    with st.form("add_fact", clear_on_submit=True):
        fact_text = st.text_input("Fact (e.g. 'Loves gardening, especially roses')")
        submitted = st.form_submit_button("Add")
    if submitted and fact_text:
        memory_bank.add_fact(elder_id, profile.id, fact_text)
        st.rerun()

with st.expander("Add a photo"):
    with st.form("add_photo", clear_on_submit=True):
        photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png", "webp"])
        caption = st.text_input("Caption (e.g. 'Family trip to Bali, 2019')")
        submitted = st.form_submit_button("Add")
    if submitted and photo and caption:
        memory_bank.add_photo(elder_id, profile.id, photo.getvalue(), caption)
        st.rerun()

st.subheader("Stored memories")
entries = memory_bank.list_entries(elder_id)
if not entries:
    st.write("No memories added yet.")
else:
    for entry in entries:
        if entry.entry_type == "photo" and entry.image_path:
            st.image(entry.image_path, width=200, caption=entry.content_text)
        else:
            st.write(f"📝 {entry.content_text}")
