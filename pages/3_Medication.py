"""Medication page: today's doses, mark-taken, and adding new medications."""

import streamlit as st

from backend import medications
from backend.strings import get_string

# "missed" deliberately isn't an alarming icon: it fires purely from
# scheduled time passing, unrelated to whether it's ever risen to a
# family alert -- ⚠️ is reserved for the Family Dashboard's actual alerts.
_STATUS_ICON = {"pending": "⏰", "taken": "✅", "missed": "🔔"}

profile = st.session_state["profile"]
lang = profile.preferred_language

st.title(get_string(lang, "nav_medication"))

doses = medications.get_todays_doses(profile.id)

if not doses:
    st.write(get_string(lang, "medication_coming_soon_body"))
else:
    for dose in doses:
        cols = st.columns([4, 1])
        with cols[0]:
            icon = _STATUS_ICON[dose.status]
            time_str = dose.scheduled_for.strftime("%H:%M")
            st.write(f"{icon} **{dose.medication_name}** ({dose.dosage}), {time_str}")
        with cols[1]:
            if dose.status != "taken" and st.button(
                get_string(lang, "medication_mark_taken_button"), key=dose.log_id
            ):
                medications.mark_taken(dose.log_id)
                st.rerun()

st.divider()

with st.expander(get_string(lang, "medication_add_expander")):
    with st.form("add_medication", clear_on_submit=True):
        name = st.text_input(get_string(lang, "medication_name_label"))
        dosage = st.text_input(get_string(lang, "medication_dosage_label"), value="1 tablet")
        times_text = st.text_input(get_string(lang, "medication_times_label"), value="08:00")
        submitted = st.form_submit_button(get_string(lang, "add_button"))
    if submitted and name:
        times = [t.strip() for t in times_text.split(",") if t.strip()]
        medications.add_medication(profile.id, name, dosage, times)
        st.rerun()
