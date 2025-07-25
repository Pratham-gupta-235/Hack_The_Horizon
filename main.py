#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Combined Solution
Main entry point supporting both Challenge 1a and Challenge 1b
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_banner():
    """Display the application banner"""
    print("\n" + "="*70)
    print("🚀 Adobe India Hackathon 2025 - Combined Solution")
    print("="*70)
    print("📋 Challenge 1a: PDF Outline Extraction")
    print("🎯 Challenge 1b: Persona-Driven Document Intelligence")
    print("="*70)


def get_mode_choice() -> str:
    """Get user choice for which challenge to run"""
    print("\n🎯 Select Mode:")
    print("1. Challenge 1a - PDF Outline Extraction")
    print("2. Challenge 1b - Persona-Driven Document Intelligence") 
    print("3. Both - Run both challenges sequentially")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\n👉 Enter your choice (1-4): ").strip()
            if choice == "1":
                return "1a"
            elif choice == "2":
                return "1b"
            elif choice == "3":
                return "both"
            elif choice == "4":
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)


def setup_directories():
    """Setup input and output directories"""
    base_dir = Path(__file__).parent
    
    # Create input directory if it doesn't exist
    input_dir = base_dir / "input"
    input_dir.mkdir(exist_ok=True)
    
    # Create output directories
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    challenge_1a_output = output_dir / "challenge_1a"
    challenge_1b_output = output_dir / "challenge_1b"
    
    challenge_1a_output.mkdir(exist_ok=True)
    challenge_1b_output.mkdir(exist_ok=True)
    
    return str(input_dir), str(challenge_1a_output), str(challenge_1b_output)


def run_challenge_1a(input_dir: str, output_dir: str) -> bool:
    """Run Challenge 1a - PDF Outline Extraction"""
    try:
        print("\n📋 Starting Challenge 1a - PDF Outline Extraction")
        print("-" * 50)
        
        from src.challenge_1a.main import RobustPDFProcessor
        from src.shared.config import load_config
        
        # Load configuration
        config = load_config("challenge_1a")
        
        # Initialize processor
        processor = RobustPDFProcessor(config)
        
        # Process PDFs
        start_time = time.time()
        results = processor.process_all_pdfs(input_dir, output_dir)
        processing_time = time.time() - start_time
        
        # Display results
        print(f"\n✅ Challenge 1a completed in {processing_time:.2f} seconds")
        print(f"📄 Processed {len(results)} PDFs")
        for pdf_file, pdf_time, success in results:
            status = "✅" if success else "❌"
            print(f"   {status} {pdf_file}: {pdf_time:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Challenge 1a failed: {e}")
        return False


def run_challenge_1b(input_dir: str, output_dir: str) -> bool:
    """Run Challenge 1b - Persona-Driven Document Intelligence"""
    try:
        print("\n🎯 Starting Challenge 1b - Persona-Driven Document Intelligence")
        print("-" * 50)
        
        from src.challenge_1b.main import PersonaDrivenProcessor
        
        # Get persona and job if not set
        persona = os.getenv('PERSONA', '').strip()
        job = os.getenv('JOB', '').strip()
        
        if not persona:
            print("\n👤 Please specify your persona/role:")
            print("Examples: Assistant Professor, Researcher, PhD Student, Data Scientist")
            persona = input("👤 Your persona: ").strip()
            
        if not job:
            print("\n💼 Please specify your specific task/job:")
            print("Examples: Research paper analysis, Technical documentation review")
            job = input("💼 Your job: ").strip()
        
        if not persona or not job:
            print("❌ Persona and job are required for Challenge 1b")
            return False
        
        # Initialize processor
        processor = PersonaDrivenProcessor(persona=persona, job=job)
        
        # Process PDFs
        start_time = time.time()
        results = processor.process_all_pdfs(input_dir, output_dir)
        processing_time = time.time() - start_time
        
        # Display results
        print(f"\n✅ Challenge 1b completed in {processing_time:.2f} seconds")
        print(f"📄 Processed {len(results)} PDFs")
        print(f"👤 Persona: {persona}")
        print(f"💼 Job: {job}")
        
        for pdf_file, pdf_time, success in results:
            status = "✅" if success else "❌"
            print(f"   {status} {pdf_file}: {pdf_time:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Challenge 1b failed: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Adobe Hackathon 2025 - Combined Solution")
    parser.add_argument("--mode", choices=["1a", "1b", "both"], 
                       help="Mode to run: 1a, 1b, or both")
    
    args = parser.parse_args()
    
    # Display banner
    display_banner()
    
    # Setup directories
    input_dir, output_1a, output_1b = setup_directories()
    
    # Check if PDFs exist in input directory
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"\n⚠️  No PDF files found in {input_dir}")
        print(f"📁 Please add PDF files to the input directory and try again.")
        return
    
    print(f"\n📁 Found {len(pdf_files)} PDF files in input directory")
    
    # Determine mode
    if args.mode:
        mode = args.mode
    else:
        mode = get_mode_choice()
    
    # Run selected mode
    overall_start = time.time()
    
    if mode == "1a":
        success = run_challenge_1a(input_dir, output_1a)
    elif mode == "1b":
        success = run_challenge_1b(input_dir, output_1b)
    elif mode == "both":
        print("\n🚀 Running both challenges sequentially...")
        success_1a = run_challenge_1a(input_dir, output_1a)
        success_1b = run_challenge_1b(input_dir, output_1b)
        success = success_1a and success_1b
    
    overall_time = time.time() - overall_start
    
    # Final summary
    print("\n" + "="*70)
    if success:
        print("🎉 All tasks completed successfully!")
    else:
        print("❌ Some tasks failed. Check logs for details.")
    
    print(f"⏱️  Total execution time: {overall_time:.2f} seconds")
    print(f"📂 Results saved to: {Path(__file__).parent / 'output'}")
    print("="*70)


if __name__ == "__main__":
    main()
