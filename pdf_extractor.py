import pymupdf
import os
from html_generator import generate_visualization_html

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
                    bbox = block.get("bbox", [])
                    
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
                    if text.strip():
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
                    continue

        # Generate visualization
        generate_visualization_html(doc, text_blocks)
        
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False 