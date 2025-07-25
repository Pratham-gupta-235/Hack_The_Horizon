"""
Challenge 1a Main Processor - PDF Outline Extraction
Adapted from Adobe_Final project for the combined solution
"""

import time
import multiprocessing
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple
import logging
import json

from .pdf_extractor import PDFOutlineExtractor
from .config import ExtractorConfig

logger = logging.getLogger(__name__)


class RobustPDFProcessor:
    """Robust PDF processor with parallel processing and error handling"""
    
    def __init__(self, config):
        self.config = config
        self.extractor = PDFOutlineExtractor(config)
        self.retry_config = {"max_retries": 3, "backoff_factor": 2}
    
    def process_pdf_with_retry(self, pdf_file: str, input_dir: str, output_dir: str) -> Tuple[str, float, bool]:
        """Process a single PDF with retry logic"""
        input_path = Path(input_dir) / pdf_file
        output_path = Path(output_dir) / f"{input_path.stem}.json"
        
        logger.info(f"📄 Processing: {pdf_file}")
        start_time = time.time()
        
        success = False
        last_error = None
        
        for attempt in range(self.retry_config["max_retries"]):
            try:
                # Extract outline
                outline_data = self.extractor.extract_outline(str(input_path))
                
                # Save result
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(outline_data, f, ensure_ascii=False, indent=2)
                
                success = True
                duration = time.time() - start_time
                
                # Display results
                outline_count = len(outline_data.get('outline', []))
                logger.info(f"   ✅ Completed in {duration:.3f}s | Found {outline_count} outline items")
                
                break
                
            except Exception as e:
                last_error = e
                if attempt < self.retry_config["max_retries"] - 1:
                    wait_time = self.retry_config["backoff_factor"] ** attempt
                    logger.warning(f"   ⚠️  Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    duration = time.time() - start_time
                    logger.error(f"   ❌ Failed after {self.retry_config['max_retries']} attempts in {duration:.3f}s")
                    logger.error(f"      Error: {str(last_error)}")
        
        duration = time.time() - start_time
        return pdf_file, duration, success
    
    def process_all_pdfs(self, input_dir: str, output_dir: str) -> List[Tuple[str, float, bool]]:
        """Process all PDFs in the input directory"""
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return []
        
        # Find all PDFs
        pdf_files = [f.name for f in input_path.iterdir() if f.suffix.lower() == '.pdf']
        if not pdf_files:
            logger.warning(f"No PDF files found in: {input_dir}")
            return []
        
        logger.info(f"🚀 Starting PDF processing...")
        logger.info(f"📁 Input: {len(pdf_files)} PDF files")
        logger.info(f"📂 Output: {output_dir}")
        
        # Optimized worker count for hackathon constraints (8 CPUs available)
        max_workers = min(6, multiprocessing.cpu_count(), len(pdf_files), getattr(self.config, 'max_workers', 6))
        
        # Process in batches
        batch_size = max_workers * getattr(self.config, 'batch_size_multiplier', 2)
        
        results = []
        total_processed = 0
        total_successful = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(0, len(pdf_files), batch_size):
                batch = pdf_files[i:i + batch_size]
                futures = [
                    executor.submit(self.process_pdf_with_retry, pdf, input_dir, output_dir)
                    for pdf in batch
                ]
                for future in as_completed(futures):
                    try:
                        pdf_file, duration, success = future.result()
                        results.append((pdf_file, duration, success))
                        total_processed += 1
                        if success:
                            total_successful += 1
                    except Exception as e:
                        logger.error(f"   ❌ Unexpected error: {str(e)}")
        
        # Summary
        total_duration = sum(duration for _, duration, _ in results)
        logger.info(f"📊 Processing Summary:")
        logger.info(f"   ✅ Successful: {total_successful}/{total_processed}")
        logger.info(f"   ⏱️  Total time: {total_duration:.3f}s")
        logger.info(f"   📈 Average per file: {total_duration/total_processed:.3f}s")
        logger.info(f"   🔧 Workers used: {max_workers}")
        
        return results


def main():
    """Standalone main function for Challenge 1a"""
    from ..shared.config import load_config
    
    logger.info("🔍 PDF Outline Extractor - Challenge 1a")
    logger.info("=" * 50)
    
    # Check if running in Docker or local development
    if Path("/app").exists():
        # Docker paths
        input_dir = "/app/input"
        output_dir = "/app/output"
    else:
        # Local development paths
        base_path = Path(__file__).parent.parent.parent
        input_dir = str(base_path / "input")
        output_dir = str(base_path / "output" / "challenge_1a")
    
    # Load config
    config = load_config("1a")
    
    # Process
    start_total = time.time()
    processor = RobustPDFProcessor(config)
    results = processor.process_all_pdfs(input_dir, output_dir)
    
    total_duration = time.time() - start_total
    logger.info(f"🎉 All processing completed in {total_duration:.3f}s")
    logger.info("=" * 50)
    
    return results


if __name__ == "__main__":
    main()
