"""Home page: the elder's landing screen. One companion, everything at a
glance, instead of five silent tabs that don't know about each other."""

import streamlit as st

from backend import activities, calendar, chat, companion_line, medications
from backend.strings import get_string
from ui import render_card, render_read_aloud_button

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_home"))

chat.maybe_send_daily_checkin(profile.id)
opener = chat.get_todays_opener(profile.id, lang)
line_type = companion_line.get_todays_line_type(profile.id)

if opener:
    render_card("", opener, icon="💬")
    render_read_aloud_button(
        opener, key="home-opener", label=get_string(lang, "voice_read_aloud_button")
    )
    if line_type == "family_nudge":
        if companion_line.family_nudge_accepted_today(profile.id):
            # Without this check, the ask + button would keep re-rendering
            # on every revisit today, even right after being accepted.
            st.caption(get_string(lang, "family_nudge_accepted_message"))
        elif st.button(get_string(lang, "home_yes_remind_button")):
            companion_line.log_family_nudge_accepted(profile.id)
            st.rerun()
    elif st.button(get_string(lang, "home_reply_button")):
        st.switch_page("pages/1_Chat.py")

doses = medications.get_todays_doses(profile.id)
next_dose = next((d for d in doses if d.status == "pending"), None)
events = calendar.list_upcoming_events(profile.id)
next_event = events[0] if events else None

if next_dose or next_event:
    glance_cols = st.columns(2)
    with glance_cols[0]:
        if next_dose:
            st.write(f"💊 {next_dose.medication_name}, {next_dose.scheduled_for.strftime('%H:%M')}")
    with glance_cols[1]:
        if next_event:
            st.write(f"📅 {next_event.title}, {next_event.start_time.strftime('%a %H:%M')}")

st.divider()

nav_cols = st.columns(2)
with nav_cols[0]:
    if st.button(f"💬 {get_string(lang, 'nav_chat')}", use_container_width=True):
        st.switch_page("pages/1_Chat.py")
    if st.button(f"💊 {get_string(lang, 'nav_medication')}", use_container_width=True):
        st.switch_page("pages/3_Medication.py")
with nav_cols[1]:
    if st.button(f"📷 {get_string(lang, 'nav_point_and_ask')}", use_container_width=True):
        st.switch_page("pages/2_Point_and_Ask.py")
    if st.button(f"📅 {get_string(lang, 'nav_calendar')}", use_container_width=True):
        st.switch_page("pages/4_Calendar.py")

with st.expander(f"🌳 {get_string(lang, 'activities_card_title')}"):
    st.write(get_string(lang, "activities_intro"))
    for activity in activities.get_nearby_activities():
        st.write(f"{activity.icon} **{activity.title}** ({activity.schedule})")

st.divider()
st.caption(get_string(lang, "companion_boundary_statement"))
