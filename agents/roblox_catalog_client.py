"""Roblox catalog HTTP client with parameter mapping and item capping."""
import asyncio
import httpx
from typing import Dict, Any, List
from agents.config import DEV_MODE

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

# Mock data for development mode
MOCK_DATA = {
    9: [  # Hats
        {"id": 1001, "name": "Knight Helmet", "subcategory": 9},
        {"id": 1002, "name": "Medieval Crown", "subcategory": 9},
        {"id": 1003, "name": "Iron Helmet", "subcategory": 9},
        {"id": 1004, "name": "Royal Knight Helm", "subcategory": 9},
        {"id": 1005, "name": "Battle Helmet", "subcategory": 9},
    ],
    10: [  # Faces
        {"id": 2001, "name": "Warrior Face", "subcategory": 10},
        {"id": 2002, "name": "Noble Expression", "subcategory": 10},
        {"id": 2003, "name": "Knight Face", "subcategory": 10},
    ],
    12: [  # Shirts
        {"id": 3001, "name": "Knight Armor", "subcategory": 12},
        {"id": 3002, "name": "Medieval Tunic", "subcategory": 12},
        {"id": 3003, "name": "Chain Mail", "subcategory": 12},
        {"id": 3004, "name": "Royal Armor", "subcategory": 12},
    ],
    14: [  # Pants
        {"id": 4001, "name": "Knight Leggings", "subcategory": 14},
        {"id": 4002, "name": "Medieval Pants", "subcategory": 14},
        {"id": 4003, "name": "Armored Pants", "subcategory": 14},
    ],
    25: [  # Back Accessories
        {"id": 5001, "name": "Knight Cape", "subcategory": 25},
        {"id": 5002, "name": "Sword Sheath", "subcategory": 25},
        {"id": 5003, "name": "Royal Cloak", "subcategory": 25},
    ],
    24: [  # Front Accessories
        {"id": 6001, "name": "Chest Armor", "subcategory": 24},
        {"id": 6002, "name": "Knight Emblem", "subcategory": 24},
        {"id": 6003, "name": "Noble Crest", "subcategory": 24},
    ],
    22: [  # Neck Accessories
        {"id": 7001, "name": "Noble Necklace", "subcategory": 22},
        {"id": 7002, "name": "Knight Chain", "subcategory": 22},
    ],
    20: [  # Hair
        {"id": 8001, "name": "Knight Hair", "subcategory": 20},
        {"id": 8002, "name": "Medieval Hair", "subcategory": 20},
    ]
}


def get_mock_data_for_subcategory(subcategory: int, keyword: str = None) -> List[Dict[str, Any]]:
    """Get mock data for a specific subcategory, optionally filtered by keyword."""
    items = MOCK_DATA.get(subcategory, [])
    if keyword:
        keyword_lower = keyword.lower()
        # Match if any word in keyword appears in item name
        keyword_words = keyword_lower.split()
        items = [item for item in items 
                if any(word in item["name"].lower() for word in keyword_words)]
    return items


async def catalog_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Perform catalog search with retries and return raw API response data.
    
    Args:
        params: Query parameters for the catalog API
        
    Returns:
        List of raw catalog items from API response
    """
    if DEV_MODE:
        # Return mock data in development mode
        subcategory = params.get("Subcategory")
        keyword = params.get("Keyword", "")
        mock_items = get_mock_data_for_subcategory(subcategory, keyword)
        await asyncio.sleep(0.1)  # Simulate network delay
        return mock_items
    
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