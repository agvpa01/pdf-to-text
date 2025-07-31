# PDF to Text Converter Web Application

A modern web application that allows users to upload multiple PDF files and convert them to text format with sanitized filenames.

## Features

- **Multiple File Upload**: Upload multiple PDF files at once
- **Drag & Drop Interface**: Intuitive drag and drop functionality
- **File Name Sanitization**: Converts filenames to `word_word_word` format with underscores
- **Progress Tracking**: Real-time conversion progress display
- **Individual Downloads**: Download each converted file separately
- **Batch Download**: Download all converted files at once
- **Error Handling**: Comprehensive error handling and user feedback
- **Responsive Design**: Works on desktop and mobile devices

## Requirements

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Upload PDF files**:
   - Click "Browse Files" or drag and drop PDF files onto the upload area
   - Multiple files can be selected at once

4. **Convert files**:
   - Click "Convert to Text" to start the conversion process
   - Monitor the progress bar for conversion status

5. **Download converted files**:
   - Download individual files using the "Download" button
   - Or download all successful conversions using "Download All"

## File Name Sanitization

The application automatically sanitizes PDF filenames according to these rules:
- Converts to lowercase
- Replaces spaces and special characters with underscores
- Removes consecutive underscores
- Removes leading/trailing underscores
- Example: `My Document (2023).pdf` → `my_document_2023.txt`

## Technical Details

### Backend (Python Flask)
- **Framework**: Flask with CORS support
- **PDF Processing**: PyPDF2 library for text extraction
- **File Handling**: Secure file upload with size and type validation
- **Error Handling**: Comprehensive error handling and logging

### Frontend (HTML/CSS/JavaScript)
- **Modern UI**: Responsive design with gradient backgrounds
- **File Management**: Drag & drop interface with file preview
- **Progress Tracking**: Real-time conversion progress
- **Download Management**: Individual and batch download options

### API Endpoints
- `GET /` - Serve the main application
- `POST /convert` - Convert PDF to text
- `GET /health` - Health check endpoint

## File Limitations

- **Maximum file size**: 16MB per PDF
- **Supported format**: PDF files only
- **Text extraction**: Works best with text-based PDFs (not scanned images)

## Troubleshooting

### Common Issues

1. **"No text could be extracted"**:
   - The PDF might be image-based or scanned
   - Try with a different PDF that contains selectable text

2. **"File too large"**:
   - Reduce the PDF file size or split large documents

3. **Server not starting**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check if port 5000 is available

4. **Conversion fails**:
   - Check the browser console for error messages
   - Ensure the PDF file is not corrupted

## Development

To run in development mode:
```bash
python app.py
```

The server will start with debug mode enabled and auto-reload on file changes.

## License

This project is open source and available under the MIT License.