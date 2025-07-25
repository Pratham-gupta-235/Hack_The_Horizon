"""
PDF Outline Extractor for Challenge 1a
Optimized for performance with proper imports and structure
"""

import fitz  # PyMuPDF
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging
import json
from dataclasses import dataclass

from .cache_manager import TTLCacheManager
from ..shared.config import OptimizedConfig


logger = logging.getLogger(__name__)


@dataclass
class OutlineItem:
    """Represents a single outline item"""
    title: str
    level: int
    page: int
    children: List['OutlineItem'] = None


class PDFOutlineExtractor:
    """Extract structured outlines from PDF documents"""
    
    def __init__(self, config: OptimizedConfig = None):
        self.config = config or OptimizedConfig()
        self.cache = TTLCacheManager(
            maxsize=self.config.cache_size, 
            ttl=self.config.cache_ttl
        )
        
    def extract_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Extract outline structure from PDF"""
        try:
            with fitz.open(pdf_path) as doc:
                outline_data = {
                    'filename': Path(pdf_path).name,
                    'total_pages': len(doc),
                    'outline': self._extract_toc(doc),
                    'metadata': self._extract_metadata(doc)
                }
                return outline_data
        except Exception as e:
            logger.error(f"Error extracting outline from {pdf_path}: {e}")
            return {
                'filename': Path(pdf_path).name,
                'error': str(e),
                'outline': [],
                'metadata': {}
            }
    
    def _extract_toc(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Extract table of contents"""
        toc = doc.get_toc()
        outline_items = []
        
        for level, title, page in toc:
            outline_items.append({
                'title': title.strip(),
                'level': level,
                'page': page,
                'type': 'heading'
            })
        
        # If no TOC, try to detect headings from text
        if not outline_items:
            outline_items = self._detect_headings(doc)
            
        return outline_items
    
    def _detect_headings(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Detect headings from text formatting"""
        headings = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if self._is_likely_heading(span, text):
                                headings.append({
                                    'title': text,
                                    'level': self._estimate_heading_level(span),
                                    'page': page_num + 1,
                                    'type': 'detected_heading'
                                })
        
        return headings
    
    def _is_likely_heading(self, span: Dict, text: str) -> bool:
        """Determine if text span is likely a heading"""
        if len(text) < 3 or len(text) > 200:
            return False
            
        # Check font size (headings usually larger)
        font_size = span.get("size", 12)
        if font_size < 14:
            return False
            
        # Check if bold
        is_bold = "bold" in span.get("font", "").lower()
        
        # Check if all caps (common for headings)
        is_caps = text.isupper()
        
        return is_bold or is_caps or font_size > 16
    
    def _estimate_heading_level(self, span: Dict) -> int:
        """Estimate heading level based on formatting"""
        font_size = span.get("size", 12)
        
        if font_size >= 20:
            return 1
        elif font_size >= 16:
            return 2
        elif font_size >= 14:
            return 3
        else:
            return 4
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract document metadata"""
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', '')
        }
