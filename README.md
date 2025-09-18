# Roblox Outfit Marketplace Agents

A FastAPI backend powered by a multi-agent CAMEL architecture that helps users build and customize Roblox outfits through natural language conversations. The system uses intelligent tool planning and session management to provide a seamless outfit building experience.

## Architecture Overview

The system employs a multi-agent architecture with the following components:

- **Conversational Agent**: Handles dialogue, understands user intent (new outfit vs. replacements vs. clarifications), manages outfit state
- **Stylist Agent**: Decides which catalog tools to use and with what parameters based on user requests
- **Roblox Catalog Tools**: 15 specialized tools, one per item category (hats, shirts, pants, accessories, etc.), each limited to 10 results

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Conversational  │    │ Stylist Agent   │    │ Catalog Tools   │
│ Agent           │    │                 │    │ (15 tools)      │
│                 │───▶│ • Plans tools   │───▶│ • search_hats   │
│ • Dialogue      │    │ • Maps params   │    │ • search_shirts │
│ • Intent        │    │ • Handles slots │    │ • search_pants  │
│ • Session state │    │                 │    │ • ...           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file (optional for enhanced AI capabilities):
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
MODEL_NAME=gpt-4o-mini
```

Without an API key, the system uses fallback rule-based parsing.

### 3. Run the Server

```bash
uvicorn server.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Use Terminal Chat

```bash
python scripts/chat_cli.py
```

## API Documentation

### POST /chat

Single endpoint for all outfit conversations.

**Request:**
```json
{
  "prompt": "I want a knight outfit",
  "user_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 123,
  "reply": "Here's your 5-piece outfit! What do you think?",
  "outfit": [
    {"assetId": "123456", "type": "Head"},
    {"assetId": "789012", "type": "Shirt"},
    {"assetId": "345678", "type": "Pants"},
    {"assetId": "901234", "type": "Back Accessory"},
    {"assetId": "567890", "type": "Front Accessory"}
  ]
}
```

## Example Conversation

```
You: Hey!
Agent: Hi! I'm here to help you build awesome Roblox outfits. What kind of style are you looking for?

You: I want a knight's outfit
Agent: Here's your 5-piece outfit! What do you think?
[returns outfit with helmet, armor, pants, cape, chest gear]

You: change the headgear to an armored one
Agent: Updated your outfit! Here's your complete look with 5 items.
[returns outfit with new helmet but same other pieces]
```

## Project Structure

```
agents/
  __init__.py                # Package initialization
  contracts.py               # Pydantic models (API + domain models)
  memory.py                  # Per-user session storage
  config.py                  # Environment configuration
  param_helpers.py           # Price parsing and constants
  roblox_catalog_client.py   # HTTP client with retries and mapping
  stylist_agent.py           # Tool planning and parameter decisions
  tools.py                   # 15 specialized catalog tools
  conversation_agent.py      # CAMEL agent for dialogue and state
  orchestrator.py            # Coordinates agents and session management

server/
  __init__.py               # Package initialization
  main.py                   # FastAPI application with CORS

scripts/
  chat_cli.py              # Terminal chat interface
```

## Features

- **Persistent outfit state**: Each user maintains their current outfit across conversations
- **Intelligent tool selection**: Stylist agent chooses appropriate tools based on natural language
- **Replacement mode**: "Change the headgear" updates only that slot
- **New outfit mode**: "Knight outfit" builds complete 3-5 piece outfits
- **Clarifying questions**: Asks for specifics when requests are ambiguous
- **Price filtering**: "under 100 robux", "50-200 robux" etc.
- **Style recognition**: "medieval", "sci-fi", "western" etc. map to appropriate genres
- **Session management**: Per-user outfit state with slot-based organization

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server  
- `httpx` - HTTP client for Roblox catalog API
- `pydantic` - Data validation and serialization
- `camel-ai` - Multi-agent conversation framework
- `python-dotenv` - Environment variable management

## API Documentation

When the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`