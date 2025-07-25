import os
import json
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class OptimizedConfig:
    """Optimized configuration settings."""

    # Processing settings
    max_workers: int = int(os.getenv('WORKERS', '4'))
    chunk_size: int = int(os.getenv('CHUNK_SIZE', '10'))
    max_memory_mb: int = int(os.getenv('MAX_MEMORY_MB', '4096'))

    # Caching settings
    cache_ttl: int = int(os.getenv('CACHE_TTL', '3600'))
    cache_size: int = int(os.getenv('CACHE_SIZE', '1000'))
    redis_url: Optional[str] = os.getenv('REDIS_URL')

    # PDF processing
    pdf_dpi: int = int(os.getenv('PDF_DPI', '150'))
    max_pdf_size_mb: int = int(os.getenv('MAX_PDF_SIZE_MB', '500'))

    # TF-IDF settings  
    max_features: int = int(os.getenv('MAX_FEATURES', '10000'))
    min_df: int = int(os.getenv('MIN_DF', '2'))
    max_df: float = float(os.getenv('MAX_DF', '0.85'))

    # Performance monitoring
    enable_profiling: bool = os.getenv('ENABLE_PROFILING', 'false').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')

    # Resource limits
    memory_threshold: float = float(os.getenv('MEMORY_THRESHOLD', '0.8'))
    cpu_threshold: float = float(os.getenv('CPU_THRESHOLD', '0.9'))

    @classmethod
    def load_optimized(cls) -> 'OptimizedConfig':
        """Load optimized configuration based on environment."""
        return cls()


def load_config(challenge_name: str):
    """Load configuration for a specific challenge"""
    
    # Try to load from config files
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_file = config_dir / f"{challenge_name}.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            return OptimizedConfig(**config_data)
        except Exception as e:
            print(f"Warning: Could not load config from {config_file}: {e}")
    
    # Return default config
    return OptimizedConfig()
