"""Configuration management for the application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
RETRIES = int(os.getenv("RETRIES", "3"))

# Development mode - when True, uses mock data instead of real Roblox API
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"

def get_model_name() -> str:
    """Get the configured model name."""
    return MODEL_NAME