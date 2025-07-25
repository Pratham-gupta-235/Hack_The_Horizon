import numpy as np
from typing import List, Tuple, Dict
from numba import jit, prange
from sklearn.feature_extraction.text import TfidfVectorizer
from functools import lru_cache
from ..shared.config import OptimizedConfig  


class EmbeddingModel:
    """
    Optimized TF-IDF processor with performance enhancements.
    """

    def __init__(
        self,
        max_features: int = 10000,
        use_idf: bool = True,
        ngram_range: Tuple[int, int] = (1, 2),
        max_df: float = 0.85,
        min_df: int = 2
    ):
        # Configure TF-IDF vectorizer for speed and quality
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            use_idf=use_idf,
            stop_words="english",
            ngram_range=ngram_range,
            max_df=max_df,
            min_df=min_df,
            lowercase=True,
            strip_accents="unicode",
            norm="l2",
            smooth_idf=True,
            sublinear_tf=True
        )

    @jit(nopython=True)
    def _fast_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors using JIT for speed.
        """
        dot = 0.0
        norm_a = 0.0
        norm_b = 0.0
        for i in prange(a.shape[0]):
            dot += a[i] * b[i]
            norm_a += a[i] ** 2
            norm_b += b[i] ** 2
        if norm_a > 0 and norm_b > 0:
            return dot / (np.sqrt(norm_a) * np.sqrt(norm_b))
        return 0.0

    @lru_cache(maxsize=128)
    def _cached_feature_names(self) -> Tuple[str, ...]:
        """
        Cache feature names to avoid repeated calls to vectorizer.
        """
        return tuple(self.vectorizer.get_feature_names_out())

    def fit_transform_optimized(self, documents: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        Fit the TF-IDF vectorizer on the documents and transform into a dense matrix.

        Args:
            documents: List of raw text documents.

        Returns:
            tfidf_matrix: 2D numpy array of TF-IDF features.
            feature_names: List of feature names.
        """
        # Batch processing for large corpora
        batch_size = 1000
        if len(documents) > batch_size:
            from scipy.sparse import vstack
            partial_matrices = []
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                if i == 0:
                    partial = self.vectorizer.fit_transform(batch)
                else:
                    partial = self.vectorizer.transform(batch)
                partial_matrices.append(partial)
            sparse_matrix = vstack(partial_matrices)
        else:
            sparse_matrix = self.vectorizer.fit_transform(documents)

        dense_matrix = sparse_matrix.toarray()
        features = list(self._cached_feature_names())
        return dense_matrix, features

    def compute_similarities(
        self,
        tfidf_matrix: np.ndarray,
        ids: List[str]
    ) -> List[Dict[str, float]]:
        """
        Compute pairwise cosine similarities between each document vector.

        Args:
            tfidf_matrix: 2D array where each row is a TF-IDF vector.
            ids: List of document identifiers.

        Returns:
            List of dicts mapping document_id -> similarity score.
        """
        results = []
        n = tfidf_matrix.shape[0]
        for i in range(n):
            row = tfidf_matrix[i]
            sims = {}
            for j in range(n):
                if i == j:
                    continue
                sims[ids[j]] = float(self._fast_similarity(row, tfidf_matrix[j]))
            # Keep top-n if desired, or return full dict
            results.append({"id": ids[i], "similarities": sims})
        return results
