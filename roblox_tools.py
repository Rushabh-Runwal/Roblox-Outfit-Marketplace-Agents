"""
Roblox Catalog API Tools

This module contains all the tools for interacting with the Roblox Catalog API.
Each tool corresponds to a specific item type or functionality within the Roblox catalog.
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from langchain.tools import tool

# Configure logging
logger = logging.getLogger(__name__)

# Roblox API Constants
ROBLOX_API_URL = "https://catalog.roblox.com/v1/search/items/details"
LIMIT = 10  # API only accepts 10, 28, or 30

# Category mappings based on Roblox catalog structure
CATEGORIES = {
    "Clothing": 3,
    "BodyParts": 4,
    "Gear": 5,
    "Accessories": 11,
    "AvatarAnimations": 12
}

# Subcategory mappings with their parent categories
# Based on API testing - only certain combinations work
SUBCATEGORY_MAPPINGS = {
    # Accessories subcategories (Category 11) 
    "HeadAccessories": {"category": 11, "subcategory": 54},  
    "FaceAccessories": {"category": 11, "subcategory": 21},  
    "NeckAccessories": {"category": 11, "subcategory": 22},  
    "ShoulderAccessories": {"category": 11, "subcategory": 23}, 
    "FrontAccessories": {"category": 11, "subcategory": 24}, 
    "BackAccessories": {"category": 11, "subcategory": 25},  
    "WaistAccessories": {"category": 11, "subcategory": 26}, 
    
    # These don't work with Category 11 - fallback to subcategory only
    "Hats": {"category": 11, "subcategory": 54},  
    "Faces": {"category": 11, "subcategory": 21},  
    "HairAccessories": {"category": 4, "subcategory": 20}, 
    
    # Clothing subcategories 
    "TShirts": {"category": 3, "subcategory": 58},
    "Shirts": {"category": 3, "subcategory": 59}, 
    "Pants": {"category": 3, "subcategory": 60},  
    
    # Body Parts and Animations - need testing
    "Heads": {"category": 4, "subcategory": 15},
    "DynamicHeads": {"category": 4, "subcategory": 66},
    "Bundles": {"category": 12, "subcategory": 37},
    "EmoteAnimations": {"category": 12, "subcategory": 39}
}

# Legacy subcategories dict for backward compatibility
SUBCATEGORIES = {
    "Featured": 0,
    "All": 1,
    "Collectibles": 2,
    "Clothing": 3,
    "BodyParts": 4,
    "Gear": 5,
    "Hats": 9,
    "Faces": 10,
    "Shirts": 12,
    "TShirts": 13,
    "Pants": 14,
    "Heads": 15,
    "Accessories": 19,
    "HairAccessories": 20,
    "FaceAccessories": 21,
    "NeckAccessories": 22,
    "ShoulderAccessories": 23,
    "FrontAccessories": 24,
    "BackAccessories": 25,
    "WaistAccessories": 26,
    "AvatarAnimations": 27,
    "Bundles": 37,
    "AnimationBundles": 38,
    "EmoteAnimations": 39,
    "CommunityCreations": 40,
    "Melee": 41,
    "Ranged": 42,
    "Explosive": 43,
    "PowerUp": 44,
    "Navigation": 45,
    "Musical": 46,
    "Social": 47,
    "Building": 48,
    "Transport": 49,
    "HeadAccessories": 54,
    "ClassicTShirts": 55,
    "ClassicShirts": 56,
    "ClassicPants": 57,
    "TShirtAccessories": 58,
    "ShirtAccessories": 59,
    "PantsAccessories": 60,
    "JacketAccessories": 61,
    "SweaterAccessories": 62,
    "ShortsAccessories": 63,
    "ShoesBundles": 64,
    "DressSkirtAccessories": 65,
    "DynamicHeads": 66
}

# Part to subcategory mapping with categories
PART_SUBCATEGORY_MAP = {
    "Head": "Hats",
    "Face": "Faces", 
    "Hair": "HairAccessories",
    "Shirt": "Shirts",
    "TShirt": "TShirts",
    "Pants": "Pants",
    "Back Accessory": "BackAccessories",
    "Neck Accessory": "NeckAccessories",
    "Shoulder Accessory": "ShoulderAccessories",
    "Front Accessory": "FrontAccessories",
    "Waist Accessory": "WaistAccessories",
    "Head Bodypart": "Heads",
    "Bundle": "Bundles",
    "Emote": "EmoteAnimations"
}


def make_roblox_api_call(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Make a call to the Roblox Catalog API"""
    try:
        # Ensure we always limit to 10 items (API only accepts 10, 28, or 30)
        params["Limit"] = LIMIT
        
        logger.info(f"Making Roblox API call with params: {params}")
        response = requests.get(ROBLOX_API_URL, params=params, timeout=10)
        
        # Log the full URL for debugging
        logger.info(f"API URL: {response.url}")
        
        response.raise_for_status()
        
        data = response.json()
        items = data.get("data", [])
        logger.info(f"Roblox API returned {len(items)} items")
        
        # Transform to our format
        result = []
        for item in items[:LIMIT]:  # Ensure max 10 items
            result.append({
                "assetId": str(item.get("id", "")),
                "type": item.get("itemType", "Unknown")
            })
        
        logger.info(f"Retrieved {len(result)} items from Roblox API")
        return result
    
    except Exception as e:
        logger.error(f"Error calling Roblox API: {e}")
        return []


# Tool functions using @tool decorator
@tool
def fetch_outfit(parts: List[str], keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch multiple outfit parts at once from Roblox catalog"""
    all_items = []
    items_per_part = max(1, LIMIT // len(parts)) if parts else LIMIT
    
    for part in parts:
        if part in PART_SUBCATEGORY_MAP:
            subcategory_key = PART_SUBCATEGORY_MAP[part]
            if subcategory_key in SUBCATEGORY_MAPPINGS:
                mapping = SUBCATEGORY_MAPPINGS[subcategory_key]
                
                params = {
                    "Subcategory": mapping["subcategory"],
                    "Limit": items_per_part
                }
                
                # Only add category if it exists in mapping
                if "category" in mapping:
                    params["Category"] = mapping["category"]
                
                if keyword:
                    params["Keyword"] = keyword
                
                items = make_roblox_api_call(params)
                # Set correct type for each item
                for item in items:
                    item["type"] = part
                
                all_items.extend(items)
    
    return all_items[:LIMIT]  # Ensure we don't exceed 10 total items


@tool
def fetch_headgear(keyword: Optional[str] = None, category: Optional[int] = None,
                  subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch headgear items (hats, helmets) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["Hats"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    # Set the correct type for all items
    for item in items:
        item["type"] = "Head"
    
    return items


@tool
def fetch_face(keyword: Optional[str] = None, category: Optional[int] = None,
              subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch face items (faces, masks) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["Faces"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Face"
    
    return items


@tool
def fetch_hair(keyword: Optional[str] = None, category: Optional[int] = None,
              subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch hair accessories from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["HairAccessories"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Hair"
    
    return items


@tool
def fetch_shirt(keyword: Optional[str] = None, category: Optional[int] = None,
               subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch shirt items from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["Shirts"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Shirt"
    
    return items


@tool
def fetch_tshirt(keyword: Optional[str] = None, category: Optional[int] = None,
                subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch t-shirt items from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["TShirts"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "TShirt"
    
    return items


@tool
def fetch_pants(keyword: Optional[str] = None, category: Optional[int] = None,
               subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch pants items from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["Pants"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Pants"
    
    return items


@tool
def fetch_back_accessory(keyword: Optional[str] = None, category: Optional[int] = None,
                        subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch back accessories (capes, wings, jetpacks) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["BackAccessories"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Back Accessory"
    
    return items


@tool
def fetch_neck_accessory(keyword: Optional[str] = None, category: Optional[int] = None,
                        subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch neck accessories (scarves, necklaces) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["NeckAccessories"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Neck Accessory"
    
    return items


@tool
def fetch_shoulder_accessory(keyword: Optional[str] = None, category: Optional[int] = None,
                            subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch shoulder accessories (pauldrons) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["ShoulderAccessories"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Shoulder Accessory"
    
    return items


@tool
def fetch_front_accessory(keyword: Optional[str] = None, category: Optional[int] = None,
                         subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch front accessories (chest plates, armor) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["FrontAccessories"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Front Accessory"
    
    return items


@tool
def fetch_waist_accessory(keyword: Optional[str] = None, category: Optional[int] = None,
                         subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch waist accessories (belts, tails) from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["WaistAccessories"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Waist Accessory"
    
    return items


@tool
def fetch_head_bodypart(keyword: Optional[str] = None, category: Optional[int] = None,
                       subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch head body parts from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["Heads"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Head Bodypart"
    
    return items


@tool
def fetch_bundle(keyword: Optional[str] = None, category: Optional[int] = None,
                subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch bundles from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["Bundles"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Bundle"
    
    return items


@tool
def fetch_emote(keyword: Optional[str] = None, category: Optional[int] = None,
               subcategory: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch emote animations from Roblox catalog"""
    mapping = SUBCATEGORY_MAPPINGS["EmoteAnimations"]
    
    params = {
        "Category": category or mapping["category"],
        "Subcategory": subcategory or mapping["subcategory"],
        "Limit": LIMIT
    }
    
    if keyword:
        params["Keyword"] = keyword
    
    items = make_roblox_api_call(params)
    
    for item in items:
        item["type"] = "Emote"
    
    return items


# Export all tools for easy import
ALL_ROBLOX_TOOLS = [
    fetch_outfit,
    fetch_headgear,
    fetch_face,
    fetch_hair,
    fetch_shirt,
    fetch_tshirt,
    fetch_pants,
    fetch_back_accessory,
    fetch_neck_accessory,
    fetch_shoulder_accessory,
    fetch_front_accessory,
    fetch_waist_accessory,
    fetch_head_bodypart,
    fetch_bundle,
    fetch_emote
]