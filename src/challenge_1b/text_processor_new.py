"""
Text processing and chunking module - Simplified version without optional dependencies.
"""

import re
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles text preprocessing, cleaning, and chunking."""
    
    def __init__(self):
        self.max_chunk_size = 500  # Maximum words per chunk
        self.overlap_size = 50     # Overlapping words between chunks
        
        # Basic stopwords (avoiding NLTK dependency)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
            'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'not', 'no', 'yes', 'from',
            'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
        }
    
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
            'sections': [],
            'chunks': [],
            'full_text': ''
        }
        
        # Collect all text
        all_text = []
        
        for page in document_data.get('pages', []):
            page_text = page.get('text', '')
            if page_text.strip():
                # Clean the text
                cleaned_text = self.clean_text(page_text)
                all_text.append(cleaned_text)
                
                # Process sections if available
                for section in page.get('sections', []):
                    section_text = section.get('text', '')
                    if section_text.strip():
                        processed_section = {
                            'title': section.get('title', ''),
                            'text': self.clean_text(section_text),
                            'page': page.get('page_num', 0),
                            'type': section.get('type', 'content')
                        }
                        processed_doc['sections'].append(processed_section)
        
        # Join all text
        full_text = ' '.join(all_text)
        processed_doc['full_text'] = full_text
        
        # Create chunks
        chunks = self.create_chunks(full_text)
        processed_doc['chunks'] = chunks
        
        return processed_doc
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'\b\w{1,2}\b', ' ', text)  # Remove very short words
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace again
        
        return text.strip()
    
    def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create overlapping chunks from text."""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.max_chunk_size - self.overlap_size):
            chunk_words = words[i:i + self.max_chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk = {
                'text': chunk_text,
                'start_index': i,
                'end_index': min(i + self.max_chunk_size, len(words)),
                'word_count': len(chunk_words)
            }
            chunks.append(chunk)
            
            # Break if we've reached the end
            if i + self.max_chunk_size >= len(words):
                break
        
        return chunks
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract keywords from text (simple frequency-based approach)."""
        if not text:
            return []
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stopwords
        words = [word for word in words if word not in self.stop_words]
        
        # Count frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def get_text_statistics(self, text: str) -> Dict[str, int]:
        """Get basic text statistics."""
        if not text:
            return {'characters': 0, 'words': 0, 'sentences': 0}
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = text.split()
        
        return {
            'characters': len(text),
            'words': len(words),
            'sentences': len(sentences)
        }
