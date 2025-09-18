"""Conversation agent using CAMEL for Roblox catalog tool decisions."""
import json
import re
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.toolkits import FunctionTool
from agents.roblox_catalog_tool import roblox_search

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger(__name__)

# Register the roblox_search function as a CAMEL tool
TOOLS = [FunctionTool(roblox_search)]

def run_conversation_agent(prompt: str, memory: Dict[str, Any]) -> Dict[str, Any]:
    """Run conversation agent to decide parameters and call tool.
    
    Args:
        prompt: User's natural language prompt
        memory: User context memory
        
    Returns:
        Dict with either {"action": "search", "params": {...}} or {"action": "clarify", "reply": "..."}
    """
    system_prompt = """You are a Roblox stylist assistant.
Goal: understand the user's request and call the tool `roblox_search` with efficient parameters.

Tool signature:
roblox_search(Keyword?: string, Limit: int, Category?: int, Subcategory?: int, Genres?: int, MinPrice?: int, MaxPrice?: int)

Rules:
- Always set Limit=10.
- Prefer precise filters (Subcategory, Genres, MinPrice/MaxPrice) over Keyword when clear.
- Use Keyword only when it adds value.
- If the user says "more/next/another", reuse previous parameters.
- If parameters are ambiguous, ask ONE short clarifying question and DO NOT call the tool.

Parameter options (for reference in your reasoning):
- Category: 1 All, 2 Collectibles, 3 Clothing, 4 BodyParts, 5 Gear, 11 Accessories, 12 AvatarAnimations, 13 CommunityCreations
- Subcategory: 1 All, 2 Collectibles, 3 Clothing, 4 BodyParts, 5 Gear, 9 Hats, 10 Faces, 12 Shirts, 13 TShirts, 14 Pants, 15 Heads, 19 Accessories, 20 HairAccessories, 21 FaceAccessories, 22 NeckAccessories, 23 ShoulderAccessories, 24 FrontAccessories, 25 BackAccessories, 26 WaistAccessories, 27 AvatarAnimations, 37 Bundles, 38 AnimationBundles, 39 EmoteAnimations, 40 CommunityCreations, 41 Melee, 42 Ranged, 43 Explosive, 44 PowerUp, 45 Navigation, 46 Musical, 47 Social, 48 Building, 49 Transport, 54 HeadAccessories, 55 ClassicTShirts, 56 ClassicShirts, 57 ClassicPants, 58 TShirtAccessories, 59 ShirtAccessories, 60 PantsAccessories, 61 JacketAccessories, 62 SweaterAccessories, 63 ShortsAccessories, 64 ShoesBundles, 65 DressSkirtAccessories, 66 DynamicHeads
- Genres: 1 TownAndCity, 2 Medieval, 3 SciFi, 4 Fighting, 5 Horror, 6 Naval, 7 Adventure, 8 Sports, 9 Comedy, 10 Western, 11 Military, 13 Building, 14 FPS, 15 RPG

Your output to the server should be either:
A) a tool call with parameters, or
B) a single short clarifying question when parameters are unclear."""

    # Check for continuation keywords
    prompt_lower = prompt.lower()
    last_params = memory.get("last_params")
    
    if any(word in prompt_lower for word in ['more', 'next', 'another', 'different']) and last_params:
        # Reuse previous parameters for continuation
        return {"action": "search", "params": last_params}

    # Create model if OpenAI key is available
    try:
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O_MINI,
            model_config_dict={"temperature": 0.1}
        )
        
        # Create agent with tools
        agent = ChatAgent(
            system_message=BaseMessage.make_user_message(
                role_name="RobloxStylist",
                content=system_prompt
            ),
            model=model,
            tools=TOOLS
        )
        
        # Get response
        user_message = BaseMessage.make_user_message(
            role_name="User",
            content=prompt
        )
        
        response = agent.step(user_message)
        
        # Check if the response contains tool calls
        if hasattr(response.msg, 'tool_calls') and response.msg.tool_calls:
            # Extract tool call parameters
            tool_call = response.msg.tool_calls[0]
            if tool_call.function.name == 'roblox_search':
                # Parse the tool call arguments
                import json
                try:
                    params = json.loads(tool_call.function.arguments)
                    # Ensure Limit is always 10
                    params["Limit"] = 10
                    return {"action": "search", "params": params}
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse tool call arguments: {tool_call.function.arguments}")
                    return {"action": "clarify", "reply": "I had trouble understanding your request. Could you be more specific?"}
        else:
            # No tool call, treat as clarifying question
            return {"action": "clarify", "reply": response.msg.content}
            
    except Exception as e:
        # Fall back to rule-based parsing if OpenAI unavailable
        logger.warning(f"OpenAI model unavailable, using rule-based parsing: {e}")
        return _fallback_rule_based_parsing(prompt, memory)


def _fallback_rule_based_parsing(prompt: str, memory: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback rule-based parsing when CAMEL/OpenAI is unavailable."""
    from agents.param_helpers import parse_price, detect_subcategory, detect_genre
    
    prompt_lower = prompt.lower()
    params = {"Limit": 10}
    
    # Simple keyword detection
    if "hat" in prompt_lower or "helmet" in prompt_lower:
        params["Subcategory"] = 9
    elif "shirt" in prompt_lower:
        params["Subcategory"] = 12
    elif "pants" in prompt_lower:
        params["Subcategory"] = 14
    
    # Detect genre
    if "medieval" in prompt_lower:
        params["Genres"] = 2
    elif "sci-fi" in prompt_lower or "futuristic" in prompt_lower:
        params["Genres"] = 3
        
    # Parse prices
    price_params = parse_price(prompt)
    params.update(price_params)
    
    # If no specific filters, use keyword
    if len(params) == 1:  # Only Limit
        # Extract meaningful keywords
        words = [w for w in prompt_lower.split() if len(w) > 3 and w not in ['want', 'need', 'looking', 'find']]
        if words:
            params["Keyword"] = " ".join(words[:3])  # First 3 meaningful words
    
    return {"action": "search", "params": params}

