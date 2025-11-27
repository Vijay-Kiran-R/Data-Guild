import os
import pandas as pd
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("DataGuild-Server")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_storage")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@mcp.tool()
def list_files() -> list[str]:
    """
    List all available data files in the storage directory.

    Returns:
        list[str]: A list of filenames.
    """
    if not os.path.exists(DATA_DIR):
        return []
    return os.listdir(DATA_DIR)

@mcp.tool()
def get_file_metadata(filename: str) -> dict:
    """
    Get metadata for a specific file (columns, types, sample).

    Args:
        filename (str): The name of the file.

    Returns:
        dict: Metadata including columns, data types, and a sample.
    """
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=5)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path, nrows=5)
        else:
            return {"error": "Unsupported file format"}
            
        return {
            "columns": list(df.columns),
            "dtypes": {k: str(v) for k, v in df.dtypes.items()},
            "sample": df.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_full_dataset(filename: str) -> str:
    """
    Read the full dataset. CAUTION: Use with care for large files.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The full dataset as a JSON string, or an error message.
    """
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found"
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return "Unsupported file format"
        
        return df.to_json(orient='records')
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    # In a real scenario, this would run as a separate process
    # For this demo, we might just import the functions directly or run it in background
    mcp.run()
