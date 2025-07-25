
# OPTIMIZED PDF PROCESSOR WITH PERFORMANCE ENHANCEMENTS
# File: optimized_pdf_processor.py

import fitz  # PyMuPDF
import numpy as np
from numba import jit, prange
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache
import cachetools
import gc
import logging
from contextlib import contextmanager
import mmap
import os
from dataclasses import dataclass
from pathlib import Path
from src.challenge_1a.cache_manager import TTLCacheManager
from shared.config import ProcessingConfig
from shared.utils import check_memory_usage, setup_logging  
from challenge_1a.cache_manager import TTLCacheManager


cache = TTLCacheManager(maxsize=1000, ttl=3600)
cache_key = f"outline_{pdf_path}_{options_hash}"
result = cache.get(cache_key)
if result is None:
    result = expensive_processing_function(pdf_path)
    cache.set(cache_key, result)


@dataclass
class ProcessingConfig:
    """Configuration class for PDF processing settings."""
    max_workers: int = 4
    chunk_size: int = 10
    cache_ttl: int = 3600
    cache_size: int = 1000
    memory_threshold: float = 0.8  # 80% memory usage threshold

class OptimizedPDFProcessor:
    """High-performance PDF processor with memory and speed optimizations."""

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.cache = cachetools.TTLCache(
            maxsize=config.cache_size, 
            ttl=config.cache_ttl
        )
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup optimized logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @contextmanager
    def managed_pdf_file(self, pdf_path: str):
        """Context manager for proper PDF file resource management."""
        pdf_doc = None
        try:
            # Use memory mapping for large files
            if os.path.getsize(pdf_path) > 100 * 1024 * 1024:  # > 100MB
                with open(pdf_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                        pdf_doc = fitz.open(stream=mmapped_file, filetype="pdf")
                        yield pdf_doc
            else:
                pdf_doc = fitz.open(pdf_path)
                yield pdf_doc
        finally:
            if pdf_doc:
                pdf_doc.close()
            gc.collect()  # Force garbage collection

    @lru_cache(maxsize=128)
    def _get_cached_page_text(self, page_hash: str, page_num: int) -> str:
        """Cache extracted text using page hash for deduplication."""
        return self._extract_page_text_optimized(page_num)

    @jit(nopython=True)
    def _process_text_array(self, text_array: np.ndarray) -> np.ndarray:
        """JIT-compiled text processing for numerical operations."""
        result = np.zeros_like(text_array)
        for i in prange(len(text_array)):
            # Example: character frequency analysis
            result[i] = len(set(text_array[i])) if text_array[i] else 0
        return result

    def extract_text_optimized(self, pdf_path: str) -> Dict[str, Any]:
        """
        Optimized text extraction with memory management and caching.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted text and metadata
        """
        cache_key = f"text_extract_{Path(pdf_path).stat().st_mtime}_{pdf_path}"

        # Check cache first
        if cache_key in self.cache:
            self.logger.info(f"Cache hit for {pdf_path}")
            return self.cache[cache_key]

        result = {
            "pages": [],
            "metadata": {},
            "processing_time": 0,
            "memory_usage": 0
        }

        try:
            with self.managed_pdf_file(pdf_path) as pdf_doc:
                total_pages = pdf_doc.page_count

                # Process in chunks to manage memory
                for chunk_start in range(0, total_pages, self.config.chunk_size):
                    chunk_end = min(chunk_start + self.config.chunk_size, total_pages)
                    chunk_texts = []

                    for page_num in range(chunk_start, chunk_end):
                        page = pdf_doc[page_num]

                        # Optimized text extraction
                        text_dict = page.get_text("dict")
                        text = self._extract_structured_text(text_dict)

                        chunk_texts.append({
                            "page_number": page_num + 1,
                            "text": text,
                            "char_count": len(text)
                        })

                        # Clear page cache periodically
                        if page_num % 100 == 0:
                            page.get_textpage().clear()

                    result["pages"].extend(chunk_texts)

                    # Memory management
                    if self._check_memory_usage() > self.config.memory_threshold:
                        gc.collect()

                result["metadata"] = {
                    "total_pages": total_pages,
                    "total_chars": sum(p["char_count"] for p in result["pages"])
                }

        except Exception as e:
            self.logger.error(f"Error processing {pdf_path}: {str(e)}")
            raise

        # Cache the result
        self.cache[cache_key] = result
        return result

    def _extract_structured_text(self, text_dict: Dict) -> str:
        """Extract and structure text from PyMuPDF text dictionary."""
        text_lines = []

        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    if line_text.strip():
                        text_lines.append(line_text.strip())

        return "\n".join(text_lines)

    def _check_memory_usage(self) -> float:
        """Check current memory usage percentage."""
        import psutil
        return psutil.virtual_memory().percent / 100.0

    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple PDFs in parallel with optimized resource management.

        Args:
            pdf_paths: List of PDF file paths

        Returns:
            List of processing results
        """
        results = []

        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.extract_text_optimized, path): path 
                for path in pdf_paths
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    result["file_path"] = path
                    results.append(result)
                    self.logger.info(f"Completed processing: {path}")
                except Exception as e:
                    self.logger.error(f"Error processing {path}: {str(e)}")
                    results.append({
                        "file_path": path,
                        "error": str(e),
                        "pages": [],
                        "metadata": {}
                    })

        return results

# OPTIMIZED TF-IDF PROCESSOR
class OptimizedTFIDFProcessor:
    """Optimized TF-IDF processor with performance enhancements."""

    def __init__(self, max_features: int = 10000, use_idf: bool = True):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            use_idf=use_idf,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.85,
            min_df=2,
            lowercase=True,
            strip_accents='unicode',
            norm='l2',
            smooth_idf=True,
            sublinear_tf=True  # Use log scaling
        )

    @jit(nopython=True)
    def _fast_similarity_computation(self, matrix1: np.ndarray, matrix2: np.ndarray) -> np.ndarray:
        """JIT-compiled similarity computation."""
        result = np.zeros((matrix1.shape[0], matrix2.shape[0]))
        for i in prange(matrix1.shape[0]):
            for j in prange(matrix2.shape[0]):
                dot_product = 0.0
                norm1 = 0.0
                norm2 = 0.0
                for k in range(matrix1.shape[1]):
                    dot_product += matrix1[i, k] * matrix2[j, k]
                    norm1 += matrix1[i, k] ** 2
                    norm2 += matrix2[j, k] ** 2

                if norm1 > 0 and norm2 > 0:
                    result[i, j] = dot_product / (np.sqrt(norm1) * np.sqrt(norm2))

        return result

    def fit_transform_optimized(self, documents: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        Optimized TF-IDF fitting and transformation.

        Args:
            documents: List of text documents

        Returns:
            Tuple of (TF-IDF matrix, feature names)
        """
        # Batch processing for large document collections
        batch_size = 1000

        if len(documents) > batch_size:
            # Process in batches
            tfidf_matrices = []

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                if i == 0:
                    # Fit on first batch
                    batch_matrix = self.vectorizer.fit_transform(batch)
                else:
                    # Transform subsequent batches
                    batch_matrix = self.vectorizer.transform(batch)

                tfidf_matrices.append(batch_matrix)

            # Combine matrices
            from scipy.sparse import vstack
            tfidf_matrix = vstack(tfidf_matrices)
        else:
            tfidf_matrix = self.vectorizer.fit_transform(documents)

        feature_names = self.vectorizer.get_feature_names_out().tolist()

        return tfidf_matrix.toarray(), feature_names

# USAGE EXAMPLE
if __name__ == "__main__":
    # Configuration
    config = ProcessingConfig(
        max_workers=4,
        chunk_size=10,
        cache_ttl=3600,
        cache_size=1000
    )

    # Initialize processors
    pdf_processor = OptimizedPDFProcessor(config)
    tfidf_processor = OptimizedTFIDFProcessor()

    # Example usage
    pdf_files = ["document1.pdf", "document2.pdf"]

    # Process PDFs
    results = pdf_processor.process_multiple_pdfs(pdf_files)

    # Extract all text for TF-IDF
    all_texts = []
    for result in results:
        document_text = " ".join([page["text"] for page in result["pages"]])
        all_texts.append(document_text)

    # Apply TF-IDF
    if all_texts:
        tfidf_matrix, features = tfidf_processor.fit_transform_optimized(all_texts)
        print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
        print(f"Number of features: {len(features)}")
