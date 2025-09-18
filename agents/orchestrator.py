"""Orchestrator to coordinate agents and provide business logic."""
import logging
from typing import Dict, Any

from agents.contracts import ChatOut, OutfitItem
from agents.conversation_agent import run_conversation_agent, apply_plan
from agents.memory import get_session

logger = logging.getLogger(__name__)


async def chat(prompt: str, user_id: int) -> ChatOut:
    """
    Main chat orchestrator that handles the full pipeline with session management.
    
    Args:
        prompt: User's natural language prompt
        user_id: User identifier
        
    Returns:
        ChatOut with success status, reply, and outfit items
    """
    try:
        logger.info(f"Chat request: user_id={user_id}, prompt_length={len(prompt)}")
        
        # Get user session
        session = get_session(user_id)
        
        # Step 1: Run Conversation Agent
        agent_result = run_conversation_agent(prompt, user_id)
        action = agent_result.get("action")
        logger.info(f"Agent action: {action}, user_id={user_id}")
        
        # Step 2: Handle agent response based on action
        reply = agent_result.get("reply", "")
        
        if action in ["greet", "clarify"]:
            # Return response without tools
            logger.info(f"Action={action}: returning reply without tools, user_id={user_id}")
            return ChatOut(
                success=True,
                user_id=user_id,
                reply=reply,
                outfit=[]
            )
        
        elif action in ["new_outfit", "replace"]:
            # Execute plan and update session
            plan = agent_result.get("plan", [])
            tool_calls_used = []
            
            if plan:
                # Track tool names for logging
                tool_calls_used = [step["tool"] for step in plan]
                
                # Execute tools in plan
                await apply_plan(session, plan)
                
                logger.info(f"Applied plan: tools={tool_calls_used}, user_id={user_id}")
            
            # Build full outfit from session
            outfit_items = []
            for slot, asset_id in session.current_outfit.items.items():
                outfit_items.append(OutfitItem(assetId=asset_id, type=slot))
            
            # Generate appropriate reply
            if not outfit_items:
                reply = "I couldn't find any items matching your criteria. Try being more specific or adjusting your requirements."
                success = False
            else:
                if action == "replace":
                    reply = f"Updated your outfit! Here's your complete look with {len(outfit_items)} items."
                else:
                    reply = f"Here's your {len(outfit_items)}-piece outfit! What do you think?"
                success = True
            
            logger.info(f"Final result: action={action}, tools_used={tool_calls_used}, outfit_size={len(outfit_items)}, user_id={user_id}")
            
            return ChatOut(
                success=success,
                user_id=user_id,
                reply=reply,
                outfit=outfit_items
            )
        
        else:
            # Unknown action
            logger.warning(f"Unknown action: {action}, user_id={user_id}")
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