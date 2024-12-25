document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('pdf-file');
    const loading = document.getElementById('loading');
    const uploadButton = document.getElementById('upload-button');
    const selectedFile = document.getElementById('selected-file');
    const fileInputContainer = document.querySelector('.file-input-container');

    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputContainer.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputContainer.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileInputContainer.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        fileInputContainer.style.borderColor = '#4299e1';
        fileInputContainer.style.background = '#ebf8ff';
    }

    function unhighlight(e) {
        fileInputContainer.style.borderColor = '#cbd5e0';
        fileInputContainer.style.background = '#f8fafc';
    }

    fileInputContainer.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', function(e) {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files[0]) {
            if (files[0].type === 'application/pdf') {
                selectedFile.textContent = `Selected: ${files[0].name}`;
                selectedFile.style.display = 'block';
                uploadButton.style.display = 'block';
            } else {
                alert('Please select a PDF file');
                fileInput.value = '';
                selectedFile.style.display = 'none';
                uploadButton.style.display = 'none';
            }
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files[0]) {
            alert('Please select a PDF file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        // Add schema if provided
        const schemaPrompt = document.getElementById('schema-prompt').value;
        if (schemaPrompt.trim()) {
            formData.append('schema', schemaPrompt);
        }
        
        loading.style.display = 'block';
        uploadButton.disabled = true;
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                window.location.href = `/output/visualization.html`;
            } else {
                alert('Upload failed');
            }
        } catch (error) {
            alert('An error occurred');
        } finally {
            loading.style.display = 'none';
            uploadButton.disabled = false;
        }
    });
}); 