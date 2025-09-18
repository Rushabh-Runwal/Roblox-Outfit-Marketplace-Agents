"""Conversation agent using CAMEL for Roblox catalog tool decisions."""
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from agents.param_helpers import parse_price, detect_subcategory, detect_genre

# Load environment variables from .env file
load_dotenv()


def run_conversation_agent(prompt: str, memory: Dict[str, Any]) -> Dict[str, Any]:
    """Run conversation agent to decide parameters and call tool.
    
    Args:
        prompt: User's natural language prompt
        memory: User context memory
        
    Returns:
        Dict with either {"action": "search", "params": {...}} or {"action": "clarify", "reply": "..."}
    """
    system_prompt = """You are a Roblox stylist assistant. Your task:
1) Understand the user's outfit request.
2) Decide efficient Roblox Catalog API parameters.
3) Call the tool `roblox_search` with a strict schema.
4) Return a short reply + up to 10 items mapped to {assetId, type}.

Tool: roblox_search(Keyword?: string, Limit: int, Category?: int, Subcategory?: int, Genres?: int, MinPrice?: int, MaxPrice?: int)
- Always set Limit=10.
- Prefer specific filters (Subcategory, Genres, price) over Keyword when clear.
- Only include Keyword if it adds value.

Parameter options:

Category:
1 All, 2 Collectibles, 3 Clothing, 4 BodyParts, 5 Gear, 11 Accessories, 12 AvatarAnimations, 13 CommunityCreations

Subcategory:
1 All, 2 Collectibles, 3 Clothing, 4 BodyParts, 5 Gear, 9 Hats, 10 Faces, 12 Shirts, 13 TShirts, 14 Pants, 15 Heads,
19 Accessories, 20 HairAccessories, 21 FaceAccessories, 22 NeckAccessories, 23 ShoulderAccessories, 24 FrontAccessories,
25 BackAccessories, 26 WaistAccessories, 27 AvatarAnimations, 37 Bundles, 38 AnimationBundles, 39 EmoteAnimations,
40 CommunityCreations, 41 Melee, 42 Ranged, 43 Explosive, 44 PowerUp, 45 Navigation, 46 Musical, 47 Social,
48 Building, 49 Transport, 54 HeadAccessories, 55 ClassicTShirts, 56 ClassicShirts, 57 ClassicPants,
58 TShirtAccessories, 59 ShirtAccessories, 60 PantsAccessories, 61 JacketAccessories, 62 SweaterAccessories,
63 ShortsAccessories, 64 ShoesBundles, 65 DressSkirtAccessories, 66 DynamicHeads

Genres:
1 TownAndCity, 2 Medieval, 3 SciFi, 4 Fighting, 5 Horror, 6 Naval, 7 Adventure, 8 Sports, 9 Comedy, 10 Western,
11 Military, 13 Building, 14 FPS, 15 RPG

Price:
- MaxPrice, MinPrice are integers in Robux.

Rules:
- If user mentions a clear part (helmet/hat → Subcategory 9; back/wings/cape/jetpack → 25; pants → 14; shirts → 12; hair → 20; mask/eyepatch → 21), set Subcategory.
- If user uses style genre (medieval, sci-fi, western, military, RPG), set Genres accordingly.
- Parse price phrases: "under 100" => MaxPrice=100; "over 50" => MinPrice=50; "50–200" => both.
- If user says "more/next/another", reuse previous parameters; do not invent new ones.
- Do not return more than 10 results. Do not fabricate IDs.
- If parameters are ambiguous, ask a **single short clarifying question** and do not call the tool.

Output to server (not to the user):
- Either: a tool call with parameters.
- Or: a clarifying question when parameters are unclear.

Respond with JSON in one of these formats:
{"action": "search", "params": {"Limit": 10, "Keyword": "...", "Category": 3, ...}}
{"action": "clarify", "reply": "What specific type of item are you looking for?"}"""

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
            model_type=ModelType.GPT_3_5_TURBO,
            model_config_dict={"temperature": 0.1}
        )
        
        # Create agent
        agent = ChatAgent(
            system_message=BaseMessage.make_user_message(
                role_name="RobloxStylist",
                content=system_prompt
            ),
            model=model
        )
        
        # Get response
        user_message = BaseMessage.make_user_message(
            role_name="User",
            content=prompt
        )
        
        response = agent.step(user_message)
        
        # Parse JSON response
        try:
            result = json.loads(response.msg.content)
            if result.get("action") == "search":
                # Ensure Limit is always 10
                result["params"]["Limit"] = 10
            return result
        except (json.JSONDecodeError, ValueError):
            # Fall back to rule-based parsing
            return _fallback_parse(prompt)
            
    except Exception:
        # Fall back to rule-based parsing if OpenAI unavailable
        return _fallback_parse(prompt)


def _fallback_parse(prompt: str) -> Dict[str, Any]:
    """Fallback rule-based parameter extraction."""
    params = {"Limit": 10}
    
    # Parse price
    price_info = parse_price(prompt)
    params.update(price_info)
    
    # Detect subcategory
    subcategory = detect_subcategory(prompt)
    if subcategory:
        params["Subcategory"] = subcategory
        
    # Detect genre
    genre = detect_genre(prompt)
    if genre:
        params["Genres"] = genre
    
    # Add keyword if no specific filters found
    if not subcategory and not genre:
        # Extract potential keywords (simple approach)
        words = re.findall(r'\b\w+\b', prompt.lower())
        outfit_words = [w for w in words if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'want', 'need']]
        if outfit_words:
            params["Keyword"] = ' '.join(outfit_words[:3])  # Take first few words
    
    return {"action": "search", "params": params}

