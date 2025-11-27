import os
from dotenv import load_dotenv
import itertools

load_dotenv()

class Config:
    """
    Configuration class for the application.
    Handles API keys, model selection, and directory paths.
    """
    _keys_str = os.getenv("GEMINI_API_KEYS", "")
    API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]
    
    # Cycle through keys
    _key_cycle = itertools.cycle(API_KEYS) if API_KEYS else None

    @classmethod
    def get_next_api_key(cls):
        """
        Retrieves the next API key from the cycle.

        Returns:
            str: The next API key, or None if no keys are available.
        """
        if not cls._key_cycle:
            return None
        return next(cls._key_cycle)

    MODEL_FLASH = "gemini-2.5-flash" 
    MODEL_PRO = "gemini-2.5-flash"
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MEMORY_DIR = os.path.join(BASE_DIR, "chroma_db")
    
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

    @classmethod
    def setup_adk_auth(cls):
        """
        Sets the GOOGLE_API_KEY environment variable for Google ADK/GenAI.

        Returns:
            bool: True if the key was set successfully, False otherwise.
        """
        key = cls.get_next_api_key()
        if key:
            os.environ["GOOGLE_API_KEY"] = key
            return True
        return False

config = Config()
# Auto-setup on import
config.setup_adk_auth()
