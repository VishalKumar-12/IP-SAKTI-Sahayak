import os
from typing import List

from huggingface_hub import InferenceClient


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384


class HuggingFaceEmbeddings:

    def __init__(self):
        hf_token = os.getenv("HF_TOKEN")

        if not hf_token:
            raise ValueError(
                "HF_TOKEN is missing. Add HF_TOKEN to environment variables."
            )

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=hf_token
        )

    def _embed(self, texts: List[str]) -> List[List[float]]:

        cleaned = [
            str(text).strip()
            for text in texts
            if text is not None and str(text).strip()
        ]

        if not cleaned:
            return []

        try:
            result = self.client.feature_extraction(
                cleaned,
                model=MODEL_NAME,
                normalize=True
            )

        except Exception as e:
            raise RuntimeError(
                f"Hugging Face embedding request failed: {e}"
            ) from e

        if hasattr(result, "tolist"):
            result = result.tolist()

        result = [
            list(map(float, vector))
            for vector in result
        ]

        for vector in result:
            if len(vector) != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Embedding dimension mismatch: "
                    f"expected {EMBEDDING_DIMENSION}, "
                    f"got {len(vector)}"
                )

        return result

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:

        result = self._embed([text])

        if not result:
            raise ValueError(
                "Could not generate query embedding."
            )

        return result[0]


def get_embeddings():
    return HuggingFaceEmbeddings()


# from langchain_huggingface import HuggingFaceEmbeddings


# MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# def get_embeddings():
#     return HuggingFaceEmbeddings(
#         model_name=MODEL_NAME,
#         model_kwargs={"device": "cpu"},
#         encode_kwargs={"normalize_embeddings": True}
#     )