# Roblox Catalog Agent - Docker Usage

## 🐳 Docker Image Available

**Public Docker Hub Repository:** `rushabhrunwal/roblox-catalog-agent`

## 📦 Quick Start

### 1. Pull the Image
```bash
docker pull rushabhrunwal/roblox-catalog-agent:latest
# Or specific version:
docker pull rushabhrunwal/roblox-catalog-agent:v1.0.0
```

### 2. Run the Agent
```bash
docker run -it --rm \
  -e CORAL_SERVER_URL="http://host.docker.internal:5556" \
  -e OPENAI_API_KEY="your-openai-api-key-here" \
  rushabhrunwal/roblox-catalog-agent:latest
```

### 3. Run with Environment File
Create a `.env` file with your configuration:
```env
OPENAI_API_KEY=your-openai-api-key-here
CORAL_SERVER_URL=http://your-coral-server:5556
```

Then run:
```bash
docker run -it --rm \
  --env-file .env \
  rushabhrunwal/roblox-catalog-agent:latest
```

## 🔧 Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI processing
- `CORAL_SERVER_URL`: URL to your Coral Protocol server (default: http://localhost:5556)

### Optional Environment Variables
- `PYTHONUNBUFFERED=1`: Already set in the image for better logging
- `PYTHONPATH=/app`: Already set in the image

## 🌐 Network Configuration

### For Local Development
Use `host.docker.internal` to connect to services running on your host machine:
```bash
-e CORAL_SERVER_URL="http://host.docker.internal:5556"
```

### For Production
Use the actual hostname or IP of your Coral server:
```bash
-e CORAL_SERVER_URL="http://coral-server:5556"
```

## 🚀 Docker Compose Example

```yaml
version: '3.8'
services:
  roblox-agent:
    image: rushabhrunwal/roblox-catalog-agent:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CORAL_SERVER_URL=http://coral-server:5556
    depends_on:
      - coral-server
    restart: unless-stopped

  coral-server:
    # Your Coral server configuration here
    ports:
      - "5556:5556"
```

## 📋 Features

This Docker image includes:
- **15 Roblox Catalog Tools**: Complete search functionality for all Roblox catalog categories
- **Coral Protocol Integration**: Full MCP over SSE communication
- **Security**: Runs as non-root user for better security
- **Optimized**: Uses UV for fast dependency management
- **Production Ready**: Proper logging and error handling

## 🔍 Roblox Catalog Tools Included

### Clothing
- `fetch_shirt` - Search for shirts
- `fetch_tshirt` - Search for t-shirts  
- `fetch_pants` - Search for pants

### Accessories
- `fetch_headgear` - Hats, helmets, etc.
- `fetch_face` - Face accessories
- `fetch_hair` - Hair accessories
- `fetch_back_accessory` - Back accessories
- `fetch_neck_accessory` - Neck accessories
- `fetch_shoulder_accessory` - Shoulder accessories
- `fetch_front_accessory` - Front accessories
- `fetch_waist_accessory` - Waist accessories

### Body & Other
- `fetch_head_bodypart` - Head body parts
- `fetch_bundle` - Item bundles
- `fetch_emote` - Emotes and animations
- `fetch_outfit` - Complete outfits

## 🆘 Troubleshooting

### Container Won't Start
- Check that your OPENAI_API_KEY is valid
- Ensure Coral server is running and accessible
- Check network connectivity between containers

### Can't Connect to Coral Server
- For local development, use `host.docker.internal` instead of `localhost`
- Ensure the Coral server port is correct (default: 5556)
- Check firewall settings

### Getting the Source Code
The source code is available at: https://github.com/Coral-Protocol/Multi-Agent-Demo