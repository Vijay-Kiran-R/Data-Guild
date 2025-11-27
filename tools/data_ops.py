import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads data from a CSV or Excel file.

    Args:
        filepath (str): The path to the file.

    Returns:
        pd.DataFrame: The loaded DataFrame.

    Raises:
        ValueError: If the file type is not supported.
    """
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file type")

def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Generates summary statistics for the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame.

    Returns:
        dict: The summary statistics.
    """
    return df.describe().to_dict()

def get_correlation_matrix(df: pd.DataFrame) -> dict:
    """
    Calculates the correlation matrix for numeric columns.

    Args:
        df (pd.DataFrame): The DataFrame.

    Returns:
        dict: The correlation matrix.
    """
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=['number'])
    return numeric_df.corr().to_dict()
