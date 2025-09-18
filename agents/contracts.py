"""Pydantic models for API contracts."""
from typing import Optional, List
from pydantic import BaseModel


class OutfitItem(BaseModel):
    """A single outfit item from Roblox catalog."""
    assetId: str
    type: str = "Unknown"


class ChatIn(BaseModel):
    """Input model for chat endpoint."""
    prompt: str
    user_id: int


class ChatOut(BaseModel):
    """Output model for chat endpoint."""
    success: bool
    user_id: int
    reply: str
    outfit: List[OutfitItem]


class IdsOut(BaseModel):
    """Output model for IDs endpoint."""
    success: bool = True
    ids: list[str]