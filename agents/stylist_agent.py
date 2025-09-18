"""Stylist agent that decides which tools to use and with what parameters."""
from typing import List, Dict, Any, Optional
from agents.param_helpers import WORD_TO_SUBCATEGORY, STYLE_TO_GENRE, parse_price


# Tool name mapping for each slot
SLOT_TOOL_MAP = {
    "Head": "search_hats",
    "Face": "search_faces", 
    "Hair": "search_hair",
    "Back Accessory": "search_back_accessories",
    "Neck Accessory": "search_neck_accessories",
    "Shoulder Accessory": "search_shoulder_accessories",
    "Front Accessory": "search_front_accessories",
    "Waist Accessory": "search_waist_accessories",
    "Shirt": "search_shirts",
    "T-Shirt": "search_tshirts",
    "Pants": "search_pants",
    "Head (Body Part)": "search_heads",
    "Dynamic Head": "search_dynamic_heads",
    "Bundle": "search_bundles",
    "Emote": "search_emotes",
}


def plan_tools(user_text: str, target_slot: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate a plan of tool calls based on user request.
    
    Args:
        user_text: Natural language request from user
        target_slot: Specific slot to replace (for replacements), None for new outfit
        
    Returns:
        List of {"slot": str, "tool": str, "params": dict} items
    """
    text_lower = user_text.lower()
    
    # Parse common parameters from text
    base_params = {}
    
    # Extract genre
    for style_word, genre_id in STYLE_TO_GENRE.items():
        if style_word in text_lower:
            base_params["Genres"] = genre_id
            break
    
    # Extract price constraints
    price_params = parse_price(user_text)
    base_params.update(price_params)
    
    # Extract keyword (meaningful words, excluding common filler)
    words = user_text.split()
    meaningful_words = [w for w in words if len(w) > 3 and w.lower() not in 
                       ['want', 'need', 'looking', 'find', 'outfit', 'clothes', 'items', 'gear']]
    if meaningful_words:
        # Use first few meaningful words as keyword
        base_params["Keyword"] = " ".join(meaningful_words[:3])
    
    # If target slot specified (replacement mode)
    if target_slot and target_slot in SLOT_TOOL_MAP:
        return [{
            "slot": target_slot,
            "tool": SLOT_TOOL_MAP[target_slot],
            "params": base_params
        }]
    
    # New outfit mode - plan 3-5 slots based on keywords
    plan = []
    
    # Always include core outfit pieces
    core_slots = ["Head", "Shirt", "Pants"]
    
    # Add optional accessories based on style/keywords
    if any(word in text_lower for word in ["knight", "medieval", "armor", "warrior"]):
        core_slots.extend(["Back Accessory", "Front Accessory"])
    elif any(word in text_lower for word in ["ninja", "stealth", "dark"]):
        core_slots.extend(["Face", "Back Accessory"])
    elif any(word in text_lower for word in ["casual", "everyday", "simple"]):
        # Keep it simple with just core pieces
        pass
    elif any(word in text_lower for word in ["fancy", "formal", "elegant"]):
        core_slots.extend(["Neck Accessory"])
    else:
        # Default: add one accessory
        core_slots.append("Back Accessory")
    
    # Create plan entries
    for slot in core_slots:
        if slot in SLOT_TOOL_MAP:
            plan.append({
                "slot": slot,
                "tool": SLOT_TOOL_MAP[slot],
                "params": base_params.copy()
            })
    
    return plan[:5]  # Cap at 5 items to avoid overwhelming


def detect_target_slot(user_text: str) -> Optional[str]:
    """
    Detect if user is requesting to replace a specific slot.
    
    Args:
        user_text: User's request text
        
    Returns:
        Slot name if replacement detected, None otherwise
    """
    text_lower = user_text.lower()
    
    # Check for replacement keywords
    replacement_indicators = ["change", "replace", "swap", "different", "new"]
    if not any(word in text_lower for word in replacement_indicators):
        return None
    
    # Map common slot references to canonical slot names
    slot_keywords = {
        "head": "Head",
        "headgear": "Head", 
        "helmet": "Head",
        "hat": "Head",
        "face": "Face",
        "hair": "Hair",
        "shirt": "Shirt",
        "top": "Shirt",
        "pants": "Pants",
        "trousers": "Pants",
        "back": "Back Accessory",
        "cape": "Back Accessory",
        "wings": "Back Accessory",
        "neck": "Neck Accessory",
        "necklace": "Neck Accessory",
    }
    
    for keyword, slot in slot_keywords.items():
        if keyword in text_lower:
            return slot
    
    return None