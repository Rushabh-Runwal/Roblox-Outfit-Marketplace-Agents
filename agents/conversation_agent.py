"""Conversation agent using CAMEL with tools via Stylist planning."""
import logging
from typing import Dict, Any, Optional
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from agents.tools import TOOLS
from agents.stylist_agent import plan_tools, detect_target_slot, SLOT_TOOL_MAP
from agents.memory import get_session
from agents.contracts import SessionState, OutfitItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Roblox stylist assistant that helps users build and customize their outfits.

Your role:
- Greet users naturally and understand their outfit requests
- Determine when users want a NEW OUTFIT vs REPLACE A SLOT vs SHOW MORE items
- Ask ONE short clarifying question if the request is unclear
- When ready to help, execute tool calls step-by-step to build outfits
- Always return a short, friendly reply along with the ENTIRE outfit

Rules:
- For new outfits: call multiple tools to build a complete look (3-5 items)
- For replacements: call one tool to replace the specific slot
- Update the user's outfit state after each successful tool call
- Always return the complete current outfit, not just new items
- If you get no results from tools, suggest being more specific
- Each tool automatically limits results to 10 items

Available tools: search_hats, search_faces, search_hair, search_back_accessories, search_neck_accessories, search_shoulder_accessories, search_front_accessories, search_waist_accessories, search_shirts, search_tshirts, search_pants, search_heads, search_dynamic_heads, search_bundles, search_emotes

Always be friendly and helpful!"""


def build_agent():
    """Build and return the conversation agent with tools."""
    try:
        from agents.config import get_model_name
        
        # Map model names to CAMEL types
        model_name = get_model_name()
        if "gpt-4o" in model_name:
            model_type = ModelType.GPT_4O_MINI if "mini" in model_name else ModelType.GPT_4O
        elif "gpt-4" in model_name:
            model_type = ModelType.GPT_4
        else:
            model_type = ModelType.GPT_4O_MINI  # default
        
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=model_type,
            model_config_dict={"temperature": 0.1}
        )
        return ChatAgent(
            system_message=BaseMessage.make_user_message(
                role_name="RobloxStylist",
                content=SYSTEM_PROMPT
            ),
            model=model,
            tools=TOOLS
        )
    except Exception as e:
        logger.warning(f"Failed to create CAMEL agent: {e}")
        return None


async def apply_plan(session: SessionState, plan: list, action: str = "new_outfit") -> list:
    """
    Execute a stylist plan and update session outfit.
    
    Args:
        session: User session state
        plan: List of {"slot": str, "tool": str, "params": dict}
        action: Type of action ("new_outfit", "replace", "show_more")
        
    Returns:
        List of all items from tool executions
    """
    all_items = []
    
    # Import tools dynamically to avoid circular imports
    from agents.tools import (
        search_hats, search_faces, search_hair, search_back_accessories,
        search_neck_accessories, search_shoulder_accessories, search_front_accessories,
        search_waist_accessories, search_shirts, search_tshirts, search_pants,
        search_heads, search_dynamic_heads, search_bundles, search_emotes
    )
    
    tool_map = {
        "search_hats": search_hats,
        "search_faces": search_faces,
        "search_hair": search_hair,
        "search_back_accessories": search_back_accessories,
        "search_neck_accessories": search_neck_accessories,
        "search_shoulder_accessories": search_shoulder_accessories,
        "search_front_accessories": search_front_accessories,
        "search_waist_accessories": search_waist_accessories,
        "search_shirts": search_shirts,
        "search_tshirts": search_tshirts,
        "search_pants": search_pants,
        "search_heads": search_heads,
        "search_dynamic_heads": search_dynamic_heads,
        "search_bundles": search_bundles,
        "search_emotes": search_emotes,
    }
    
    logger.info(f"Applying plan with {len(plan)} steps for action: {action}")
    
    for step in plan:
        slot = step["slot"]
        tool_name = step["tool"]
        params = step["params"]
        
        logger.info(f"Executing step: slot={slot}, tool={tool_name}, params={params}")
        
        if tool_name in tool_map:
            try:
                # Execute tool
                items = await tool_map[tool_name](**params)
                logger.info(f"Tool {tool_name} returned {len(items)} items: {items}")
                all_items.extend(items)
                
                # Update session with appropriate item
                if items:
                    if action == "show_more" and slot in session.last_index_by_slot and len(items) > 1:
                        # For show_more, try to get next item
                        current_index = session.last_index_by_slot[slot]
                        next_index = (current_index + 1) % len(items)
                        session.current_outfit.items[slot] = items[next_index]["assetId"]
                        session.last_index_by_slot[slot] = next_index
                        logger.info(f"Show more: Updated outfit slot {slot} with item {next_index} (assetId {items[next_index]['assetId']})")
                    else:
                        # For new outfit or replace, use first item
                        session.current_outfit.items[slot] = items[0]["assetId"]
                        session.last_index_by_slot[slot] = 0
                        logger.info(f"Updated outfit slot {slot} with assetId {items[0]['assetId']}")
                    
                    session.last_params_by_slot[slot] = params
                else:
                    logger.warning(f"No items returned from {tool_name}")
                    
            except Exception as e:
                logger.error(f"Tool execution failed for {tool_name}: {e}")
        else:
            logger.error(f"Unknown tool: {tool_name}")
    
    logger.info(f"Final outfit state: {session.current_outfit.items}")
    return all_items


def run_conversation_agent(prompt: str, user_id: int) -> Dict[str, Any]:
    """
    Run conversation agent with session management and tool planning.
    
    Args:
        prompt: User's natural language prompt
        user_id: User identifier
        
    Returns:
        Dict with action, reply, and outfit data
    """
    session = get_session(user_id)
    
    # Check for simple greetings
    prompt_lower = prompt.lower().strip()
    if any(greeting in prompt_lower for greeting in ["hi", "hello", "hey", "sup"]) and len(prompt_lower) < 10:
        return {
            "action": "greet",
            "reply": "Hi! I'm here to help you build awesome Roblox outfits. What kind of style are you looking for?",
            "outfit": []
        }
    
    # Detect replacement requests
    target_slot = detect_target_slot(prompt)
    
    if target_slot:
        # Replacement mode
        plan = plan_tools(prompt, target_slot)
        
        if not plan:
            return {
                "action": "clarify", 
                "reply": f"What kind of {target_slot.lower()} are you looking for?",
                "outfit": []
            }
        
        return {
            "action": "replace",
            "reply": f"I'll find a new {target_slot.lower()} for you!",
            "plan": plan,
            "outfit": []
        }
    
    # Check for "more" requests
    if any(word in prompt_lower for word in ["more", "another", "different", "other"]):
        # For "more" requests, use a simplified slot detection
        more_slot_keywords = {
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
        
        more_target_slot = None
        for keyword, slot in more_slot_keywords.items():
            if keyword in prompt_lower:
                more_target_slot = slot
                break
        
        if more_target_slot and more_target_slot in session.last_params_by_slot:
            # Reuse last params for the specified slot
            last_params = session.last_params_by_slot[more_target_slot].copy()
            
            return {
                "action": "show_more",
                "reply": f"I'll find more {more_target_slot.lower()} options for you!",
                "plan": [{
                    "slot": more_target_slot,
                    "tool": SLOT_TOOL_MAP.get(more_target_slot, "search_hats"),
                    "params": last_params
                }],
                "outfit": []
            }
        elif session.last_params_by_slot:
            # Ask for clarification on which slot they want more of
            available_slots = list(session.last_params_by_slot.keys())
            return {
                "action": "clarify",
                "reply": f"Which item would you like more options for? I have suggestions for: {', '.join(available_slots).lower()}",
                "outfit": []
            }
        else:
            return {
                "action": "clarify",
                "reply": "I haven't made any suggestions yet. What kind of outfit are you looking for?",
                "outfit": []
            }
    
    # New outfit mode
    plan = plan_tools(prompt)
    
    if not plan:
        return {
            "action": "clarify",
            "reply": "What style of outfit are you looking for? For example: medieval knight, casual wear, or futuristic gear?",
            "outfit": []
        }
    
    return {
        "action": "new_outfit",
        "reply": "I'll put together an outfit for you!",
        "plan": plan,
        "outfit": []
    }

