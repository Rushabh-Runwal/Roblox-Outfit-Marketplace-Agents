"""Conversation agent using CAMEL for outfit keyword extraction."""
import json
import os
import re
from typing import Dict, Any

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False


def run_conversation_agent(prompt: str) -> dict:
    """
    Extract outfit requirements from user text and return KeywordSpec dict.
    
    Args:
        prompt: User's natural language description of desired outfit
        
    Returns:
        dict: KeywordSpec dictionary with theme, style, parts, color, budget
    """
    # Try CAMEL agent first if available and configured
    if CAMEL_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            return _run_camel_agent(prompt)
        except Exception as e:
            print(f"CAMEL agent failed, falling back to simple extraction: {e}")
    
    # Fallback to simple keyword extraction
    return _run_simple_extraction(prompt)


def _run_camel_agent(prompt: str) -> dict:
    """Use CAMEL ChatAgent for sophisticated keyword extraction."""
    system_prompt = """Extract outfit requirements from user text and output **ONLY** a valid JSON KeywordSpec with fields: theme, style?, parts?, color?, budget?. No prose.

KeywordSpec format:
{
  "theme": "required string describing main outfit theme",
  "style": "optional string for style modifier (futuristic, medieval, etc.)",
  "parts": "optional array of Roblox outfit parts like ['Head', 'Shirt', 'Pants', 'Back Accessory']",
  "color": "optional color preference",
  "budget": "optional integer budget in Robux"
}

Examples:
Input: "I want a futuristic knight armor with cape"
Output: {"theme": "knight", "style": "futuristic", "parts": ["Back Accessory"], "color": null, "budget": null}

Input: "red ninja outfit under 500 robux"
Output: {"theme": "ninja", "style": null, "parts": null, "color": "red", "budget": 500}

Only respond with valid JSON."""

    # Create model
    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=ModelType.GPT_3_5_TURBO,
        model_config_dict={"temperature": 0.1}
    )
    
    # Create agent
    agent = ChatAgent(
        system_message=BaseMessage.make_user_message(
            role_name="KeywordExtractor",
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
        # Ensure required theme field exists
        if "theme" not in result:
            raise ValueError("Missing required 'theme' field")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse CAMEL response as JSON: {e}")
        print(f"Response was: {response.msg.content}")
        # Fall back to simple extraction
        return _run_simple_extraction(prompt)


def _run_simple_extraction(prompt: str) -> dict:
    """Simple keyword-based extraction as fallback."""
    prompt_lower = prompt.lower()
    
    # Common themes
    themes = {
        "knight": ["knight", "armor", "medieval", "warrior", "paladin"],
        "ninja": ["ninja", "assassin", "stealth", "shadow"],
        "pirate": ["pirate", "buccaneer", "sailor", "ship"],
        "wizard": ["wizard", "mage", "magic", "spell", "staff"],
        "robot": ["robot", "cyber", "mech", "android"],
        "superhero": ["hero", "super", "cape", "powers"],
        "casual": ["casual", "everyday", "normal", "basic"],
        "formal": ["formal", "suit", "dress", "elegant"],
        "sporty": ["sport", "athletic", "gym", "fitness"]
    }
    
    # Detect theme
    theme = "casual"  # default
    for theme_name, keywords in themes.items():
        if any(keyword in prompt_lower for keyword in keywords):
            theme = theme_name
            break
    
    # Detect style modifiers
    style = None
    styles = ["futuristic", "medieval", "sci-fi", "vintage", "modern", "retro", "cyberpunk"]
    for style_word in styles:
        if style_word in prompt_lower:
            style = style_word
            break
    
    # Common parts mentioned
    parts = []
    part_keywords = {
        "Head": ["hat", "helmet", "crown", "mask", "head"],
        "Shirt": ["shirt", "top", "tunic", "armor", "chest"],
        "Pants": ["pants", "legs", "trousers", "leggings"],
        "Back Accessory": ["cape", "wings", "backpack", "cloak", "back"]
    }
    
    for part_name, keywords in part_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            parts.append(part_name)
    
    # If no specific parts mentioned, add defaults for the theme
    if not parts:
        if theme in ["knight", "warrior"]:
            parts = ["Head", "Shirt", "Pants", "Back Accessory"]
        elif theme == "ninja":
            parts = ["Head", "Shirt", "Pants"]
        else:
            parts = ["Shirt", "Pants"]
    
    # Extract color
    color = None
    colors = ["red", "blue", "green", "yellow", "black", "white", "purple", "orange", "pink", "gray", "brown"]
    for color_word in colors:
        if color_word in prompt_lower:
            color = color_word
            break
    
    # Extract budget
    budget = None
    budget_match = re.search(r'(\d+)\s*(?:robux|r\$|bucks?)', prompt_lower)
    if budget_match:
        budget = int(budget_match.group(1))
    
    return {
        "theme": theme,
        "style": style,
        "parts": parts if parts else None,
        "color": color,
        "budget": budget
    }