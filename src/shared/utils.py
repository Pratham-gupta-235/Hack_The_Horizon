"""
Shared utilities for Adobe Combined Solution
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Tuple, Optional


logger = logging.getLogger(__name__)


def find_pdf_files(directory: str) -> List[Path]:
    """Find all PDF files in a directory"""
    input_path = Path(directory)
    if not input_path.exists():
        logger.warning(f"Input directory does not exist: {directory}")
        return []
    
    pdf_files = list(input_path.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
    return pdf_files


def ensure_directory_exists(directory: str) -> Path:
    """Ensure a directory exists, create if it doesn't"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_filename(input_file: str, output_dir: str, suffix: str = "") -> str:
    """Generate output filename based on input file"""
    input_path = Path(input_file)
    output_path = Path(output_dir)
    
    if suffix:
        filename = f"{input_path.stem}_{suffix}.json"
    else:
        filename = f"{input_path.stem}.json"
    
    return str(output_path / filename)


def format_execution_time(seconds: float) -> str:
    """Format execution time in a human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def log_processing_start(filename: str, challenge: str):
    """Log the start of processing a file"""
    logger.info(f"[{challenge}] Processing: {filename}")


def log_processing_end(filename: str, challenge: str, execution_time: float, success: bool):
    """Log the end of processing a file"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    time_str = format_execution_time(execution_time)
    logger.info(f"[{challenge}] {status} {filename} ({time_str})")


def validate_pdf_file(file_path: str) -> bool:
    """Validate if a file is a valid PDF"""
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        if not path.suffix.lower() == '.pdf':
            logger.error(f"File is not a PDF: {file_path}")
            return False
        
        if path.stat().st_size == 0:
            logger.error(f"PDF file is empty: {file_path}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating PDF file {file_path}: {e}")
        return False


def create_processing_summary(results: List[Tuple[str, float, bool]], challenge: str) -> dict:
    """Create a processing summary from results"""
    total_files = len(results)
    successful_files = sum(1 for _, _, success in results if success)
    failed_files = total_files - successful_files
    total_time = sum(time for _, time, _ in results)
    
    summary = {
        "challenge": challenge,
        "total_files": total_files,
        "successful_files": successful_files,
        "failed_files": failed_files,
        "success_rate": (successful_files / total_files * 100) if total_files > 0 else 0,
        "total_processing_time": total_time,
        "average_time_per_file": total_time / total_files if total_files > 0 else 0,
        "files": [
            {
                "filename": filename,
                "processing_time": proc_time,
                "success": success
            }
            for filename, proc_time, success in results
        ]
    }
    
    return summary


def print_processing_summary(summary: dict):
    """Print a nicely formatted processing summary"""
    print(f"\n📊 {summary['challenge'].upper()} Processing Summary")
    print("-" * 50)
    print(f"📄 Total files: {summary['total_files']}")
    print(f"✅ Successful: {summary['successful_files']}")
    print(f"❌ Failed: {summary['failed_files']}")
    print(f"📈 Success rate: {summary['success_rate']:.1f}%")
    print(f"⏱️  Total time: {format_execution_time(summary['total_processing_time'])}")
    print(f"⏱️  Average time per file: {format_execution_time(summary['average_time_per_file'])}")
    
    if summary['failed_files'] > 0:
        print(f"\n❌ Failed files:")
        for file_info in summary['files']:
            if not file_info['success']:
                print(f"   • {file_info['filename']}")


class PerformanceMonitor:
    """Monitor performance metrics during processing"""
    
    def __init__(self, challenge_name: str):
        self.challenge_name = challenge_name
        self.start_time = None
        self.file_count = 0
        self.success_count = 0
        
    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        logger.info(f"Starting {self.challenge_name} processing...")
        
    def record_file(self, success: bool):
        """Record processing of a file"""
        self.file_count += 1
        if success:
            self.success_count += 1
            
    def finish(self) -> dict:
        """Finish monitoring and return metrics"""
        if self.start_time is None:
            return {}
            
        total_time = time.time() - self.start_time
        
        metrics = {
            "challenge": self.challenge_name,
            "total_time": total_time,
            "total_files": self.file_count,
            "successful_files": self.success_count,
            "failed_files": self.file_count - self.success_count,
            "success_rate": (self.success_count / self.file_count * 100) if self.file_count > 0 else 0,
            "average_time_per_file": total_time / self.file_count if self.file_count > 0 else 0
        }
        
        logger.info(f"Finished {self.challenge_name} processing in {format_execution_time(total_time)}")
        return metrics
