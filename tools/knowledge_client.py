import requests
import json

class KnowledgeBaseClient:
    """
    Client for interacting with the corporate Knowledge Base.
    """
    def __init__(self, base_url: str = "https://api.company-kb.com"):
        """
        Initialize the KnowledgeBaseClient.

        Args:
            base_url (str): The base URL of the Knowledge Base API.
        """
        self.base_url = base_url

    def get_schema(self, dataset_id: str) -> dict:
        """
        Fetches the validation schema for a given dataset ID.
        
        In a real scenario, this would make a GET request:
        response = requests.get(f"{self.base_url}/schemas/{dataset_id}")
        return response.json()
        
        For this implementation, we return a mock schema based on the ID.

        Args:
            dataset_id (str): The ID of the dataset.

        Returns:
            dict: The validation schema or an error message.
        """
        # Mock Schema for demonstration
        if "sales" in dataset_id.lower() or "complex" in dataset_id.lower():
            return {
                "dataset_id": dataset_id,
                "required_columns": ["date", "region", "sales_amount", "units_sold"],
                "rules": {
                    "sales_amount": {"type": "float", "min": 0},
                    "units_sold": {"type": "int", "min": 0},
                    "customer_rating": {"type": "float", "min": 1.0, "max": 5.0},
                    "region": {"type": "enum", "values": ["North", "South", "East", "West"]}
                },
                "description": "Standard Sales Data Schema v1.0"
            }
        else:
            return {"error": "Schema not found"}

# Global instance
kb_client = KnowledgeBaseClient()
