"""
Challenge 1b Main Processor - Persona-Driven Document Intelligence
Adapted from adobe_1b project for the combined solution
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor
from .embedding_model import EmbeddingModel
from .relevance_scorer import RelevanceScorer
from .output_formatter import OutputFormatter

logger = logging.getLogger(__name__)


class PersonaDrivenProcessor:
    """Main processor for persona-driven document intelligence"""
    
    def __init__(self, persona: str, job: str):
        self.persona = persona
        self.job = job
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.text_processor = TextProcessor()
        self.embedding_model = EmbeddingModel()
        self.relevance_scorer = RelevanceScorer(max_features=10000)
        self.output_formatter = OutputFormatter()
    
    def process_single_pdf(self, pdf_file: Path, output_dir: str) -> Tuple[str, float, bool]:
        """Process a single PDF file"""
        logger.info(f"📄 Processing: {pdf_file.name}")
        start_time = time.time()
        
        try:
            # Extract text from PDF
            document_data = self.pdf_processor.extract_text_with_structure(pdf_file)
            document_data['filename'] = pdf_file.name
            
            # Process text (clean, chunk, etc.)
            processed_doc = self.text_processor.process_document(document_data)
            
            # Score relevance
            scored_sections = self.relevance_scorer.score_documents(
                [processed_doc], self.persona, self.job
            )
            
            # Format output
            output_data = self.output_formatter.format_output(
                scored_sections, self.persona, self.job, datetime.now()
            )
            
            # Save output
            output_file = Path(output_dir) / f"{pdf_file.stem}.json"
            self.output_formatter.save_json(output_data, output_file)
            
            duration = time.time() - start_time
            logger.info(f"   ✅ Completed in {duration:.3f}s")
            
            return pdf_file.name, duration, True
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"   ❌ Failed in {duration:.3f}s - Error: {str(e)}")
            return pdf_file.name, duration, False
    
    def process_all_pdfs(self, input_dir: str, output_dir: str) -> List[Tuple[str, float, bool]]:
        """Process all PDFs in the input directory and create consolidated output"""
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return []
        
        # Find PDF files
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in: {input_dir}")
            return []
        
        logger.info(f"🚀 Starting persona-driven processing...")
        logger.info(f"👤 Persona: {self.persona}")
        logger.info(f"💼 Job: {self.job}")
        logger.info(f"📁 Input: {len(pdf_files)} PDF files")
        logger.info(f"📂 Output: {output_dir}")
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Process all PDFs and collect data
        start_time = time.time()
        all_processed_docs = []
        results = []
        successful_files = []
        
        for pdf_file in pdf_files:
            logger.info(f"📄 Processing: {pdf_file.name}")
            file_start = time.time()
            
            try:
                # Extract text from PDF
                document_data = self.pdf_processor.extract_text_with_structure(pdf_file)
                document_data['filename'] = pdf_file.name
                
                # Process text (clean, chunk, etc.)
                processed_doc = self.text_processor.process_document(document_data)
                all_processed_docs.append(processed_doc)
                successful_files.append(pdf_file.name)
                
                duration = time.time() - file_start
                logger.info(f"   ✅ Completed in {duration:.3f}s")
                results.append((pdf_file.name, duration, True))
                
            except Exception as e:
                duration = time.time() - file_start
                logger.error(f"   ❌ Failed in {duration:.3f}s - Error: {str(e)}")
                results.append((pdf_file.name, duration, False))
        
        # If we have successfully processed documents, create consolidated output
        if all_processed_docs:
            logger.info(f"🎯 Creating consolidated analysis for {len(all_processed_docs)} documents")
            
            # Extract text content from processed documents for scoring
            doc_texts = []
            doc_ids = []
            for doc in all_processed_docs:
                # Combine all section content into one text
                full_text = ' '.join([
                    section.get('cleaned_content', '') 
                    for section in doc.get('processed_sections', [])
                ])
                doc_texts.append(full_text)
                doc_ids.append(doc.get('filename', 'unknown'))
            
            # Create persona query
            persona_query = f"As a {self.persona}, I need to {self.job}"
            
            # Score relevance across all documents
            all_scored_sections = self.relevance_scorer.score_documents(
                doc_texts, doc_ids, persona_query
            )
            
            # Create consolidated output
            consolidated_output = self.output_formatter.format_consolidated_output(
                all_scored_sections, successful_files, self.persona, self.job, datetime.now()
            )
            
            # Save consolidated output
            output_file = Path(output_dir) / "consolidated_analysis.json"
            self.output_formatter.save_json(consolidated_output, output_file)
            
            logger.info(f"💾 Saved consolidated analysis to {output_file}")
        
        # Summary
        total_duration = time.time() - start_time
        total_successful = len([r for r in results if r[2]])
        logger.info(f"📊 Processing Summary:")
        logger.info(f"   ✅ Successful: {total_successful}/{len(pdf_files)}")
        logger.info(f"   ⏱️  Total time: {total_duration:.3f}s")
        logger.info(f"   📈 Average per file: {total_duration/len(pdf_files):.3f}s")
        
        return results


def get_user_input():
    """Get persona and job from user input if not provided via environment."""
    persona = os.getenv('PERSONA', '').strip()
    job = os.getenv('JOB', '').strip()
    
    # If running interactively and no persona/job provided, prompt user
    if not persona or not job:
        if sys.stdin.isatty():  # Interactive mode
            logger.info("🎯 Adobe Hackathon Round 1B - Persona-Driven Document Intelligence")
            
            if not persona:
                logger.info("📋 Please specify your persona/role:")
                logger.info("Examples: Assistant Professor, Researcher, PhD Student, Data Scientist")
                persona = input("👤 Your persona: ").strip()
                
                if not persona:
                    logger.error("Persona is required!")
                    sys.exit(1)
            
            if not job:
                logger.info(f"🎯 What specific task/job do you want to accomplish as a {persona}?")
                logger.info("Examples: 'Find teaching resources for semester planning'")
                job = input("📝 Your job/task: ").strip()
                
                if not job:
                    logger.error("Job description is required!")
                    sys.exit(1)
        else:
            # Non-interactive mode - use defaults with warning
            logger.warning("No PERSONA or JOB specified. Using defaults.")
            persona = persona or "Assistant Professor"
            job = job or "Shortlist best teaching resources for semester planning"
    
    return persona, job


def main():
    """Standalone main function for Challenge 1b"""
    logger.info("🎯 Persona-Driven Document Intelligence - Challenge 1b")
    logger.info("=" * 50)
    
    start_time = time.time()
    
    try:
        # Get persona and job from user input or environment
        persona, job = get_user_input()
        
        # Get directory configuration
        if Path("/app").exists():
            # Docker paths
            input_dir = "/app/input"
            output_dir = "/app/output"
        else:
            # Local development paths
            base_path = Path(__file__).parent.parent.parent
            input_dir = str(base_path / "input")
            output_dir = str(base_path / "output" / "challenge_1b")
        
        # Initialize processor
        processor = PersonaDrivenProcessor(persona=persona, job=job)
        
        # Process all PDFs
        results = processor.process_all_pdfs(input_dir, output_dir)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"🎉 All processing completed in {processing_time:.2f} seconds")
        logger.info("=" * 50)
        
        return results
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)
        return []


if __name__ == "__main__":
    main()
