"""Supabase client and profile lookup shared across the app."""

from dataclasses import dataclass
from typing import Literal

import streamlit as st
from supabase import Client, create_client


@dataclass
class Profile:
    id: str
    role: Literal["elder", "family"]
    display_name: str
    elder_id: str | None


@st.cache_resource
def get_client() -> Client:
    """Return a cached Supabase client built from Streamlit secrets.

    Returns:
        Client: an authenticated Supabase client instance.
    """
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_profile(user_id: str) -> Profile | None:
    """Fetch a user's profile row by id.

    Args:
        user_id: Supabase auth user id.

    Returns:
        Profile | None: the matching profile, or None if not found.
    """
    response = get_client().table("profiles").select("*").eq("id", user_id).limit(1).execute()
    rows = response.data
    if not rows:
        return None
    row = rows[0]
    return Profile(
        id=row["id"],
        role=row["role"],
        display_name=row["display_name"],
        elder_id=row.get("elder_id"),
    )
