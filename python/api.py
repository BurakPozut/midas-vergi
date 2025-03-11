from flask import Flask, request, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from extract_tables import extract_tables_and_save
from logger import get_logger
import json

# Initialize logger
logger = get_logger('python_api')

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/extract-tables', methods=['POST'])
def extract_tables():
    logger.info("Received extract-tables request")
    
    # Check if user_id is provided
    if 'user_id' not in request.form:
        logger.error("No user_id provided")
        return jsonify({
            "success": False,
            "error": "user_id is required",
            "hasData": False
        }), 400
    
    # Check if file is provided
    if 'file' not in request.files:
        logger.error("No file provided")
        return jsonify({
            "success": False,
            "error": "PDF dosyası yüklenmedi",
            "hasData": False
        }), 400
    
    file = request.files['file']
    user_id = request.form['user_id']
    
    # Check if filename is empty
    if file.filename == '':
        logger.error("Empty filename")
        return jsonify({
            "success": False,
            "error": "Dosya seçilmedi",
            "hasData": False
        }), 400
    
    # Check if file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        logger.error("File is not a PDF")
        return jsonify({
            "success": False,
            "error": "PDF dosyası değil",
            "hasData": False
        }), 400
    
    try:
        # Create user directory if it doesn't exist
        user_upload_dir = os.path.join(UPLOAD_FOLDER, user_id)
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save the file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_upload_dir, filename)
        file.save(file_path)
        
        logger.info(f"File saved at {file_path}, processing...")
        
        # Process the file
        result = extract_tables_and_save(file_path, user_id)
        
        # Clean up the file after processing
        try:
            os.remove(file_path)
            # Try to remove the directory if empty
            if not os.listdir(user_upload_dir):
                os.rmdir(user_upload_dir)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Dosya işleme hatası: {str(e)}",
            "hasData": False
        }), 500

@app.route('/process-file', methods=['POST'])
def process_file():
    logger.info("Received process-file request")
    
    # Get request data
    data = request.json
    
    # Check if file_path and user_id are provided
    if not data or 'file_path' not in data or 'user_id' not in data:
        logger.error("Missing required parameters")
        return jsonify({
            "success": False,
            "error": "file_path and user_id are required",
            "hasData": False
        }), 400
    
    file_path = data['file_path']
    user_id = data['user_id']
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return jsonify({
            "success": False,
            "error": f"Dosya bulunamadı: {file_path}",
            "hasData": False
        }), 404
    
    # Check if file is a PDF
    if not file_path.lower().endswith('.pdf'):
        logger.error("File is not a PDF")
        return jsonify({
            "success": False,
            "error": "PDF dosyası değil",
            "hasData": False
        }), 400
    
    try:
        logger.info(f"Processing file: {file_path} for user: {user_id}")
        
        # Process the file
        result = extract_tables_and_save(file_path, user_id)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Dosya işleme hatası: {str(e)}",
            "hasData": False
        }), 500

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False) 