# src/main.py

from .challenge_1a.pdf_extractor import PDFOutlineExtractor
from .challenge_1b.embedding_model import EmbeddingModel
from .shared.config import OptimizedConfig
from .challenge_1b.relevance_scorer import RelevanceScorer


def main():
    # SETUP: You can adjust these config options as needed
    config = OptimizedConfig(
        max_workers=4,
        chunk_size=10,
        cache_ttl=3600,
        cache_size=1000
    )

    # Instantiate processors
    pdf_processor = PDFOutlineExtractor()
    embedding_model = EmbeddingModel()

    # Example: Process one or more PDFs
    pdf_files = ["input/document1.pdf", "input/document2.pdf"]  # UPDATE with actual filenames
    
    print("Example main function - update with actual processing logic")
    print("Available PDF files:", pdf_files)
    print("Config:", config)

if __name__ == "__main__":
    main()
