# src/main.py

from challenge_1a.pdf_extractor import OptimizedPDFProcessor
from challenge_1b.embedding_model import OptimizedTFIDFProcessor
from shared.config import ProcessingConfig
from challenge_1b.relevance_scorer import RelevanceScorer
from challenge_1a.pdf_extractor import OptimizedPDFProcessor
from challenge_1b.relevance_scorer import RelevanceScorer



scorer = RelevanceScorer(max_features=5000)
scores = scorer.score_documents(doc_texts, doc_ids, persona_query)
print(scores)


def main():
    # SETUP: You can adjust these config options as needed
    config = ProcessingConfig(
        max_workers=4,
        chunk_size=10,
        cache_ttl=3600,
        cache_size=1000
    )

    # Instantiate processors
    pdf_processor = OptimizedPDFProcessor(config)
    tfidf_processor = OptimizedTFIDFProcessor()

    # Example: Process one or more PDFs
    pdf_files = ["input/document1.pdf", "input/document2.pdf"]  # UPDATE with actual filenames
    results = pdf_processor.process_multiple_pdfs(pdf_files)

    # Gather all text for TF-IDF analysis (persona-driven challenge)
    all_texts = [" ".join([page["text"] for page in result["pages"]]) for result in results]
    if all_texts:
        tfidf_matrix, features = tfidf_processor.fit_transform_optimized(all_texts)
        print("TF-IDF matrix shape:", tfidf_matrix.shape)
        print("Features extracted:", features)

    # Print metadata as an example (optional)
    for result in results:
        print("File:", result.get("file_path", "N/A"))
        print("Metadata:", result.get("metadata", {}))

if __name__ == "__main__":
    main()
