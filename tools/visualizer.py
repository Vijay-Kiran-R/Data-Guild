import plotly.express as px
import pandas as pd
import json

def create_histogram(df: pd.DataFrame, column: str):
    """
    Creates a histogram for a specific column.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column to visualize.

    Returns:
        str: The JSON representation of the Plotly figure.
    """
    fig = px.histogram(df, x=column)
    return fig.to_json()

def create_scatter(df: pd.DataFrame, x_col: str, y_col: str):
    """
    Creates a scatter plot for two columns.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        x_col (str): The name of the column for the x-axis.
        y_col (str): The name of the column for the y-axis.

    Returns:
        str: The JSON representation of the Plotly figure.
    """
    fig = px.scatter(df, x=x_col, y=y_col)
    return fig.to_json()

def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str):
    """
    Creates a line chart for two columns.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        x_col (str): The name of the column for the x-axis.
        y_col (str): The name of the column for the y-axis.

    Returns:
        str: The JSON representation of the Plotly figure.
    """
    fig = px.line(df, x=x_col, y=y_col)
    return fig.to_json()
