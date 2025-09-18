"""Pydantic models for API contracts."""
from typing import Optional, List, Dict
from pydantic import BaseModel


# API I/O
class ChatIn(BaseModel):
    """Input model for chat endpoint."""
    prompt: str
    user_id: int


class OutfitItem(BaseModel):
    """A single outfit item from Roblox catalog."""
    assetId: str
    type: str  # e.g., "Head", "Back Accessory", "Pants"


class ChatOut(BaseModel):
    """Output model for chat endpoint."""
    success: bool
    user_id: int
    reply: str
    outfit: List[OutfitItem]


# Internal domain models
class Outfit(BaseModel):
    """Internal outfit representation with canonical slots."""
    # canonical slot -> assetId
    items: Dict[str, str] = {}  # {"Head":"123", "Pants":"456"}


class SessionState(BaseModel):
    """Per-user session state for outfit building."""
    current_outfit: Outfit = Outfit(items={})
    last_params_by_slot: Dict[str, dict] = {}  # slot -> last tool params used


class IdsOut(BaseModel):
    """Output model for IDs endpoint."""
    success: bool = True
    ids: list[str]