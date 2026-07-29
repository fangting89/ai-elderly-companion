"""Calendar page: upcoming events and adding new ones."""

from datetime import datetime, time

import streamlit as st

from backend import calendar
from backend.strings import get_string

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_calendar"))

events = calendar.list_upcoming_events(profile.id)

if not events:
    st.write(get_string(lang, "calendar_no_events_message"))
else:
    for event in events:
        st.write(f"📅 **{event.title}**, {event.start_time.strftime('%a %d %b, %H:%M')}")
        if event.notes:
            st.caption(event.notes)

st.divider()

with st.expander(get_string(lang, "calendar_add_expander")):
    with st.form("add_event", clear_on_submit=True):
        title = st.text_input(get_string(lang, "calendar_title_label"))
        event_date = st.date_input(get_string(lang, "calendar_date_label"))
        event_time = st.time_input(get_string(lang, "calendar_time_label"), value=time(9, 0))
        notes = st.text_input(get_string(lang, "calendar_notes_label"))
        submitted = st.form_submit_button(get_string(lang, "add_button"))
    if submitted and title:
        start_time = datetime.combine(event_date, event_time)
        calendar.add_event(profile.id, title, start_time, notes=notes or None)
        st.rerun()
