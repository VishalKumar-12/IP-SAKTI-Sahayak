import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi
from langchain_community.document_loaders import PyPDFLoader


INDEX_FILE = Path("data/bm25_index.pkl")
DATA_FOLDER = Path("data")


def tokenize(text):
    return text.lower().split()


def load_all_documents():
    documents = []

    pdf_files = list(
        DATA_FOLDER.rglob("*.pdf")
    )

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:

        try:
            loader = PyPDFLoader(
                str(pdf_file)
            )

            pages = loader.load()

            for page in pages:

                page.metadata["source"] = str(
                    pdf_file
                )

                page.metadata["file_path"] = str(
                    pdf_file
                )

                page.metadata["page"] = (
                    page.metadata.get("page", 0) + 1
                )

                documents.append(page)

        except Exception as error:

            print(
                f"Skipping {pdf_file}: {error}"
            )

    print(
        f"Loaded {len(documents)} pages."
    )

    return documents


def build_bm25_index():

    documents = load_all_documents()

    if not documents:
        raise ValueError(
            "No PDF documents found in data folder."
        )

    corpus = [
        tokenize(document.page_content)
        for document in documents
    ]

    bm25 = BM25Okapi(corpus)

    INDEX_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        INDEX_FILE,
        "wb"
    ) as file:

        pickle.dump(
            {
                "bm25": bm25,
                "documents": documents
            },
            file
        )

    print(
        f"BM25 index saved to: {INDEX_FILE}"
    )

    print(
        f"Indexed documents: {len(documents)}"
    )


def load_bm25_index():

    if not INDEX_FILE.exists():

        raise FileNotFoundError(
            "BM25 index not found. "
            "Run build_bm25_index() first."
        )

    with open(
        INDEX_FILE,
        "rb"
    ) as file:

        data = pickle.load(file)

    return (
        data["bm25"],
        data["documents"]
    )


if __name__ == "__main__":

    build_bm25_index()