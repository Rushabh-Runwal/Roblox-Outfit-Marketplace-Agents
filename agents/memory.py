"""In-memory user session storage."""
from typing import Dict
from agents.contracts import SessionState

USER_SESSIONS: Dict[int, SessionState] = {}

def get_session(user_id: int) -> SessionState:
    """Get or create a session for the given user ID."""
    if user_id not in USER_SESSIONS:
        USER_SESSIONS[user_id] = SessionState()
    return USER_SESSIONS[user_id]