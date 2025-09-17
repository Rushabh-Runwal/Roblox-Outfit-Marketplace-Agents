"""Roblox Catalog Client for searching items using the official API."""
import asyncio
import logging
from typing import List, Dict, Any
import httpx

from .contracts import OutfitItem

logger = logging.getLogger(__name__)

# Shared HTTP client with timeouts and retries
_http_client = None

async def get_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTP client with appropriate settings."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
    return _http_client

async def search_catalog(theme: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search Roblox catalog for items based on theme.
    
    Args:
        theme: The theme/keyword to search for
        limit: Maximum number of items to return (default 10)
        
    Returns:
        List of raw item dictionaries from Roblox API
    """
    client = await get_http_client()
    
    params = {
        "Category": 11,  # Accessories category
        "Keyword": theme,
        "Limit": min(limit, 12)  # Cap at 12 for processing
    }
    
    url = "https://catalog.roblox.com/v1/search/items/details"
    
    for attempt in range(3):  # 3 retries with backoff
        try:
            logger.info(f"Searching Roblox catalog: keyword='{theme}', limit={params['Limit']}, attempt={attempt + 1}")
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("data", [])
            
            logger.info(f"Found {len(items)} items from Roblox catalog")
            return items
            
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error on attempt {attempt + 1}: {e.response.status_code}")
            if e.response.status_code == 429:  # Rate limited
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            elif attempt == 2:  # Last attempt
                logger.error(f"Failed to search catalog after 3 attempts: {e}")
                break
            else:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.warning(f"Error on attempt {attempt + 1}: {e}")
            if attempt == 2:  # Last attempt
                logger.error(f"Failed to search catalog after 3 attempts: {e}")
                break
            await asyncio.sleep(0.5)
    
    return []  # Return empty list on failure

def map_items(raw_items: List[Dict[str, Any]]) -> List[OutfitItem]:
    """
    Map raw Roblox API items to OutfitItem objects.
    
    Args:
        raw_items: List of raw item dictionaries from Roblox API
        
    Returns:
        List of OutfitItem objects
    """
    outfit_items = []
    
    for item in raw_items:
        if not item:
            continue
            
        # Extract assetId (required)
        asset_id = item.get("id")
        if not asset_id:
            continue
            
        # Extract type from various possible fields
        item_type = (
            item.get("itemType") or 
            item.get("assetType") or 
            item.get("assetTypeDisplayName") or
            "Unknown"
        )
        
        try:
            outfit_item = OutfitItem(
                assetId=str(asset_id),
                type=str(item_type)
            )
            outfit_items.append(outfit_item)
        except Exception as e:
            logger.warning(f"Failed to create OutfitItem from {item}: {e}")
            continue
    
    # Cap to maximum 10 items
    return outfit_items[:10]

async def close_http_client():
    """Close the shared HTTP client."""
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None