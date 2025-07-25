# Adobe India Hackathon 2025 - Combined Solution

## 🚀 Overview

A unified solution combining both **Challenge 1a (PDF Outline Extraction)** and **Challenge 1b (Persona-Driven Document Intelligence)** from the Adobe India Hackathon 2025.

## 🎯 Features

### Challenge 1a - PDF Outline Extraction
- **Fast Processing**: Processes PDFs in under 10 seconds (optimized for 50-page documents)
- **Universal Compatibility**: Works with any PDF format
- **Multilingual Support**: Handles Japanese, Chinese, Korean, Arabic, Hebrew, Cyrillic and other scripts
- **Intelligent Extraction**: Uses advanced text analysis and formatting detection
- **Resource Efficient**: Optimized for 8 CPU + 16GB RAM constraints

### Challenge 1b - Persona-Driven Document Intelligence
- **User-Configurable Personas**: Define your own role and specific job requirements
- **Intelligent PDF Processing**: Extracts structured text with headers and sections
- **Semantic Understanding**: TF-IDF based similarity matching
- **High Performance**: <60s processing, <1GB models, offline execution
- **Detailed Analytics**: Subsection analysis with confidence scores

## 🛠 Technology Stack

- **Language**: Python 3.10
- **PDF Processing**: PyMuPDF (open source)
- **ML/NLP**: scikit-learn, transformers, sentence-transformers
- **Parallel Processing**: ThreadPoolExecutor
- **Container**: Docker with linux/amd64 platform

## 🏗 Architecture

```
src/
├── main.py                  # Main entry point with mode selection
├── challenge_1a/            # Challenge 1a specific modules
│   ├── pdf_extractor.py     # PDF outline extraction engine
│   ├── text_processor.py    # Text cleaning and formatting
│   ├── heading_classifier.py # Intelligent heading detection
│   ├── outline_hierarchy.py # Structure building
│   └── cache_manager.py     # Performance caching
├── challenge_1b/            # Challenge 1b specific modules
│   ├── pdf_processor.py     # PDF text extraction
│   ├── text_processor.py    # Text cleaning and chunking
│   ├── embedding_model.py   # Lightweight TF-IDF embeddings
│   ├── relevance_scorer.py  # Persona-driven scoring algorithm
│   └── output_formatter.py  # JSON output formatting
└── shared/                  # Shared utilities
    ├── config.py            # Configuration management
    └── utils.py             # Common utilities
```

## 🚀 Quick Start

### Option 1: Interactive Mode
```bash
python main.py
```
This will prompt you to choose between:
- Challenge 1a: PDF Outline Extraction
- Challenge 1b: Persona-Driven Document Intelligence
- Both: Run both challenges sequentially

### Option 2: Direct Mode Selection
```bash
# Run Challenge 1a only
python main.py --mode 1a

# Run Challenge 1b only
python main.py --mode 1b

# Run both challenges
python main.py --mode both
```

### Option 3: Docker
```bash
# Build and run with Docker Compose
docker-compose up

# Or build manually
docker build -t adobe-combined .
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe-combined
```

## 📁 Input/Output Structure

```
input/           # Place your PDF files here
output/
├── challenge_1a/    # PDF outline extraction results
│   └── *.json       # Structured outline data
└── challenge_1b/    # Persona-driven analysis results
    └── *.json       # Relevance scoring and insights
```

## ⚙️ Configuration

### Challenge 1a Configuration (`config/challenge_1a.json`)
- Heading detection thresholds
- Font size parameters
- Performance settings

### Challenge 1b Configuration (`config/challenge_1b.json`)
- Persona definitions
- Scoring parameters
- Model settings

## 🔧 Environment Variables

```bash
# For Challenge 1b
export PERSONA="Your Role Here"
export JOB="Your Specific Task Here"

# For combined mode
export MODE="1a|1b|both"
```

## 📋 Requirements Compliance

### Challenge 1a
✅ **Execution Time**: ≤ 10 seconds for 50-page PDFs  
✅ **Resource Usage**: Works within 8 CPU + 16GB RAM  
✅ **Architecture**: AMD64 compatible  
✅ **Network**: No internet access required  
✅ **Open Source**: Uses only open-source libraries  

### Challenge 1b
✅ **Processing Time**: ≤ 60 seconds per document  
✅ **Model Size**: <1GB total model size  
✅ **Offline Execution**: No internet access required  
✅ **Persona Flexibility**: User-configurable roles and tasks  

## 🐳 Docker Deployment

The solution is fully containerized and ready for submission:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📊 Output Format

### Challenge 1a Output
```json
{
  "outline": [
    {
      "level": 1,
      "title": "Chapter Title",
      "page": 1
    }
  ],
  "metadata": {
    "processing_time": 8.5,
    "total_pages": 50
  }
}
```

### Challenge 1b Output
```json
{
  "persona": "Assistant Professor",
  "job": "Research paper analysis",
  "sections": [
    {
      "title": "Section Title",
      "relevance_score": 0.95,
      "content_summary": "Key insights...",
      "page_numbers": [1, 2, 3]
    }
  ],
  "metadata": {
    "processing_time": 45.2,
    "total_sections": 12
  }
}
```

## 🎉 Success Metrics

- **Challenge 1a**: Successfully extracts structured outlines from complex PDFs
- **Challenge 1b**: Accurately identifies and prioritizes relevant content for specific personas
- **Combined**: Provides comprehensive document analysis covering both structural and content-based insights

---

*Built for Adobe India Hackathon 2025 - Combining the power of structural analysis with intelligent content understanding.*
