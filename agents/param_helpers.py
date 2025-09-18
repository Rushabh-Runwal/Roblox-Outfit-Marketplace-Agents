"""Parameter parsing helpers for Roblox catalog search."""
import re
from typing import Optional, Dict

def parse_price(text: str) -> Dict[str, Optional[int]]:
    """Parse price expressions from text.
    
    Args:
        text: Input text that may contain price expressions
        
    Returns:
        Dict with MinPrice and/or MaxPrice keys
    """
    text = text.lower()
    result = {}
    
    # Match "under X" or "below X"
    under_match = re.search(r'\b(?:under|below|less than)\s*(\d+)', text)
    if under_match:
        result["MaxPrice"] = int(under_match.group(1))
    
    # Match "over X" or "above X" or "more than X"
    over_match = re.search(r'\b(?:over|above|more than)\s*(\d+)', text)
    if over_match:
        result["MinPrice"] = int(over_match.group(1))
    
    # Match "X-Y" or "X to Y" range
    range_match = re.search(r'\b(\d+)(?:\s*[-–—]\s*|\s+to\s+)(\d+)', text)
    if range_match:
        min_price = int(range_match.group(1))
        max_price = int(range_match.group(2))
        result["MinPrice"] = min_price
        result["MaxPrice"] = max_price
    
    return result


def detect_subcategory(text: str) -> Optional[int]:
    """Detect subcategory from text keywords.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Subcategory ID if detected, None otherwise
    """
    text = text.lower()
    
    # Hat/helmet keywords
    if any(word in text for word in ['helmet', 'hat', 'crown', 'beanie', 'cap']):
        return 9  # Hats
    
    # Mask/face accessories
    if any(word in text for word in ['mask', 'eyepatch', 'glasses', 'goggles']):
        return 21  # FaceAccessories
    
    # Hair
    if any(word in text for word in ['hair', 'hairstyle']):
        return 20  # HairAccessories
    
    # Back accessories
    if any(word in text for word in ['back', 'jetpack', 'wings', 'cape', 'backpack']):
        return 25  # BackAccessories
    
    # Pants
    if any(word in text for word in ['pants', 'trousers', 'jeans']):
        return 14  # Pants
    
    # Shirts
    if any(word in text for word in ['shirt', 'blouse', 'top']):
        return 12  # Shirts
        
    # T-shirts
    if any(word in text for word in ['t-shirt', 'tshirt', 'tee']):
        return 13  # TShirts
    
    return None


def detect_genre(text: str) -> Optional[int]:
    """Detect genre from text keywords.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Genre ID if detected, None otherwise
    """
    text = text.lower()
    
    # Medieval/Knight
    if any(word in text for word in ['medieval', 'knight', 'armor', 'castle', 'sword']):
        return 2  # Medieval
    
    # Sci-Fi/Futuristic
    if any(word in text for word in ['sci-fi', 'scifi', 'futuristic', 'cyber', 'robot', 'space']):
        return 3  # SciFi
    
    # Western/Cowboy
    if any(word in text for word in ['western', 'cowboy', 'cowgirl', 'sheriff', 'saloon']):
        return 10  # Western
    
    # Military
    if any(word in text for word in ['military', 'army', 'soldier', 'combat', 'tactical']):
        return 11  # Military
    
    # RPG/Fantasy
    if any(word in text for word in ['rpg', 'fantasy', 'magic', 'wizard', 'mage', 'fantasy']):
        return 15  # RPG
    
    # Horror
    if any(word in text for word in ['horror', 'scary', 'zombie', 'vampire', 'ghost']):
        return 5  # Horror
    
    return None