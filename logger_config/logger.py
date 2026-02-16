import logging
import sys

def configure_logging(level=logging.DEBUG):
    """
    Configure the root logger with a standard format.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG, logging.ERROR)
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name):
    """
    Get a logger instance for the given module name.
    
    Args:
        name: Usually __name__ from the calling module
        
    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)
