"""Roblox catalog tool for searching items."""
from typing import Optional, Dict, Any, List
import httpx
import asyncio

CATALOG_URL = "https://catalog.roblox.com/v1/search/items/details"

async def roblox_search(
    *,
    Keyword: Optional[str] = None,
    Limit: int = 10,
    Category: Optional[int] = None,
    Subcategory: Optional[int] = None,
    Genres: Optional[int] = None,
    MinPrice: Optional[int] = None,
    MaxPrice: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Call Roblox catalog search and return raw 'data' list."""
    params: Dict[str, Any] = {
        "Limit": Limit
    }
    if Keyword: params["Keyword"] = Keyword
    if Category is not None: params["Category"] = Category
    if Subcategory is not None: params["Subcategory"] = Subcategory
    if Genres is not None: params["Genres"] = Genres
    if MinPrice is not None: params["MinPrice"] = MinPrice
    if MaxPrice is not None: params["MaxPrice"] = MaxPrice

    async with httpx.AsyncClient(timeout=10) as client:
        for _ in range(3):
            r = await client.get(CATALOG_URL, params=params)
            if r.status_code == 200:
                j = r.json()
                return j.get("data", []) if isinstance(j, dict) else (j if isinstance(j, list) else [])
            await asyncio.sleep(0.2)
    return []


def map_items(raw: List[Dict[str, Any]]) -> List[dict]:
    """Map raw Roblox catalog items to simplified format."""
    out = []
    for it in raw:
        _id = it.get("id")
        if _id is None: 
            continue
        out.append({
            "assetId": str(_id),
            "type": it.get("itemType") or it.get("assetType") or "Unknown"
        })
    return out[:10]  # hard cap 10