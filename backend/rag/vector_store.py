import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from backend.rag.embeddings import get_embeddings


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")


def get_vector_store():

    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is missing in Render")

    if not PINECONE_INDEX_NAME:
        raise ValueError("PINECONE_INDEX_NAME is missing in Render")

    # SAFE DIAGNOSTIC — API key itself is NOT printed
    print("PINECONE_API_KEY loaded:", bool(PINECONE_API_KEY))
    print("PINECONE_API_KEY length:", len(PINECONE_API_KEY))
    print("PINECONE_INDEX_NAME:", PINECONE_INDEX_NAME)

    pc = Pinecone(api_key=PINECONE_API_KEY)

    index = pc.Index(PINECONE_INDEX_NAME)

    embeddings = get_embeddings()

    return PineconeVectorStore(
        index=index,
        embedding=embeddings
    )




# import os
# from dotenv import load_dotenv
# from pinecone import Pinecone
# from langchain_pinecone import PineconeVectorStore

# from backend.rag.embeddings import get_embeddings


# load_dotenv()

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")


# def get_vector_store():
#     if not PINECONE_API_KEY:
#         raise ValueError("PINECONE_API_KEY is missing in .env")

#     if not PINECONE_INDEX_NAME:
#         raise ValueError("PINECONE_INDEX_NAME is missing in .env")

#     pc = Pinecone(api_key=PINECONE_API_KEY)

#     index = pc.Index(PINECONE_INDEX_NAME)

#     embeddings = get_embeddings()

#     return PineconeVectorStore(
#         index=index,
#         embedding=embeddings
#     )