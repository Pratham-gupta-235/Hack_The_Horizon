"""
Relevance scoring module for persona-driven document analysis.
"""

import logging
import re
from typing import List, Dict, Any, Tuple
import numpy as np
from .embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Scores document sections based on persona and job relevance."""
    
    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model
        
        # Persona-specific keywords and weights
        self.persona_keywords = {
            'assistant professor': {
                'teaching': 2.0, 'education': 2.0, 'curriculum': 2.0, 'students': 1.8,
                'learning': 1.8, 'pedagogy': 2.0, 'course': 1.8, 'classroom': 1.5,
                'lecture': 1.5, 'academic': 1.8, 'research': 1.5, 'university': 1.3
            },
            'researcher': {
                'research': 2.0, 'study': 1.8, 'analysis': 1.8, 'methodology': 2.0,
                'findings': 1.8, 'data': 1.8, 'experiment': 1.8, 'hypothesis': 1.5,
                'publication': 1.5, 'investigation': 1.5, 'academic': 1.5
            },
            'student': {
                'learning': 2.0, 'study': 2.0, 'education': 1.8, 'knowledge': 1.8,
                'understanding': 1.8, 'skills': 1.8, 'assignment': 1.5, 'exam': 1.5,
                'course': 1.8, 'tutorial': 1.8, 'practice': 1.5
            },
            'manager': {
                'management': 2.0, 'strategy': 1.8, 'leadership': 1.8, 'team': 1.8,
                'planning': 1.8, 'decision': 1.8, 'process': 1.5, 'efficiency': 1.5,
                'performance': 1.8, 'organization': 1.5, 'business': 1.5
            }
        }
        
        # Job-specific keywords
        self.job_keywords = {
            'teaching': ['curriculum', 'lesson', 'pedagogy', 'instruction', 'assessment'],
            'research': ['methodology', 'analysis', 'findings', 'study', 'investigation'],
            'planning': ['strategy', 'roadmap', 'schedule', 'timeline', 'preparation'],
            'resources': ['materials', 'tools', 'references', 'bibliography', 'sources'],
            'evaluation': ['assessment', 'criteria', 'metrics', 'feedback', 'quality']
        }
    
    def score_documents(self, documents: List[Dict[str, Any]], 
                       persona: str, job: str) -> List[Dict[str, Any]]:
        """
        Score all document sections based on persona and job relevance.
        
        Args:
            documents: List of processed documents
            persona: User persona (e.g., "Assistant Professor")
            job: Job description or task
            
        Returns:
            List of scored sections sorted by relevance
        """
        logger.info(f"Scoring documents for persona: {persona}, job: {job}")
        
        # Prepare all sections for scoring
        all_sections = []
        for doc in documents:
            for section in doc.get('processed_sections', []):
                section_data = {
                    'document': doc['filename'],
                    'page': section['page_number'],
                    'section_title': section['cleaned_title'],
                    'content': section['cleaned_content'],
                    'chunks': section.get('chunks', []),
                    'key_phrases': section.get('key_phrases', []),
                    'word_count': section.get('word_count', 0),
                    'font_size': section.get('font_size', 0)
                }
                all_sections.append(section_data)
        
        # Create query from persona and job
        query_text = self._create_query_text(persona, job)
        logger.info(f"Query text: {query_text}")
        
        # Score each section
        scored_sections = []
        for section in all_sections:
            score_data = self._score_section(section, persona, job, query_text)
            if score_data['total_score'] > 0.1:  # Filter very low relevance
                scored_sections.append(score_data)
        
        # Sort by total score
        scored_sections.sort(key=lambda x: x['total_score'], reverse=True)
        
        logger.info(f"Scored {len(scored_sections)} relevant sections")
        return scored_sections
    
    def _create_query_text(self, persona: str, job: str) -> str:
        """Create comprehensive query text from persona and job."""
        # Combine persona and job description
        query_parts = [persona.lower(), job.lower()]
        
        # Add persona-specific keywords
        persona_key = persona.lower().replace(' ', '_')
        for key_persona in self.persona_keywords:
            if key_persona in persona_key:
                keywords = list(self.persona_keywords[key_persona].keys())
                query_parts.extend(keywords[:5])  # Add top 5 keywords
                break
        
        # Add job-specific keywords
        job_lower = job.lower()
        for job_type, keywords in self.job_keywords.items():
            if job_type in job_lower:
                query_parts.extend(keywords)
        
        return ' '.join(query_parts)
    
    def _score_section(self, section: Dict[str, Any], persona: str, 
                      job: str, query_text: str) -> Dict[str, Any]:
        """Score a single section for relevance."""
        
        # Combine title and content for scoring
        section_text = f"{section['section_title']} {section['content']}"
        
        # 1. Semantic similarity score (40% weight)
        semantic_score = self.embedding_model.compute_similarity(query_text, section_text)
        
        # 2. Keyword matching score (30% weight)
        keyword_score = self._compute_keyword_score(section, persona, job)
        
        # 3. Structural importance score (20% weight)
        structural_score = self._compute_structural_score(section)
        
        # 4. Content quality score (10% weight)
        quality_score = self._compute_quality_score(section)
        
        # Combine scores
        total_score = (
            0.4 * semantic_score +
            0.3 * keyword_score +
            0.2 * structural_score +
            0.1 * quality_score
        )
        
        # Score subsections
        subsection_analysis = self._score_subsections(section, query_text)
        
        score_data = {
            'document': section['document'],
            'page': section['page'],
            'section_title': section['section_title'],
            'text': section['content'],  # Keep full content, don't truncate
            'importance_rank': 0,  # Will be set after sorting
            'relevance_score': total_score,  # Add this field for easier access
            'total_score': total_score,
            'score_breakdown': {
                'semantic_score': semantic_score,
                'keyword_score': keyword_score,
                'structural_score': structural_score,
                'quality_score': quality_score
            },
            'subsection_analysis': subsection_analysis,
            'key_phrases': section.get('key_phrases', [])
        }
        
        return score_data
    
    def _compute_keyword_score(self, section: Dict[str, Any], 
                             persona: str, job: str) -> float:
        """Compute keyword-based relevance score."""
        text = f"{section['section_title']} {section['content']}".lower()
        
        # Get persona keywords
        persona_key = persona.lower().replace(' ', '_')
        persona_weights = {}
        
        for key_persona in self.persona_keywords:
            if key_persona in persona_key:
                persona_weights = self.persona_keywords[key_persona]
                break
        
        # Score based on keyword presence and weights
        score = 0.0
        total_weight = 0.0
        
        for keyword, weight in persona_weights.items():
            if keyword in text:
                # Count occurrences with diminishing returns
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                keyword_score = min(1.0, count * 0.3)  # Max 1.0 per keyword
                score += keyword_score * weight
                total_weight += weight
        
        # Add job-specific keyword scoring
        job_lower = job.lower()
        for job_type, keywords in self.job_keywords.items():
            if job_type in job_lower:
                for keyword in keywords:
                    if keyword in text:
                        count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                        score += min(1.0, count * 0.2) * 1.5  # Job relevance bonus
                        total_weight += 1.5
        
        # Normalize by total possible weight
        if total_weight > 0:
            score = min(1.0, score / total_weight)
        
        return score
    
    def _compute_structural_score(self, section: Dict[str, Any]) -> float:
        """Compute structural importance score."""
        score = 0.5  # Base score
        
        # Font size indicates importance
        font_size = section.get('font_size', 0)
        if font_size > 14:
            score += 0.3
        elif font_size > 12:
            score += 0.2
        elif font_size > 10:
            score += 0.1
        
        # Title characteristics
        title = section.get('section_title', '').lower()
        
        # Header patterns that suggest importance
        important_patterns = [
            r'introduction', r'methodology', r'results', r'conclusion',
            r'overview', r'summary', r'key', r'important', r'main',
            r'objective', r'goal', r'purpose', r'framework'
        ]
        
        for pattern in important_patterns:
            if re.search(pattern, title):
                score += 0.2
                break
        
        # Section length (moderate length preferred)
        word_count = section.get('word_count', 0)
        if 50 <= word_count <= 300:
            score += 0.2
        elif 300 < word_count <= 500:
            score += 0.1
        
        return min(1.0, score)
    
    def _compute_quality_score(self, section: Dict[str, Any]) -> float:
        """Compute content quality score."""
        content = section.get('content', '')
        
        if not content:
            return 0.0
        
        score = 0.5  # Base score
        
        # Check for structured content
        if re.search(r'[•\-\*]\s', content):  # Bullet points
            score += 0.2
        
        if re.search(r'\d+\.\s', content):  # Numbered lists
            score += 0.2
        
        # Check for academic/professional language
        academic_indicators = [
            'according to', 'research shows', 'studies indicate',
            'framework', 'methodology', 'analysis', 'findings'
        ]
        
        for indicator in academic_indicators:
            if indicator in content.lower():
                score += 0.1
        
        # Penalize very short or very long sections
        word_count = len(content.split())
        if word_count < 20:
            score *= 0.5
        elif word_count > 1000:
            score *= 0.8
        
        return min(1.0, score)
    
    def _score_subsections(self, section: Dict[str, Any], 
                          query_text: str) -> List[Dict[str, Any]]:
        """Score subsections/chunks within a section."""
        chunks = section.get('chunks', [])
        
        if not chunks:
            return []
        
        subsection_analysis = []
        
        for chunk in chunks[:5]:  # Limit to first 5 chunks
            chunk_text = chunk.get('text', '')
            if len(chunk_text.strip()) < 20:  # Skip very short chunks
                continue
            
            # Compute similarity with query
            similarity = self.embedding_model.compute_similarity(query_text, chunk_text)
            
            if similarity > 0.2:  # Only include relevant chunks
                subsection_analysis.append({
                    'subtext': chunk_text[:200] + ('...' if len(chunk_text) > 200 else ''),
                    'score': round(similarity, 3)
                })
        
        # Sort by score
        subsection_analysis.sort(key=lambda x: x['score'], reverse=True)
        
        return subsection_analysis[:3]  # Return top 3 subsections
