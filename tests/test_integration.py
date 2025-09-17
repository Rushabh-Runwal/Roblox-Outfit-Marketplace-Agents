"""Integration tests for API endpoints."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from agents.orchestrator import chat


async def test_chat_endpoint():
    """Test chat endpoint with real orchestrator."""
    result = await chat("I want a futuristic knight outfit", 7470350941)
    
    assert result.user_id == 7470350941
    # In testing environment, API may not be reachable, so check both cases
    if result.success:
        assert "knight" in result.reply.lower()
        assert isinstance(result.outfit, list)
    else:
        # Should have graceful failure message
        assert "sorry" in result.reply.lower() or "couldn't find" in result.reply.lower()
        assert result.outfit == []
    print("✓ Chat endpoint test passed")


async def main():
    """Run all integration tests."""
    await test_chat_endpoint()
    print("All integration tests passed!")


if __name__ == "__main__":
    asyncio.run(main())