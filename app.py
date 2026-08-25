import streamlit as st
from google import genai
from pypdf import PdfReader
import json

st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🤖"
)

st.title("🤖 AI Meeting Summarizer")
st.write("Turn meeting notes or transcripts into a clear, organized summary.")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

uploaded_file = st.file_uploader(
    "📎 Upload a meeting transcript",
    type=["pdf", "txt"]
)

meeting_notes = st.text_area(
    "Or paste your meeting notes here:",
    height=250,
    placeholder="Paste your meeting notes here..."
)

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

if file_text.strip():
    final_notes = file_text
else:
    final_notes = meeting_notes

if st.button("✨ Summarize Meeting"):

    if not final_notes.strip():

        st.warning("Please upload a file or paste meeting notes first.")

    else:

        prompt = f"""
You are an expert meeting assistant.

Analyze the meeting notes below.

Return ONLY valid JSON using exactly this structure:

{{
  "summary": "A concise summary of the meeting",
  "decisions": [
    "Decision 1",
    "Decision 2"
  ],
  "action_items": [
    {{
      "task": "Task description",
      "person": "Person responsible",
      "deadline": "Deadline"
    }}
  ],
  "deadlines": [
    "Important deadline or date"
  ],
  "people_responsible": [
    "Person and their responsibility"
  ]
}}

If information is not available, use an empty list.

Meeting notes:

{final_notes}
"""

        with st.spinner("🤖 Analyzing your meeting..."):

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

        try:

            result = json.loads(response.text)

            st.success("Meeting successfully summarized! 🎉")

            st.subheader("📋 Meeting Summary")
            st.write(result["summary"])

            st.subheader("✅ Key Decisions")

            for decision in result["decisions"]:
                st.write(f"• {decision}")

            st.subheader("📝 Action Items")

if result["action_items"]:

    for item in result["action_items"]:
        st.markdown(
            f"""
            **Task:** {item['task']}

            **Responsible:** {item['person']}

            **Deadline:** {item['deadline']}

            ---
            """
        )

else:
    st.write("No action items were identified.")

            st.subheader("📅 Important Deadlines")

            for deadline in result["deadlines"]:
                st.write(f"• {deadline}")

            st.subheader("👤 People Responsible")

            for person in result["people_responsible"]:
                st.write(f"• {person}")

            download_text = f"""
AI MEETING SUMMARY

MEETING SUMMARY
{result["summary"]}

KEY DECISIONS
{"".join("• " + d + chr(10) for d in result["decisions"])}

ACTION ITEMS
{"".join("• " + i["task"] + " — " + i["person"] + " — " + i["deadline"] + chr(10) for i in result["action_items"])}

IMPORTANT DEADLINES
{"".join("• " + d + chr(10) for d in result["deadlines"])}

PEOPLE RESPONSIBLE
{"".join("• " + p + chr(10) for p in result["people_responsible"])}
"""

            st.download_button(
                label="📥 Download Meeting Summary",
                data=download_text,
                file_name="meeting_summary.txt",
                mime="text/plain"
            )

        except json.JSONDecodeError:

            st.error(
                "The AI returned an unexpected format. "
                "Please try summarizing again."
            )
