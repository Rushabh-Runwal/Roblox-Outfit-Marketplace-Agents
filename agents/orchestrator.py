"""Orchestrator to coordinate agents and provide business logic."""
import logging
from typing import Dict, Any

from agents.contracts import ChatOut, OutfitItem
from agents.conversation_agent import run_conversation_agent
from agents.roblox_catalog_tool import roblox_search, map_items

logger = logging.getLogger(__name__)

# Simple in-memory user context storage
USER_CTX: Dict[int, Dict[str, Any]] = {}


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
        
        # Initialize user context if not exists
        if user_id not in USER_CTX:
            USER_CTX[user_id] = {"last_params": None}
        
        # Step 1: Run Conversation Agent
        agent_result = run_conversation_agent(prompt, USER_CTX[user_id])
        logger.info(f"Agent result: {agent_result}")
        # Step 2: Handle agent response
        if agent_result.get("action") == "clarify":
            # Return clarifying question
            return ChatOut(
                success=True,
                user_id=user_id,
                reply=agent_result["reply"],
                outfit=[]
            )
        
        elif agent_result.get("action") == "search":
            # Enforce Limit=10 and perform search
            params = agent_result["params"]
            params["Limit"] = 10
            
            logger.info(f"Searching with params: {params} for user_id={user_id}")
            
            # Call Roblox catalog tool
            raw_items = await roblox_search(**params)
            items = map_items(raw_items)
            
            logger.info(f"Found {len(items)} items for user_id={user_id}")
            
            # Save last params for continuation
            USER_CTX[user_id]["last_params"] = params
            
            # Convert to OutfitItem objects
            outfit_items = [OutfitItem(**item) for item in items]
        
            # Generate successful reply
            reply = agent_result["reply"]
            if not outfit_items:
                item_count = len(outfit_items)
                if item_count == 1:
                    reply = "I found a great item for you!"
                else:
                    reply = f"Great! I found {item_count} items that match your request."
                
            return ChatOut(
                success=True,
                user_id=user_id,
                reply=reply,
                outfit=outfit_items
            )
        
        else:
            # Unknown action
            return ChatOut(
                success=False,
                user_id=user_id,
                reply="I'm not sure how to help with that. Could you try rephrasing your request?",
                outfit=[]
            )
        
    except Exception as e:
        logger.error(f"Error in chat orchestrator for user_id={user_id}: {e}")
        return ChatOut(
            success=False,
            user_id=user_id,
            reply="I'm sorry, I had trouble processing your request. Could you try again?",
            outfit=[]
        )