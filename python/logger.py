import logging
import os
import sys
import codecs
import io
import time
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Define log categories
LOG_CATEGORIES = {
    'extract_tables': 'pdf_processing',
    'run_extract_tables': 'pdf_processing',
    'test_pdf_processing': 'pdf_processing',
    'db_connection': 'database',
    'test_logging': 'system',
    'default': 'system'
}

# Configure the logger
def setup_logger(name='python_script'):
    """Set up and return a logger that writes to a categorized log file and stdout"""
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Determine the category for this logger
    category = LOG_CATEGORIES.get(name, 'default')
    
    # Create file handler with rotation
    log_filename = f"{category}.log"
    file_path = os.path.join(logs_dir, log_filename)
    
    # Use RotatingFileHandler to limit file size and keep backups
    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=10*1024*1024,  # 10MB max file size
        backupCount=5,          # Keep 5 backup files
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler with proper encoding for Windows
    if sys.platform == 'win32':
        # On Windows, use utf-8 encoding for console output
        try:
            # Try to use utf-8 for console output
            sys.stdout.reconfigure(encoding='utf-8')
            console_handler = logging.StreamHandler(sys.stdout)
        except (AttributeError, io.UnsupportedOperation):
            # For older Python versions or when reconfigure is not available
            console_stream = codecs.getwriter('utf-8')(sys.stdout.buffer)
            console_handler = logging.StreamHandler(console_stream)
    else:
        # On other platforms, use default
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatter with process ID and thread ID
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [PID:%(process)d] - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup information
    logger.info(f"Logger initialized for {name} (category: {category})")
    
    return logger

# Function to get the logger for a specific module
def get_logger(module_name):
    """Get a logger for a specific module"""
    return setup_logger(module_name) 