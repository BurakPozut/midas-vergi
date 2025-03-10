import sys
import os
import subprocess
import json
from logger import get_logger

# Initialize logger
logger = get_logger('run_extract_tables')

def main():
    """
    Wrapper script to run extract_tables.py with proper logging
    Usage: python run_extract_tables.py <pdf_path> <user_id>
    """
    logger.info("Starting run_extract_tables.py wrapper")
    
    # Check arguments
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments")
        # print("Usage: python run_extract_tables.py <pdf_path> <user_id>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    user_id = sys.argv[2]
    
    logger.info(f"Running extract_tables.py with PDF: {pdf_path}, User ID: {user_id}")
    
    # Validate PDF path
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        # print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Run the extract_tables.py script
    try:
        # logger.info("Executing extract_tables.py as subprocess")
        
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        extract_tables_path = os.path.join(script_dir, "extract_tables.py")
        
        # Run the script as a subprocess
        process = subprocess.Popen(
            [sys.executable, extract_tables_path, pdf_path, user_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'  # Ensure UTF-8 encoding
        )
        
        # Capture output
        stdout, stderr = process.communicate()
        
        # Log the output
        if stdout:
            logger.info(f"Script stdout: {stdout}")
        
        if stderr:
            logger.error(f"Script stderr: {stderr}")
        
        # Check return code
        if process.returncode != 0:
            logger.error(f"Script failed with return code {process.returncode}")
            result = {
                "success": False,
                "error": stderr or "Unknown error occurred",
                "hasData": False
            }
            # Print only the JSON result for the API to parse
            # print(json.dumps(result, ensure_ascii=False))
            sys.exit(process.returncode)
        
        # Extract the result from extract_tables.py
        # The script should return a JSON object
        try:
            # Try to parse the output as JSON
            result = json.loads(stdout)
            logger.info(f"Parsed JSON result: {result}")
        except json.JSONDecodeError:
            # If parsing fails, create a default result
            logger.warning("Failed to parse JSON from stdout, using default result")
            result = {
                "success": True,
                "message": "İşlem başarıyla tamamlandı, ancak ayrıntılar alınamadı",
                "hasData": False
            }
        
        # Print only the JSON result for the API to parse
        # print(json.dumps(result, ensure_ascii=False))
        logger.info("Script completed successfully")
        
    except Exception as e:
        logger.error(f"Error running extract_tables.py: {str(e)}", exc_info=True)
        result = {
            "success": False,
            "error": str(e),
            "hasData": False
        }
        # Print only the JSON result for the API to parse
        # print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main() 