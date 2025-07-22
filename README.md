# Adobe Outline Extractor

A high-performance tool for extracting document structure and headings from PDF files, converting them into well-structured JSON output. Developed for the Adobe India Hackathon 2025 Challenge 1a.

![Adobe Hackathon 2025](https://img.shields.io/badge/Adobe-Hackathon%202025-red)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Features

- **Smart Extraction:** Automatically identifies and extracts document outlines and headings
- **Dual Extraction Methods:** Uses both native TOC extraction and heuristic heading detection
- **High Performance:** Implements parallel processing with efficient resource usage
- **Container Ready:** Fully dockerized solution requiring no internet access
- **Adaptable:** Handles simple and complex PDF structures with robust error handling
- **Clean Output:** Provides well-structured JSON for easy integration

## 📁 Project Structure

```
adobe_outline_extractor/
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── app/
    ├── extract_outline.py  # Main extraction logic
    ├── utils.py           # Helper functions and utilities
    ├── input/             # PDF input directory
    └── output/            # JSON output directory
```

## 🔧 Technologies

### Core Libraries:
- **PyMuPDF (fitz)** - Fast PDF processing with built-in structure analysis
- **concurrent.futures** - Parallel execution for processing multiple files
- **PyPDF2 & pdfplumber** - Additional PDF parsing capabilities
- **Regular Expressions** - Advanced pattern matching for heading detection

### Technical Advantages:
- **No Dependencies**: Operates without internet access
- **Resource Efficient**: Memory usage under 16GB, even for large documents
- **Cross-platform**: Containerized for consistent execution
- **Fast Processing**: Optimized algorithms with < 10 sec/50-page processing
- **No ML Required**: Pure algorithmic approach staying under 200MB limit

## 🚀 Quick Start

### Prerequisites:
- Docker installed
- PDF files to process

### Build the Docker Image:
```bash
# Navigate to the project directory
cd adobe_outline_extractor

# Build the Docker image (AMD64 platform)
docker build --platform linux/amd64 -t adobe-outline-extractor .
```

### Run the Extractor:
```bash
# Place PDF files in ./app/input/ directory
# Run the container (no internet access)
docker run --rm \
  -v "$(pwd)/app/input:/app/input:ro" \
  -v "$(pwd)/app/output:/app/output" \
  --network none \
  adobe-outline-extractor
```

### Without Docker:
```bash
# Navigate to the app directory
cd adobe_outline_extractor/app

# Install requirements
pip install -r ../requirements.txt

# Run the extractor
python extract_outline.py
```

## ⚡ Performance

- **Speed**: Processes 50-page PDFs in under 10 seconds
- **Memory Efficiency**: Peak usage under 16GB, even for complex documents
- **Parallelization**: Automatically scales to utilize available CPU cores
- **Platform Support**: Optimized for AMD64 architecture
- **Network Independence**: Zero internet connectivity required

## 📊 Output Format

The tool generates structured JSON output that can be easily integrated into other systems:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter Title",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Section Heading",
      "page": 3
    }
  ]
}
```

## 🧪 Testing & Compatibility

The tool has been extensively tested on various PDF types:

| PDF Type | Support | Notes |
|----------|---------|-------|
| Simple documents | ✅ Excellent | Fast processing with high accuracy |
| Complex layouts | ✅ Strong | Handles multi-column text and nested layouts |
| Large documents | ✅ Efficient | Tested on 50+ page documents |
| Scanned PDFs | ⚠️ Limited | Best with machine-readable text layers |
| Table of Contents | ✅ Excellent | Utilizes existing TOC when available |

## 🔒 Security & Compliance

- **Data Privacy**: All processing happens locally with no data transmission
- **No External Services**: Zero calls to external APIs or services
- **Containerized**: Isolated execution environment

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Developed for Adobe India Hackathon 2025 - Challenge 1a*
