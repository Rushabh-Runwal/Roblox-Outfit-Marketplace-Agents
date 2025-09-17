"""FastAPI main application."""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.contracts import ChatIn, ChatOut, KeywordSpec, IdsOut

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Roblox Outfit Marketplace Agents",
    description="CAMEL agents for Roblox outfit recommendations",
    version="1.0.0"
)

# Configure CORS for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
        # TODO: Implement orchestrator.chat() in Issue 4
        # For now, return a placeholder response
        keyword_spec = KeywordSpec(
            theme="placeholder",
            style="temporary",
            parts=["Head", "Shirt", "Pants"],
            color="blue",
            budget=1000
        )
        
        return ChatOut(
            success=True,
            user_id=chat_input.user_id,
            reply="Chat endpoint is not yet implemented. Please wait for Issue 4.",
            keywordSpec=keyword_spec
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/keywords-to-ids", response_model=IdsOut)
async def keywords_to_ids(keyword_spec: KeywordSpec) -> IdsOut:
    """Convert KeywordSpec to Roblox catalog item IDs."""
    try:
        # TODO: Implement orchestrator.keywords_to_ids() in Issue 4
        # For now, return a placeholder response
        return IdsOut(
            success=True,
            ids=["placeholder_id_1", "placeholder_id_2"]
        )
    except Exception as e:
        logger.error(f"Error in keywords-to-ids endpoint: {e}")
        # Return 502 on Firecrawl failure as specified
        raise HTTPException(status_code=502, detail={"success": False, "message": "firecrawl_error"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)