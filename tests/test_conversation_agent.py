"""Unit tests for conversation agent."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.conversation_agent import run_conversation_agent


def test_futuristic_knight():
    """Test the specified example case."""
    result = run_conversation_agent("futuristic knight armor with cape")
    
    assert result["theme"] == "knight"
    assert result["style"] == "futuristic"
    assert "Back Accessory" in result["parts"]
    print("✓ Futuristic knight test passed")


def test_ninja_with_budget():
    """Test ninja with color and budget extraction."""
    result = run_conversation_agent("red ninja outfit under 500 robux")
    
    assert result["theme"] == "ninja"
    assert result["color"] == "red"
    assert result["budget"] == 500
    print("✓ Ninja with budget test passed")


def test_casual_outfit():
    """Test casual outfit detection."""
    result = run_conversation_agent("I want a casual shirt and pants")
    
    assert result["theme"] == "casual"
    assert "Shirt" in result["parts"]
    assert "Pants" in result["parts"]
    print("✓ Casual outfit test passed")


def test_required_theme_field():
    """Test that theme field is always present."""
    result = run_conversation_agent("something random")
    
    assert "theme" in result
    assert isinstance(result["theme"], str)
    print("✓ Required theme field test passed")


if __name__ == "__main__":
    test_futuristic_knight()
    test_ninja_with_budget()
    test_casual_outfit()
    test_required_theme_field()
    print("All conversation agent tests passed!")