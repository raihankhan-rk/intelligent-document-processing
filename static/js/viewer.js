// Make highlightPair globally accessible
function highlightPair(id, highlight) {
    const overlay = document.getElementById('overlay-' + id);
    const text = document.getElementById('text-' + id);
    if (overlay && text) {
        if (highlight) {
            text.classList.add('highlight');
            overlay.style.background = 'rgba(255, 0, 0, 0.2)';
            overlay.style.borderColor = 'red';
            text.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            text.classList.remove('highlight');
            overlay.style.background = 'rgba(255, 0, 0, 0.1)';
            overlay.style.borderColor = 'rgba(255, 0, 0, 0.5)';
        }
    }
}

function initializeViewer(textBlocks) {
    function renderPages(blocks) {
        // Group blocks by page
        const pages = {};
        blocks.forEach(block => {
            if (!pages[block.page]) {
                pages[block.page] = [];
            }
            pages[block.page].push(block);
        });

        // Generate PDF view HTML
        let pdfHtml = '';
        let textHtml = '';
        let blockId = 0;

        // For each page
        Object.keys(pages).sort((a, b) => a - b).forEach(pageNum => {
            // Add page container and image
            pdfHtml += `
                <div class='page-container'>
                    <img class='pdf-page' src='page_${pageNum}.png' onload="adjustOverlays()" />
            `;

            textHtml += `<div class='page-title'>Page ${pageNum}</div>`;

            // Add overlays for each text block
            pages[pageNum].forEach(block => {
                const pos = block.position;
                const x1 = pos.x1 * 2; // Multiply by zoom factor
                const y1 = pos.y1 * 2;
                const width = (pos.x2 - pos.x1) * 2;
                const height = (pos.y2 - pos.y1) * 2;
                
                pdfHtml += `
                    <div id="overlay-${blockId}" 
                         class='text-overlay' 
                         data-x="${x1}"
                         data-y="${y1}"
                         data-width="${width}"
                         data-height="${height}"
                         style='left: ${x1}px; top: ${y1}px; width: ${width}px; height: ${height}px;'
                         onmouseover="highlightPair(${blockId}, true)"
                         onmouseout="highlightPair(${blockId}, false)">
                    </div>
                `;

                textHtml += `
                    <div id="text-${blockId}" 
                         class='text-block'
                         onmouseover="highlightPair(${blockId}, true)"
                         onmouseout="highlightPair(${blockId}, false)">
                        ${block.text}
                    </div>
                `;

                blockId++;
            });

            pdfHtml += `</div>`;
        });

        // Insert the generated HTML
        document.getElementById('pdf-view').innerHTML = pdfHtml;
        document.getElementById('text-view').innerHTML = textHtml;
    }

    function adjustOverlays() {
        const containers = document.querySelectorAll('.page-container');
        containers.forEach(container => {
            const image = container.querySelector('.pdf-page');
            if (!image.complete) return; // Skip if image not loaded
            
            const overlays = container.querySelectorAll('.text-overlay');
            const scale = image.clientWidth / image.naturalWidth;
            
            overlays.forEach(overlay => {
                const originalLeft = parseFloat(overlay.dataset.x);
                const originalTop = parseFloat(overlay.dataset.y);
                const originalWidth = parseFloat(overlay.dataset.width);
                const originalHeight = parseFloat(overlay.dataset.height);
                
                overlay.style.left = (originalLeft * scale) + 'px';
                overlay.style.top = (originalTop * scale) + 'px';
                overlay.style.width = (originalWidth * scale) + 'px';
                overlay.style.height = (originalHeight * scale) + 'px';
            });
        });
    }

    // Initialize the viewer
    renderPages(textBlocks);
    
    // Add global adjustOverlays function
    window.adjustOverlays = adjustOverlays;
    
    window.addEventListener('load', adjustOverlays);
    window.addEventListener('resize', adjustOverlays);
} 