"""Orchestrator to coordinate agents and provide business logic."""
import logging
from typing import Dict, Any

from agents.contracts import ChatOut, OutfitItem, KeywordSpec
from agents.conversation_agent import run_conversation_agent
from agents.roblox_catalog_client import search_catalog, map_items
from agents.light_ranker import LightRanker

logger = logging.getLogger(__name__)


async def chat(prompt: str, user_id: int) -> ChatOut:
    """
    Main chat orchestrator that handles the full pipeline:
    1. ConversationAgent.run(prompt) → KeywordSpec (internal only)
    2. RobloxCatalogClient.search_catalog(theme, limit=12) → candidates
    3. LightRanker.run(candidates, n=6..10) → final list
    
    Args:
        prompt: User's natural language prompt
        user_id: User identifier
        
    Returns:
        ChatOut with success status, reply, and outfit items
    """
    try:
        logger.info(f"Processing chat request: user_id={user_id}, prompt_length={len(prompt)}")
        
        # Step 1: Extract keywords using conversation agent
        keyword_spec_dict = run_conversation_agent(prompt)
        keyword_spec = KeywordSpec(**keyword_spec_dict)
        
        theme = keyword_spec.theme
        style = keyword_spec.style
        
        logger.info(f"Extracted theme='{theme}', style='{style}' for user_id={user_id}")
        
        # Step 2: Search Roblox catalog
        raw_items = await search_catalog(theme, limit=12)
        
        if not raw_items:
            logger.warning(f"No items found for theme '{theme}' for user_id={user_id}")
            return ChatOut(
                success=False,
                user_id=user_id,
                reply="Sorry, I couldn't find items right now. Please try again later.",
                outfit=[]
            )
        
        # Step 3: Map raw items to OutfitItem objects
        candidate_items = map_items(raw_items)
        logger.info(f"Mapped {len(candidate_items)} candidate items for user_id={user_id}")
        
        if not candidate_items:
            logger.warning(f"No valid items after mapping for user_id={user_id}")
            return ChatOut(
                success=False,
                user_id=user_id,
                reply="Sorry, I couldn't find items right now. Please try again later.",
                outfit=[]
            )
        
        # Step 4: Use light ranker to get final diverse selection
        final_items = LightRanker.run(candidate_items, n=8)  # Target 8 items for good variety
        logger.info(f"Ranked to {len(final_items)} final items for user_id={user_id}")
        
        # Step 5: Generate reply
        reply = _generate_chat_reply(keyword_spec, len(final_items))
        
        return ChatOut(
            success=True,
            user_id=user_id,
            reply=reply,
            outfit=final_items
        )
        
    except Exception as e:
        logger.error(f"Error in chat orchestrator for user_id={user_id}: {e}")
        return ChatOut(
            success=False,
            user_id=user_id,
            reply="I'm sorry, I had trouble processing your request. Could you try again?",
            outfit=[]
        )


def _generate_chat_reply(keyword_spec: KeywordSpec, item_count: int) -> str:
    """
    Generate a friendly chat reply based on the keyword specification and results.
    
    Args:
        keyword_spec: The extracted keywords and requirements
        item_count: Number of items found
        
    Returns:
        Friendly reply string
    """
    theme = keyword_spec.theme
    style = keyword_spec.style
    
    if item_count == 0:
        return "Sorry, I couldn't find any matching items right now."
    
    # Build descriptive text
    outfit_desc = theme
    if style:
        outfit_desc = f"{style} {theme}"
    
    if item_count == 1:
        return f"I found a great {outfit_desc} item for you!"
    else:
        return f"Your {outfit_desc} outfit is ready! I found {item_count} great items for you."


# Development/testing functions
def test_chat_orchestrator():
    """Test the chat orchestrator with sample inputs."""
    import asyncio
    
    async def run_tests():
        test_cases = [
            ("I want a futuristic knight outfit", 12345),
            ("red ninja gear under 500 robux", 67890),
            ("casual shirt and pants", 11111)
        ]
        
        for prompt, user_id in test_cases:
            print(f"\nTesting: '{prompt}'")
            result = await chat(prompt, user_id)
            print(f"Success: {result.success}")
            print(f"Reply: {result.reply}")
            print(f"Items: {len(result.outfit)}")
            if result.outfit:
                for item in result.outfit[:3]:  # Show first 3 items
                    print(f"  - {item.assetId} ({item.type})")
    
    asyncio.run(run_tests())


if __name__ == "__main__":
    # Run tests if executed directly
    print("Testing chat orchestrator...")
    test_chat_orchestrator()