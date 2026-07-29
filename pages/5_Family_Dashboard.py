"""Family dashboard page: alerts, adherence, sentiment trend, and memory bank.

Family-facing throughout, so left in English per the established scope
boundary (family already operates the admin flow in English regardless).
"""

import altair as alt
import pandas as pd
import streamlit as st

from backend import dashboard, memory_bank

profile = st.session_state["profile"]
elder_id = profile.elder_id

st.title("Family Dashboard")

# --- Alerts ---------------------------------------------------------------
st.subheader("Alerts")
alerts = dashboard.get_alerts(elder_id)
open_alerts = [a for a in alerts if a["status"] == "open"]
if not open_alerts:
    st.write("No open alerts.")
else:
    for alert in open_alerts:
        cols = st.columns([5, 1])
        with cols[0]:
            label = alert["alert_type"].replace("_", " ").title()
            st.warning(f"**{label}**: {alert['message']}")
        with cols[1]:
            if st.button("Acknowledge", key=alert["id"]):
                dashboard.acknowledge_alert(alert["id"])
                st.rerun()

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

# --- Sentiment trend --------------------------------------------------------
st.subheader("Mood trend (last 14 days)")
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
this_week, last_week = dashboard.get_repeated_question_weekly_counts(elder_id)
st.metric(
    "This week vs. last week",
    this_week,
    delta=this_week - last_week,
    delta_color="inverse",
)
st.caption("Never shown to the elder — a rising trend can be an early sign worth a check-in call.")

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
