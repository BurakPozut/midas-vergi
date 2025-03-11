import os
import sys
from logger import get_logger

# Initialize logger
logger = get_logger('start_api')

def main():
    """
    Script to start the Python API
    """
    logger.info("Starting Python API")
    
    try:
        # Import the Flask app
        from api import app
        
        # Get port from environment variable or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Start the Flask app
        logger.info(f"Starting Flask app on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"Error starting Python API: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 