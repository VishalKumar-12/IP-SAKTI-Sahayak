import os
from huggingface_hub import InferenceClient

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class HuggingFaceEmbeddings:

    def __init__(self):
        hf_token = os.getenv("HF_TOKEN")

        if not hf_token:
            raise ValueError("HF_TOKEN is missing")

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=hf_token
        )

    def embed_documents(self, texts):

        if not texts:
            return []

        result = self.client.feature_extraction(
            texts,
            model=MODEL_NAME
        )

        if hasattr(result, "tolist"):
            result = result.tolist()

        return result

    def embed_query(self, text):

        result = self.client.feature_extraction(
            text,
            model=MODEL_NAME
        )

        if hasattr(result, "tolist"):
            result = result.tolist()

        return result


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