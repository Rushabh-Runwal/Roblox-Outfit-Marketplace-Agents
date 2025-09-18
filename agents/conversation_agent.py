"""Conversation agent using CAMEL for outfit keyword extraction."""
import json
import os
import re
from typing import Dict, Any
from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Load environment variables from .env file
load_dotenv()


def run_conversation_agent(prompt: str) -> dict:
    """Run CAMEL-based extraction with OpenAI."""
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
        raise e

