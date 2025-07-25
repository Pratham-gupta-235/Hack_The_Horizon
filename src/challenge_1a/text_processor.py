import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class TextElement:
    """Structured representation of text element"""
    text: str
    font_size: float
    font_flags: int
    y_pos: float
    page: int

class TextProcessor:
    """text processing with caching and pattern compilation"""
    
    def __init__(self, config):
        self.config = config
        self._exclusion_patterns = self._compile_exclusion_patterns()
        self._cache = {}
    
    def _compile_exclusion_patterns(self) -> Dict[str, re.Pattern]:
        """Pre-compile regex patterns for better performance with multilingual support"""
        return {
            'dates': re.compile(r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$', re.I),
            'long_dates': re.compile(
                r'^(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}$', 
                re.I
            ),
            'times': re.compile(r'^\d{1,2}:\d{2}(\s*(am|pm))?$', re.I),
            'page_refs': re.compile(r'^(page\s+\d+|p\.\s*\d+|ページ\s*\d+|第\s*\d+\s*页)$', re.I),  # Added Japanese/Chinese page refs
            'pure_numbers': re.compile(r'^\d+$'),
            'emails_urls': re.compile(r'.*([@.]com|[@.]org|[@.]ca|[@.]edu).*', re.I),
            'table_headers': re.compile(r'^(s\.no|sr\.no|no\.|name|date|signature|remarks|version|名前|日付|署名)\.?$', re.I),  # Added Japanese
            'artifacts': re.compile(r'^(\.{3,}|_{3,}|-{3,}|…{2,})$'),  # Added ellipsis
            # Multilingual common words to exclude (but not headings)
            'common_excludes': re.compile(r'^(and|or|the|of|in|to|for|with|by|from|at|on|は|が|を|に|で|と|から|まで|参考文献)$', re.I)
        }
    
    def clean_text_optimized(self, text: str) -> Optional[str]:
        """Optimized text cleaning with caching and multilingual support"""
        if not text:
            return None
        
        # Use cache for repeated text
        cache_key = hash(text)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Remove excessive dots early (but be more lenient for non-Latin scripts)
        has_cjk = self._has_cjk_characters(text)
        has_non_latin = self._has_non_latin_characters(text)
        
        if not (has_cjk or has_non_latin):
            if text.count('.') > len(text) * self.config.exclusion_ratio_threshold:
                self._cache[cache_key] = None
                return None
        
        # Normalize whitespace (preserve Unicode characters)
        cleaned = ' '.join(text.split()).strip()
        
        # Adjust length checks for different scripts
        min_length = self._get_min_length_for_script(cleaned)
        if len(cleaned) <= min_length:
            self._cache[cache_key] = None
            return None
        
        # Pattern matching
        cleaned_lower = cleaned.lower()
        for pattern in self._exclusion_patterns.values():
            if pattern.match(cleaned_lower):
                self._cache[cache_key] = None
                return None
        
        # Advanced filtering
        if not self._passes_advanced_filters(cleaned, cleaned_lower):
            self._cache[cache_key] = None
            return None
        
        self._cache[cache_key] = cleaned
        return cleaned
    
    def _get_min_length_for_script(self, text: str) -> int:
        """Get minimum length based on script type"""
        if self._has_cjk_characters(text):
            return 1  # CJK characters can be very meaningful even when short
        elif self._has_non_latin_characters(text):
            return 2  # Other non-Latin scripts
        else:
            return self.config.min_heading_length  # Default for Latin scripts
    
    def _passes_advanced_filters(self, text: str, text_lower: str) -> bool:
        """Advanced filtering logic with multilingual support"""
        # Check if text contains CJK characters (Chinese, Japanese, Korean)
        has_cjk = self._has_cjk_characters(text)
        
        # For CJK languages, use different filtering rules
        if has_cjk:
            return self._passes_cjk_filters(text, text_lower)
        
        # Check for other non-Latin scripts
        has_non_latin = self._has_non_latin_characters(text)
        if has_non_latin:
            return self._passes_non_latin_filters(text, text_lower)
        
        # Original Latin-based filtering
        # Filter out fragments without vowels (likely broken words)
        if (len(text) < 15 and 
            not any(v in text_lower for v in 'aeiou') and 
            not text.startswith(tuple(f'{i}.' for i in range(1, 10)))):
            return False
        
        # Filter single word fragments unless important
        if (len(text.split()) == 1 and 
            len(text) < 10 and 
            text_lower not in {'summary', 'background', 'introduction', 'conclusion', 'references', 'appendix'}):
            return False
        
        return True
    
    def _has_cjk_characters(self, text: str) -> bool:
        """Check if text contains Chinese, Japanese, or Korean characters"""
        for char in text:
            # CJK Unified Ideographs, Hiragana, Katakana, Hangul
            if any([
                '\u4e00' <= char <= '\u9fff',  # CJK Unified Ideographs
                '\u3040' <= char <= '\u309f',  # Hiragana
                '\u30a0' <= char <= '\u30ff',  # Katakana
                '\uac00' <= char <= '\ud7af',  # Hangul Syllables
                '\u3400' <= char <= '\u4dbf',  # CJK Extension A
                '\u20000' <= char <= '\u2a6df', # CJK Extension B
            ]):
                return True
        return False
    
    def _has_non_latin_characters(self, text: str) -> bool:
        """Check if text contains non-Latin script characters"""
        for char in text:
            # Arabic, Hebrew, Cyrillic, Thai, Devanagari, etc.
            if any([
                '\u0600' <= char <= '\u06ff',  # Arabic
                '\u0590' <= char <= '\u05ff',  # Hebrew
                '\u0400' <= char <= '\u04ff',  # Cyrillic
                '\u0e00' <= char <= '\u0e7f',  # Thai
                '\u0900' <= char <= '\u097f',  # Devanagari
                '\u1000' <= char <= '\u109f',  # Myanmar
            ]):
                return True
        return False
    
    def _passes_cjk_filters(self, text: str, text_lower: str) -> bool:
        """Filtering rules for CJK languages (Chinese, Japanese, Korean)"""
        # CJK languages don't use spaces like Latin languages
        # More lenient length requirements
        if len(text) < 2:
            return False
        
        # Skip pure punctuation or symbols
        if all(not char.isalnum() and not self._has_cjk_characters(char) for char in text):
            return False
        
        # Allow shorter headings for CJK since they can be more concise
        return True
    
    def _passes_non_latin_filters(self, text: str, text_lower: str) -> bool:
        """Filtering rules for non-Latin scripts (Arabic, Hebrew, Cyrillic, etc.)"""
        # More lenient than Latin filtering
        if len(text) < 3:
            return False
        
        # Skip pure punctuation
        if all(not char.isalnum() and not self._has_non_latin_characters(char) for char in text):
            return False
        
        return True
    
    def extract_text_with_formatting_optimized(self, page) -> List[TextElement]:
        """Memory-efficient text extraction"""
        text_elements = []
        
        try:
            blocks = page.get_text("dict", flags=0)  # Minimal flags for performance
            
            for block in blocks.get("blocks", []):
                if block.get("type") != 0:  # Skip non-text blocks early
                    continue
                
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    
                    # Process spans efficiently
                    line_text, max_size, flags = self._process_spans_optimized(spans)
                    
                    if line_text and len(line_text) > 3:
                        text_elements.append(TextElement(
                            text=line_text.strip(),
                            font_size=max_size,
                            font_flags=flags,
                            y_pos=line["bbox"][1],
                            page=page.number + 1
                        ))
        
        except Exception:
            return []  # Return empty list on error
        
        # Single sort operation
        return sorted(text_elements, key=lambda x: (-x.font_size, x.y_pos))
    
    def _process_spans_optimized(self, spans) -> tuple:
        """Optimized span processing"""
        text_parts = []
        max_size = 0
        combined_flags = 0
        
        for span in spans:
            text_parts.append(span.get("text", ""))
            size = span.get("size", 0)
            if size > max_size:
                max_size = size
                combined_flags = span.get("flags", 0)
        
        return ''.join(text_parts).strip(), max_size, combined_flags
    
    def merge_text_fragments_optimized(self, fragments: List[str]) -> List[str]:
        """Optimized fragment merging"""
        if not fragments:
            return []
        
        merged = []
        current_line = ""
        
        for fragment in fragments:
            fragment = fragment.strip()
            if not fragment:
                continue
            
            # Check if this starts a new heading
            if self._is_heading_start(fragment) or not current_line:
                if current_line and len(current_line) > self.config.min_heading_length:
                    merged.append(current_line.strip())
                current_line = fragment
            else:
                current_line = f"{current_line} {fragment}" if current_line else fragment
        
        # Don't forget the last line
        if current_line and len(current_line) > self.config.min_heading_length:
            merged.append(current_line.strip())
        
        return merged
    
    def _is_heading_start(self, text: str) -> bool:
        """Check if text starts a new heading with multilingual support"""
        if not text:
            return False
        
        # Check for CJK characters
        if self._has_cjk_characters(text):
            # For CJK, check for chapter markers, numbers, or uppercase Latin mixed in
            return (text[0].isupper() or 
                    text.startswith(tuple(f'{i}.' for i in range(1, 10))) or
                    text.startswith(tuple(f'第{i}' for i in range(1, 10))) or  # Japanese chapter markers
                    text.startswith(tuple(f'{i}章' for i in range(1, 10))) or  # Japanese chapter
                    text.startswith(tuple(f'제{i}장' for i in range(1, 10))) or  # Korean chapter
                    any(char in text[:5] for char in '第章節編部제장'))  # Common CJK heading markers
        
        # Check for other non-Latin scripts  
        if self._has_non_latin_characters(text):
            # For non-Latin scripts, be more permissive
            return (text[0].isupper() or 
                    text.startswith(tuple(f'{i}.' for i in range(1, 10))) or
                    any(char.isupper() for char in text[:3]) or
                    'الفصل' in text or 'Глава' in text)  # Arabic/Russian chapter markers
        
        # Original Latin-based logic
        return (text[0].isupper() or 
                text.startswith(tuple(f'{i}.' for i in range(1, 10))))
