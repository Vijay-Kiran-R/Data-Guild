import os
import asyncio
from agents.orchestrator import Orchestrator
from memory.session_manager import SessionManager
from memory.memory_bank import MemoryBank
from infrastructure.observability import trace_logger, configure_telemetry
from infrastructure.stream_handler import configure_file_logging
import logging
import warnings
import glob
from datetime import datetime
import shutil
from infrastructure.file_browser import browse_for_file
warnings.simplefilter(action='ignore', category=FutureWarning) 

logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

class Colors:
    """
    ANSI color codes for terminal output formatting.
    """
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """
    Prints a formatted header with the given text.

    Args:
        text (str): The text to display in the header.
    """
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_info(text):
    """
    Prints an informational message.

    Args:
        text (str): The message to display.
    """
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")

def print_success(text):
    """
    Prints a success message.

    Args:
        text (str): The message to display.
    """
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """
    Prints a warning message.

    Args:
        text (str): The message to display.
    """
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """
    Prints an error message.

    Args:
        text (str): The message to display.
    """
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_prompt(text):
    """
    Formats a prompt string.

    Args:
        text (str): The prompt text.

    Returns:
        str: The formatted prompt string.
    """
    return f"{Colors.BOLD}{text}{Colors.ENDC}"

def list_available_datasets():
    """
    Lists all CSV files in the data_storage directory.

    Returns:
        list: A list of paths to available CSV files.
    """
    data_dir = "data_storage"
    if not os.path.exists(data_dir):
        return []
    
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    csv_files = [f for f in csv_files if not os.path.basename(f).startswith("cleaned_")]
    return csv_files

def select_dataset():
    """
    Interactive prompt for selecting a dataset.

    Returns:
        str: The path to the selected dataset, or None if cancelled.
    """
    datasets = list_available_datasets()
    
    if not datasets:
        print_warning("No datasets found in data_storage/")
        print(f"  {Colors.BOLD}[B]{Colors.ENDC} Browse System")
        
        choice = input(print_prompt("\nEnter full path to CSV file (or press Enter to skip, B to browse): "))
        
        if choice.upper() == "B":
            print_info("Opening file browser...")
            selected_file = browse_for_file()
            if selected_file:
                # Copy to data_storage
                dest_dir = "data_storage"
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                
                filename = os.path.basename(selected_file)
                dest_path = os.path.join(dest_dir, filename)
                
                # Handle duplicate names
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = os.path.join(dest_dir, f"{base}_{timestamp}{ext}")
                
                try:
                    shutil.copy2(selected_file, dest_path)
                    print_success(f"File imported to: {dest_path}")
                    return dest_path
                except Exception as e:
                    print_error(f"Failed to copy file: {e}")
                    return None
            return None

        if choice and os.path.exists(choice):
            return choice
        return None
    
    print_info("Available datasets:")
    for i, dataset in enumerate(datasets, 1):
        file_size = os.path.getsize(dataset)
        size_kb = file_size / 1024
        mod_time = datetime.fromtimestamp(os.path.getmtime(dataset)).strftime("%Y-%m-%d %H:%M")
        print(f"  {Colors.BOLD}[{i}]{Colors.ENDC} {os.path.basename(dataset):<30} ({size_kb:.1f} KB, modified: {mod_time})")
    
    print(f"  {Colors.BOLD}[B]{Colors.ENDC} Browse System")
    print(f"  {Colors.BOLD}[0]{Colors.ENDC} Enter custom path")
    
    while True:
        try:
            choice = input(print_prompt("\nSelect dataset [1-{}] (or 0 for custom, B to browse): ".format(len(datasets))))
            if choice.upper() == "B":
                print_info("Opening file browser...")
                selected_file = browse_for_file()
                if selected_file:
                    # Copy to data_storage
                    dest_dir = "data_storage"
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    
                    filename = os.path.basename(selected_file)
                    dest_path = os.path.join(dest_dir, filename)
                    
                    # Handle duplicate names
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest_path = os.path.join(dest_dir, f"{base}_{timestamp}{ext}")
                    
                    try:
                        shutil.copy2(selected_file, dest_path)
                        print_success(f"File imported to: {dest_path}")
                        return dest_path
                    except Exception as e:
                        print_error(f"Failed to copy file: {e}")
                        continue
                else:
                    print_warning("No file selected.")
                    continue

            if choice == "0":
                custom_path = input(print_prompt("Enter full path to CSV file: "))
                if os.path.exists(custom_path):
                    return custom_path
                else:
                    print_error("File not found!")
                    continue
            
            idx = int(choice) - 1
            if 0 <= idx < len(datasets):
                return datasets[idx]
            else:
                print_error(f"Please enter a number between 1 and {len(datasets)}")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            return None

def list_sessions(session_service):
    """
    Lists all available sessions.

    Args:
        session_service: The session service instance.

    Returns:
        list: A list of dictionaries containing session details.
    """
    sessions = session_service.list_sessions()
    if not sessions:
        return []
    
    session_data = []
    for session in sessions:
        filepath = os.path.join("session_storage", f"{session.id}.json")
        if os.path.exists(filepath):
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M")
            state = session.state.get("state", "UNKNOWN") if isinstance(session.state, dict) else "UNKNOWN"
            name = session.state.get("name", "Untitled Session") if isinstance(session.state, dict) else "Untitled Session"
            session_data.append({
                "id": session.id,
                "state": state,
                "modified": mod_time,
                "name": name
            })
    
    return session_data

def select_session(session_service):
    """
    Interactive prompt for selecting a session.

    Args:
        session_service: The session service instance.

    Returns:
        str: The ID of the selected session, or None for a new session.
    """
    sessions = list_sessions(session_service)
    
    if not sessions:
        print_info("No previous sessions found.")
        return None
    
    print_info("Available sessions:")
    for i, session in enumerate(sessions, 1):
        state_color = Colors.GREEN if session['state'] == 'IDLE' else Colors.YELLOW
        print(f"  {Colors.BOLD}[{i}]{Colors.ENDC} {session['name']} (ID: {session['id'][:8]}...) | State: {state_color}{session['state']}{Colors.ENDC} | Modified: {session['modified']}")
    
    print(f"  {Colors.BOLD}[0]{Colors.ENDC} Start new session")
    
    while True:
        try:
            choice = input(print_prompt("\nSelect session [1-{}] (or 0 for new): ".format(len(sessions))))
            if choice == "0":
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                return sessions[idx]['id']
            else:
                print_error(f"Please enter a number between 1 and {len(sessions)}")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            return None

def print_help():
    """
    Prints available commands.
    """
    print_info("Available commands:")
    commands = [
        ("start / <filename.csv>", "Start data processing workflow"),
        ("clean", "Proceed to data cleaning (after ingestion)"),
        ("analyze", "Proceed to analysis (after cleaning)"),
        ("report", "Generate final report (after analysis)"),
        ("reset", "Reset workflow to IDLE state"),
        ("save", "Save current session"),
        ("status", "Show current workflow state"),
        ("help", "Show this help message"),
        ("exit / quit", "Exit the application")
    ]
    for cmd, desc in commands:
        print(f"  {Colors.BOLD}{cmd:<25}{Colors.ENDC} {desc}")

async def main():
    """
    Main entry point for the application.
    Initializes components, handles session management, and processes user input.
    """
    print_header("DataGuild - Autonomous Data Intelligence System")
    
    # Initialize Memory
    memory_bank = MemoryBank()
    session_manager = SessionManager(memory_bank)
    
    # Initialize Orchestrator
    orchestrator = Orchestrator(session_manager)
    
    # Session selection
    print_info("Session Management:")
    selected_session_id = select_session(session_manager.session_service)
    
    if selected_session_id:
        if session_manager.load_state(selected_session_id):
            print_success(f"Resumed session: {session_manager.session_name} ({selected_session_id[:8]}...)")
            print_info(f"Current state: {Colors.BOLD}{session_manager.state}{Colors.ENDC}")
            
            # Re-configure logging for resumed session
            configure_telemetry(selected_session_id)
            configure_file_logging(selected_session_id)
            print_info(f"Logs switched to: logs/agent_logs/{selected_session_id}.log")
            
        else:
            print_error("Failed to load session, starting new one")
            # Configure logging for new session (fallback)
            configure_telemetry(session_manager.current_session_id)
            configure_file_logging(session_manager.current_session_id)
            print_info(f"Logs: logs/agent_logs/{session_manager.current_session_id}.log")
    else:
        print_success("Started new session")
        # Configure logging for new session
        configure_telemetry(session_manager.current_session_id)
        configure_file_logging(session_manager.current_session_id)
        print_info(f"Logs: logs/agent_logs/{session_manager.current_session_id}.log")
    
    print_info(f"Session ID: {Colors.BOLD}{session_manager.current_session_id[:8]}...{Colors.ENDC}")
    print_help()
    print()
    
    while True:
        try:
            # Color-coded prompt based on state
            state_colors = {
                "IDLE": Colors.GREEN,
                "INGESTING": Colors.CYAN,
                "CLEANING": Colors.YELLOW,
                "ANALYZING": Colors.BLUE,
                "REPORTING": Colors.GREEN
            }
            state_color = state_colors.get(session_manager.state, Colors.ENDC)
            
            prompt = f"{state_color}[{session_manager.state}]{Colors.ENDC} {Colors.BOLD}>{Colors.ENDC} "
            user_input = await asyncio.to_thread(input, prompt)
            
            if not user_input.strip():
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit']:
                save = input(print_prompt("Save session before exiting? (y/n): "))
                if save.lower() == 'y':
                    session_manager.save_state()
                    print_success("Session saved!")
                break
            
            elif user_input.lower() == 'save':
                session_manager.save_state()
                print_success(f"Session saved: {session_manager.current_session_id[:8]}...")
                continue
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'status':
                print_info(f"Current State: {Colors.BOLD}{session_manager.state}{Colors.ENDC}")
                if orchestrator.current_file:
                    print_info(f"Current File: {Colors.BOLD}{orchestrator.current_file}{Colors.ENDC}")
                continue
            
            elif user_input.lower() == 'select' or user_input.lower() == 'dataset':
                if session_manager.state == "IDLE":
                    dataset = select_dataset()
                    if dataset:
                        # Pass the selected dataset to the orchestrator as if typed
                        print(f"\n{Colors.CYAN}→{Colors.ENDC} Selected: {dataset}\n")
                        response = await orchestrator.route_request(dataset)
                        print(f"\n{Colors.CYAN}→{Colors.ENDC} {response}\n")
                    else:
                        print_warning("No dataset selected")
                    continue
                else:
                    print_warning("Can only select dataset in IDLE state. Type 'reset' first.")
                    continue

            elif user_input.lower() == 'start':
                if session_manager.state == "IDLE":
                    dataset = select_dataset()
                    if dataset:
                        # Pass the selected dataset to the orchestrator as if typed
                        print(f"\n{Colors.CYAN}→{Colors.ENDC} Selected: {dataset}\n")
                        response = await orchestrator.route_request(dataset)
                        print(f"\n{Colors.CYAN}→{Colors.ENDC} {response}\n")
                    else:
                        print_warning("No dataset selected")
                    continue
            
            print() 
            response = await orchestrator.route_request(user_input)
            print(f"\n{Colors.CYAN}→{Colors.ENDC} {response}\n")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted. Type 'exit' to quit.{Colors.ENDC}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    print(f"\n{Colors.GREEN}Thank you for using DataGuild!{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.ENDC}\n")
