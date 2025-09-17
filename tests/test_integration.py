"""Integration tests for API endpoints."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from agents.orchestrator import chat, keywords_to_ids


def test_chat_endpoint():
    """Test chat endpoint with real orchestrator."""
    result = chat("I want a futuristic knight outfit", 7470350941)
    
    assert result.success is True
    assert result.user_id == 7470350941
    assert "knight" in result.reply.lower()
    assert result.keywordSpec.theme == "knight"
    assert result.keywordSpec.style == "futuristic"
    print("✓ Chat endpoint test passed")


async def test_keywords_to_ids_endpoint():
    """Test keywords-to-ids endpoint."""
    spec = {"theme": "knight", "style": "futuristic", "parts": ["Back Accessory"]}
    result = await keywords_to_ids(spec)
    
    assert result.success is True
    assert isinstance(result.ids, list)
    # Without API key, should return empty list
    assert len(result.ids) == 0
    print("✓ Keywords-to-IDs endpoint test passed")


async def main():
    """Run all integration tests."""
    test_chat_endpoint()
    await test_keywords_to_ids_endpoint()
    print("All integration tests passed!")


if __name__ == "__main__":
    asyncio.run(main())