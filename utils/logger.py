import logging
from rich.logging import RichHandler
from rich.console import Console
import sys

console = Console()

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a rich-formatted logger."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is requested multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True
        )
        
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
