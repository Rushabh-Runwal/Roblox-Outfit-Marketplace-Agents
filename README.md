# Roblox Catalog Agent

A Coral Protocol agent that can search and retrieve items from the Roblox Catalog API for outfit creation and customization.

## Features

This agent provides comprehensive access to the Roblox Catalog through the following tools:

### Multi-Part Tools
- **fetch_outfit**: Retrieve multiple outfit parts at once with theme-based filtering

### Individual Part Tools
- **fetch_headgear**: Hats, helmets, and head accessories
- **fetch_face**: Faces, masks, and face accessories
- **fetch_hair**: Hair accessories and styles
- **fetch_shirt**: Shirts and classic shirts
- **fetch_tshirt**: T-shirts and classic t-shirts
- **fetch_pants**: Pants and classic pants
- **fetch_back_accessory**: Capes, wings, jetpacks, and backpacks
- **fetch_neck_accessory**: Scarves, necklaces, and neck accessories
- **fetch_shoulder_accessory**: Pauldrons and shoulder accessories
- **fetch_front_accessory**: Chest plates, armor, and front accessories
- **fetch_waist_accessory**: Belts, tails, and waist accessories
- **fetch_head_bodypart**: Head body parts and dynamic heads
- **fetch_bundle**: Complete outfit bundles
- **fetch_emote**: Emote animations

## API Integration

The agent interfaces with the Roblox Catalog API at `https://catalog.roblox.com/v1/search/items/details` using the following parameters:

- **Category**: Item categories (Clothing, BodyParts, Gear, Accessories, AvatarAnimations)
- **Subcategory**: Specific item types (Hats, Shirts, Pants, etc.)
- **Keyword**: Free text search for themes and styles
- **MinPrice/MaxPrice**: Price filtering
- **Limit**: Always set to 10 for consistent results

## Usage Examples

### Basic Outfit Request
```
"I want a knight outfit"
```
→ Uses `fetch_outfit` with parts ["Head","Shirt","Pants","Back Accessory"] and keyword "knight"

### Specific Item Type
```
"Show me futuristic helmets"
```
→ Uses `fetch_headgear` with keyword "futuristic"

### Themed Accessories
```
"Find me pirate accessories for my back"
```
→ Uses `fetch_back_accessory` with keyword "pirate"

## Response Format

All tools return items in the following format:
```json
[
  {
    "assetId": "string-id",
    "type": "Head"
  }
]
```

## Configuration

The agent requires the following environment variables:

- `MODEL_API_KEY`: API key for the LLM provider
- `MODEL_NAME`: Model to use (default: "gpt-4o")
- `MODEL_PROVIDER`: LLM provider (default: "openai")
- `MODEL_TEMPERATURE`: Model temperature (default: "0.1")
- `MODEL_MAX_TOKENS`: Maximum tokens (default: "8000")
- `CORAL_CONNECTION_URL`: URL to connect to the Coral server
- `CORAL_AGENT_ID`: Agent ID for Coral server communication

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Set up environment variables in `.env` file

3. Run the agent:
```bash
./run_agent.sh
```

## Docker Support

Build and run with Docker:
```bash
docker build -t roblox-catalog-agent .
docker run --env-file .env roblox-catalog-agent
```

## Development

The agent follows the Coral Protocol agent pattern:
1. Waits for mentions from other agents
2. Parses the request to understand catalog needs
3. Calls appropriate Roblox API tools
4. Returns formatted results to the requesting agent

## Limitations

- Maximum 10 items returned per tool call
- Relies on Roblox Catalog API availability
- No authentication required for public catalog access
- Results limited to publicly available catalog items