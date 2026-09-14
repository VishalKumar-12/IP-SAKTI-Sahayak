from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    for document in documents:
        document.metadata["source"] = path.name
        document.metadata["file_path"] = str(path)
        document.metadata["page"] = document.metadata.get("page", 0) + 1

    return documents


def load_pdf_folder(folder_path):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    pdf_files = list(folder.rglob("*.pdf"))

    documents = []

    for pdf_file in pdf_files:
        documents.extend(load_pdf(pdf_file))

    return documents