"""
ResearchForge v2 — LLM Factory
Returns Groq llama-3.3-70b as primary, Gemini as fallback.
Import get_llm() in any node.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.4):
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")

    if groq_key:
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=temperature)

    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=temperature)

    raise ValueError(
        "No LLM API key found. Set GROQ_API_KEY or GOOGLE_API_KEY in .env"
    )
