import streamlit as st

st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🤖"
)

st.title("🤖 AI Meeting Summarizer")
st.write("Turn meeting notes into a clear summary, decisions, and action items.")

meeting_notes = st.text_area(
    "Paste your meeting notes or transcript here:",
    height=300,
    placeholder="Paste your meeting notes here..."
)

if st.button("✨ Summarize Meeting"):
    if not meeting_notes.strip():
        st.warning("Please paste some meeting notes first.")
    else:
        st.info("Your meeting notes are ready to be summarized!")
