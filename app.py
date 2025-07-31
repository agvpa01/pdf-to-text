from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import PyPDF2
import io
import os
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF file using PyPDF2
    """
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Initialize text variable
        text = ""
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            
            # Add page separator if there's content
            if page_text.strip():
                if text:
                    text += "\n\n--- Page {} ---\n\n".format(page_num + 1)
                text += page_text
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/styles.css')
def styles():
    """Serve the CSS file"""
    return send_from_directory('.', 'styles.css')

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    return send_from_directory('.', 'script.js')

@app.route('/convert', methods=['POST'])
def convert_pdf():
    """Convert PDF to text"""
    try:
        # Check if file is present in request
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        file = request.files['pdf']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        if file_size == 0:
            return jsonify({'error': 'Empty file provided'}), 400
        
        logger.info(f"Processing PDF file: {file.filename} ({file_size} bytes)")
        
        # Create a BytesIO object from the file
        pdf_stream = io.BytesIO(file.read())
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_stream)
        
        if not extracted_text.strip():
            return jsonify({'error': 'No text could be extracted from the PDF. The file might be image-based or corrupted.'}), 400
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters from {file.filename}")
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'filename': file.filename,
            'text_length': len(extracted_text)
        })
    
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'PDF to Text Converter API is running'
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting PDF to Text Converter Server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )