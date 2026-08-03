"""Entry point: demo role selector and role-based page navigation.

No real login for this POC — a sidebar selector switches between the
seeded demo elder and family profiles.
"""

import streamlit as st

from backend.db import get_profile_by_role
from backend.strings import get_string
from ui import inject_global_css

st.set_page_config(page_title="AI Elderly Companion", layout="centered")
inject_global_css()


def _elder_pages(language: str) -> list[st.Page]:
    return [
        st.Page("pages/0_Home.py", title=get_string(language, "nav_home"), icon="🏠"),
        st.Page("pages/1_Chat.py", title=get_string(language, "nav_chat"), icon="💬"),
        st.Page(
            "pages/2_Point_and_Ask.py", title=get_string(language, "nav_point_and_ask"), icon="📷"
        ),
        st.Page("pages/3_Medication.py", title=get_string(language, "nav_medication"), icon="💊"),
        st.Page("pages/4_Calendar.py", title=get_string(language, "nav_calendar"), icon="📅"),
    ]


def _family_pages() -> list[st.Page]:
    return [
        st.Page("pages/5_Family_Dashboard.py", title="Dashboard", icon="👨‍👩‍👧"),
        st.Page("pages/6_Family_Settings.py", title="Settings", icon="⚙️"),
    ]


with st.sidebar:
    role = st.selectbox("View as", ["elder", "family"], format_func=str.title)

profile = get_profile_by_role(role)
if profile is None:
    st.error("No demo profile found. Restart the app to reseed demo data.")
    st.stop()

st.session_state["profile"] = profile

with st.sidebar:
    st.write(f"Viewing as **{profile.display_name}** ({profile.role})")

pages = _elder_pages(profile.preferred_language) if profile.role == "elder" else _family_pages()
st.navigation(pages).run()
