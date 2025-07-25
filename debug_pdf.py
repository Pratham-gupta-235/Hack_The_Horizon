#!/usr/bin/env python3
"""
Debug script to examine PDF content and why heading detection isn't working
"""

import fitz
from pathlib import Path

def debug_pdf_content(pdf_path):
    """Debug PDF content to see why heading detection fails"""
    print(f"Debugging: {pdf_path}")
    
    with fitz.open(pdf_path) as doc:
        print(f"Total pages: {len(doc)}")
        
        # Check if there's a TOC
        toc = doc.get_toc()
        print(f"Built-in TOC items: {len(toc)}")
        if toc:
            for level, title, page in toc[:5]:  # Show first 5
                print(f"  Level {level}: {title} (page {page})")
        
        # Examine first few pages for text formatting
        for page_num in range(min(3, len(doc))):
            print(f"\n--- PAGE {page_num + 1} ---")
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            text_items = []
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(text) > 3:
                                font_size = span.get("size", 12)
                                font_name = span.get("font", "")
                                is_bold = "bold" in font_name.lower()
                                text_items.append({
                                    'text': text[:50] + "..." if len(text) > 50 else text,
                                    'size': round(font_size, 1),
                                    'font': font_name,
                                    'bold': is_bold
                                })
            
            # Sort by font size (largest first)
            text_items.sort(key=lambda x: x['size'], reverse=True)
            
            print(f"Text by font size (top 10):")
            for item in text_items[:10]:
                print(f"  Size {item['size']}: {item['text']} (Bold: {item['bold']})")

if __name__ == "__main__":
    pdf_path = Path("input") / "South of France - Cities.pdf"
    debug_pdf_content(pdf_path)
