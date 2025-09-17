"""Pydantic models for API contracts."""
from typing import Optional
from pydantic import BaseModel


class KeywordSpec(BaseModel):
    """Specification for outfit keywords and requirements."""
    theme: str
    style: Optional[str] = None
    parts: Optional[list[str]] = None
    color: Optional[str] = None
    budget: Optional[int] = None


class ChatIn(BaseModel):
    """Input model for chat endpoint."""
    prompt: str
    user_id: int


class ChatOut(BaseModel):
    """Output model for chat endpoint."""
    success: bool = True
    user_id: int
    reply: str
    keywordSpec: KeywordSpec


class IdsOut(BaseModel):
    """Output model for IDs endpoint."""
    success: bool = True
    ids: list[str]