"""
PDF text extraction and structure analysis module.
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction with structural information."""
    
    def __init__(self):
        self.min_font_size = 8
        self.header_font_threshold = 12
    
    def extract_text_with_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF with structural information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing structured text data
        """
        doc = None
        try:
            logger.info(f"Opening PDF: {pdf_path}")
            doc = fitz.open(str(pdf_path))
            logger.info(f"Successfully opened PDF with {len(doc)} pages")
            
            document_data = {
                'pages': [],
                'total_pages': len(doc),
                'metadata': doc.metadata
            }
            
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}")
                page = doc[page_num]
                page_data = self._extract_page_structure(page, page_num + 1)
                document_data['pages'].append(page_data)
            
            logger.info(f"Extracted text from {pdf_path.name} ({len(doc)} pages)")
            return document_data
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
        finally:
            if doc:
                doc.close()
    
    def _extract_page_structure(self, page, page_num: int) -> Dict[str, Any]:
        """Extract structured text from a single page."""
        blocks = page.get_text("dict")
        
        page_data = {
            'page_number': page_num,
            'sections': [],
            'full_text': '',
            'bbox': page.rect
        }
        
        current_section = None
        text_elements = []
        
        for block in blocks.get("blocks", []):
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    font_size = span.get("size", 0)
                    text = span.get("text", "").strip()
                    
                    if not text or font_size < self.min_font_size:
                        continue
                    
                    # Detect headers based on font size and formatting
                    is_header = self._is_likely_header(span, text)
                    
                    if is_header:
                        # Save previous section if exists
                        if current_section:
                            page_data['sections'].append(current_section)
                        
                        # Start new section
                        current_section = {
                            'title': text,
                            'content': '',
                            'font_size': font_size,
                            'bbox': span.get('bbox', []),
                            'subsections': []
                        }
                    else:
                        # Add to current section or create default section
                        if current_section is None:
                            current_section = {
                                'title': f'Content (Page {page_num})',
                                'content': '',
                                'font_size': 0,
                                'bbox': [],
                                'subsections': []
                            }
                        
                        current_section['content'] += text + ' '
                    
                    text_elements.append({
                        'text': text,
                        'font_size': font_size,
                        'bbox': span.get('bbox', []),
                        'is_header': is_header
                    })
        
        # Add final section
        if current_section:
            page_data['sections'].append(current_section)
        
        # Create full page text
        page_data['full_text'] = ' '.join([elem['text'] for elem in text_elements])
        
        return page_data
    
    def _is_likely_header(self, span: Dict, text: str) -> bool:
        """Determine if text span is likely a header."""
        font_size = span.get("size", 0)
        flags = span.get("flags", 0)
        
        # Check font size threshold
        if font_size >= self.header_font_threshold:
            return True
        
        # Check if bold (flag 20 = bold)
        is_bold = flags & 20
        
        # Check text patterns that suggest headers
        header_patterns = [
            r'^\d+\.?\s+[A-Z]',  # Numbered sections
            r'^[A-Z][A-Z\s]+$',  # All caps
            r'^[A-Z][a-z]+\s*:',  # Title case with colon
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, text):
                return True
        
        # Short text with bold formatting
        if is_bold and len(text.split()) <= 5 and font_size > 10:
            return True
        
        return False
