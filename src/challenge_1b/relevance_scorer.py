from typing import List, Dict
from .embedding_model import OptimizedTFIDFProcessor
from challenge_1b.embedding_model import OptimizedTFIDFProcessor


class RelevanceScorer:
    """
    Uses OptimizedTFIDFProcessor to score relevance of each document
    to a given persona query or job description.
    """

    def __init__(self, max_features: int = 10000):
        self.tfidf = OptimizedTFIDFProcessor(max_features=max_features)

    def score_documents(
        self,
        documents: List[str],
        doc_ids: List[str],
        persona_query: str
    ) -> List[Dict[str, float]]:
        """
        Score how relevant each document is to the persona_query.

        Args:
            documents: List of document texts.
            doc_ids: Corresponding list of document IDs.
            persona_query: The query text representing the persona's needs.

        Returns:
            List of dicts: { "id": doc_id, "score": relevance_score }.
        """
        # Fit and transform all documents plus the persona query
        corpus = documents + [persona_query]
        matrix, features = self.tfidf.fit_transform_optimized(corpus)
        # Last row is the persona vector
        persona_vec = matrix[-1]
        doc_matrix = matrix[:-1]

        # Compute similarity scores
        similarities = self.tfidf.compute_similarities(doc_matrix, doc_ids)
        # Extract only the score for persona
        scored = [
            {"id": sim["id"], "score": sim["similarities"].get(sim["id"], 0.0)}
            for sim in similarities
        ]
        # Sort by descending score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
