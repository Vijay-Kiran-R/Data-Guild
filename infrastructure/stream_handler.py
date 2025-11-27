import logging
import sys
from datetime import datetime

# ANSI color codes
class Colors:
    """
    ANSI color codes for terminal output.
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
    GREY = '\033[90m'

class StreamHandler(logging.Handler):
    """
    Custom logging handler to stream agent thoughts and actions to the console
    with color coding and formatting.
    """
    def __init__(self):
        """
        Initialize the StreamHandler.
        """
        super().__init__()
        self.formatter = logging.Formatter('%(message)s')

    def emit(self, record):
        """
        Emit a record.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        try:
            msg = self.format(record)
            
            # Determine color based on log level or content
            color = Colors.ENDC
            prefix = ""
            
            if record.levelno == logging.INFO:
                if "STEP:" in msg:
                    color = Colors.CYAN
                    prefix = "⚡ "
                elif "THOUGHT:" in msg:
                    color = Colors.GREY
                    prefix = "🤔 "
                else:
                    color = Colors.GREEN
                    prefix = "ℹ️ "
            elif record.levelno == logging.WARNING:
                color = Colors.YELLOW
                prefix = "⚠️ "
            elif record.levelno == logging.ERROR:
                color = Colors.RED
                prefix = "❌ "
            
            # Format timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Construct final message
            final_msg = f"{Colors.GREY}[{timestamp}]{Colors.ENDC} {color}{prefix}{msg}{Colors.ENDC}"
            
            print(final_msg)
            sys.stdout.flush()
            
        except Exception:
            self.handleError(record)

def get_stream_logger(name: str):
    """
    Get a logger configured with StreamHandler.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
        
    handler = StreamHandler()
    logger.addHandler(handler)
    logger.propagate = False # Prevent propagation to root logger to avoid double printing
    return logger

def configure_file_logging(session_id: str):
    """
    Configure all stream loggers to also write to a file.

    Args:
        session_id (str): The ID of the session.

    Returns:
        logging.FileHandler: The file handler added to the loggers.
    """
    import os
    log_dir = "logs/agent_logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file_path = os.path.join(log_dir, f"{session_id}.log")
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Attach to all existing loggers that use StreamHandler
    # This is a bit tricky since we don't track them. 
    # But we can iterate over logging.Logger.manager.loggerDict
    
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        if isinstance(logger, logging.Logger):
            # Check if it has a StreamHandler (our custom one)
            has_stream_handler = any(isinstance(h, StreamHandler) for h in logger.handlers)
            if has_stream_handler:
                # Remove old FileHandlers to avoid duplicates/wrong files
                for h in logger.handlers[:]:
                    if isinstance(h, logging.FileHandler):
                        logger.removeHandler(h)
                        h.close()
                
                logger.addHandler(file_handler)
                
    # Also return the handler in case we need it for new loggers
    return file_handler
