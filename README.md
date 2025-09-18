# Roblox Outfit Marketplace Agents

A FastAPI backend powered by CAMEL agents that helps users find Roblox catalog items based on natural language descriptions. The system uses intelligent parameter detection and the Roblox Catalog API to provide relevant outfit recommendations.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup (Optional)

For enhanced AI capabilities, create a `.env` file:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Without an API key, the system uses fallback rule-based parsing.

### 3. Run the Server

```bash
uvicorn server.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Use Terminal Chat (Optional)

```bash
python scripts/chat_cli.py
```

## API Endpoints

### POST /chat

Chat with the agent to get outfit recommendations with actual Roblox catalog items.

**Request:**
```json
{
  "prompt": "I want a medieval knight outfit under 200 robux",
  "user_id": 7470350941
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 7470350941,
  "reply": "Great! I found 5 items that match your request.",
  "outfit": [
    {
      "assetId": "505526012",
      "type": "Pants"
    },
    {
      "assetId": "91950361017105", 
      "type": "Back Accessory"
    },
    {
      "assetId": "123456789",
      "type": "Hat"
    }
  ]
}
```

**Features:**
- Intelligent parameter detection (price ranges, item types, genres)
- Conversation memory (say "more" for additional items)
- Clarifying questions when requests are ambiguous
- Up to 10 items per response

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"I want a futuristic knight outfit","user_id":7470350941}'
```

**Note:** The backend only returns Roblox asset IDs and types. Actual purchases happen in-game through the official Roblox platform.

## Project Structure

```
agents/
  __init__.py                # Package initialization
  contracts.py               # Pydantic models for API contracts
  conversation_agent.py      # CAMEL agent for chat processing and tool decisions
  roblox_catalog_tool.py     # Roblox catalog API integration
  param_helpers.py           # Price parsing and item type detection
  orchestrator.py            # Orchestrates agent interactions

server/
  __init__.py               # Package initialization
  main.py                   # FastAPI application and endpoints

scripts/
  chat_cli.py              # Terminal chat interface
```

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - HTTP client for external APIs
- `pydantic` - Data validation and serialization
- `camel-ai` - Multi-agent conversation framework
- `python-dotenv` - Environment variable management

## API Documentation

When the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`