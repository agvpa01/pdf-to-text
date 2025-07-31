# PDF to Text Converter

A FastAPI web application that converts multiple PDF files to text files with sanitized filenames.

## Features

- Upload multiple PDF files simultaneously
- Drag and drop file upload interface
- Convert PDF files to text format
- Sanitized filenames (word_word_word format with underscores)
- Download individual converted files
- Download all converted files as a ZIP archive
- Modern, responsive web interface

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the FastAPI server:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. Upload your PDF files using the web interface:
   - Drag and drop PDF files onto the upload area, or
   - Click "Select PDF Files" to browse and select files

4. Click "Convert to Text" to process the files

5. Download the converted text files individually or as a ZIP archive

## File Naming Convention

The application automatically sanitizes PDF filenames by:
- Removing special characters
- Converting spaces to underscores
- Converting to lowercase
- Format: `word_word_word.txt`

Example:
- `My Document (2023).pdf` → `my_document_2023.txt`
- `Report #1 - Final.pdf` → `report_1_final.txt`

## API Endpoints

- `GET /` - Main web interface
- `POST /convert` - Convert PDF files to text
- `GET /download/{filename}` - Download individual text file
- `GET /download-all` - Download all converted files as ZIP

## Directory Structure

```
project-pdf-to-text/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── uploads/            # Temporary PDF storage (auto-created)
├── converted/          # Converted text files (auto-created)
└── static/             # Static files (auto-created)
```

## Requirements

- Python 3.7+
- FastAPI
- PyPDF2
- Uvicorn
- python-multipart
- aiofiles

## Notes

- Uploaded PDF files are temporarily stored and automatically deleted after conversion
- Converted text files are stored in the `converted/` directory
- The application creates necessary directories automatically on startup