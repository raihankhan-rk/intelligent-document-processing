document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdf-file');
    const loading = document.getElementById('loading');
    
    if (!fileInput.files[0]) {
        alert('Please select a PDF file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    loading.style.display = 'block';
    
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
    }
}); 