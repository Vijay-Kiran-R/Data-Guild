import pandas as pd
import io
import sys
from agents.base_agent import BaseAgent
from config import config

class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="QAAgent", model_name=config.MODEL_FLASH)

    async def answer_question(self, question: str, file_path: str) -> str:
        self.log_step("Q&A", f"Analyzing: {question}")
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return f"Error loading data: {e}"

        prompt = f"""
        You are a Data Analyst.
        CONTEXT: Columns: {list(df.columns)}
        Sample: {df.head().to_string()}
        QUESTION: {question}
        
        INSTRUCTIONS:
        1. Check relevance. Is the question related to the dataset?
        2. If IRRELEVANT, output exactly: "I can only answer questions about the dataset."
        3. If RELEVANT, write Python code to answer.
           - Assume 'df' is already loaded.
           - CRITICAL: Print the answer as a COMPLETE SENTENCE.
             (e.g., "The average sales amount is $150.")
           - Wrap code in ```python ... ```
        """
        
        response = await self.generate(prompt)
        
        # --- FIX STARTS HERE ---
        # If the model refuses, return the text directly
        if "only answer questions about the dataset" in response:
            self.log_step("Q&A", "Question deemed irrelevant.")
            return response.replace("```", "").strip()
        # --- FIX ENDS HERE ---

        code = self._extract_code(response)
        if not code: return "Could not generate executable code to answer your question."
        
        self.log_step("Code Gen", code)

        try:
            old_stdout = sys.stdout
            redirected_output = io.StringIO()
            sys.stdout = redirected_output
            local_scope = {'df': df, 'pd': pd}
            exec(code, {}, local_scope)
            sys.stdout = old_stdout
            result = redirected_output.getvalue().strip()
            return result if result else "Code ran but printed nothing."
        except Exception as e:
            sys.stdout = old_stdout
            return f"Error executing code: {e}"

    def _extract_code(self, text: str) -> str:
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return None