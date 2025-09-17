#!/usr/bin/env python3
"""Terminal chat client for Roblox Outfit Marketplace Agents."""
import asyncio
import json
import httpx
import sys
from typing import Dict, Any


async def chat_with_agent(prompt: str, user_id: int = 7470350941) -> Dict[str, Any]:
    """
    Send a chat request to the agent API.
    
    Args:
        prompt: User's prompt
        user_id: User identifier (default: 7470350941)
        
    Returns:
        API response as dictionary
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/chat",
                json={"prompt": prompt, "user_id": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            return {
                "error": "Could not connect to server. Is it running on http://localhost:8000?"
            }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {e}"
            }


def print_response(response: Dict[str, Any]) -> None:
    """Print the agent's response in a user-friendly format."""
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return
    
    success = response.get("success", False)
    reply = response.get("reply", "No reply")
    outfit = response.get("outfit", [])
    
    print(f"\n{'✅' if success else '❌'} Agent Response:")
    print(f"💬 {reply}")
    
    if outfit:
        print(f"\n👕 Found {len(outfit)} outfit items:")
        for i, item in enumerate(outfit, 1):
            asset_id = item.get("assetId", "Unknown")
            item_type = item.get("type", "Unknown")
            print(f"  {i}. {asset_id} ({item_type})")
    else:
        print("\n🔍 No outfit items found")
    
    print()  # Extra line for spacing


async def main():
    """Main interactive chat loop."""
    print("🎮 Roblox Outfit Marketplace Agent - Terminal Chat")
    print("=" * 50)
    print("💡 Type your outfit requests and I'll help you find items!")
    print("💡 Examples:")
    print("   - 'I want a futuristic knight outfit'")
    print("   - 'red ninja gear under 500 robux'")
    print("   - 'casual shirt and pants'")
    print("💡 Type 'quit' or 'exit' to stop")
    print()
    
    user_id = 7470350941  # Default user ID
    
    while True:
        try:
            # Get user input
            prompt = input("👤 You: ").strip()
            
            if not prompt:
                continue
                
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Send request to agent
            print("🤖 Agent is thinking...")
            response = await chat_with_agent(prompt, user_id)
            
            # Print response
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)