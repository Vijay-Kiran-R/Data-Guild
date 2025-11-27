from agents.base_agent import BaseAgent
from google.adk.agents import Agent
from tools.search_tool import search_tool
import json

class Critic(BaseAgent):
    """
    Agent responsible for critiquing analysis and adding context using external search.
    """
    def __init__(self):
        super().__init__(name="Critic")
        self.agent = Agent(
            model=self.model,
            name="Critic",
            tools=[search_tool],
            instruction="You are a Chief Data Officer and Strategic Storyteller."
        )

    async def evaluate_and_report(self, insights: dict) -> str:
        self.log_step("Critique", "Reviewing insights and searching for context...")
        
        # Extract Schema
        metadata_text = ""
        if "dataset_metadata" in insights:
            meta = insights["dataset_metadata"].get("schema", {})
            metadata_text = f"\nDataset Schema:\n{json.dumps(meta, indent=2)}\n"
        
        # Prepare Findings (Combines Phase 1 and Phase 2 data)
        findings_json = json.dumps(insights.get("findings", {}), indent=2, default=str)

        prompt = f"""
        INPUT DATA (Analysis Findings):
        {findings_json}
        {metadata_text}
        
        TASK: Write a Strategic Data Report for the C-Suite.
        
        INSTRUCTIONS:
        1. **Synthesize**: Combine the 'Initial_Scan' with the 'Deep_Dive_Iter' findings. 
           - Don't just list them separately. If the Deep Dive explained *why* the trend in the Initial Scan happened, tell that story together.
        2. **Grounding**: Use 'google_search' to validate hypotheses (e.g., "Was there a holiday during the spike?").
        3. **Structure (Use Markdown)**:
           - **# Executive Summary**: High-level health check.
           - **## Strategic Deep Dive**: The most important story found by the Lead Analyst (connect the initial finding to the deep dive result).
           - **## Visual Evidence**: Cite specific plots (e.g., "See Figure: Trend_chart.png" or "See Figure: DeepDive_0_Spike.png").
           - **## Operational Recommendations**: 3 specific, actionable business steps.
        
        STYLE: Professional, concise, data-driven. No emojis.
        """
        
        response = await self.generate(prompt)
        self.log_step("Report Generated", "Final report ready.")
        return response