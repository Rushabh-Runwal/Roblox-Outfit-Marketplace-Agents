#!/usr/bin/env python3
"""
Interactive Chat Terminal for Roblox Catalog Agent

This allows you to chat with the agent in real-time via terminal input.
"""

import asyncio
import logging
import sys
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chat_models import init_chat_model
from roblox_tools import ALL_ROBLOX_TOOLS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Store for chat sessions
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

async def create_agent(tools):
    """Create the Roblox catalog agent"""
    
    # System prompt for the agent
    system_prompt = """You are a specialized Roblox Catalog Agent that helps users find items in the Roblox catalog.

    Your primary function is to help users discover and explore Roblox catalog items including:
    - Clothing (shirts, t-shirts, pants)
    - Accessories (hats, hair, face accessories, back accessories, front accessories, etc.)
    - Body parts and heads
    - Bundles and emotes

    IMPORTANT GUIDELINES:
    1. Always use the available tools to search for items when users request catalog items
    2. Focus on accessories (back, front, shoulder, neck, waist) as they work best with the API
    3. Provide clear, organized responses with asset IDs and types
    4. If certain searches fail, suggest working alternatives (like accessories instead of clothing)
    5. Be helpful and engaging while staying focused on catalog searches

    Available tools:
    - fetch_outfit: Get multiple outfit parts at once
    - fetch_headgear: Find hats and helmets
    - fetch_face: Find faces and masks  
    - fetch_hair: Find hair accessories
    - fetch_shirt: Find shirts
    - fetch_tshirt: Find t-shirts
    - fetch_pants: Find pants
    - fetch_back_accessory: Find capes, wings, jetpacks
    - fetch_neck_accessory: Find scarves, necklaces
    - fetch_shoulder_accessory: Find shoulder armor, pauldrons
    - fetch_front_accessory: Find chest plates, front armor
    - fetch_waist_accessory: Find belts, waist items
    - fetch_head_bodypart: Find head body parts
    - fetch_bundle: Find avatar bundles
    - fetch_emote: Find emote animations

    Remember: Accessories (back, front, shoulder, neck, waist) work most reliably!
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Initialize the model
    model = init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        api_key=os.getenv("MODEL_API_KEY"),
        temperature=0.7,
    )

    # Create the agent
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Add message history
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    return agent_with_chat_history

async def main():
    """Main chat loop"""
    print("🤖 Roblox Catalog Agent - Interactive Chat Terminal")
    print("=" * 60)
    print("💡 I can help you find Roblox catalog items!")
    print("💡 Try: 'Find knight armor accessories' or 'Show me cool back accessories'")
    print("💡 Type 'quit', 'exit', or 'bye' to end the chat")
    print("💡 Accessories work best: back, front, shoulder, neck, waist items")
    print("-" * 60)
    
    try:
        # Initialize agent
        logger.info("Initializing Roblox Catalog Agent...")
        agent_tools = ALL_ROBLOX_TOOLS
        agent = await create_agent(agent_tools)
        logger.info("✅ Agent initialized successfully!")
        
        session_id = "main_session"
        
        while True:
            try:
                # Get user input
                user_input = input("\n🔍 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Thanks for using the Roblox Catalog Agent! Goodbye!")
                    break
                
                if not user_input:
                    print("💭 Please enter a search request or 'quit' to exit.")
                    continue
                
                print(f"\n🤖 Agent: Searching for '{user_input}'...")
                
                # Process the request
                response = await agent.ainvoke(
                    {"input": user_input},
                    config={"configurable": {"session_id": session_id}}
                )
                
                print(f"\n✨ {response['output']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("💡 Try rephrasing your request or ask for accessories (they work best!)")
                
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print(f"❌ Failed to start agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())