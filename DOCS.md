# PDF Parser Documentation

## Overview
PDF Parser is a Python package designed for parsing and processing PDF documents. It provides functionality for text extraction, OCR processing, and PDF manipulation.

## Dependencies

### System Requirements
- Python 3.8 or higher
- Tesseract OCR engine

### Installing Tesseract

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Python Dependencies
The project uses Poetry for dependency management. Main dependencies include:
- pdfplumber: PDF text extraction
- pytesseract: OCR processing
- Pillow: Image processing
- pandas: Data manipulation
- pytest: Testing framework

Development dependencies include additional tools for development, testing, and API functionality.

## Installation

### Using Poetry (Recommended)
1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/Oxford-Data-Processes/pdf-parser.git
   cd pdf-parser
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

### Using Docker
1. Build the Docker image:
   ```bash
   docker build -t pdf-parser .
   ```

2. Run tests in Docker:
   ```bash
   docker run pdf-parser
   ```

## Development Setup
1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Activate the virtual environment:
   ```bash
   poetry shell
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Project Structure
```
pdf-parser/
├── pdf_parser/         # Main package directory
├── tests/             # Test files
├── pyproject.toml     # Poetry configuration and dependencies
├── Dockerfile         # Docker configuration
└── README.md         # Project overview
```

## Using Docker for Testing
The included Dockerfile sets up a complete environment with all necessary dependencies, including Tesseract OCR. This ensures consistent testing across different environments.

To verify the package installation:
```bash
docker build -t pdf-parser .
docker run pdf-parser python3 -c "import pdf_parser"
```

## Common Issues and Solutions

### Tesseract Not Found
If you encounter a `TesseractNotFound` error, ensure that Tesseract is properly installed on your system and that the path to the Tesseract executable is correctly set in your environment.

### PDF Processing Issues
Make sure your PDF files are not encrypted or password-protected. The package may have limited functionality with secured PDFs.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License
[Add your license information here] 