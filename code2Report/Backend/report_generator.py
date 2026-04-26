import google.generativeai as genai
from Backend.rag_engine import retrieve_relevant_context


def generate_report_with_rag(
    api_key,
    vector_store,
    project_title,
    tech_stack,
    project_description,
    code_or_details,
    report_type,
    tone,
    sections
):
    """
    Generates report section-wise using RAG.
    Each section retrieves relevant context from the vector database.
    """

    if not api_key:
        return "API key not found. Please add GEMINI_API_KEY in your .env file."

    if not project_title or not project_description:
        return "Please enter at least Project Title and Project Description."

    if not sections:
        return "Please select at least one section to generate."

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash")

    final_report = f"# {project_title}\n\n"
    final_report += f"**Report Type:** {report_type}\n\n"
    final_report += f"**Technology Stack:** {tech_stack}\n\n"

    for section in sections:
        query = f"""
        Project Title: {project_title}
        Technology Stack: {tech_stack}
        Project Description: {project_description}
        Required Section: {section}
        """

        relevant_context = retrieve_relevant_context(
            vector_store=vector_store,
            query=query,
            k=5
        )

        prompt = f"""
You are an expert academic project report writer.

Generate only the following section:

{section}

Report Type:
{report_type}

Project Title:
{project_title}

Technology Stack:
{tech_stack}

Project Description:
{project_description}

Extra Project Details / APIs / Database Schema:
{code_or_details}

Relevant Context Retrieved from Uploaded Project Files:
{relevant_context}

Writing Style:
{tone}

Strict Instructions:
1. Generate only the requested section.
2. Use academic and student-friendly language.
3. Use the uploaded project context wherever relevant.
4. Do not add fake APIs, fake database tables, fake features, or fake technologies.
5. If some details are missing, write a general explanation without making false claims.
6. Use clear headings and proper formatting.
7. For Viva Questions, generate questions with short answers.
8. For Diagram Suggestions, mention which diagram should be added and where.
9. Keep the content suitable for college project submission.
10. Avoid unnecessary repetition.
"""

        try:
            response = model.generate_content(prompt)

            final_report += f"\n\n## {section}\n\n"
            final_report += response.text

        except Exception as e:
            final_report += f"\n\n## {section}\n\n"
            final_report += f"Error while generating this section: {e}"

    return final_report