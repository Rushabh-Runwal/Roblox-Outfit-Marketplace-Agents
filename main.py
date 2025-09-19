import urllib.parse
from dotenv import load_dotenv
import os
import json
import asyncio
import logging
from typing import List, Dict, Any
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Import all Roblox tools from our separate module
from roblox_tools import ALL_ROBLOX_TOOLS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_tools_description(tools):
    return "\n".join(
        f"Tool: {tool.name}, Schema: {json.dumps(tool.args).replace('{', '{{').replace('}', '}}')}"
        for tool in tools
    )

async def create_agent(agent_tools):
    agent_tools_description = get_tools_description(agent_tools)
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are the **Catalog Agent** for a Roblox outfit assistant.
Your job: convert a natural request into **Roblox Catalog API** calls (via tools), then return **up to 10 items per tool** as {{{{assetId, type}}}}. Prefer precise filters over free-text keywords. Never fabricate IDs.

When you receive a request, analyze what Roblox catalog items the user wants and use the appropriate tools to fetch items from the Roblox catalog API.

### Tool Usage Guidelines:

**fetch_outfit**: Use for multi-part requests. Input: {{{{parts: ["Head","Shirt","Pants"], keyword: "knight armored"}}}}

**Individual part tools**: Use for specific item types:
- fetch_headgear → Hats, HeadAccessories
- fetch_face → Faces, FaceAccessories  
- fetch_hair → HairAccessories
- fetch_shirt → Shirts, ClassicShirts
- fetch_tshirt → TShirts, ClassicTShirts
- fetch_pants → Pants, ClassicPants
- fetch_back_accessory → BackAccessories (capes, wings, jetpacks)
- fetch_neck_accessory → NeckAccessories (scarves, necklaces)
- fetch_shoulder_accessory → ShoulderAccessories (pauldrons)
- fetch_front_accessory → FrontAccessories (chest plates, armor)
- fetch_waist_accessory → WaistAccessories (belts, tails)
- fetch_head_bodypart → Heads, DynamicHeads
- fetch_bundle → Bundles
- fetch_emote → EmoteAnimations

### Parameter Guidelines:
- Use **keyword** for themes/styles ("knight", "futuristic", "pirate")
- Use **subcategory** for precise item types (automatically handled by tools)
- Always cap results to **10** per tool call
- Output format: [{{{{"assetId": "string-id", "type": "Head"}}}}]

### Example Usage:
User: "I want a knight outfit"
→ Use fetch_outfit with parts ["Head","Shirt","Pants","Back Accessory"] and keyword "knight"

User: "Show me futuristic helmets"
→ Use fetch_headgear with keyword "futuristic"

Available tools: {agent_tools_description}"""
        ),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Model configuration - hardcoded except for API key
    model = init_chat_model(
        model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
        model_provider="openai",
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=0.1,
        max_tokens=8000
    )

    agent = create_tool_calling_agent(model, agent_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)
    return agent_executor

async def main():
    load_dotenv()
    
    # Check if API key is provided
    api_key = os.getenv("MODEL_API_KEY")
    if not api_key:
        logger.error("MODEL_API_KEY environment variable is required")
        return
    
    logger.info("Initializing Roblox Catalog Agent...")
    
    # Use all Roblox catalog tools from the imported module
    agent_tools = ALL_ROBLOX_TOOLS
    
    agent_executor = await create_agent(agent_tools)
    
    logger.info("Roblox Catalog Agent started successfully")
    logger.info("You can now test the agent by providing catalog requests!")
    
    # Simple test to verify the agent works
    test_input = "headgear for a knight"
    logger.info(f"Testing with input: '{test_input}'")
    
    try:
        result = await agent_executor.ainvoke({"input": test_input})
        logger.info(f"Agent response: {result}")
    except Exception as e:
        logger.error(f"Error during test execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())