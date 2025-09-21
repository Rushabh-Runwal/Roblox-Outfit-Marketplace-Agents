# Roblox Catalog Agent - Docker Usage

> **🚀 Ready to use:** `docker run -it --rm -e OPENAI_API_KEY="your-key" -e CORAL_SERVER_URL="http://host.docker.internal:5556" rushabhrunwal/roblox-catalog-agent:v1.0.1`

## 🐳 Docker Image Available

**Public Docker Hub Repository:** `rushabhrunwal/roblox-catalog-agent`

** **Image Size:** 1.26GB | **Base:** Python 3.11.13

## 📦 Quick Start

### 1. Pull the Image
```bash
# Latest version (recommended)
docker pull rushabhrunwal/roblox-catalog-agent:latest

# Specific versions available:
docker pull rushabhrunwal/roblox-catalog-agent:v1.0.1  
```

### 2. Run the Agent
```bash
docker run -it --rm \
  -e CORAL_SERVER_URL="http://host.docker.internal:5556" \
  -e OPENAI_API_KEY="your-openai-api-key-here" \
  rushabhrunwal/roblox-catalog-agent:v1.0.1
```

### 3. Run with Environment File
Create a `.env` file with your configuration:
```env
OPENAI_API_KEY=your-openai-api-key-here
CORAL_SERVER_URL=http://your-coral-server:5556
MODEL_NAME=gpt-4o-mini
MODEL_TEMPERATURE=0.1
MODEL_MAX_TOKENS=16000
TIMEOUT_MS=60000
```

Then run:
```bash
docker run -it --rm \
  --env-file .env \
  rushabhrunwal/roblox-catalog-agent:v1.0.1
```

## 🔧 Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI processing
- `CORAL_SERVER_URL`: URL to your Coral Protocol server (default: http://localhost:5556)

### Optional Environment Variables
- `MODEL_NAME`: AI model to use (default: "gpt-4o-mini")
- `MODEL_PROVIDER`: Model provider (default: "openai") 
- `MODEL_MAX_TOKENS`: Maximum tokens per request (default: "16000")
- `MODEL_TEMPERATURE`: AI response creativity (default: "0.1")
- `TIMEOUT_MS`: Connection timeout in milliseconds (default: "60000")
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
    image: rushabhrunwal/roblox-catalog-agent:v1.0.1
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CORAL_SERVER_URL=http://coral-server:5556
      - MODEL_NAME=gpt-4o-mini
      - MODEL_TEMPERATURE=0.1
      - MODEL_MAX_TOKENS=16000
    depends_on:
      - coral-server
    restart: unless-stopped
    networks:
      - coral-network

  coral-server:
    # Your Coral server configuration here
    ports:
      - "5556:5556"
    networks:
      - coral-network

networks:
  coral-network:
    driver: bridge
```

## 🆕 Version History

| Version | Released | Changes |
|---------|----------|---------|
| v1.0.1 | 2025-09-21 | Updated configuration, marketplace compliance |

## 📋 Features

This Docker image includes:
- **15 Roblox Catalog Tools**: Complete search functionality for all Roblox catalog categories
- **Coral Protocol Integration**: Full MCP over SSE communication
- **Marketplace Ready**: Compliant with Coral Protocol marketplace standards
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

## 🧪 Testing Your Setup

### Quick Health Check
```bash
# Test Python version
docker run --rm rushabhrunwal/roblox-catalog-agent:v1.0.1 python --version

# Test basic container functionality
docker run --rm rushabhrunwal/roblox-catalog-agent:v1.0.1 ls -la /app

# Test UV package manager
docker run --rm rushabhrunwal/roblox-catalog-agent:v1.0.1 uv --version
```

### Integration Test
```bash
# Start a test run (will fail without valid OPENAI_API_KEY but tests container startup)
docker run --rm \
  -e OPENAI_API_KEY="test-key" \
  -e CORAL_SERVER_URL="http://host.docker.internal:5556" \
  rushabhrunwal/roblox-catalog-agent:v1.0.1
```

### Verify Image Contents
```bash
# Check installed packages
docker run --rm rushabhrunwal/roblox-catalog-agent:v1.0.1 uv pip list

# Inspect the image
docker inspect rushabhrunwal/roblox-catalog-agent:v1.0.1
```

## 🆘 Troubleshooting

### Container Won't Start
- **Invalid API Key**: Check that your `OPENAI_API_KEY` is valid and has sufficient credits
- **Missing Environment Variables**: Ensure both `OPENAI_API_KEY` and `CORAL_SERVER_URL` are set
- **Network Issues**: Verify Docker can access external networks for API calls

### Can't Connect to Coral Server
- **Local Development**: Use `host.docker.internal` instead of `localhost` when running in Docker
- **Port Configuration**: Ensure the Coral server port is correct (default: 5556)  
- **Firewall Settings**: Check that port 5556 is open and accessible
- **Server Status**: Verify Coral server is running: `curl http://localhost:5556/health`

### Performance Issues
- **Memory Limits**: Increase Docker memory allocation if experiencing slowdowns
- **Token Limits**: Adjust `MODEL_MAX_TOKENS` if hitting API limits
- **Timeout Issues**: Increase `TIMEOUT_MS` for slower network connections

### Common Error Messages
```bash
# Error: "runc create failed"
# Solution: Restart Docker Desktop

# Error: "pull access denied"  
# Solution: Use correct image name: rushabhrunwal/roblox-catalog-agent:v1.0.1

# Error: "connection refused"
# Solution: Check CORAL_SERVER_URL and ensure server is running
```

## 📚 Resources

### Documentation
- **Coral Protocol Docs**: https://docs.coralprotocol.org/
- **Docker Hub Page**: https://hub.docker.com/r/rushabhrunwal/roblox-catalog-agent
- **Source Code**: https://github.com/Coral-Protocol/Multi-Agent-Demo

### Support
- **GitHub Issues**: Report bugs and feature requests
- **Docker Logs**: Use `docker logs <container-id>` for debugging
- **Version Check**: Always use the latest version for bug fixes

## 🔄 Building from Source

If you want to build the image yourself:
```bash
git clone https://github.com/Coral-Protocol/Multi-Agent-Demo.git
cd Multi-Agent-Demo/agents/robloxCatalogAgent
docker build -t my-roblox-agent:latest .
```

---

**Last Updated**: September 21, 2025 | **Version**: v1.0.1 | **Maintained by**: rushabhrunwal