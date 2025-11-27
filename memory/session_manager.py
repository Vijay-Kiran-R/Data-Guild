from typing import List, Dict, Any
import uuid
import json
import os
from memory.memory_bank import MemoryBank
from memory.file_session_service import FileSessionService

class SessionManager:
    """
    Manages the current user session, state transitions, and interaction history.
    Acts as the bridge between the Orchestrator and the SessionService/MemoryBank.
    """
    def __init__(self, memory_bank: MemoryBank):
        """
        Initialize the SessionManager.

        Args:
            memory_bank (MemoryBank): The memory bank instance.
        """
        self.memory_bank = memory_bank
        self.session_service = FileSessionService()
        self.current_session = self.session_service.create_session()
        self.current_session_id = self.current_session.id
        self.chat_history: List[Dict[str, str]] = []
        self.state = "IDLE" 
        self.context: Dict[str, Any] = {} # Persist variables like filenames
        self.session_name = "Untitled Session"

    def add_message(self, role: str, content: str):
        """
        Adds a message to the chat history.

        Args:
            role (str): The role of the message sender (e.g., "user", "system").
            content (str): The content of the message.
        """
        self.chat_history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        """
        Retrieves the chat history.

        Returns:
            List[Dict[str, str]]: The list of messages in the chat history.
        """
        return self.chat_history

    def set_state(self, new_state: str):
        """
        Updates the session state.

        Args:
            new_state (str): The new state to transition to.
        """
        self.state = new_state
        print(f"State transition: -> {self.state}")

    def save_state(self):
        """
        Saves the current session state to disk.
        """
        # Update session object
        self.current_session.state = {
            "state": self.state,
            "chat_history": self.chat_history,
            "context": self.context,
            "name": getattr(self, "session_name", "Untitled Session")
        }
        self.session_service._save_session(self.current_session)
        print(f"Session saved: {self.current_session.id}")

    def load_state(self, session_id: str = None):
        """
        Loads a session state from disk.

        Args:
            session_id (str, optional): The ID of the session to load. If None, loads the most recent session.

        Returns:
            bool: True if the session was loaded successfully, False otherwise.
        """
        if not session_id:
            # Try to find the last modified session
            sessions = self.session_service.list_sessions()
            if not sessions:
                return False
            # Simple logic: pick the first one for now
            session_id = sessions[0].id
            
        session = self.session_service.get_session(session_id)
        if not session:
            return False
            
        self.current_session = session
        self.current_session_id = session.id
        
        data = session.state
        self.state = data.get("state", "IDLE")
        self.chat_history = data.get("chat_history", [])
        self.context = data.get("context", {})
        self.session_name = data.get("name", "Untitled Session")
        
        print(f"Session loaded: {self.session_name} ({session_id})")
        return True

    def summarize_and_flush(self, summarizer_agent=None):
        """
        Generates a prompt to summarize the current session.

        Args:
            summarizer_agent (optional): Not used in current implementation.

        Returns:
            str: A prompt string for the summarizer.
        """
        # Return prompt for Orchestrator to handle
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history])
        return f"Summarize this data session (issues, cleaning actions, errors):\n{history_text}"

    def flush_with_summary(self, summary: str):
        """
        Stores the session summary and clears the chat history.

        Args:
            summary (str): The summary of the session.
        """
        self.memory_bank.store_summary(summary, self.current_session_id)
        self.chat_history = []
        self.add_message("system", f"Previous Context Summary: {summary}")