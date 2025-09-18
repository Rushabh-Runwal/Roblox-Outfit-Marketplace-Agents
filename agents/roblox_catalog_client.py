"""Roblox catalog HTTP client with parameter mapping and item capping."""
import asyncio
import httpx
from typing import Dict, Any, List

CATALOG_URL = "https://catalog.roblox.com/v1/search/items/details"
REQUEST_TIMEOUT = 10
RETRIES = 3
BACKOFF = 0.2

# Subcategory -> UI slot mapping (what the frontend expects in "type")
SUBCATEGORY_SLOT = {
    9: "Head",      # Hats (simplify to "Head")
    54: "Head",     # HeadAccessories -> "Head"
    10: "Face",     # Faces
    20: "Hair",     # HairAccessories
    22: "Neck Accessory",
    23: "Shoulder Accessory",
    24: "Front Accessory",
    25: "Back Accessory",
    26: "Waist Accessory",
    12: "Shirt",
    13: "T-Shirt",
    14: "Pants",
    15: "Head (Body Part)",
    66: "Dynamic Head",
    37: "Bundle",
    39: "Emote",
}


async def catalog_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Perform catalog search with retries and return raw API response data.
    
    Args:
        params: Query parameters for the catalog API
        
    Returns:
        List of raw catalog items from API response
    """
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        for _ in range(RETRIES):
            try:
                r = await client.get(CATALOG_URL, params=params)
                if r.status_code == 200:
                    j = r.json()
                    return j.get("data", []) if isinstance(j, dict) else (j if isinstance(j, list) else [])
            except httpx.RequestError:
                pass  # Continue to retry
            await asyncio.sleep(BACKOFF)
    return []


def map_items(raw: List[Dict[str, Any]], default_slot: str | None = None) -> List[dict]:
    """
    Map raw Roblox catalog items to simplified format with UI slot mapping.
    
    Args:
        raw: Raw catalog items from API
        default_slot: Default slot if subcategory mapping not found
        
    Returns:
        List of mapped items with assetId and type, capped at 10 items
    """
    out: List[dict] = []
    for it in raw:
        _id = it.get("id")
        if _id is None:
            continue
        # Prefer explicit subcategory mapping to UI slot; else fallback to default_slot; else "Unknown"
        subcat = it.get("subcategory") or it.get("subCategory")  # depends on payload
        ui_slot = SUBCATEGORY_SLOT.get(subcat) or default_slot or "Unknown"
        out.append({"assetId": str(_id), "type": ui_slot})
    return out[:10]