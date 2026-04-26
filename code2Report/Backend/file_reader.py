import zipfile
from pypdf import PdfReader


def read_uploaded_files(uploaded_files):
    """
    Reads uploaded files and returns combined text.

    Supported:
    - Code/text files: .py, .js, .jsx, .html, .css, .sql, .md, .txt, .json
    - PDF files
    - ZIP files containing supported files
    """

    combined_text = ""

    allowed_extensions = (
        ".py", ".js", ".jsx", ".html", ".css",
        ".sql", ".md", ".txt", ".json"
    )

    ignored_folders = (
        "node_modules/",
        ".git/",
        ".venv/",
        "venv/",
        "__pycache__/",
        "dist/",
        "build/"
    )

    if not uploaded_files:
        return combined_text

    for file in uploaded_files:
        try:
            file_name = file.name.lower()
            combined_text += f"\n\n--- Uploaded File: {file.name} ---\n"

            if file_name.endswith(".pdf"):
                combined_text += read_pdf_file(file)

            elif file_name.endswith(".zip"):
                combined_text += read_zip_file(
                    file,
                    allowed_extensions,
                    ignored_folders
                )

            else:
                content = file.read().decode("utf-8", errors="ignore")
                combined_text += content

        except Exception as e:
            combined_text += f"\n\nCould not read file: {file.name}. Error: {e}"

    return combined_text


def read_pdf_file(file):
    """
    Extracts text from PDF file.
    """

    pdf_text = ""

    try:
        pdf_reader = PdfReader(file)

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()

            if text:
                pdf_text += f"\n--- Page {page_num} ---\n"
                pdf_text += text
            else:
                pdf_text += f"\n--- Page {page_num}: No readable text found ---\n"

    except Exception as e:
        pdf_text += f"\nCould not read PDF. Error: {e}"

    return pdf_text


def read_zip_file(file, allowed_extensions, ignored_folders):
    """
    Reads useful files from a ZIP project folder.
    """

    zip_text = ""

    try:
        with zipfile.ZipFile(file, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                file_path = file_info.filename

                if file_info.is_dir():
                    continue

                if any(folder in file_path for folder in ignored_folders):
                    continue

                if not file_path.lower().endswith(allowed_extensions):
                    continue

                try:
                    with zip_ref.open(file_info) as extracted_file:
                        content = extracted_file.read().decode(
                            "utf-8",
                            errors="ignore"
                        )

                        zip_text += f"\n\n--- ZIP File: {file_path} ---\n"
                        zip_text += content

                except Exception as e:
                    zip_text += (
                        f"\nCould not read file inside ZIP: "
                        f"{file_path}. Error: {e}\n"
                    )

    except Exception as e:
        zip_text += f"\nCould not read ZIP file. Error: {e}"

    return zip_text