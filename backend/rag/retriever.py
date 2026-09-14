from backend.rag.vector_store import get_vector_store


# Create vector store only once
_vector_store = get_vector_store()


def get_retriever():

    return _vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8}
    )


def remove_duplicate_documents(documents):

    unique_documents = []
    seen = set()

    for document in documents:

        content = " ".join(
            document.page_content.split()
        ).lower()

        key = content[:1000]

        if key not in seen:
            seen.add(key)
            unique_documents.append(document)

    return unique_documents


def retrieve_with_scores(
    query,
    k=8,
    min_score=0.65
):

    results = _vector_store.similarity_search_with_score(
        query,
        k=k
    )

    unique_results = []
    seen = set()

    for document, score in results:

        if score < min_score:
            continue

        content = " ".join(
            document.page_content.split()
        ).lower()

        key = content[:1000]

        if key not in seen:
            seen.add(key)

            unique_results.append(
                (document, score)
            )

    return unique_results