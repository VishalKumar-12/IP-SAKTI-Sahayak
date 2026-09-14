import os
from huggingface_hub import InferenceClient

print("RERANKER MODULE LOADED")

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_reranker():

    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        raise ValueError(
            "HF_TOKEN is missing. Add HF_TOKEN to environment variables."
        )

    return InferenceClient(
        provider="hf-inference",
        api_key=hf_token
    )


def rerank_documents(query, results, top_k=5):

    if not results:
        return []

    reranker = get_reranker()

    documents = [
        document
        for document, score in results
    ]

    reranked = []

    for document in documents:

        text = document.page_content

        prompt = f"""
Query: {query}

Document:
{text}

Rate how relevant this document is to the query.
Return only a relevance score from 0 to 1.
"""

        try:

            response = reranker.text_classification(
                text=prompt,
                model=MODEL_NAME
            )

            # Get the highest returned score
            if response:
                score = max(
                    float(item.score)
                    for item in response
                )
            else:
                score = 0.0

        except Exception as e:

            print(f"Reranker API error: {e}")

            score = 0.0

        reranked.append(
            (document, score)
        )

    reranked.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return reranked[:top_k]


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