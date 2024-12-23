def generate_visualization_html(doc, text_blocks):
    import pymupdf
    import json
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Text Extraction Visualization</title>
        <link rel="stylesheet" href="/static/css/styles.css">
    </head>
    <body>
        <div id="pdf-view"></div>
        <div id="text-view"></div>
        <script src="/static/js/viewer.js"></script>
        <script>
            window.onload = function() {
                const textBlocks = BLOCKS_PLACEHOLDER;
                initializeViewer(textBlocks);
            }
        </script>
    </body>
    </html>
    """
    
    # Process pages and generate images
    for page_num in range(1, doc.page_count + 1):
        page = doc[page_num - 1]
        zoom = 2
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        pix.save(f'output/page_{page_num}.png')
    
    # Replace placeholder with JSON-serialized text blocks
    html = html.replace('BLOCKS_PLACEHOLDER', json.dumps(text_blocks))
    
    with open('output/visualization.html', 'w') as f:
        f.write(html) 