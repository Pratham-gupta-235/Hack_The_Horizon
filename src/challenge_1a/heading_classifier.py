import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class HeadingResult:
    """Result of heading classification"""
    level: str
    confidence: float
    reasoning: List[str]

class HeadingClassifier:
    """Advanced heading classification with scoring system"""
    
    def __init__(self, config):
        self.config = config
        self._patterns = self._compile_patterns()
        self._exclusion_cache = {}
        self._major_sections = self._define_major_sections()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Pre-compile all regex patterns"""
        return {
            'numbered_main': re.compile(r'^[1-9]\.(?!\d)', re.I),
            'numbered_sub': re.compile(r'^\d+\.\d+(?!\.)'),
            'numbered_subsub': re.compile(r'^\d+\.\d+\.\d+'),
            'appendix': re.compile(r'\b(appendix|annex)\b', re.I),
            'major_sections': re.compile(
                r'\b(introduction|summary|conclusion|references|bibliography|acknowledgements|abstract|overview)\b', 
                re.I
            ),
            'dates': re.compile(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}'),
            'times': re.compile(r'\d{1,2}:\d{2}(\s*(am|pm))?', re.I),
            'funding': re.compile(r'(\$|million|funding)', re.I),
            'timeline_months': re.compile(
                r'\b(march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b', 
                re.I
            )
        }
    
    def _define_major_sections(self) -> Dict[str, int]:
        """Define major section keywords and their priority"""
        return {
            'revision history': 1, 'table of contents': 1, 'acknowledgements': 1,
            'introduction': 1, 'overview': 1, 'references': 1, 'abstract': 1,
            'conclusion': 1, 'appendix': 1, 'bibliography': 1,
            'summary': 2, 'background': 2, 'approach': 2, 'evaluation': 2,
            'milestones': 2, 'business plan': 2, 'specific proposal': 2,
            'equitable access': 3, 'shared decision': 3, 'shared governance': 3,
            'local points': 3, 'guidance': 3, 'training': 3
        }
    
    def classify_heading(self, text: str, font_size: float, font_flags: int, 
                        context: Optional[Dict] = None) -> Optional[HeadingResult]:
        """Advanced heading classification with confidence scoring"""
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # Quick exclusion check
        if self._is_excluded(text_lower):
            return None
        
        # Calculate confidence score
        score, reasoning = self._calculate_confidence_score(text, text_lower, font_size, font_flags, context)
        
        if score >= self.config.confidence_threshold:
            level = self._determine_level_advanced(text, text_lower, font_size, score, context)
            return HeadingResult(level=level, confidence=score, reasoning=reasoning)
        
        return None
    
    def _is_excluded(self, text_lower: str) -> bool:
        """Quick exclusion check with caching"""
        cache_key = hash(text_lower)
        if cache_key in self._exclusion_cache:
            return self._exclusion_cache[cache_key]
        
        excluded = bool(
            self._patterns['dates'].search(text_lower) or
            self._patterns['times'].search(text_lower) or
            self._patterns['funding'].search(text_lower) or
            self._patterns['timeline_months'].search(text_lower)
        )
        
        self._exclusion_cache[cache_key] = excluded
        return excluded
    
    def _calculate_confidence_score(self, text: str, text_lower: str, font_size: float, 
                                   font_flags: int, context: Optional[Dict]) -> tuple[float, List[str]]:
        """Calculate confidence score for heading classification"""
        score = 0.0
        reasoning = []
        
        # Formatting indicators
        if font_flags & 16:  # Bold
            score += 0.3
            reasoning.append("bold formatting")
        
        if font_size >= self.config.font_size_h1_threshold:
            score += 0.4
            reasoning.append(f"large font size ({font_size})")
        elif font_size >= self.config.font_size_h2_threshold:
            score += 0.3
            reasoning.append(f"medium font size ({font_size})")
        elif font_size >= self.config.font_size_h3_threshold:
            score += 0.2
            reasoning.append(f"above-average font size ({font_size})")
        
        # Content indicators
        if self._patterns['numbered_main'].match(text):
            score += 0.5
            reasoning.append("numbered main section")
        elif self._patterns['numbered_sub'].match(text):
            score += 0.4
            reasoning.append("numbered subsection")
        elif self._patterns['numbered_subsub'].match(text):
            score += 0.3
            reasoning.append("numbered sub-subsection")
        
        if self._patterns['major_sections'].search(text_lower):
            score += 0.4
            reasoning.append("major section keyword")
        
        if self._patterns['appendix'].search(text_lower):
            score += 0.5
            reasoning.append("appendix section")
        
        # Structure indicators
        if text.endswith(':'):
            score += 0.2
            reasoning.append("ends with colon")
        
        if text.istitle():
            score += 0.15
            reasoning.append("title case")
        
        if text.isupper() and len(text) > 8:
            score += 0.2
            reasoning.append("all caps")
        
        # Length considerations
        length = len(text)
        if 10 <= length <= 80:
            score += 0.1
            reasoning.append("appropriate length")
        elif length > 200:
            score -= 0.2
            reasoning.append("too long for heading")
        
        # Context considerations
        if context:
            if context.get('position') == 'top_of_page':
                score += 0.1
                reasoning.append("top of page")
            
            if context.get('preceded_by_whitespace'):
                score += 0.05
                reasoning.append("preceded by whitespace")
        
        return min(score, 1.0), reasoning
    
    def _determine_level_advanced(self, text: str, text_lower: str, font_size: float, 
                                 score: float, context: Optional[Dict]) -> str:
        """Advanced level determination"""
        # Numbered sections take precedence
        if self._patterns['numbered_main'].match(text):
            return "H1"
        elif self._patterns['numbered_sub'].match(text):
            return "H2"
        elif self._patterns['numbered_subsub'].match(text):
            return "H3"
        
        # Major sections
        for section, priority in self._major_sections.items():
            if section in text_lower:
                return f"H{priority}"
        
        # Font size based with confidence adjustment
        if font_size >= self.config.font_size_h1_threshold and score >= 0.8:
            return "H1"
        elif font_size >= self.config.font_size_h2_threshold and score >= 0.7:
            return "H2"
        elif font_size >= self.config.font_size_h3_threshold:
            return "H3"
        else:
            return "H4"
