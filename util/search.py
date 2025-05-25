from pydantic import BaseModel, Field

from duckduckgo_search import DDGS
from tavily import TavilyClient


class WebSearchResult(BaseModel):
    title: str = Field(..., description="short descriptive title of the web search result")
    url: str = Field(..., description="URL of the web search result")
    content: str | None = Field(None, description="main content of the web search result in Markdown format")
    summary: str | None = Field(None, description="summary of the web search result")


def duckduckgo_search(query: str, max_results: int) -> list[WebSearchResult]:
    """Perform a web search using DuckDuckGo and return a list of results.

    Args:
        query (str): The search query to execute.
        max_results (int): The max count of returning results.
    Returns:
        list[WebSearchResult]: list of search results.
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        WebSearchResult(
            title=r.get("title", ""),
            url=r.get("href", ""),
            content=r.get("body", ""),
            summary=""
        )
        for r in results
    ]


def tavily_search(query: str, max_results: int) -> list[WebSearchResult]:
    """Perform a web search using Tavily and return a list of results.

    Args:
        query (str): The search query to execute.
        max_results (int): The max count of returning results.
    Returns:
        list[WebSearchResult]: list of search results.
    """
    import os
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set")

    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, search_depth="basic", max_results=max_results)

    return [
        WebSearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            content=r.get("content", ""),
            summary=""
        )
        for r in response.get("results", [])
    ]
