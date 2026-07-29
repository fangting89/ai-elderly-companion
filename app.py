"""Entry point: Supabase auth and role-based page navigation."""

import streamlit as st

from backend.db import get_client, get_profile

st.set_page_config(page_title="AI Elderly Companion", layout="centered")


def _sign_in_form() -> None:
    """Render the sign-in form and populate st.session_state on success."""
    st.title("AI Elderly Companion")
    with st.form("sign_in"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if not submitted:
        return

    try:
        result = get_client().auth.sign_in_with_password({"email": email, "password": password})
    except Exception as exc:
        st.error(f"Sign in failed: {exc}")
        return

    profile = get_profile(result.user.id)
    if profile is None:
        st.error("No profile found for this account. Ask an admin to set one up.")
        return

    st.session_state["profile"] = profile
    st.rerun()


def _elder_pages() -> list[st.Page]:
    return [
        st.Page("pages/1_Chat.py", title="Chat", icon="💬"),
        st.Page("pages/2_Point_and_Ask.py", title="Point & Ask", icon="📷"),
        st.Page("pages/3_Medication.py", title="Medication", icon="💊"),
        st.Page("pages/4_Calendar.py", title="Calendar", icon="📅"),
    ]


def _family_pages() -> list[st.Page]:
    return [
        st.Page("pages/5_Family_Dashboard.py", title="Dashboard", icon="👨‍👩‍👧"),
        st.Page("pages/6_Family_Settings.py", title="Settings", icon="⚙️"),
    ]


profile = st.session_state.get("profile")

if profile is None:
    _sign_in_form()
else:
    with st.sidebar:
        st.write(f"Signed in as **{profile.display_name}** ({profile.role})")
        if st.button("Sign out"):
            get_client().auth.sign_out()
            del st.session_state["profile"]
            st.rerun()

    pages = _elder_pages() if profile.role == "elder" else _family_pages()
    st.navigation(pages).run()
