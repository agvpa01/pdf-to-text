from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import PyPDF2
import os
import re
import tempfile
import zipfile
from typing import List
import shutil
from pathlib import Path

app = FastAPI(title="PDF to Text Converter", description="Convert PDF files to text files")

# Create directories for uploads and converted files
UPLOADS_DIR = "uploads"
CONVERTED_DIR = "converted"
STATIC_DIR = "static"

for directory in [UPLOADS_DIR, CONVERTED_DIR, STATIC_DIR]:
    os.makedirs(directory, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def sanitize_filename(filename: str) -> str:
    """Convert filename to word_word_word format and remove special characters"""
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Replace special characters and spaces with underscores
    # Keep only alphanumeric characters and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\s]', ' ', name_without_ext)
    
    # Split by whitespace and join with underscores
    words = sanitized.split()
    
    # Filter out empty strings and convert to lowercase
    words = [word.lower() for word in words if word.strip()]
    
    return '_'.join(words) if words else 'converted_file'

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    
    return text

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF to Text Converter</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 2px dashed #ddd;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin-bottom: 20px;
                transition: border-color 0.3s;
            }
            .upload-area:hover {
                border-color: #007bff;
            }
            .upload-area.dragover {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            input[type="file"] {
                display: none;
            }
            .upload-btn {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
            .upload-btn:hover {
                background-color: #0056b3;
            }
            .convert-btn {
                background-color: #28a745;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
                margin-top: 20px;
            }
            .convert-btn:hover {
                background-color: #218838;
            }
            .convert-btn:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
            .file-list {
                margin-top: 20px;
            }
            .file-item {
                background-color: #f8f9fa;
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .remove-btn {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
            }
            .remove-btn:hover {
                background-color: #c82333;
            }
            .progress {
                display: none;
                margin-top: 20px;
            }
            .progress-bar {
                width: 100%;
                height: 20px;
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background-color: #007bff;
                width: 0%;
                transition: width 0.3s;
            }
            .download-section {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }
            .download-btn {
                background-color: #17a2b8;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
            }
            .download-btn:hover {
                background-color: #138496;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PDF to Text Converter</h1>
            
            <div class="upload-area" id="uploadArea">
                <p>Drag and drop PDF files here or click to select</p>
                <button class="upload-btn" onclick="document.getElementById('fileInput').click()">Select PDF Files</button>
                <input type="file" id="fileInput" multiple accept=".pdf">
            </div>
            
            <div class="file-list" id="fileList"></div>
            
            <button class="convert-btn" id="convertBtn" onclick="convertFiles()" disabled>Convert to Text</button>
            
            <div class="progress" id="progress">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <p id="progressText">Converting...</p>
            </div>
            
            <div class="download-section" id="downloadSection" style="display: none;">
                <h3>Download Converted Files</h3>
                <div style="margin-bottom: 15px;">
                    <a href="/download-all" class="download-btn" style="background-color: #6f42c1;">Download All as ZIP</a>
                </div>
                <div id="downloadLinks"></div>
            </div>
        </div>
        
        <script>
            let selectedFiles = [];
            
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const fileList = document.getElementById('fileList');
            const convertBtn = document.getElementById('convertBtn');
            const progress = document.getElementById('progress');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const downloadSection = document.getElementById('downloadSection');
            const downloadLinks = document.getElementById('downloadLinks');
            
            // Drag and drop functionality
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = Array.from(e.dataTransfer.files).filter(file => file.type === 'application/pdf');
                addFiles(files);
            });
            
            fileInput.addEventListener('change', (e) => {
                addFiles(Array.from(e.target.files));
            });
            
            function addFiles(files) {
                files.forEach(file => {
                    if (!selectedFiles.find(f => f.name === file.name)) {
                        selectedFiles.push(file);
                    }
                });
                updateFileList();
                updateConvertButton();
            }
            
            function removeFile(index) {
                selectedFiles.splice(index, 1);
                updateFileList();
                updateConvertButton();
            }
            
            function updateFileList() {
                fileList.innerHTML = '';
                selectedFiles.forEach((file, index) => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <span>${file.name}</span>
                        <button class="remove-btn" onclick="removeFile(${index})">Remove</button>
                    `;
                    fileList.appendChild(fileItem);
                });
            }
            
            function updateConvertButton() {
                convertBtn.disabled = selectedFiles.length === 0;
            }
            
            async function convertFiles() {
                if (selectedFiles.length === 0) return;
                
                progress.style.display = 'block';
                convertBtn.disabled = true;
                downloadSection.style.display = 'none';
                
                const formData = new FormData();
                selectedFiles.forEach(file => {
                    formData.append('files', file);
                });
                
                try {
                    const response = await fetch('/convert', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        progressFill.style.width = '100%';
                        progressText.textContent = 'Conversion completed!';
                        
                        // Show download links
                        downloadLinks.innerHTML = '';
                        result.files.forEach(file => {
                            const link = document.createElement('a');
                            link.href = `/download/${file.filename}`;
                            link.className = 'download-btn';
                            link.textContent = `Download ${file.original_name}`;
                            link.download = file.filename;
                            downloadLinks.appendChild(link);
                        });
                        
                        downloadSection.style.display = 'block';
                    } else {
                        const error = await response.json();
                        alert('Error: ' + error.detail);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    setTimeout(() => {
                        progress.style.display = 'none';
                        convertBtn.disabled = false;
                        progressFill.style.width = '0%';
                    }, 2000);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/convert")
async def convert_pdfs(files: List[UploadFile] = File(...)):
    """Convert multiple PDF files to text files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    converted_files = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            continue
            
        # Save uploaded file temporarily
        temp_pdf_path = os.path.join(UPLOADS_DIR, file.filename)
        with open(temp_pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # Extract text from PDF
            text_content = extract_text_from_pdf(temp_pdf_path)
            
            # Create sanitized filename
            sanitized_name = sanitize_filename(file.filename)
            text_filename = f"{sanitized_name}.txt"
            text_filepath = os.path.join(CONVERTED_DIR, text_filename)
            
            # Save text file
            with open(text_filepath, 'w', encoding='utf-8') as text_file:
                text_file.write(text_content)
            
            converted_files.append({
                "filename": text_filename,
                "original_name": file.filename,
                "path": text_filepath
            })
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing {file.filename}: {str(e)}")
        finally:
            # Clean up temporary PDF file
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
    
    return {"message": f"Successfully converted {len(converted_files)} files", "files": converted_files}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a converted text file"""
    file_path = os.path.join(CONVERTED_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/plain'
    )

@app.get("/download-all")
async def download_all_files():
    """Download all converted files as a ZIP archive"""
    converted_files = [f for f in os.listdir(CONVERTED_DIR) if f.endswith('.txt')]
    
    if not converted_files:
        raise HTTPException(status_code=404, detail="No converted files found")
    
    # Create a temporary ZIP file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
        with zipfile.ZipFile(tmp_zip.name, 'w') as zip_file:
            for filename in converted_files:
                file_path = os.path.join(CONVERTED_DIR, filename)
                zip_file.write(file_path, filename)
        
        return FileResponse(
            path=tmp_zip.name,
            filename="converted_texts.zip",
            media_type='application/zip'
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)