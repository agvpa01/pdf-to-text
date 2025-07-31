let selectedFiles = [];
let convertedFiles = [];

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filesSection = document.getElementById('filesSection');
const fileList = document.getElementById('fileList');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const resultsList = document.getElementById('resultsList');
const convertBtn = document.getElementById('convertBtn');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
}

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    addFiles(files);
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files).filter(file => file.type === 'application/pdf');
    addFiles(files);
}

function addFiles(files) {
    files.forEach(file => {
        if (file.type === 'application/pdf' && !selectedFiles.find(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    });
    
    updateFileList();
    
    if (selectedFiles.length > 0) {
        filesSection.style.display = 'block';
    }
}

function updateFileList() {
    fileList.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        fileItem.innerHTML = `
            <div class="file-info">
                <div class="file-icon">📄</div>
                <div class="file-details">
                    <h4>${file.name}</h4>
                    <p>${formatFileSize(file.size)}</p>
                </div>
            </div>
            <button class="remove-btn" onclick="removeFile(${index})">Remove</button>
        `;
        
        fileList.appendChild(fileItem);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    
    if (selectedFiles.length === 0) {
        filesSection.style.display = 'none';
    }
}

function clearFiles() {
    selectedFiles = [];
    convertedFiles = [];
    filesSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    fileInput.value = '';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function sanitizeFileName(fileName) {
    // Remove file extension
    const nameWithoutExt = fileName.replace(/\.[^/.]+$/, '');
    
    // Replace special characters and spaces with underscores
    // Keep only alphanumeric characters and underscores
    const sanitized = nameWithoutExt
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ') // Replace special chars with spaces
        .replace(/\s+/g, '_') // Replace spaces with underscores
        .replace(/_+/g, '_') // Replace multiple underscores with single
        .replace(/^_|_$/g, ''); // Remove leading/trailing underscores
    
    return sanitized || 'converted_file';
}

async function convertFiles() {
    if (selectedFiles.length === 0) return;
    
    convertBtn.disabled = true;
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    convertedFiles = [];
    
    const totalFiles = selectedFiles.length;
    let completedFiles = 0;
    
    for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        
        try {
            updateProgress(completedFiles, totalFiles, `Converting ${file.name}...`);
            
            const formData = new FormData();
            formData.append('pdf', file);
            
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                const sanitizedName = sanitizeFileName(file.name);
                
                convertedFiles.push({
                    originalName: file.name,
                    sanitizedName: sanitizedName,
                    text: result.text,
                    status: 'success'
                });
            } else {
                const error = await response.json();
                convertedFiles.push({
                    originalName: file.name,
                    sanitizedName: sanitizeFileName(file.name),
                    text: '',
                    status: 'error',
                    error: error.error || 'Conversion failed'
                });
            }
        } catch (error) {
            convertedFiles.push({
                originalName: file.name,
                sanitizedName: sanitizeFileName(file.name),
                text: '',
                status: 'error',
                error: 'Network error or server unavailable'
            });
        }
        
        completedFiles++;
        updateProgress(completedFiles, totalFiles, `Completed ${completedFiles}/${totalFiles} files`);
    }
    
    convertBtn.disabled = false;
    displayResults();
}

function updateProgress(completed, total, message) {
    const percentage = Math.round((completed / total) * 100);
    progressFill.style.width = percentage + '%';
    progressText.textContent = `${percentage}% Complete - ${message}`;
}

function displayResults() {
    resultsSection.style.display = 'block';
    resultsList.innerHTML = '';
    
    convertedFiles.forEach((file, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const statusClass = file.status === 'success' ? 'success' : 'error';
        const statusText = file.status === 'success' ? 'Converted' : 'Failed';
        
        resultItem.innerHTML = `
            <div class="file-info">
                <div class="file-icon">${file.status === 'success' ? '📝' : '❌'}</div>
                <div class="file-details">
                    <h4>${file.originalName}</h4>
                    <p>Output: ${file.sanitizedName}.txt</p>
                    ${file.error ? `<p style="color: #ff4757; font-size: 0.8rem;">${file.error}</p>` : ''}
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="status ${statusClass}">${statusText}</span>
                ${file.status === 'success' ? `<button class="download-btn" onclick="downloadFile(${index})">Download</button>` : ''}
            </div>
        `;
        
        resultsList.appendChild(resultItem);
    });
}

function downloadFile(index) {
    const file = convertedFiles[index];
    if (file.status !== 'success') return;
    
    const blob = new Blob([file.text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${file.sanitizedName}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadAll() {
    const successfulFiles = convertedFiles.filter(file => file.status === 'success');
    
    if (successfulFiles.length === 0) {
        alert('No successfully converted files to download.');
        return;
    }
    
    successfulFiles.forEach((file, index) => {
        setTimeout(() => {
            downloadFile(convertedFiles.indexOf(file));
        }, index * 100); // Small delay between downloads
    });
}

// Error handling for fetch requests
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});