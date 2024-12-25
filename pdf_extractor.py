import pymupdf
import os
import json
from html_generator import generate_visualization_html
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from difflib import SequenceMatcher

def extract_structured_text(text_blocks, schema_prompt):
    """Extract structured information using LLM"""
    # Initialize ChatGPT
    llm = ChatOpenAI(
        temperature=0.2,
        model_name="gpt-4o",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Prepare the text content
    full_text = "\n".join([block["text"] for block in text_blocks])
    
    # Create prompt template with explicit JSON instruction
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a precise data extractor. Extract information according to the schema provided.
         Return ONLY valid JSON without any markdown formatting or additional text."""),
        ("system", f"Schema requirements: {schema_prompt}"),
        ("user", f"Extract information from the following text into JSON format according to the schema:\n{full_text}")
    ])
    
    # Get structured response from LLM
    response = llm.invoke(prompt.format_messages())
    
    try:
        # Clean the response to ensure it's valid JSON
        json_str = response.content
        if '```json' in json_str:
            # Extract JSON from markdown code block if present
            json_str = json_str.split('```json')[1].split('```')[0]
        json_str = json_str.strip()
        
        # Parse the JSON response
        structured_data = json.loads(json_str)
        return structured_data
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        print(f"Raw response: {response.content}")
        return None

def map_json_to_positions(structured_data, text_blocks):
    """Map extracted JSON fields to their positions in the PDF"""
    positioned_data = {"data": structured_data, "positions": {}}
    
    def normalize_text(text):
        """Normalize text for comparison"""
        return str(text).lower().strip()
    
    def find_best_match(value, blocks):
        """Find the best matching block for a value"""
        value_normalized = normalize_text(value)
        best_match = None
        best_ratio = 0
        
        for block in blocks:
            block_text = normalize_text(block["text"])
            
            # Direct match
            if value_normalized in block_text:
                return {
                    "page": block["page"],
                    "bbox": block["position"],
                    "text": block["text"]
                }
            
            # Partial match with ratio calculation
            ratio = SequenceMatcher(None, value_normalized, block_text).ratio()
            if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
                best_ratio = ratio
                best_match = block
        
        if best_match:
            return {
                "page": best_match["page"],
                "bbox": best_match["position"],
                "text": best_match["text"]
            }
        return None
    
    def process_json(data, path=""):
        """Recursively process JSON structure"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, (str, int, float)):
                    pos = find_best_match(value, text_blocks)
                    if pos:
                        positioned_data["positions"][current_path] = pos
                else:
                    process_json(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                process_json(item, current_path)
    
    process_json(structured_data)
    return positioned_data

def extract_text_with_positions(pdf_path, schema_prompt=None):
    try:
        # Open the PDF file
        doc = pymupdf.open(pdf_path)
        
        # Create a list to store all text blocks with their positions
        text_blocks = []
        
        # Extract text blocks with positions
        for page_num in range(len(doc)):
            page = doc[page_num]
            for block in page.get_text("dict")["blocks"]:
                try:
                    bbox = block.get("bbox", [])
                    if "lines" not in block or not block["lines"]:
                        continue
                    
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

        # If schema prompt is provided, extract structured data
        if schema_prompt:
            print("Extracting structured data...")
            structured_data = extract_structured_text(text_blocks, schema_prompt)
            if structured_data:
                print("Mapping positions...")
                positioned_data = map_json_to_positions(structured_data, text_blocks)
                
                # Save structured data with positions
                os.makedirs('output', exist_ok=True)
                with open('output/structured_data.json', 'w') as f:
                    json.dump(positioned_data, f, indent=2)
                print("Structured data saved with positions")

        # Generate visualization
        generate_visualization_html(doc, text_blocks)
        
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False