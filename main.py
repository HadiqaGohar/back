import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI backend URL (set in secrets.toml for Streamlit Cloud)
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.title("HG Resume Craft")

# Input form for resume summary
st.header("Generate Resume Summary")
education = st.text_area("Enter Education (comma-separated)", placeholder="BSc Computer Science, XYZ University, 2023")
skills = st.text_area("Enter Skills (comma-separated)", placeholder="Python, JavaScript, Teamwork")

if st.button("Generate Summary"):
    if education and skills:
        try:
            response = requests.post(
                f"{FASTAPI_URL}/api/resume/summary",
                json={
                    "education": [e.strip() for e in education.split(",") if e.strip()],
                    "skills": [s.strip() for s in skills.split(",") if s.strip()]
                }
            )
            response.raise_for_status()
            summary = response.json().get("summary", "No summary returned")
            st.success("Summary generated successfully!")
            st.write(summary)
        except requests.RequestException as e:
            st.error(f"Error generating summary: {str(e)}")
    else:
        st.error("Please enter both education and skills.")

# File upload for resume extraction
st.header("Extract Resume Data")
uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
if uploaded_file and st.button("Extract Data"):
    try:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{FASTAPI_URL}/api/resume/extract", files=files)
        response.raise_for_status()
        data = response.json()
        st.success("Resume data extracted successfully!")
        st.json(data)
    except requests.RequestException as e:
        st.error(f"Error extracting resume data: {str(e)}")
