import json
from pathlib import Path
from typing import Dict, Any

class ExtractorConfig:
    """Flexible configuration class for PDF outline extraction"""
    
    def __init__(self, **kwargs):
        # Default values
        self.defaults = {
            # Text processing
            'min_heading_length': 5,
            'max_heading_length': 200,
            'min_font_size': 10,
            'exclusion_ratio_threshold': 0.3,
            
            # Heading detection
            'confidence_threshold': 0.7,
            'max_outline_depth': 6,
            'font_size_h1_threshold': 18,
            'font_size_h2_threshold': 16,
            'font_size_h3_threshold': 14,
            
            # Performance
            'max_workers': 4,
            
            # Batch processing
            'batch_size_multiplier': 2
        }
        
        # Set defaults
        for key, value in self.defaults.items():
            setattr(self, key, value)
        
        # Override with provided values
        for key, value in kwargs.items():
            if key in self.defaults:
                setattr(self, key, value)
        
        self._validate()
    
    def _validate(self):
        """Validate configuration values"""
        if self.min_heading_length < 1:
            self.min_heading_length = 1
        if self.max_heading_length < self.min_heading_length:
            self.max_heading_length = self.min_heading_length + 50
        if not 0.1 <= self.confidence_threshold <= 1.0:
            self.confidence_threshold = 0.7
        if self.max_workers < 1:
            self.max_workers = 1
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ExtractorConfig':
        """Load configuration from JSON file"""
        config_path = Path(config_path)
        if not config_path.exists():
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except Exception as e:
            print(f"Warning: Error loading config from {config_path}: {e}")
            print("Using default configuration")
            return cls()
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = {key: getattr(self, key) for key in self.defaults.keys()}
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def update(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if key in self.defaults:
                setattr(self, key, value)
        self._validate()
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return getattr(self, key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {key: getattr(self, key) for key in self.defaults.keys()}
    
    def __repr__(self):
        return f"ExtractorConfig({self.to_dict()})"
