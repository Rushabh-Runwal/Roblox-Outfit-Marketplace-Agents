"""Firecrawl agent for searching and scraping Roblox catalog items."""
import asyncio
import os
import re
from typing import List, Dict, Any
import httpx


async def fetch_ids_from_firecrawl(keyword_spec: dict, limit: int = 10) -> List[str]:
    """
    Fetch Roblox catalog item IDs using Firecrawl search and scrape.
    
    Args:
        keyword_spec: Dictionary with theme, style, parts, color, budget
        limit: Maximum number of IDs to return
        
    Returns:
        List of Roblox catalog item IDs
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("No FIRECRAWL_API_KEY found, returning empty list")
        return []
    
    # Build search query
    query_parts = ["site:roblox.com/catalog"]
    
    if keyword_spec.get("theme"):
        query_parts.append(keyword_spec["theme"])
    
    if keyword_spec.get("style"):
        query_parts.append(keyword_spec["style"])
    
    query_parts.append("outfit")
    
    query = " ".join(query_parts)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: Search for relevant pages
            search_results = await _search_firecrawl(client, api_key, query)
            
            # Step 2: Extract IDs from search results
            ids = _extract_ids_from_results(search_results)
            
            # Step 3: If we need more results, scrape individual pages
            if len(ids) < limit and search_results:
                additional_ids = await _scrape_additional_pages(
                    client, api_key, search_results, limit - len(ids)
                )
                ids.extend(additional_ids)
            
            # Deduplicate and limit results
            unique_ids = list(dict.fromkeys(ids))  # Preserves order while removing duplicates
            return unique_ids[:limit]
            
    except Exception as e:
        print(f"Error in fetch_ids_from_firecrawl: {e}")
        return []


async def _search_firecrawl(client: httpx.AsyncClient, api_key: str, query: str) -> List[Dict[str, Any]]:
    """Search using Firecrawl API."""
    search_url = "https://api.firecrawl.dev/v1/search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "limit": 5,
        "scrapeOptions": {
            "formats": ["markdown"]
        }
    }
    
    for attempt in range(3):  # 3 retries
        try:
            response = await client.post(search_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and "data" in data:
                return data["data"]
            else:
                print(f"Search API returned unsuccessful response: {data}")
                return []
                
        except httpx.HTTPStatusError as e:
            print(f"HTTP error on attempt {attempt + 1}: {e}")
            if attempt == 2:  # Last attempt
                raise
            await asyncio.sleep(1)  # Wait before retry
        except Exception as e:
            print(f"Search error on attempt {attempt + 1}: {e}")
            if attempt == 2:  # Last attempt
                raise
            await asyncio.sleep(1)
    
    return []


async def _scrape_additional_pages(
    client: httpx.AsyncClient, 
    api_key: str, 
    search_results: List[Dict[str, Any]], 
    needed_count: int
) -> List[str]:
    """Scrape individual pages for more IDs."""
    scrape_url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    additional_ids = []
    
    for result in search_results:
        if len(additional_ids) >= needed_count:
            break
            
        page_url = result.get("url")
        if not page_url:
            continue
            
        try:
            payload = {
                "url": page_url,
                "formats": ["markdown"]
            }
            
            response = await client.post(scrape_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and "data" in data:
                markdown_content = data["data"].get("markdown", "")
                ids = _extract_ids_from_content(markdown_content)
                additional_ids.extend(ids)
                
        except Exception as e:
            print(f"Error scraping {page_url}: {e}")
            continue
    
    return additional_ids


def _extract_ids_from_results(search_results: List[Dict[str, Any]]) -> List[str]:
    """Extract catalog IDs from search results."""
    ids = []
    
    for result in search_results:
        # Extract from URL
        url = result.get("url", "")
        url_ids = _extract_ids_from_content(url)
        ids.extend(url_ids)
        
        # Extract from markdown content if available
        markdown = result.get("markdown", "")
        if markdown:
            markdown_ids = _extract_ids_from_content(markdown)
            ids.extend(markdown_ids)
    
    return ids


def _extract_ids_from_content(content: str) -> List[str]:
    """Extract catalog item IDs from content using regex."""
    if not content:
        return []
    
    # Regex to match /catalog/{id} pattern
    id_pattern = r"/catalog/(\d+)"
    matches = re.findall(id_pattern, content)
    
    # Filter out IDs that are too short (likely not real catalog items)
    valid_ids = [match for match in matches if len(match) >= 8]
    
    return valid_ids


# Test function for development
async def test_firecrawl_agent():
    """Test the Firecrawl agent with sample data."""
    # Test with a simple keyword spec
    test_spec = {
        "theme": "knight",
        "style": "futuristic",
        "parts": ["Back Accessory"]
    }
    
    print("Testing Firecrawl agent...")
    ids = await fetch_ids_from_firecrawl(test_spec, limit=5)
    print(f"Found {len(ids)} IDs: {ids}")
    
    return ids


if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_firecrawl_agent())