import os
from sentence_transformers import CrossEncoder

print("RERANKER MODULE LOADED")

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = None


def is_reranker_enabled():
    """
    Disable reranker on low-memory deployment environments.
    Local development remains enabled by default.
    """
    return os.getenv("DISABLE_RERANKER", "false").lower() != "true"


def get_reranker():

    global _reranker

    if not is_reranker_enabled():
        return None

    if _reranker is None:
        _reranker = CrossEncoder(MODEL_NAME)

    return _reranker


def rerank_documents(query, results, top_k=5):

    if not results:
        return []

    reranker = get_reranker()

    # If reranker is disabled, use hybrid-search ranking directly
    if reranker is None:
        print("RERANKER DISABLED - USING HYBRID SEARCH RESULTS")
        return results[:top_k]

    pairs = [
        [query, document.page_content]
        for document, score in results
    ]

    try:

        scores = reranker.predict(pairs)

        reranked = [
            (document, float(score))
            for (document, _), score
            in zip(results, scores)
        ]

        reranked.sort(
            key=lambda item: item[1],
            reverse=True
        )

        return reranked[:top_k]

    except Exception as e:

        print(f"Reranker error: {e}")

        return results[:top_k]
    

# from sentence_transformers import CrossEncoder

# print("RERANKER MODULE LOADED")

# MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# # Load model only once
# _reranker = CrossEncoder(
#     MODEL_NAME,
#     max_length=512
# )


# def get_reranker():
#     return _reranker


# def rerank_documents(query, results, top_k=5):

#     if not results:
#         return []

#     reranker = get_reranker()

#     documents = [
#         document
#         for document, score in results
#     ]

#     pairs = [
#         (query, document.page_content)
#         for document in documents
#     ]

#     scores = reranker.predict(
#     pairs,
#     show_progress_bar=False
# )

#     reranked = []

#     for document, score in zip(documents, scores):

#         reranked.append(
#             (document, float(score))
#         )

#     reranked.sort(
#         key=lambda item: item[1],
#         reverse=True
#     )

#     return reranked[:top_k]