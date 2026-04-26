import os
import streamlit as st
from dotenv import load_dotenv

from Backend.file_reader import read_uploaded_files
from Backend.rag_engine import create_vector_store
from Backend.report_generator import generate_report_with_rag
from Backend.docx_generator import create_docx


# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.write("API Key Loaded:", bool(api_key))


# Page configuration
st.set_page_config(
    page_title="Code2Report",
    page_icon="/",
    layout="wide"
)


# Hide only Deploy button
st.markdown(
    """
    <style>
    [data-testid="stDeployButton"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Main title
st.markdown(
    """
    <h1 style='text-align: center;'>📘 Code2Report</h1>
    <h3 style='text-align: center; color: gray;'>
        AI-Powered Academic Project Report Generator using RAG
    </h3>
    """,
    unsafe_allow_html=True
)

st.write(
    "Generate academic project reports, viva questions, and diagram suggestions "
    "from project files using Retrieval-Augmented Generation."
)


# Sidebar settings
st.sidebar.title("Report Settings")

report_type = st.sidebar.selectbox(
    "Select Report Type",
    [
        "Mini Project Report",
        "Final Year Project Report",
        "Internship Project Report",
        "Practical Experiment Report",
        "API Documentation Report",
        "Database Design Report"
    ]
)

tone = st.sidebar.selectbox(
    "Select Writing Style",
    [
        "Academic",
        "Simple Student-Friendly",
        "Professional",
        "Detailed"
    ]
)


# User inputs
project_title = st.text_input("Project Title")

tech_stack = st.text_input(
    "Technology Stack",
    placeholder="Example: React, Node.js, Express.js, MySQL"
)

project_description = st.text_area(
    "Project Description",
    height=150,
    placeholder="Briefly describe what your project does..."
)

uploaded_files = st.file_uploader(
    "Upload Project Files / PDFs / ZIP",
    type=[
        "py", "js", "jsx", "html", "css", "sql",
        "md", "txt", "json", "pdf", "zip"
    ],
    accept_multiple_files=True
)

code_or_details = st.text_area(
    "Paste Extra Project Details / APIs / Database Schema",
    height=220,
    placeholder=(
        "Paste important APIs, database schema, README content, "
        "team details, modules, etc."
    )
)

sections = st.multiselect(
    "Select Sections to Generate",
    [
        "Abstract",
        "Introduction",
        "Problem Statement",
        "Objectives",
        "Existing System",
        "Proposed System",
        "System Architecture",
        "Technology Stack",
        "Modules Description",
        "Database Design",
        "API Description",
        "Implementation Details",
        "Testing",
        "Advantages",
        "Limitations",
        "Future Scope",
        "Conclusion",
        "Viva Questions",
        "Diagram Suggestions"
    ],
    default=[
        "Abstract",
        "Introduction",
        "Objectives",
        "Proposed System",
        "Technology Stack",
        "Modules Description",
        "Conclusion",
        "Viva Questions",
        "Diagram Suggestions"
    ]
)


# Generate report
if st.button("Generate Report using RAG"):
    if not api_key:
        st.error("GEMINI_API_KEY not found. Please add it in your .env file.")

    elif not project_title or not project_description:
        st.warning("Please enter Project Title and Project Description.")

    else:
        with st.spinner("Reading uploaded files..."):
            uploaded_text = read_uploaded_files(uploaded_files)

        full_text = uploaded_text + "\n\n" + code_or_details

        if not full_text.strip():
            st.warning("Please upload project files or paste project details.")

        else:
            with st.spinner("Creating RAG vector database..."):
                vector_store = create_vector_store(
                    text=full_text,
                    api_key=api_key
                )

            with st.spinner("Generating report using RAG..."):
                output = generate_report_with_rag(
                    api_key=api_key,
                    vector_store=vector_store,
                    project_title=project_title,
                    tech_stack=tech_stack,
                    project_description=project_description,
                    code_or_details=code_or_details,
                    report_type=report_type,
                    tone=tone,
                    sections=sections
                )

                st.session_state["generated_report"] = output


# Display generated report and download options
if "generated_report" in st.session_state:
    st.success("Report generated successfully!")

    st.markdown(st.session_state["generated_report"])

    safe_project_title = (
        project_title.replace(" ", "_")
        if project_title
        else "project"
    )

    st.download_button(
        label="Download Report as TXT",
        data=st.session_state["generated_report"],
        file_name=f"{safe_project_title}_report.txt",
        mime="text/plain"
    )

    docx_file = create_docx(
        st.session_state["generated_report"],
        project_title
    )

    st.download_button(
        label="Download Report as DOCX",
        data=docx_file,
        file_name=f"{safe_project_title}_report.docx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )