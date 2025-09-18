"""FastAPI main application."""
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.contracts import ChatIn, ChatOut

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Roblox Outfit Marketplace Agents",
    description="CAMEL agents for Roblox outfit recommendations",
    version="1.0.0"
)

# Configure CORS for localhost development (any port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Roblox Outfit Marketplace Agents API"}


@app.post("/chat", response_model=ChatOut)
async def chat(chat_input: ChatIn) -> ChatOut:
    """Chat endpoint to process user prompts and return outfit recommendations."""
    try:
        from agents.orchestrator import chat as orchestrator_chat
        return await orchestrator_chat(chat_input.prompt, chat_input.user_id)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)