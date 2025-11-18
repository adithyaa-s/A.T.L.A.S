# search.py

import os
import requests
import dotenv
from google.adk.tools import FunctionTool
from typing import List, Dict, Any

# Load environment variables (needed if run outside the ADK runner)
dotenv.load_dotenv()

# --- Configuration ---
SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

def google_search(query: str, num_results: int = 5) -> str:
    """
    Performs a search using the Google Custom Search Engine (CSE) API.

    Args:
        query: The search query string (e.g., "latest Gemini model").
        num_results: The maximum number of results to return (max 10).

    Returns:
        A structured string summarizing the top search results, or an error message.
    """
    if not SEARCH_API_KEY or not SEARCH_ENGINE_ID:
        return "ERROR: Google Search API credentials are not configured in .env."

    try:
        params = {
            "key": SEARCH_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "num": min(num_results, 10)  # Max results is 10 for CSE
        }
        
        response = requests.get(SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        items = data.get('items', [])
        
        if not items:
            return "No search results found for the query."

        # Format results into a structured string for the LLM to use
        results_list = []
        for i, item in enumerate(items):
            result = f"Result {i+1}: "
            result += f"Title: {item.get('title', 'N/A')}\n"
            result += f"URL: {item.get('link', 'N/A')}\n"
            result += f"Snippet: {item.get('snippet', 'No snippet.')}\n"
            results_list.append(result)

        return "Search Results:\n" + "\n---\n".join(results_list)

    except requests.exceptions.RequestException as e:
        return f"ERROR: Failed to connect to Google Search API: {e}"
    except Exception as e:
        return f"ERROR: An unexpected error occurred during search: {e}"

# ----------------------------------------------------
# ADK Tool Definition (Following Positional Argument Pattern)
# ----------------------------------------------------

# 1. Instantiate with function only
google_search_tool = FunctionTool(google_search)

# 2. Set attributes post-instantiation
google_search_tool.name = "google_search"
google_search_tool.description = (
    "Performs a real-time web search for the user's query and returns a list of "
    "URLs, titles, and summaries. Use this for questions about current events, "
    "weather, public knowledge, or anything outside of personal calendar/email."
)