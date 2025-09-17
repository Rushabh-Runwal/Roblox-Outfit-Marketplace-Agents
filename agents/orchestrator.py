"""Orchestrator to coordinate agents and provide business logic."""
import logging
from typing import Dict, Any
from agents.contracts import ChatOut, IdsOut, KeywordSpec
from agents.conversation_agent import run_conversation_agent
from agents.firecrawl_agent import fetch_ids_from_firecrawl

logger = logging.getLogger(__name__)


def chat(prompt: str, user_id: int) -> ChatOut:
    """
    Process user chat input and return outfit recommendations.
    
    Args:
        prompt: User's natural language input
        user_id: Unique user identifier
        
    Returns:
        ChatOut with success status, user_id, reply, and keywordSpec
    """
    try:
        # Step 1: Extract keyword specification from prompt
        keyword_spec_dict = run_conversation_agent(prompt)
        keyword_spec = KeywordSpec(**keyword_spec_dict)
        
        # Step 2: Generate a helpful NPC-style reply
        reply = _generate_chat_reply(keyword_spec, prompt)
        
        # Step 3: Return structured response
        return ChatOut(
            success=True,
            user_id=user_id,
            reply=reply,
            keywordSpec=keyword_spec
        )
        
    except Exception as e:
        logger.error(f"Error in chat orchestrator: {e}")
        # Return error response with minimal keyword spec
        fallback_spec = KeywordSpec(theme="unknown")
        return ChatOut(
            success=False,
            user_id=user_id,
            reply="I'm sorry, I had trouble understanding your request. Could you try describing your outfit again?",
            keywordSpec=fallback_spec
        )


async def keywords_to_ids(keyword_spec: dict) -> IdsOut:
    """
    Convert KeywordSpec to Roblox catalog item IDs.
    
    Args:
        keyword_spec: Dictionary containing theme, style, parts, color, budget
        
    Returns:
        IdsOut with success status and list of catalog item IDs
    """
    try:
        # Use Firecrawl agent to find matching catalog items
        ids = await fetch_ids_from_firecrawl(keyword_spec, limit=10)
        
        return IdsOut(
            success=True,
            ids=ids
        )
        
    except Exception as e:
        logger.error(f"Error in keywords_to_ids orchestrator: {e}")
        return IdsOut(
            success=False,
            ids=[]
        )


def _generate_chat_reply(keyword_spec: KeywordSpec, original_prompt: str) -> str:
    """
    Generate a helpful NPC-style reply based on the extracted keyword spec.
    
    Args:
        keyword_spec: Extracted outfit requirements
        original_prompt: User's original input
        
    Returns:
        Friendly response string
    """
    theme = keyword_spec.theme
    style = keyword_spec.style
    parts = keyword_spec.parts
    color = keyword_spec.color
    budget = keyword_spec.budget
    
    # Start with acknowledgment
    if style:
        reply = f"I found some great {style} {theme} options for you! "
    else:
        reply = f"I found some great {theme} outfit options for you! "
    
    # Add color mention if specified
    if color:
        reply += f"I'll focus on {color} items. "
    
    # Add budget consideration if specified
    if budget:
        reply += f"I'll keep it under {budget} Robux. "
    
    # Add parts information
    if parts and len(parts) > 0:
        if len(parts) == 1:
            reply += f"I'll look for {parts[0]} items specifically. "
        else:
            parts_str = ", ".join(parts[:-1]) + f" and {parts[-1]}"
            reply += f"I'll search for {parts_str} pieces. "
    
    # Add call to action
    if not keyword_spec.style and theme not in ["casual", "unknown"]:
        reply += "Would you like me to focus on a specific style like futuristic or medieval? "
    elif not parts:
        reply += "Would you like me to search for specific outfit parts? "
    else:
        reply += "Let me search for those items now!"
    
    return reply


# Development/testing functions
def test_chat_orchestrator():
    """Test the chat orchestrator with sample inputs."""
    test_cases = [
        ("I want a futuristic knight outfit", 12345),
        ("red ninja gear under 500 robux", 67890),
        ("casual shirt and pants", 11111)
    ]
    
    for prompt, user_id in test_cases:
        print(f"\nTesting: '{prompt}'")
        result = chat(prompt, user_id)
        print(f"Reply: {result.reply}")
        print(f"KeywordSpec: {result.keywordSpec.model_dump()}")


if __name__ == "__main__":
    # Run tests if executed directly
    import asyncio
    
    print("Testing chat orchestrator...")
    test_chat_orchestrator()
    
    print("\nTesting keywords_to_ids orchestrator...")
    async def test_keywords_to_ids():
        test_spec = {"theme": "knight", "style": "futuristic", "parts": ["Back Accessory"]}
        result = await keywords_to_ids(test_spec)
        print(f"IDs result: {result.model_dump()}")
    
    asyncio.run(test_keywords_to_ids())