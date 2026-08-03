"""Family dashboard page: a weekly summary, alerts, adherence, sentiment,
and memory bank.

Family-facing throughout, so left in English per the established scope
boundary (family already operates the admin flow in English regardless).
No two-way messaging here by design -- family is meant to call, not add
another app-mediated channel to check.
"""

import altair as alt
import pandas as pd
import streamlit as st

from backend import dashboard, memory_bank

profile = st.session_state["profile"]
elder_id = profile.elder_id

st.title("Family Dashboard")

# --- Weekly summary, in the companion's voice -------------------------------
# Cached in session_state -- only regenerated on explicit request, since it's
# an LLM call and the Anthropic API is a self-funded personal budget.
summary_key = f"weekly_summary_{elder_id}"
cols = st.columns([5, 1])
with cols[1]:
    if st.button("Refresh"):
        st.session_state[summary_key] = dashboard.get_weekly_summary(elder_id)
with cols[0]:
    if summary_key in st.session_state:
        st.info(st.session_state[summary_key])
    else:
        st.caption("Click Refresh for a plain-language summary of this week.")

st.divider()

# --- Alerts ---------------------------------------------------------------
st.subheader("Alerts")
alerts = dashboard.get_alerts(elder_id)
open_alerts = [a for a in alerts if a["status"] == "open"]
if not open_alerts:
    st.write("No open alerts.")
else:
    for alert in open_alerts:
        alert_cols = st.columns([5, 1])
        with alert_cols[0]:
            label = alert["alert_type"].replace("_", " ").title()
            # Streamlit's markdown renderer treats a "$...$" pair as inline
            # LaTeX -- two dollar amounts in one message (e.g. a scam sum
            # and a fine) form an unintended math span that fails to parse
            # and falls back to showing the raw source in backticks.
            message = alert["message"].replace("$", "\\$")
            st.warning(f"**{label}**: {message}")
        with alert_cols[1]:
            if st.button("Acknowledge", key=alert["id"]):
                dashboard.acknowledge_alert(alert["id"])
                st.rerun()

if any(a["alert_type"] == "sentiment_decline" for a in open_alerts):
    st.info(
        "**Consider a befriending or counselling service.** Sustained low mood "
        "can sometimes benefit from more than a check-in call. Local eldercare "
        "agencies or community health services typically offer befriending "
        "programs or a referral to counselling, if you feel it would help."
    )

non_escalated = dashboard.get_non_escalated_misses(elder_id)
if non_escalated:
    names = ", ".join(row["medication_name"] for row in non_escalated)
    st.caption(
        f"Also: a single missed dose of {names} this week, no pattern yet. "
        "You'll only hear from me if that changes."
    )

st.divider()

# --- Connections facilitated -------------------------------------------------
st.subheader("Connections facilitated")
connections = dashboard.get_connections_facilitated_count(elder_id)
st.metric("Family contacts encouraged this month", connections)
st.caption(
    "How often the companion nudged a reach-out to family, and it was acted "
    "on, not how much time was spent talking to the AI."
)

st.divider()

# --- Adherence --------------------------------------------------------------
st.subheader("Medication adherence (last 7 days)")
adherence_rows = dashboard.get_adherence_by_day(elder_id)
if not adherence_rows:
    st.write("No medication data yet.")
else:
    adherence_df = pd.DataFrame(adherence_rows)
    status_colors = alt.Scale(
        domain=["taken", "pending", "missed"], range=["#0ca30c", "#fab219", "#d03b3b"]
    )
    chart = (
        alt.Chart(adherence_df)
        .mark_bar()
        .encode(
            x=alt.X("date:O", title="Date"),
            y=alt.Y("count:Q", title="Doses"),
            color=alt.Color("status:N", scale=status_colors, legend=alt.Legend(title="Status")),
            order=alt.Order("status:N"),
        )
        .properties(height=250)
    )
    st.altair_chart(chart, use_container_width=True)

st.divider()

# --- Mood ---------------------------------------------------------------
st.subheader("Mood")
this_week_mood, last_week_mood = dashboard.get_mood_weekly_comparison(elder_id)
if this_week_mood is None:
    st.write("No chat activity yet this week.")
else:
    mood_delta = round(this_week_mood - last_week_mood, 1) if last_week_mood is not None else None
    st.metric("Mood this week", dashboard.mood_score_to_label(this_week_mood), delta=mood_delta)
with st.expander("See day-by-day detail"):
    sentiment_rows = dashboard.get_sentiment_trend(elder_id)
    if not sentiment_rows:
        st.write("No chat sentiment data yet.")
    else:
        sentiment_df = pd.DataFrame(sentiment_rows).set_index("date")
        st.caption("Scored distress=0, low=1, neutral=2, positive=3, averaged per day.")
        st.line_chart(sentiment_df["score"])

st.divider()

# --- Repeated-question frequency --------------------------------------------
st.subheader("Repeated questions")
if not dashboard.has_chat_activity_this_week(elder_id):
    st.write("No chat activity yet this week.")
else:
    this_week, last_week = dashboard.get_repeated_question_weekly_counts(elder_id)
    st.metric(
        "This week vs. last week",
        this_week,
        delta=this_week - last_week,
        delta_color="inverse",
    )
st.caption("Never shown to the elder. A rising trend can be an early sign worth a check-in call.")

st.divider()

# --- Supporting a loved one ---------------------------------------------------
st.subheader("Supporting a loved one")
st.caption(
    "Caring for a family member can be tiring too. If you need it, caregiver "
    "support resources (respite care, counselling, peer support groups) are "
    "usually available through local eldercare or community health services."
)

st.divider()

# --- Memory Bank -------------------------------------------------------------
st.subheader("Memory Bank")
st.caption(
    "Facts and photos you add here help the companion talk naturally about "
    "your family member's life. It never invents details beyond what you provide."
)

with st.expander("Add a fact"):
    with st.form("add_fact", clear_on_submit=True):
        fact_text = st.text_input("Fact (e.g. 'Loves gardening, especially roses')")
        fact_submitted = st.form_submit_button("Add")
    if fact_submitted and fact_text:
        memory_bank.add_fact(elder_id, profile.id, fact_text)
        st.rerun()

with st.expander("Add a photo"):
    with st.form("add_photo", clear_on_submit=True):
        photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png", "webp"])
        caption = st.text_input("Caption (e.g. 'Family trip to Bali, 2019')")
        photo_submitted = st.form_submit_button("Add")
    if photo_submitted and photo and caption:
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
