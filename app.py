import streamlit as st
from google import genai

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
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        prompt = f"""
You are an expert meeting assistant.

Analyze the meeting notes below and provide:

1. Meeting Summary
2. Key Decisions
3. Action Items
4. Important Deadlines
5. People Responsible for Tasks

Make the answer clear, organized, and easy to read.

Meeting notes:
{meeting_notes}
"""

        with st.spinner("🤖 Analyzing your meeting..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

        st.subheader("📋 Meeting Results")
        st.markdown(response.text)
