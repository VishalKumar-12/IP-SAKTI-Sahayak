# from langchain_ollama import ChatOllama


# def get_llm():
#     return ChatOllama(
#         model="qwen3:1.7b",
#         temperature=0,
#         think=False,
#         num_ctx=4096,
#         num_predict=300,
#         keep_alive="5m"
#     )
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in .env")

    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        reasoning_effort="low"
    )