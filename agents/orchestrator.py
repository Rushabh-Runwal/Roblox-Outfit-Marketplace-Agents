"""Orchestrator to coordinate agents and provide business logic."""
import logging
from typing import Dict, Any

from agents.contracts import ChatOut, OutfitItem, KeywordSpec
from agents.conversation_agent import run_conversation_agent
from agents.light_ranker import LightRanker

logger = logging.getLogger(__name__)


async def chat(prompt: str, user_id: int) -> ChatOut:
    """
    Main chat orchestrator that handles the full pipeline:
    
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
        
        # Step 2: Search Roblox catalog for items matching user requirement
        final_items = []

        # Generate reply
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