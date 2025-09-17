"""Light Ranker for diversifying and ranking outfit items."""
import logging
from typing import List
from collections import defaultdict

from .contracts import OutfitItem

logger = logging.getLogger(__name__)

class LightRanker:
    """Light ranker that prioritizes diversity by item type."""
    
    @staticmethod
    def run(candidates: List[OutfitItem], n: int = 6) -> List[OutfitItem]:
        """
        Rank and filter candidates to return top diverse items.
        
        Args:
            candidates: List of candidate OutfitItem objects
            n: Target number of items to return (default 6, max 10)
            
        Returns:
            List of top ranked OutfitItem objects with diversity by type
        """
        if not candidates:
            logger.info("No candidates provided to ranker")
            return []
        
        # Cap n to maximum of 10
        target_count = min(n, 10)
        
        logger.info(f"Ranking {len(candidates)} candidates, target={target_count}")
        
        # Group items by type for diversity
        items_by_type = defaultdict(list)
        for item in candidates:
            items_by_type[item.type].append(item)
        
        logger.info(f"Found {len(items_by_type)} unique types: {list(items_by_type.keys())}")
        
        # First pass: Select one item from each type for maximum diversity
        selected = []
        for item_type, items in items_by_type.items():
            if len(selected) < target_count:
                selected.append(items[0])  # Take first item of each type
        
        # Second pass: Fill remaining slots with any remaining items
        if len(selected) < target_count:
            remaining_slots = target_count - len(selected)
            
            # Collect all remaining items
            remaining_items = []
            for item_type, items in items_by_type.items():
                # Skip first item of each type (already selected)
                remaining_items.extend(items[1:])
            
            # Add remaining items up to target count
            selected.extend(remaining_items[:remaining_slots])
        
        logger.info(f"Selected {len(selected)} items after ranking")
        
        return selected[:target_count]  # Ensure we don't exceed target