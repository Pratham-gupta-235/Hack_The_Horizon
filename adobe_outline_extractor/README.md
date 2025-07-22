# Adobe Outline Extractor

This project extracts outlines/headings from PDF files and outputs them as structured JSON files. It's designed for the Adobe India Hackathon 2025 Challenge 1a.

## Features

- Extracts document outlines and headings from PDF files
- Uses PyMuPDF for efficient PDF processing
- Parallel processing for improved performance
- Dockerized solution with no internet dependency
- Supports both simple and complex PDF structures

## Structure

- `app/input/` - Place input PDF files here
- `app/output/` - Output JSON files generated here  
- `app/extract_outline.py` - Main processing script
- `Dockerfile` - Docker configuration
- `requirements.txt` - Python dependencies

## Libraries and Models Used

### Core Libraries:
- **PyMuPDF (fitz)**: Primary PDF processing library for text extraction and document structure analysis
- **concurrent.futures**: For parallel processing of multiple PDFs
- **json**: For structured output generation
- **os, time**: System utilities

### Why PyMuPDF?
- High performance PDF processing
- Excellent support for document structure extraction
- Built-in table of contents (TOC) extraction
- Cross-platform compatibility (AMD64)
- No ML models required - stays under 200MB constraint

## Build and Run Instructions

### Build Docker Image:
```bash
docker build --platform linux/amd64 -t adobe-outline-extractor .
```

### Run Docker Container:
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-outline-extractor
```

## Performance Specifications

- **Execution Time**: Optimized for <10 seconds per 50-page PDF
- **Memory Usage**: Efficient processing within 16GB RAM limit
- **CPU**: Utilizes parallel processing for multi-core systems
- **Architecture**: Compatible with AMD64 (linux/amd64)
- **Network**: No internet access required during execution

## Output Format

Each PDF generates a corresponding JSON file with the structure:
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter Title",
      "page": 1
    }
  ]
}
```

## Testing

The solution handles:
- Simple PDFs with basic structure
- Complex PDFs with multiple columns, images, tables
- Large PDFs (tested up to 50+ pages)
- PDFs with existing table of contents
- PDFs requiring heuristic heading detection
