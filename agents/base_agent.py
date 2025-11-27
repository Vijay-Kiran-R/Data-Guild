import os
import logging
from google.adk import Agent, Runner
from google.adk.models import Gemini
from google.adk.sessions import InMemorySessionService
from config import config
from infrastructure.stream_handler import get_stream_logger

class SimplePart:
    """
    Represents a simple text part of a message.
    """
    def __init__(self, text):
        self.text = text

class SimpleMessage:
    """
    Represents a simple message with a role and content.
    """
    def __init__(self, role, content):
        self.role = role
        self.parts = [SimplePart(content)]

class BaseAgent:
    """
    Base class for all agents in the system.
    Wraps the Google ADK Agent and provides common functionality.
    """
    def __init__(self, name: str, model_name: str = config.MODEL_FLASH, system_instruction: str = None):
        """
        Initialize the BaseAgent.

        Args:
            name (str): The name of the agent.
            model_name (str): The model to use (default: config.MODEL_FLASH).
            system_instruction (str): The system instruction for the agent.
        """
        self.name = name
        self.logger = get_stream_logger(name)
        self.model_name = model_name
        
        self.model = Gemini(model=model_name)
        
        valid_instruction = system_instruction if system_instruction else f"You are the {name} agent."
        
        self.agent = Agent(
            model=self.model, 
            name=name, 
            instruction=valid_instruction 
        )
        
        self.logger.info(f"Initialized ADK Agent: {name}")

    def log_step(self, step_name: str, details: str):
        """
        Logs a step in the agent's execution.

        Args:
            step_name (str): The name of the step.
            details (str): Details about the step.
        """
        self.logger.info(f"STEP: {step_name} | {details}")

    async def generate(self, prompt: str, system_instruction: str = None, tools: list = None):
        """
        Generates content using the ADK Runner.

        Args:
            prompt (str): The user prompt.
            system_instruction (str): Optional system instruction override.
            tools (list): Optional list of tools to use.

        Returns:
            str: The generated response text.
        """
        import time
        start_time = time.time()
        
        # Create a new ephemeral session for each generation request
        session_service = InMemorySessionService()
        import uuid
        session_id = str(uuid.uuid4())
        await session_service.create_session(app_name="DataGuild", user_id="user", session_id=session_id)

        runner = Runner(agent=self.agent, session_service=session_service, app_name="DataGuild")

        response_text = ""
        try:
            message = SimpleMessage(role="user", content=prompt)
            
            # Execute the runner and collect text from events
            for event in runner.run(user_id="user", session_id=session_id, new_message=message):
                if hasattr(event, 'text') and event.text:
                     response_text += event.text
                elif hasattr(event, 'part') and hasattr(event.part, 'text') and event.part.text:
                     response_text += event.part.text
            
            # Fallback: If no text was collected from events, inspect the session history
            if not response_text.strip():
                session = await session_service.get_session(session_id=session_id, app_name="DataGuild", user_id="user")
                if hasattr(session, 'events') and session.events:
                    for event in reversed(session.events):
                        if hasattr(event, 'content') and hasattr(event.content, 'role') and event.content.role == 'model':
                            if hasattr(event.content, 'parts'):
                                text_parts = [
                                    p.text for p in event.content.parts 
                                    if hasattr(p, 'text') and p.text is not None
                                ]
                                if text_parts:
                                    response_text = "".join(text_parts)
                                    break

        except Exception as e:
            self.logger.error(f"ADK Execution Error: {e}")
            return f"Error: {e}"

        self.logger.info(f"Thinking: {response_text[:500]}..." if len(response_text) > 500 else f"Thinking: {response_text}")
        return response_text