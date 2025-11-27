import tkinter as tk
from tkinter import filedialog
import os

def browse_for_file(file_types=None):
    """
    Opens a system file dialog to select a file.
    
    Args:
        file_types (list): List of tuples for file filters, e.g., [("CSV files", "*.csv"), ("All files", "*.*")]
                           Defaults to CSV files and All files.
                           
    Returns:
        str: The absolute path to the selected file, or None if cancelled.
    """
    if file_types is None:
        file_types = [("CSV files", "*.csv"), ("All files", "*.*")]
        
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()
    
    # Make sure it's on top
    root.attributes('-topmost', True)
    
    try:
        file_path = filedialog.askopenfilename(
            title="Select a Dataset",
            filetypes=file_types
        )
        return file_path if file_path else None
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        return None
    finally:
        root.destroy()
