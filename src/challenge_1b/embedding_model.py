"""
Lightweight embedding model for semantic similarity.
"""

import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Lightweight embedding model using TF-IDF for semantic similarity."""
    
    def __init__(self, model_cache_dir: str = "/app/models"):
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # TF-IDF parameters optimized for efficiency and quality
        self.vectorizer = TfidfVectorizer(
            max_features=5000,  # Limit vocabulary size for efficiency
            ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english',
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,  # Apply sublinear TF scaling
            norm='l2'
        )
        
        self.is_fitted = False
        self.vocabulary_cache_file = self.model_cache_dir / "tfidf_vocabulary.pkl"
        
        # Try to load pre-trained vocabulary if available
        self._load_cached_model()
    
    def _load_cached_model(self):
        """Load cached TF-IDF model if available."""
        try:
            if self.vocabulary_cache_file.exists():
                with open(self.vocabulary_cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    
                self.vectorizer.vocabulary_ = cached_data['vocabulary']
                self.vectorizer.idf_ = cached_data['idf']
                self.is_fitted = True
                logger.info("Loaded cached TF-IDF model")
        except Exception as e:
            logger.warning(f"Could not load cached model: {str(e)}")
    
    def _save_model_cache(self):
        """Save TF-IDF model to cache."""
        try:
            cache_data = {
                'vocabulary': self.vectorizer.vocabulary_,
                'idf': self.vectorizer.idf_
            }
            
            with open(self.vocabulary_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
                
            logger.info("Saved TF-IDF model to cache")
        except Exception as e:
            logger.warning(f"Could not save model cache: {str(e)}")
    
    def fit_documents(self, documents: List[str]):
        """Fit the TF-IDF model on document corpus."""
        if not documents:
            logger.warning("No documents provided for fitting")
            return
        
        try:
            logger.info(f"Fitting TF-IDF model on {len(documents)} documents")
            self.vectorizer.fit(documents)
            self.is_fitted = True
            
            # Cache the model
            self._save_model_cache()
            
        except Exception as e:
            logger.error(f"Error fitting TF-IDF model: {str(e)}")
            raise
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            Matrix of text embeddings
        """
        if not texts:
            return np.array([])
        
        if not self.is_fitted:
            # If not fitted, fit on the input texts
            self.fit_documents(texts)
        
        try:
            embeddings = self.vectorizer.transform(texts)
            return embeddings.toarray()
        except Exception as e:
            logger.error(f"Error encoding texts: {str(e)}")
            # Fallback: refit and try again
            self.fit_documents(texts)
            embeddings = self.vectorizer.transform(texts)
            return embeddings.toarray()
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            embeddings = self.encode_texts([text1, text2])
            if embeddings.shape[0] < 2:
                return 0.0
            
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.warning(f"Error computing similarity: {str(e)}")
            return 0.0
    
    def compute_similarities(self, query_text: str, candidate_texts: List[str]) -> List[float]:
        """
        Compute similarities between query and multiple candidates.
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            
        Returns:
            List of similarity scores
        """
        if not candidate_texts:
            return []
        
        try:
            all_texts = [query_text] + candidate_texts
            embeddings = self.encode_texts(all_texts)
            
            if embeddings.shape[0] < 2:
                return [0.0] * len(candidate_texts)
            
            query_embedding = embeddings[0:1]
            candidate_embeddings = embeddings[1:]
            
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Clamp similarities to [0, 1]
            similarities = np.clip(similarities, 0.0, 1.0)
            
            return similarities.tolist()
            
        except Exception as e:
            logger.warning(f"Error computing batch similarities: {str(e)}")
            return [0.0] * len(candidate_texts)
    
    def get_top_matches(self, query_text: str, candidate_texts: List[str], 
                       top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get top-k most similar texts to query.
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of top matches to return
            
        Returns:
            List of matches with indices and scores
        """
        similarities = self.compute_similarities(query_text, candidate_texts)
        
        # Create list of (index, score, text) tuples
        matches = [
            {
                'index': i,
                'score': score,
                'text': candidate_texts[i]
            }
            for i, score in enumerate(similarities)
        ]
        
        # Sort by score in descending order
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:top_k]
