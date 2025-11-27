from typing import Dict, Any, List
from pydantic import BaseModel

class AgentCard(BaseModel):
    """
    Represents the metadata and configuration for an agent.
    """
    name: str
    role: str
    capabilities: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    module_path: str
    class_name: str

class A2ARegistry:
    """
    Registry for managing and retrieving agent definitions.
    """
    def __init__(self):
        """
        Initialize the registry.
        """
        self.agents = {}

    def register_agent(self, card: AgentCard):
        """
        Registers a new agent.

        Args:
            card (AgentCard): The agent card to register.
        """
        self.agents[card.name] = card

    def get_agent(self, name: str) -> AgentCard:
        """
        Retrieves an agent card by name.

        Args:
            name (str): The name of the agent.

        Returns:
            AgentCard: The agent card, or None if not found.
        """
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """
        Lists the names of all registered agents.

        Returns:
            List[str]: A list of agent names.
        """
        return list(self.agents.keys())

# Global Registry
registry = A2ARegistry()

# Define Agent Cards
steward_card = AgentCard(
    name="Steward",
    role="Data Ingestion & Privacy",
    capabilities=["ingest_file", "extract_metadata"],
    input_schema={"filename": "str"},
    output_schema={"metadata": "dict", "status": "str"},
    module_path="agents.steward",
    class_name="Steward"
)

refinery_card = AgentCard(
    name="Refinery",
    role="Data Cleaning",
    capabilities=["audit_data", "clean_data", "verify_quality"],
    input_schema={"dataset_id": "str"},
    output_schema={"cleaned_dataset_id": "str", "quality_report": "dict"},
    module_path="agents.refinery",
    class_name="Refinery"
)

analyst_card = AgentCard(
    name="AnalystSquad",
    role="Data Analysis",
    capabilities=["univariate_analysis", "bivariate_analysis", "trend_analysis"],
    input_schema={"dataset_id": "str", "analysis_type": "str"},
    output_schema={"insights": "list"},
    module_path="agents.analyst_squad",
    class_name="AnalystSquad"
)

critic_card = AgentCard(
    name="Critic",
    role="Evaluation & Reporting",
    capabilities=["evaluate_insights", "generate_report"],
    input_schema={"insights": "list"},
    output_schema={"final_report": "str", "score": "float"},
    module_path="agents.critic",
    class_name="Critic"
)

qa_card = AgentCard(
    name="QAAgent",
    role="Ad-hoc Q&A",
    capabilities=["answer_question"],
    input_schema={"question": "str", "file_path": "str"},
    output_schema={"answer": "str"},
    module_path="agents.qa_agent",
    class_name="QAAgent"
)

# Register all agents
registry.register_agent(steward_card)
registry.register_agent(refinery_card)
registry.register_agent(analyst_card)
registry.register_agent(critic_card)
registry.register_agent(qa_card)
