"""
Shared configuration management for Adobe Combined Solution
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Challenge1aConfig:
    """Configuration for Challenge 1a - PDF Outline Extraction"""
    min_heading_length: int = 5
    max_heading_length: int = 200
    min_font_size: float = 10
    exclusion_ratio_threshold: float = 0.3
    confidence_threshold: float = 0.7
    max_outline_depth: int = 6
    font_size_h1_threshold: float = 18
    font_size_h2_threshold: float = 16
    font_size_h3_threshold: float = 14
    max_workers: int = 6
    cache_enabled: bool = True
    cache_dir: str = "cache"
    batch_size_multiplier: int = 2


@dataclass
class Challenge1bConfig:
    """Configuration for Challenge 1b - Persona-Driven Intelligence"""
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    min_relevance_score: float = 0.1
    top_k_sections: int = 10
    embedding_model: str = "tfidf"
    cache_enabled: bool = True
    cache_dir: str = "cache"
    max_workers: int = 4


def load_config(challenge: str) -> Any:
    """Load configuration for specified challenge"""
    config_dir = Path(__file__).parent.parent.parent / "config"
    
    if challenge == "1a" or challenge == "challenge_1a":
        config_file = config_dir / "challenge_1a.json"
        default_config = Challenge1aConfig()
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update default config with loaded values
                for key, value in config_data.items():
                    if hasattr(default_config, key):
                        setattr(default_config, key, value)
                        
            except Exception as e:
                print(f"Warning: Could not load config from {config_file}: {e}")
                print("Using default configuration.")
        
        return default_config
    
    elif challenge == "1b" or challenge == "challenge_1b":
        config_file = config_dir / "challenge_1b.json"
        default_config = Challenge1bConfig()
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update default config with loaded values
                for key, value in config_data.items():
                    if hasattr(default_config, key):
                        setattr(default_config, key, value)
                        
            except Exception as e:
                print(f"Warning: Could not load config from {config_file}: {e}")
                print("Using default configuration.")
        
        return default_config
    
    else:
        raise ValueError(f"Unknown challenge: {challenge}")


def save_config(config: Any, challenge: str):
    """Save configuration to file"""
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / f"{challenge}.json"
    
    # Convert dataclass to dict
    if hasattr(config, '__dict__'):
        config_dict = config.__dict__
    else:
        config_dict = config
    
    with open(config_file, 'w') as f:
        json.dump(config_dict, f, indent=2)


def get_environment_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    return {
        'persona': os.getenv('PERSONA', ''),
        'job': os.getenv('JOB', ''),
        'mode': os.getenv('MODE', ''),
        'input_dir': os.getenv('INPUT_DIR', 'input'),
        'output_dir': os.getenv('OUTPUT_DIR', 'output'),
    }
