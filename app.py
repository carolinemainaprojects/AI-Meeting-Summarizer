import streamlit as st
from google import genai
from pypdf import PdfReader

st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🤖"
)

st.title("🤖 AI Meeting Summarizer")
st.write("Turn meeting notes or transcripts into a clear, organized summary.")

# Get Gemini API client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Upload a file
uploaded_file = st.file_uploader(
    "📎 Upload a meeting transcript",
    type=["pdf", "txt"]
)

# Paste notes
meeting_notes = st.text_area(
    "Or paste your meeting notes here:",
    height=250,
    placeholder="Paste your meeting notes here..."
)

# Extract text from uploaded file
file_text = ""

if uploaded_file is not None:

    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        file_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")

# Choose the source
if file_text.strip():
    final_notes = file_text
else:
    final_notes = meeting_notes

# Summarize button
if st.button("✨ Summarize Meeting"):

    if not final_notes.strip():

        st.warning("Please upload a file or paste meeting notes first.")

    else:

        prompt = f"""
You are an expert meeting assistant.

Analyze the meeting notes below and provide:

## 📋 Meeting Summary
Give a concise summary of the main discussion.

## ✅ Key Decisions
List the important decisions that were made.

## 📝 Action Items
List each task and the person responsible for it.

## 📅 Important Deadlines
List any deadlines or important dates mentioned.

## 👤 People Responsible
Identify people and the tasks assigned to them.

Make the response clear, professional, and easy to read.

Meeting notes:

{final_notes}
"""

        with st.spinner("🤖 Analyzing your meeting..."):

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

        st.success("Meeting successfully summarized! 🎉")

result = response.text

st.markdown(result)

st.download_button(
    label="📥 Download Meeting Summary",
    data=result,
    file_name="meeting_summary.txt",
    mime="text/plain"
)
