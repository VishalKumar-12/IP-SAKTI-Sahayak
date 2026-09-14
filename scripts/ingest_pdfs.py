from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from backend.rag.chunking import split_documents
from backend.rag.vector_store import get_vector_store


DATA_FOLDER = Path("data")

NEW_FILES = [
    "1 designated repositories.pdf",
    "Designationofrepositories190626.pdf",
    "Designationofrepositories240326.pdf",
    "Designationofrepositories230323.pdf",
    "CS-III OM division dt 25 Sept 2020.pdf",
    "designated_repositories_2013.pdf",
    "designated_repositories_2012.pdf",
]


def main():
    all_documents = []

    print("Loading new PDFs...")

    for filename in NEW_FILES:
        pdf_path = DATA_FOLDER / filename

        if not pdf_path.exists():
            print("File not found:", filename)
            continue

        print("Loading:", filename)

        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        for document in documents:
            document.metadata["source"] = filename

        all_documents.extend(documents)

    print("Pages loaded:", len(all_documents))

    if not all_documents:
        print("No documents found.")
        return

    print("Creating chunks...")

    chunks = split_documents(all_documents)

    print("Chunks created:", len(chunks))

    print("Connecting to Pinecone...")

    vector_store = get_vector_store()

    print("Uploading new chunks to Pinecone...")

    vector_store.add_documents(chunks)

    print("New PDFs successfully added to Pinecone!")


if __name__ == "__main__":
    main()