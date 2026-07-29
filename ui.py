"""Shared design-system styling and layout helpers.

Every page should call inject_global_css() once, near the top, and use
render_card() instead of raw st.info()/st.write() for content blocks, so the
whole app stays visually consistent as new pages are added.
"""

import streamlit as st


def inject_global_css() -> None:
    """Inject the shared design-system CSS for this run.

    Reads card background color from the active theme (.streamlit/config.toml)
    so it stays in sync with the rest of the palette automatically.
    """
    secondary_bg = st.get_option("theme.secondaryBackgroundColor") or "#F2E9DD"
    css = f"""
    <style>
    html, body, [class*="css"] {{
        font-size: 18px;
    }}
    h1 {{ font-size: 2.2rem !important; }}
    h2 {{ font-size: 1.6rem !important; }}
    h3 {{ font-size: 1.3rem !important; }}

    .stButton > button {{
        min-height: 3rem;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-size: 1.1rem;
        font-weight: 600;
    }}

    .app-card {{
        background: {secondary_bg};
        border-radius: 1rem;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }}
    .app-card h3 {{ margin-top: 0; }}
    .app-card p {{ margin-bottom: 0; }}

    /* Hide the "Made with Streamlit" footer and the old hamburger menu for a
       more product-like feel. Deliberately NOT touching the header/toolbar
       area beyond this -- it also hosts the sidebar re-expand control, and
       hiding it left users unable to bring a collapsed sidebar back. */
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_card(title: str, body: str, icon: str = "") -> None:
    """Render a styled content card.

    Args:
        title: card heading text.
        body: card body text, rendered as markdown-in-HTML.
        icon: optional leading emoji shown next to the title.
    """
    heading = f"{icon} {title}".strip()
    st.markdown(
        f'<div class="app-card"><h3>{heading}</h3><p>{body}</p></div>',
        unsafe_allow_html=True,
    )
