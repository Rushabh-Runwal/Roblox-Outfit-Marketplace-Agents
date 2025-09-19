# Roblox Outfit Marketplace Agents

A FastAPI backend powered by a multi-agent CAMEL architecture that helps users build and customize Roblox outfits through natural language conversations. The system uses intelligent tool planning and session management to provide a seamless outfit building experience.

## Architecture Overview

The system employs a **Conversational Agent + Tool architecture** with the following components:

- **Conversation Agent**: CAMEL ChatAgent that handles natural language dialogue, understands user intent (new outfit vs. replacements vs. show more), and manages conversation flow
- **Stylist Agent**: Plans tool calls by mapping user requests to appropriate Roblox catalog search parameters and item slots
- **Roblox Catalog Tools**: 15 specialized CAMEL FunctionTools, one per item category (hats, shirts, pants, accessories, etc.), each limited to 10 results
- **Session Management**: Per-user outfit state with slot-based organization and "show more" functionality
- **Orchestrator**: Coordinates agents, executes tool plans, and manages the complete request pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Conversation    │    │ Stylist Agent   │    │ Catalog Tools   │
│ Agent (CAMEL)   │    │                 │    │ (15 CAMEL tools)│
│                 │───▶│ • Plans tools   │───▶│ • search_hats   │
│ • Dialogue      │    │ • Maps params   │    │ • search_shirts │
│ • Intent detect │    │ • Handles slots │    │ • search_pants  │
│ • Tool calls    │    │ • Show more     │    │ • ...           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                                              │
        ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Session Memory  │    │ Orchestrator    │    │ FastAPI Server  │
│                 │    │                 │    │                 │
│ • User outfits  │◀───│ • Agent coord   │───▶│ • Single /chat  │
│ • Last params   │    │ • Tool execution│    │ • CORS enabled  │
│ • Item indices  │    │ • Outfit builds │    │ • JSON I/O      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Configure your environment:
```bash
# For AI-powered conversation (optional)
OPENAI_API_KEY=sk-your-openai-api-key-here
MODEL_NAME=gpt-4o-mini

# Development mode (uses mock data instead of real Roblox API)
DEV_MODE=true
```

In development mode, the system uses realistic mock data for testing without external API dependencies.

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

### Single Endpoint: POST /chat

All outfit conversations go through one endpoint with simple JSON I/O.

**Request:**
```json
{
  "prompt": "I want a medieval knight outfit",
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
    {"assetId": "1001", "type": "Head"},
    {"assetId": "3001", "type": "Shirt"},
    {"assetId": "4001", "type": "Pants"},
    {"assetId": "5001", "type": "Back Accessory"},
    {"assetId": "6002", "type": "Front Accessory"}
  ]
}
```

## Example Conversation

```
You: hi
Agent: Hi! I'm here to help you build awesome Roblox outfits. What kind of style are you looking for?

You: I want a medieval knight outfit
Agent: Here's your 5-piece outfit! What do you think?
[Returns outfit: Knight Helmet, Knight Armor, Knight Leggings, Knight Cape, Knight Emblem]

You: change my helmet
Agent: I'll find a new head for you!
[Returns outfit with: Medieval Crown, Knight Armor, Knight Leggings, Knight Cape, Knight Emblem]

You: show me more helmet options
Agent: I'll find more head options for you!
[Returns outfit with: Iron Helmet, Knight Armor, Knight Leggings, Knight Cape, Knight Emblem]

You: show me more helmet options
Agent: I'll find more head options for you!
[Returns outfit with: Royal Knight Helm, Knight Armor, Knight Leggings, Knight Cape, Knight Emblem]
```

## Core Features

### Conversation Management
- **Greetings**: Natural welcome responses
- **Intent Detection**: Understands new outfit vs. replace vs. show more requests
- **Clarifying Questions**: Asks for specifics when requests are ambiguous
- **Session Persistence**: Each user maintains their current outfit across conversations

### Outfit Building
- **New Outfits**: "knight outfit" builds complete 3-5 piece outfits with complementary accessories
- **Slot Replacement**: "change the headgear" updates only that specific slot
- **Show More**: "show me more helmet options" cycles through alternative items for that slot
- **Smart Planning**: Stylist agent chooses appropriate tools and parameters based on style keywords

### Advanced Features
- **Style Recognition**: "medieval", "knight", "ninja", "casual" etc. map to appropriate search parameters
- **Price Filtering**: "under 100 robux", "50-200 robux" etc.
- **Item Cycling**: "Show more" functionality cycles through available options
- **Logging**: Comprehensive logging per request including user_id, agent decisions, tool parameters, and final outfit size

## Project Structure

```
agents/
  config.py                   # Environment configuration + DEV_MODE
  contracts.py               # Pydantic models (API + domain models)
  memory.py                  # Per-user session storage
  param_helpers.py           # Price parsing and style constants
  roblox_catalog_client.py   # HTTP client with mock data support
  roblox_catalog_tool.py     # Core Roblox search function
  tools.py                   # 15 specialized CAMEL FunctionTools
  stylist_agent.py           # Tool planning and parameter mapping
  conversation_agent.py      # CAMEL ChatAgent for dialogue
  orchestrator.py            # Agent coordination and pipeline

server/
  main.py                    # FastAPI application with CORS

scripts/
  chat_cli.py               # Terminal chat interface
```

## Logging

The system provides comprehensive logging for debugging and monitoring:

- **Per /chat request**: user_id, prompt length, agent decision (greet/new_outfit/replace/show_more/clarify)
- **Tool execution**: Parameters used, items returned, outfit slot updates
- **Final results**: Tool names used, final outfit size, success/failure status

Example log output:
```
INFO:agents.orchestrator:Chat request: user_id=123, prompt_length=31
INFO:agents.orchestrator:Agent action: new_outfit, user_id=123
INFO:agents.conversation_agent:Applying plan with 5 steps for action: new_outfit
INFO:agents.conversation_agent:Tool search_hats returned 2 items: [{'assetId': '1001', 'type': 'Head'}, {'assetId': '1004', 'type': 'Head'}]
INFO:agents.orchestrator:Final result: action=new_outfit, tools_used=['search_hats', 'search_shirts', 'search_pants', 'search_back_accessories', 'search_front_accessories'], outfit_size=5, user_id=123
```

## Dependencies

- `fastapi>=0.104.1` - Modern web framework
- `uvicorn[standard]>=0.24.0` - ASGI server with auto-reload
- `httpx>=0.25.0` - Async HTTP client for Roblox catalog API
- `pydantic>=2.8.2` - Data validation and serialization
- `camel-ai>=0.2.0` - Multi-agent conversation framework with tool support
- `python-dotenv>=1.0.0` - Environment variable management

## Development

When `DEV_MODE=true` (default), the system uses mock data instead of calling the real Roblox catalog API. This enables:
- Testing without external dependencies
- Consistent, predictable responses
- Realistic knight-themed outfit data
- Full feature testing including "show more" cycling

## API Documentation

When the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`