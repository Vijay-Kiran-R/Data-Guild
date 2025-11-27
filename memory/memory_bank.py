import chromadb
from chromadb.config import Settings
import os
import uuid
from typing import List, Dict, Any

class MemoryBank:
    """
    Manages long-term memory using ChromaDB.
    Stores insights, user preferences, and session summaries.
    """
    def __init__(self, persistence_path: str = "chroma_db"):
        """
        Initialize the MemoryBank.

        Args:
            persistence_path (str): The path to the ChromaDB persistence directory.
        """
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # Collection for Insights (Analysis results)
        self.insights_collection = self.client.get_or_create_collection(name="insights")
        
        # Collection for User Preferences
        self.preferences_collection = self.client.get_or_create_collection(name="user_preferences")
        
        # Collection for Session Summaries (Context Compaction)
        self.summaries_collection = self.client.get_or_create_collection(name="session_summaries")

    def store_insight(self, content: str, metadata: Dict[str, Any] = None):
        """
        Store an analytical insight.

        Args:
            content (str): The insight text.
            metadata (Dict[str, Any], optional): Metadata associated with the insight.
        """
        self.insights_collection.add(
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[str(uuid.uuid4())]
        )

    def retrieve_insights(self, query: str, n_results: int = 5) -> List[str]:
        """
        Retrieve relevant insights.

        Args:
            query (str): The query string.
            n_results (int): The number of results to retrieve.

        Returns:
            List[str]: A list of relevant insights.
        """
        results = self.insights_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]

    def store_preference(self, preference: str):
        """
        Store a user preference.

        Args:
            preference (str): The user preference text.
        """
        self.preferences_collection.add(
            documents=[preference],
            ids=[str(uuid.uuid4())]
        )

    def get_all_preferences(self) -> List[str]:
        """
        Get all user preferences.

        Returns:
            List[str]: A list of all user preferences.
        """
        # Chroma doesn't have a 'get_all' easily without ID, so we query with a generic term or scan
        # For simplicity, we'll just query with "preference"
        results = self.preferences_collection.query(
            query_texts=["preference"],
            n_results=100 
        )
        return results['documents'][0]

    def store_summary(self, summary: str, session_id: str):
        """
        Store a session summary (Context Compaction).

        Args:
            summary (str): The summary text.
            session_id (str): The ID of the session.
        """
        self.summaries_collection.add(
            documents=[summary],
            metadatas=[{"session_id": session_id}],
            ids=[str(uuid.uuid4())]
        )

    def get_session_summary(self, session_id: str) -> str:
        """
        Retrieve summary for a specific session.

        Args:
            session_id (str): The ID of the session.

        Returns:
            str: The session summary, or an empty string if not found.
        """
        results = self.summaries_collection.get(
            where={"session_id": session_id}
        )
        if results['documents']:
            return results['documents'][0]
        return ""
