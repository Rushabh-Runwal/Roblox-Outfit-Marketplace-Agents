# Roblox Outfit Marketplace Agents

A FastAPI backend powered by CAMEL agents that helps users find Roblox catalog items based on natural language descriptions.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
uvicorn server.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Use Terminal Chat (Optional)

```bash
python scripts/chat_cli.py
```

## API Endpoints

### POST /chat

Chat with the agent to get outfit recommendations with actual Roblox catalog items.

**Request:**
```json
{
  "prompt": "I want a knight outfit",
  "user_id": 7470350941
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 7470350941,
  "reply": "Your knight outfit is ready! I found 6 great items for you.",
  "outfit": [
    {
      "assetId": "505526012",
      "type": "Pants"
    },
    {
      "assetId": "91950361017105", 
      "type": "Back Accessory"
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"I want a futuristic knight outfit","user_id":7470350941}'
```

## Project Structure

```
agents/
  __init__.py                # Package initialization
  contracts.py               # Pydantic models for API contracts
  conversation_agent.py      # CAMEL agent for chat processing
  roblox_catalog_client.py   # Roblox catalog API integration
  light_ranker.py           # Item ranking and diversity logic
  orchestrator.py           # Orchestrates agent interactions

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