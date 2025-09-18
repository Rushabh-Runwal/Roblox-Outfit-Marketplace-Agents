"""Parameter constants and helper functions for Roblox catalog search."""
import re
from typing import Optional, Dict


# Parameter option constants
CATEGORY_OPTIONS = {
    1: "All",
    2: "Collectibles", 
    3: "Clothing",
    4: "BodyParts",
    5: "Gear",
    11: "Accessories",
    12: "AvatarAnimations",
    13: "CommunityCreations"
}

SUBCATEGORY_OPTIONS = {
    1: "All",
    2: "Collectibles",
    3: "Clothing", 
    4: "BodyParts",
    5: "Gear",
    9: "Hats",
    10: "Faces",
    12: "Shirts",
    13: "TShirts",
    14: "Pants",
    15: "Heads",
    19: "Accessories",
    20: "HairAccessories",
    21: "FaceAccessories",
    22: "NeckAccessories", 
    23: "ShoulderAccessories",
    24: "FrontAccessories",
    25: "BackAccessories",
    26: "WaistAccessories",
    27: "AvatarAnimations",
    37: "Bundles",
    38: "AnimationBundles",
    39: "EmoteAnimations",
    40: "CommunityCreations",
    41: "Melee",
    42: "Ranged",
    43: "Explosive",
    44: "PowerUp",
    45: "Navigation",
    46: "Musical",
    47: "Social",
    48: "Building",
    49: "Transport",
    54: "HeadAccessories",
    55: "ClassicTShirts",
    56: "ClassicShirts",
    57: "ClassicPants",
    58: "TShirtAccessories",
    59: "ShirtAccessories",
    60: "PantsAccessories",
    61: "JacketAccessories",
    62: "SweaterAccessories",
    63: "ShortsAccessories",
    64: "ShoesBundles",
    65: "DressSkirtAccessories",
    66: "DynamicHeads"
}

GENRE_OPTIONS = {
    1: "TownAndCity",
    2: "Medieval",
    3: "SciFi",
    4: "Fighting",
    5: "Horror",
    6: "Naval",
    7: "Adventure",
    8: "Sports",
    9: "Comedy",
    10: "Western",
    11: "Military",
    13: "Building", 
    14: "FPS",
    15: "RPG"
}


def parse_price(text: str) -> Dict[str, Optional[int]]:
    """Parse price phrases into MinPrice/MaxPrice parameters.
    
    Args:
        text: Text containing price information like "under 100", "over 50", "50-200"
        
    Returns:
        Dict with MinPrice and/or MaxPrice keys, or empty dict if no price found
    """
    result = {}
    text = text.lower().strip()
    
    # Pattern for "under X" or "below X"
    under_match = re.search(r'(?:under|below|less than)\s*(\d+)', text)
    if under_match:
        result['MaxPrice'] = int(under_match.group(1))
    
    # Pattern for "over X" or "above X" 
    over_match = re.search(r'(?:over|above|more than)\s*(\d+)', text)
    if over_match:
        result['MinPrice'] = int(over_match.group(1))
    
    # Pattern for "X-Y", "X to Y", "X–Y"
    range_match = re.search(r'(\d+)\s*(?:-|to|–)\s*(\d+)', text)
    if range_match:
        min_price = int(range_match.group(1))
        max_price = int(range_match.group(2))
        result['MinPrice'] = min_price
        result['MaxPrice'] = max_price
    
    return result


def detect_subcategory(text: str) -> Optional[int]:
    """Detect subcategory from text keywords.
    
    Args:
        text: User input text
        
    Returns:
        Subcategory ID if detected, None otherwise
    """
    text = text.lower()
    
    # Simple keyword matching for common items
    if any(word in text for word in ['hat', 'helmet', 'cap', 'beanie']):
        return 9  # Hats
    elif any(word in text for word in ['shirt', 'top', 'blouse']):
        return 12  # Shirts
    elif any(word in text for word in ['tshirt', 't-shirt', 'tee']):
        return 13  # TShirts 
    elif any(word in text for word in ['pants', 'trousers', 'jeans']):
        return 14  # Pants
    elif any(word in text for word in ['hair', 'hairstyle']):
        return 20  # HairAccessories
    elif any(word in text for word in ['mask', 'eyepatch', 'glasses']):
        return 21  # FaceAccessories
    elif any(word in text for word in ['back', 'wings', 'cape', 'jetpack']):
        return 25  # BackAccessories
    
    return None


def detect_genre(text: str) -> Optional[int]:
    """Detect genre from text keywords.
    
    Args:
        text: User input text
        
    Returns:
        Genre ID if detected, None otherwise  
    """
    text = text.lower()
    
    # Keyword matching for genres
    if any(word in text for word in ['medieval', 'knight', 'castle', 'armor']):
        return 2  # Medieval
    elif any(word in text for word in ['sci-fi', 'scifi', 'futuristic', 'space', 'robot']):
        return 3  # SciFi
    elif any(word in text for word in ['fighting', 'combat', 'warrior']):
        return 4  # Fighting
    elif any(word in text for word in ['horror', 'scary', 'spooky', 'zombie']):
        return 5  # Horror
    elif any(word in text for word in ['western', 'cowboy', 'sheriff']):
        return 10  # Western
    elif any(word in text for word in ['military', 'soldier', 'army']):
        return 11  # Military
    elif any(word in text for word in ['rpg', 'fantasy', 'magic']):
        return 15  # RPG
    
    return None