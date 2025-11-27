from google.adk.sessions import BaseSessionService, Session, State
import json
import os
from typing import Optional, List, Dict, Any

class FileSessionService(BaseSessionService):
    """
    A file-based implementation of the SessionService.
    Stores session data as JSON files in a specified directory.
    """
    def __init__(self, storage_dir: str = "session_storage"):
        """
        Initialize the FileSessionService.

        Args:
            storage_dir (str): The directory to store session files.
        """
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def create_session(self, session_id: str = None) -> Session:
        """
        Creates a new session.

        Args:
            session_id (str, optional): The ID for the new session. If None, a UUID is generated.

        Returns:
            Session: The created session object.
        """
        import uuid
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = Session(id=session_id, app_name="DataAgent", user_id="user", state={})
        self._save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieves a session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            Optional[Session]: The session object, or None if not found.
        """
        return self._load_session(session_id)

    def list_sessions(self) -> List[Session]:
        """
        Lists all available sessions.

        Returns:
            List[Session]: A list of all session objects.
        """
        sessions = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                session_id = filename.replace(".json", "")
                session = self._load_session(session_id)
                if session:
                    sessions.append(session)
        return sessions

    def delete_session(self, session_id: str) -> None:
        """
        Deletes a session by its ID.

        Args:
            session_id (str): The ID of the session to delete.
        """
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)

    def _save_session(self, session: Session) -> None:
        """
        Saves a session to disk.

        Args:
            session (Session): The session object to save.
        """
        filepath = os.path.join(self.storage_dir, f"{session.id}.json")
        data = {
            "session_id": session.id,
            "appName": session.app_name,
            "userId": session.user_id,
            "state": session.state,
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, default=str)

    def _load_session(self, session_id: str) -> Optional[Session]:
        """
        Loads a session from disk.

        Args:
            session_id (str): The ID of the session to load.

        Returns:
            Optional[Session]: The loaded session object, or None if it fails.
        """
        filepath = os.path.join(self.storage_dir, f"{session_id}.json")
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct Session object
            session = Session(
                id=data["session_id"],
                app_name=data.get("appName", "DataAgent"),
                user_id=data.get("userId", "user"),
                state=data.get("state", {})
            ) 
            return session
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
