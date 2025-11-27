from agents.base_agent import BaseAgent
from google.adk.agents import Agent
from tools.search_tool import search_tool
from infrastructure.mcp_server import get_file_metadata
import json
import os

class Steward(BaseAgent):
    """
    Agent responsible for data ingestion and profiling.
    Uses external search to understand data context and quality issues.
    """
    def __init__(self):
        """
        Initialize the Steward agent.
        """
        super().__init__(name="Steward")
        
        # Initialize Agent with the Google Search Tool
        self.agent = Agent(
            model=self.model,
            name="Steward",
            tools=[search_tool], 
            instruction="""
            You are a Data Steward.
            Your Goal: Create a comprehensive Data Profile for a dataset.
            
            Capabilities:
            - You can use the 'google_search' tool to research common data quality issues or schema standards for specific domains.
            """
        )

    async def ingest(self, file_path: str):
        """
        Ingests a file and generates a data profile.

        Args:
            file_path (str): The path to the file to ingest.

        Returns:
            str: The generated data profile.
        """
        self.log_step("Ingestion", f"Reading file: {file_path}")
        
        metadata = get_file_metadata(file_path)
        filename = os.path.basename(file_path)
        
        # Prompt the Agent to use the tool internally
        prompt = f"""
        I have ingested a file named '{filename}'.
        
        Metadata extracted:
        {json.dumps(metadata)}
        
        INSTRUCTIONS:
        1. Use the 'google_search' tool to research common data schema patterns, expected value ranges, and quality issues associated with datasets in this domain (inferred from filename/columns).
        2. Combine search findings with the provided metadata to create a Data Profile.
        
        OUTPUT FORMAT (Markdown):
        ## Data Profile for '{filename}'
        
        ### 1. Domain Context
        [Describe what this data likely represents based on columns and search results]
        
        ### 2. Column Analysis
        [List key columns, their expected types, and what they likely represent]
        
        ### 3. Potential Quality Pitfalls
        [List specific things to watch out for: e.g., "Negative values in Price column", "Inconsistent date formats"]
        """
        
        response = await self.generate(prompt)
        
        self.log_step("Profile Created", "Data Profile generated successfully.")
        return response