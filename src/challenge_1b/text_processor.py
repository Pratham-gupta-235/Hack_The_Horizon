"""
Text processing and chunking module.
"""

import re
import logging
from typing import Dict, List, Any, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from langdetect import detect
import spacy

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles text preprocessing, cleaning, and chunking."""
    
    def __init__(self):
        self.max_chunk_size = 500  # Maximum words per chunk
        self.overlap_size = 50     # Overlapping words between chunks
        
        # Initialize language resources
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            logger.warning("NLTK stopwords not available, using basic set")
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Try to load spacy model for better text processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("Spacy model not available, using basic processing")
            self.nlp = None
    
    def process_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document with text cleaning and chunking.
        
        Args:
            document_data: Raw document data from PDF processor
            
        Returns:
            Processed document with cleaned and chunked text
        """
        processed_doc = {
            'filename': document_data.get('filename', ''),
            'total_pages': document_data.get('total_pages', 0),
            'metadata': document_data.get('metadata', {}),
            'processed_sections': []
        }
        
        for page in document_data.get('pages', []):
            page_sections = self._process_page(page)
            processed_doc['processed_sections'].extend(page_sections)
        
        # Detect document language
        full_text = ' '.join([
            section.get('cleaned_content', '') 
            for section in processed_doc['processed_sections']
        ])
        
        try:
            language = detect(full_text[:1000])  # Use first 1000 chars for detection
            processed_doc['language'] = language
        except:
            processed_doc['language'] = 'en'  # Default to English
        
        logger.info(f"Processed document {processed_doc['filename']} "
                   f"({len(processed_doc['processed_sections'])} sections, "
                   f"language: {processed_doc['language']})")
        
        return processed_doc
    
    def _process_page(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process all sections in a page."""
        processed_sections = []
        page_num = page_data.get('page_number', 1)
        
        for section in page_data.get('sections', []):
            processed_section = self._process_section(section, page_num)
            if processed_section:
                processed_sections.append(processed_section)
        
        return processed_sections
    
    def _process_section(self, section: Dict[str, Any], page_num: int) -> Dict[str, Any]:
        """Process a single section with cleaning and chunking."""
        title = section.get('title', '').strip()
        content = section.get('content', '').strip()
        
        if not content and not title:
            return None
        
        # Clean text
        cleaned_title = self._clean_text(title)
        cleaned_content = self._clean_text(content)
        
        # Create chunks from content
        chunks = self._create_chunks(cleaned_content)
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(cleaned_content)
        
        processed_section = {
            'original_title': title,
            'cleaned_title': cleaned_title,
            'cleaned_content': cleaned_content,
            'page_number': page_num,
            'font_size': section.get('font_size', 0),
            'bbox': section.get('bbox', []),
            'chunks': chunks,
            'key_phrases': key_phrases,
            'word_count': len(cleaned_content.split()) if cleaned_content else 0
        }
        
        return processed_section
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,;:!?\-\'\"()]', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'\b([a-z])([A-Z])', r'\1 \2', text)  # Split joined words
        text = re.sub(r'(\w)([.!?])([A-Z])', r'\1\2 \3', text)  # Add space after punctuation
        
        # Normalize case
        text = text.strip()
        
        return text
    
    def _create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create overlapping chunks from text."""
        if not text:
            return []
        
        words = text.split()
        if len(words) <= self.max_chunk_size:
            return [{
                'text': text,
                'start_word': 0,
                'end_word': len(words),
                'word_count': len(words)
            }]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + self.max_chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'text': chunk_text,
                'start_word': start,
                'end_word': end,
                'word_count': len(chunk_words)
            })
            
            # Move start position with overlap
            if end >= len(words):
                break
            start = end - self.overlap_size
        
        return chunks
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        if not text or self.nlp is None:
            return []
        
        try:
            doc = self.nlp(text[:1000])  # Limit text length for performance
            
            # Extract named entities and noun phrases
            key_phrases = []
            
            # Named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'TECH']:
                    key_phrases.append(ent.text.strip())
            
            # Noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Multi-word phrases
                    key_phrases.append(chunk.text.strip())
            
            # Remove duplicates and filter
            unique_phrases = []
            for phrase in key_phrases:
                if (phrase not in unique_phrases and 
                    len(phrase) > 3 and 
                    not phrase.lower() in self.stop_words):
                    unique_phrases.append(phrase)
            
            return unique_phrases[:10]  # Return top 10 phrases
            
        except Exception as e:
            logger.warning(f"Error extracting key phrases: {str(e)}")
            return []
