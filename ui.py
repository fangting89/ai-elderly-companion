"""Shared design-system styling and layout helpers.

Every page should call inject_global_css() once, near the top, and use
render_card() instead of raw st.info()/st.write() for content blocks, so the
whole app stays visually consistent as new pages are added.
"""

import json

import streamlit as st


def _js_string(text: str) -> str:
    """JSON-encode text for safe embedding inside an inline <script> block.

    json.dumps alone isn't enough: a literal "</script>" inside the string
    would still close the surrounding tag early when the browser's HTML
    parser scans for it, regardless of JS string-quoting. Chat content is
    user-typed (elder or family), so this has to be handled, not assumed away.
    """
    return json.dumps(text).replace("</", "<\\/")


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


def render_read_aloud_button(text: str, key: str, label: str = "🔊") -> None:
    """Render a "read aloud" button using the browser's native speechSynthesis API.

    Best-effort and free: no API cost, no new dependency, works in most
    modern browsers. If the browser doesn't support it, the button just
    disables itself rather than erroring.

    Args:
        text: the text to speak aloud.
        key: a unique id for this button instance (a page renders one per
            chat message, so ids must not collide).
        label: the button's visible label (pass a localized string; this
            comes from strings.py, not user input, so it's safe to inline).
    """
    button_id = f"read-aloud-{key}"
    payload = _js_string(text)
    st.iframe(
        f"""
        <button id="{button_id}" style="
            font-size: 0.9rem; padding: 0.3rem 0.6rem; border-radius: 0.5rem;
            border: 1px solid #ccc; background: #fff; cursor: pointer;
        ">{label}</button>
        <script>
        (function() {{
            const btn = document.getElementById("{button_id}");
            if (!window.speechSynthesis) {{
                btn.disabled = true;
                return;
            }}
            btn.onclick = function() {{
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(new SpeechSynthesisUtterance({payload}));
            }};
        }})();
        </script>
        """,
        height=45,
    )


def render_voice_input_widget(key: str, not_supported_text: str, label: str = "🎤") -> None:
    """Render a microphone button that fills Streamlit's chat input via speech-to-text.

    Uses the browser's native SpeechRecognition API (Chrome/Edge only,
    requires mic permission) -- free, no new dependency, but genuinely
    best-effort: st.iframe renders this in a same-origin iframe, so this
    reaches into the parent page's DOM to set Streamlit's chat input
    textarea and click its submit button. That's a DOM-reliant trick, not an
    officially supported Streamlit API, so it can break on a Streamlit
    version bump; it degrades to showing the transcript as plain text for
    manual copy-paste if the expected elements aren't found.

    Args:
        key: a unique id for this widget instance.
        not_supported_text: localized message shown if the browser lacks
            SpeechRecognition support.
        label: the button's visible label (pass a localized string; this
            comes from strings.py, not user input, so it's safe to inline).
    """
    button_id = f"mic-btn-{key}"
    status_id = f"mic-status-{key}"
    not_supported_json = _js_string(not_supported_text)
    st.iframe(
        f"""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <button id="{button_id}" style="
              font-size: 0.9rem; padding: 0.3rem 0.6rem; border-radius: 0.5rem;
              border: 1px solid #ccc; background: #fff; cursor: pointer;
          ">{label}</button>
          <span id="{status_id}" style="color: #666; font-size: 0.85rem;"></span>
        </div>
        <script>
        (function() {{
            const btn = document.getElementById("{button_id}");
            const status = document.getElementById("{status_id}");
            const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!Recognition) {{
                btn.disabled = true;
                status.innerText = {not_supported_json};
                return;
            }}
            const recognition = new Recognition();
            recognition.lang = "en-US";
            recognition.interimResults = false;

            btn.onclick = function() {{
                status.innerText = "...";
                recognition.start();
            }};

            recognition.onresult = function(event) {{
                const transcript = event.results[0][0].transcript;
                try {{
                    const doc = window.parent.document;
                    const textarea = doc.querySelector(
                        'textarea[data-testid="stChatInputTextArea"]'
                    );
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.parent.HTMLTextAreaElement.prototype, "value"
                    ).set;
                    nativeSetter.call(textarea, transcript);
                    textarea.dispatchEvent(new Event("input", {{ bubbles: true }}));
                    status.innerText = "";
                    const submitBtn = doc.querySelector(
                        'button[data-testid="stChatInputSubmitButton"]'
                    );
                    if (submitBtn) {{
                        submitBtn.click();
                    }}
                }} catch (e) {{
                    status.innerText = transcript;
                }}
            }};

            recognition.onerror = function() {{
                status.innerText = "";
            }};
        }})();
        </script>
        """,
        height=45,
    )
