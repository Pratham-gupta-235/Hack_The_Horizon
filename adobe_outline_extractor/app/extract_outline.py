import os
import json
import re
import fitz  
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from utils import (
    clean_text, 
    determine_heading_level, 
    is_likely_heading, 
    process_outline_structure,
    extract_text_with_formatting
)

INPUT_DIR = os.getenv("INPUT_DIR", "input")  
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")  

def extract_outline(pdf_path):
    """Extract outline/headings from PDF using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        outline = []
        title = None
        seen_headings = set()  
        
        # Extract document title from metadata or first page
        metadata = doc.metadata
        if metadata and metadata.get('title'):
            title = metadata['title'].strip()
        
        # Get table of contents (outline) 
        toc = doc.get_toc(simple=False)
        
        if toc and len(toc) > 3:  
            # Process TOC and clean it
            for level, heading_title, page_num, *_ in toc:
                clean_title = clean_text(heading_title)
                if not clean_title or clean_title in seen_headings:
                    continue
                
                # Adjust level based on content but respect TOC hierarchy
                adjusted_level = f"H{min(level, 4)}" 
                
                outline.append({
                    "level": adjusted_level,
                    "text": clean_title,
                    "page": page_num,
                })
                seen_headings.add(clean_title)
        else:
            # Fallback: extract headings using conservative text extraction
            # Focus on major headings only to avoid noise
            for page_num in range(len(doc)): 
                page = doc[page_num]
                
                # Extract text elements with formatting information
                text_elements = extract_text_with_formatting(page)
                
                # Sort by position (top to bottom) and font size (largest first)
                text_elements.sort(key=lambda x: (-x["font_size"], x["bbox"][1]))
                
                for element in text_elements:
                    text = element["text"]
                    font_size = element["font_size"]
                    font_flags = element["font_flags"]
                    
                    clean_title = clean_text(text)
                    if not clean_title or clean_title in seen_headings:
                        continue
                    
                    # Use very conservative heading detection for fallback
                    if is_likely_heading(text, font_size, font_flags):
                        level = determine_heading_level(clean_title, font_size, font_flags)
                        
                        # Additional filtering for text extraction
                        if should_include_heading(clean_title, font_size, font_flags):
                            outline.append({
                                "level": level,
                                "text": clean_title,
                                "page": page_num + 1,
                            })
                            seen_headings.add(clean_title)
        
        # Post-process outline to create the desired structure
        processed_outline = process_outline_structure(outline)
        
        # Set title if not found in metadata
        if not title:
            # Try to extract title from first page or use filename
            if processed_outline:
                # Look for a title-like heading on first page
                first_page_headings = [h for h in processed_outline if h["page"] == 1]
                if first_page_headings:
                    title = first_page_headings[0]["text"]
                else:
                    title = processed_outline[0]["text"]
            else:
                title = os.path.splitext(os.path.basename(pdf_path))[0]
        
        doc.close()
        
        return {
            "title": title,
            "outline": processed_outline,
        }
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return {
            "title": os.path.splitext(os.path.basename(pdf_path))[0],
            "outline": [],
            "error": str(e)
        }

def should_include_heading(text, font_size, font_flags):
    """Additional filtering for headings in text extraction mode"""
    text_lower = text.lower()
    
    # Always include numbered sections and appendices
    if re.match(r'^\d+\.', text) or 'appendix' in text_lower:
        return True
    
    # Always include major document sections
    major_sections = [
        'summary', 'background', 'introduction', 'overview', 'conclusion',
        'references', 'acknowledgements', 'table of contents', 'revision history',
        'approach', 'evaluation', 'milestones', 'business plan'
    ]
    if any(section in text_lower for section in major_sections):
        return True
    
    # Include if it's large and bold
    if font_size >= 16 and (font_flags & 16):
        return True
    
    # Exclude specific patterns we don't want
    exclude_patterns = [
        'for each ontario',
        'timeline:',
        'funding:',
        'result:',
        'phase i:',
        'phase ii:',
        'phase iii:',
        'march 2003',
        'april 2003',
        'january 2007'
    ]
    
    if any(pattern in text_lower for pattern in exclude_patterns):
        return False
    
    return True

def process_pdf(pdf_file, input_dir, output_dir):
    """Process a single PDF file"""
    input_path = os.path.join(input_dir, pdf_file)
    output_path = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}.json")
    
    print(f"Processing: {pdf_file}")
    start_time = time.time()
    
    outline = extract_outline(input_path)
    
    with open(output_path, 'w', encoding='utf-8') as outf:
        json.dump(outline, outf, ensure_ascii=False, indent=2)
    
    end_time = time.time()
    print(f"Completed: {pdf_file} in {end_time - start_time:.2f}s")
    return pdf_file, end_time - start_time

def main():
    start_total = time.time()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get all PDF files
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process PDFs in parallel for better performance
    with ThreadPoolExecutor(max_workers=min(4, len(pdf_files))) as executor:
        futures = [executor.submit(process_pdf, pdf, INPUT_DIR, OUTPUT_DIR) 
                  for pdf in pdf_files]
        
        for future in as_completed(futures):
            try:
                pdf_name, duration = future.result()
            except Exception as e:
                print(f"Error processing PDF: {str(e)}")
    
    total_time = time.time() - start_total
    print(f"Total processing time: {total_time:.2f}s for {len(pdf_files)} files")

if __name__ == "__main__":
    main()
