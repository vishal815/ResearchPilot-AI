"""
ResearchPilot AI — Search Tool (Tavily wrapper)
"""
import os
from dotenv import load_dotenv

load_dotenv()


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using Tavily. Falls back gracefully if key missing."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return f"[Search unavailable — no TAVILY_API_KEY] Query was: {query}"

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, max_results=max_results)
        items = results.get("results", [])
        output = []
        for i, item in enumerate(items, 1):
            output.append(
                f"[{i}] {item.get('title', 'No title')}\n"
                f"    URL: {item.get('url', '')}\n"
                f"    {item.get('content', '')[:500]}"
            )
        return "\n\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"
