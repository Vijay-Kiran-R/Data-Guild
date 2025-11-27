from agents.base_agent import BaseAgent
from tools.knowledge_client import kb_client
from google.adk.agents import Agent
import pandas as pd
import os
import traceback
import json
from pydantic import BaseModel, Field

class CleaningPlan(BaseModel):
    """
    Structure for the data cleaning plan.
    """
    explanation: str = Field(..., description="Summary of cleaning.")
    code: str = Field(..., description="Executable Python code.")

class Refinery(BaseAgent):
    """
    Agent responsible for cleaning and refining data.
    Uses a knowledge base to infer schemas and generates cleaning code.
    """
    def __init__(self):
        """
        Initialize the Refinery agent.
        """
        super().__init__(name="Refinery")
        self.agent = Agent(
            model=self.model,
            name="Refinery",
            instruction="You are a Data Engineer. Generate Python code to clean the dataframe 'df'. Return valid JSON."
        )

    async def clean_data(self, dataset_path: str) -> str:
        """
        Cleans the data at the given path.

        Args:
            dataset_path (str): The path to the dataset file.

        Returns:
            str: The path to the cleaned dataset file, or an error message.
        """
        self.log_step("Start Cleaning", f"Cleaning {dataset_path}")
        try:
            df = pd.read_csv(dataset_path)
        except Exception as e:
            return f"Error: Failed to load data: {e}"

        dataset_id = os.path.basename(dataset_path).split('.')[0]
        
        try:
            schema = kb_client.get_schema(dataset_id)
        except:
            schema = "Infer from data."

        audit_report = f"Nulls: {df.isnull().sum().to_dict()}"
        
        prompt = f"""
        You are a generic Data Cleaning expert.
        
        TASK: Generate a cleaning plan and executable Python code for the dataframe 'df'.
        
        CONTEXT: 
        - Audit: {audit_report}
        - Schema: {schema}
        - Columns: {list(df.columns)}
        
        INSTRUCTIONS:
        1. Analyze the Audit and Schema to identify issues (nulls, data type mismatches, outliers).
        2. Write robust Pandas code to fix these issues. 
           - Assume 'df' is already loaded.
           - Use `inplace=True` or reassign `df` (e.g., `df = df.dropna()`).
           - Handle edge cases (e.g., check if column exists before dropping).
        3. Output a VALID JSON object with two keys: 'explanation' and 'code'.
        
        EXAMPLE OUTPUT FORMAT:
        {{
            "explanation": "Imputed missing values in 'age' with median and converted 'date' to datetime.",
            "code": "df['age'].fillna(df['age'].median(), inplace=True)\\ndf['date'] = pd.to_datetime(df['date'])"
        }}
        
        CRITICAL: Return ONLY the JSON object. Do not add markdown formatting or extra text.
        """
        
        response_text = await self.generate(prompt)
        
        try:
            clean_json = self._clean_json_string(response_text)
            plan = CleaningPlan.model_validate_json(clean_json)
            self.log_step("Plan Generated", plan.explanation)
            
            local_scope = {'df': df, 'pd': pd, 'np': __import__('numpy')}
            exec(plan.code, local_scope)
            
            cleaned_filename = f"cleaned_{os.path.basename(dataset_path)}"
            storage_dir = os.path.dirname(dataset_path) or "data_storage"
            if not os.path.exists(storage_dir): os.makedirs(storage_dir)
            
            cleaned_path = os.path.join(storage_dir, cleaned_filename)
            local_scope['df'].to_csv(cleaned_path, index=False)
            
            self.log_step("Success", f"Cleaned data saved to {cleaned_path}")
            return cleaned_path

        except Exception as e:
            self.logger.error(f"Cleaning failed: {e}")
            return f"Error during cleaning: {e}"

    def _clean_json_string(self, text):
        """
        Cleans a string to extract a valid JSON object.

        Args:
            text (str): The string containing JSON.

        Returns:
            str: The cleaned JSON string.
        """
        text = text.strip()
        start = text.find('{')
        end = text.rfind('}')
        return text[start:end+1] if start != -1 and end != -1 else text