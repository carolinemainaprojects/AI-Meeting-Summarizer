import streamlit as st
from google import genai
from pypdf import PdfReader
import json
import csv
import io
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="AI Meeting Summarizer",
    page_icon="🤖"
)

st.title("🤖 AI Meeting Summarizer")

st.markdown(
    """
    ### Turn long meetings into clear, actionable insights.

    Upload a meeting transcript or paste your notes below.
    Get an AI-powered summary, decisions, action items, deadlines,
    and responsible team members in seconds.
    """
)

st.divider()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

google_credentials = Credentials.from_service_account_info(
    json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"]),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)

google_client = gspread.authorize(google_credentials)
try:
    sheet = google_client.open("AI Meeting Action Items").sheet1
except Exception as e:
    st.error(f"Google Sheets connection failed: {e}")
    st.stop()
st.subheader("📥 Add Your Meeting")

uploaded_file = st.file_uploader(
    "Upload a meeting transcript",
    type=["pdf", "txt"],
    help="Supported formats: PDF and TXT"
)

st.write("**Or paste your meeting notes below:**")

meeting_notes = st.text_area(
    "Meeting notes",
    height=250,
    placeholder="Example: Caroline will prepare the report by Friday..."
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

        st.warning(
            "Please upload a file or paste meeting notes first."
        )

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

            st.success(
                "Meeting successfully summarized! 🎉"
            )

            st.subheader("📋 Meeting Summary")

            st.write(result["summary"])

            st.subheader("✅ Key Decisions")

            if result["decisions"]:

                for decision in result["decisions"]:

                    st.write(f"• {decision}")

         else:

                st.info("No key decisions were identified.")


            st.subheader("📝 Action Items")

            if result["action_items"]:

                for number, item in enumerate(
                    result["action_items"],
                    start=1
                ):

                    with st.container(border=True):

                        st.markdown(
                            f"### Task {number}"
                        )

                        st.write(
                            f"**Task:** {item['task']}"
                        )

                        st.write(
                            f"**👤 Responsible:** "
                            f"{item['person']}"
                        )

                        st.write(
                            f"**📅 Deadline:** "
                            f"{item['deadline']}"
                        )

            else:

                st.info(
                    "No action items were identified."
                )
                            # Save action items to Google Sheets
            if result["action_items"]:
                for item in result["action_items"]:
                    sheet.append_row([
                        item["task"],
                        item["person"],
                        item["deadline"]
                    ])

                st.success("✅ Action items saved to Google Sheets!")


            st.subheader("📅 Important Deadlines")

            if result["deadlines"]:

                for deadline in result["deadlines"]:

                    st.write(
                        f"• {deadline}"
                    )

            else:

                st.info(
                    "No important deadlines were identified."
                )


            st.subheader("👤 People Responsible")

            if result["people_responsible"]:

                for person in result[
                    "people_responsible"
                ]:

                    st.write(
                        f"• {person}"
                    )

            else:

                st.info(
                    "No responsible people were identified."
                )


            # Create TXT download

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


            # Create CSV download

            csv_buffer = io.StringIO()

            writer = csv.writer(csv_buffer)

            writer.writerow(
                ["Task", "Responsible", "Deadline"]
            )

            for item in result["action_items"]:

                writer.writerow(
                    [
                        item["task"],
                        item["person"],
                        item["deadline"]
                    ]
                )

            st.download_button(
                label="📊 Download Action Items as CSV",
                data=csv_buffer.getvalue(),
                file_name="meeting_action_items.csv",
                mime="text/csv"
            )


        except json.JSONDecodeError:

            st.error(
                "The AI returned an unexpected format. "
                "Please try summarizing again."
)
