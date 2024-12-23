import pymupdf  # PyMuPDF
import os

def extract_text_with_positions(pdf_path):
    try:
        # Open the PDF file
        doc = pymupdf.open(pdf_path)
        
        # Create a list to store all text blocks with their positions
        text_blocks = []
        
        # Loop through each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text with positional information
            for block in page.get_text("dict")["blocks"]:
                try:
                    bbox = block.get("bbox", [])  # Use get() with default value
                    
                    # Skip blocks without lines or with empty lines
                    if "lines" not in block or not block["lines"]:
                        continue
                    
                    # Safely extract text from spans
                    text_parts = []
                    for line in block["lines"]:
                        if "spans" in line and line["spans"]:
                            for span in line["spans"]:
                                if "text" in span:
                                    text_parts.append(span["text"])
                    
                    text = " ".join(text_parts)
                    if text.strip():  # Only include if there's actual text
                        text_blocks.append({
                            "page": page_num + 1,
                            "text": text,
                            "position": {
                                "x1": bbox[0],
                                "y1": bbox[1],
                                "x2": bbox[2],
                                "y2": bbox[3]
                            }
                        })
                        
                except Exception as block_error:
                    continue  # Skip problematic blocks

        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Generate visualization with PDF pages and overlays
        generate_pdf_visualization(doc, text_blocks)
        
        print("Extraction complete! Check output/visualization.html")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_pdf_visualization(doc, text_blocks):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Text Extraction Visualization</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0;
                padding: 0;
                display: flex;
                height: 100vh;
            }
            #pdf-view {
                width: 50%;
                height: 100vh;
                overflow-y: auto;
                padding: 20px;
                box-sizing: border-box;
                background: #f0f0f0;
            }
            #text-view {
                width: 50%;
                height: 100vh;
                overflow-y: auto;
                padding: 20px;
                box-sizing: border-box;
                background: white;
            }
            .page-container { 
                position: relative; 
                margin: 20px 0;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                display: inline-block;
                width: 100%;
            }
            .pdf-page { 
                width: 100%;
                display: block;
            }
            .text-overlay {
                position: absolute;
                border: 2px solid rgba(255, 0, 0, 0.5);
                background: rgba(255, 0, 0, 0.1);
                cursor: pointer;
                transition: all 0.2s;
                box-sizing: border-box;
            }
            .text-overlay:hover {
                background: rgba(255, 0, 0, 0.2);
                border-color: red;
            }
            .text-block {
                padding: 10px;
                margin: 5px 0;
                border: 2px solid transparent;
                background: #f8f8f8;
                transition: all 0.2s;
            }
            .text-block.highlight {
                border-color: red;
                background: #fff0f0;
            }
            .page-title {
                font-weight: bold;
                margin: 20px 0 10px 0;
                padding: 5px;
                background: #eee;
            }
        </style>
    </head>
    <body>
        <div id="pdf-view"></div>
        <div id="text-view"></div>

        <script>
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

            function adjustOverlays() {
                const containers = document.querySelectorAll('.page-container');
                containers.forEach(container => {
                    const image = container.querySelector('.pdf-page');
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

            window.addEventListener('load', adjustOverlays);
            window.addEventListener('resize', adjustOverlays);
        </script>
    """
    
    # Group blocks by page
    pages = {}
    for block in text_blocks:
        page_num = block["page"]
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append(block)
    
    pdf_html = ""
    text_html = ""
    block_id = 0
    
    for page_num in range(1, doc.page_count + 1):
        page = doc[page_num - 1]
        zoom = 2  # Higher quality for base image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        
        img_path = f'output/page_{page_num}.png'
        pix.save(img_path)
        
        pdf_html += f"""
        <div class='page-container'>
            <img class='pdf-page' src='{os.path.basename(img_path)}' />
        """
        
        text_html += f"<div class='page-title'>Page {page_num}</div>"
        
        if page_num in pages:
            for block in pages[page_num]:
                pos = block["position"]
                
                # Store original coordinates
                x1 = pos["x1"] * zoom
                y1 = pos["y1"] * zoom
                width = (pos["x2"] - pos["x1"]) * zoom
                height = (pos["y2"] - pos["y1"]) * zoom
                
                pdf_html += f"""
                    <div id="overlay-{block_id}" 
                         class='text-overlay' 
                         data-x="{x1}"
                         data-y="{y1}"
                         data-width="{width}"
                         data-height="{height}"
                         style='left: {x1}px; top: {y1}px; width: {width}px; height: {height}px;'
                         onmouseover="highlightPair({block_id}, true)"
                         onmouseout="highlightPair({block_id}, false)">
                    </div>
                """
                
                text_html += f"""
                    <div id="text-{block_id}" 
                         class='text-block'
                         onmouseover="highlightPair({block_id}, true)"
                         onmouseout="highlightPair({block_id}, false)">
                        {block['text']}
                    </div>
                """
                
                block_id += 1
        
        pdf_html += "</div>"
    
    html += f"""
        <script>
            document.getElementById('pdf-view').innerHTML = `{pdf_html}`;
            document.getElementById('text-view').innerHTML = `{text_html}`;
        </script>
    </body>
    </html>
    """
    
    with open('output/visualization.html', 'w') as f:
        f.write(html)

# Specify the path to your PDF file
pdf_path = "gas_oil.pdf"
extract_text_with_positions(pdf_path)
