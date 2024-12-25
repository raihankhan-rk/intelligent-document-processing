def generate_visualization_html(doc, text_blocks):
    import pymupdf
    import json
    import os
    
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
        <div id="schema-view"></div>
        <script src="/static/js/viewer.js"></script>
        <script>
            window.onload = function() {
                const textBlocks = BLOCKS_PLACEHOLDER;
                const structuredData = STRUCTURED_DATA_PLACEHOLDER;
                initializeViewer(textBlocks, structuredData);
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
    
    # Load structured data if it exists
    structured_data = None
    if os.path.exists('output/structured_data.json'):
        with open('output/structured_data.json', 'r') as f:
            structured_data = json.load(f)
    
    # Replace placeholders
    html = html.replace('BLOCKS_PLACEHOLDER', json.dumps(text_blocks))
    html = html.replace('STRUCTURED_DATA_PLACEHOLDER', json.dumps(structured_data))
    
    with open('output/visualization.html', 'w') as f:
        f.write(html) 