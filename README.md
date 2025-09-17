# Roblox Outfit Marketplace Agents

A FastAPI backend powered by CAMEL agents that helps users find Roblox catalog items based on natural language descriptions.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the Server

```bash
uvicorn server.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /chat

Chat with the agent to get outfit recommendations.

**Request:**
```json
{
  "prompt": "I want a futuristic knight outfit",
  "user_id": 7470350941
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 7470350941,
  "reply": "I found some great futuristic knight options! Would you like me to search for specific parts?",
  "keywordSpec": {
    "theme": "knight",
    "style": "futuristic",
    "parts": ["Back Accessory"],
    "color": null,
    "budget": null
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"I want a futuristic knight outfit","user_id":7470350941}'
```

### POST /keywords-to-ids

Convert keyword specifications to Roblox catalog item IDs.

**Request:**
```json
{
  "theme": "knight",
  "style": "futuristic",
  "parts": ["Back Accessory"]
}
```

**Response:**
```json
{
  "success": true,
  "ids": ["91950361017105", "505526012", "..."]
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/keywords-to-ids" \
  -H "Content-Type: application/json" \
  -d '{"theme":"knight","style":"futuristic","parts":["Back Accessory"]}'
```

## Project Structure

```
agents/
  __init__.py              # Package initialization
  contracts.py             # Pydantic models for API contracts
  conversation_agent.py    # CAMEL agent for chat processing
  firecrawl_agent.py      # Firecrawl integration for web scraping
  orchestrator.py         # Orchestrates agent interactions

server/
  __init__.py             # Package initialization
  main.py                 # FastAPI application and endpoints
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