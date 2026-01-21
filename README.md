# ACORD Form Field Extractor

A Python-based tool that extracts field names from ACORD PDF forms using Optical Character Recognition (OCR).

## Overview

This tool processes ACORD insurance forms in PDF format and automatically identifies and extracts all field names present on the form. It uses OCR technology to read the document and pattern matching to identify field labels.

## Features

- **OCR-based extraction**: Uses Tesseract OCR to read PDF documents
- **Image preprocessing**: Enhances image quality for better OCR accuracy
- **Multiple field patterns**: Recognizes various ACORD field naming conventions:
  - Colon-based fields (e.g., "Named Insured:")
  - Underscore-based fields (e.g., "Name _______")
  - Numbered fields (e.g., "1. Policy Number")
  - Checkbox fields (e.g., "☐ Yes")
- **Automatic deduplication**: Removes duplicate field names across pages
- **Sorted output**: Alphabetically sorted field list for easy reference

## Requirements

### System Dependencies

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- Add both to your system PATH

### Python Dependencies

Python 3.7 or higher is required.

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Document-Information-Extraction
```

2. Install system dependencies (see Requirements section above)

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python extract_acord_fields.py --help
```

## Usage

### Basic Usage

Extract field names from an ACORD PDF:
```bash
python extract_acord_fields.py acord_form.pdf
```

This will create a text file named `acord_form.txt` with all extracted field names.

### Custom Output File

Specify a custom output file:
```bash
python extract_acord_fields.py acord_form.pdf -o my_fields.txt
```

### High-Quality OCR

For better accuracy, increase the DPI (slower but more accurate):
```bash
python extract_acord_fields.py acord_form.pdf --dpi 400
```

### Command-Line Options

```
usage: extract_acord_fields.py [-h] [-o OUTPUT] [--dpi DPI] pdf_file

positional arguments:
  pdf_file              Path to the ACORD PDF file

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output text file path (default: same name as PDF with .txt extension)
  --dpi DPI             DPI for PDF to image conversion (default: 300)
```

## Output Format

The output text file contains:
- Header with source file information
- Total count of unique fields found
- Alphabetically sorted list of field names

Example output:
```
ACORD Form Field Names
==================================================
Source: acord_25.pdf
Total Fields Found: 45
==================================================

1. Additional Insured
2. Agent Name
3. Certificate Holder
4. Commercial General Liability
5. Description of Operations
...
```

## How It Works

1. **PDF to Image Conversion**: Converts each PDF page to a high-resolution image
2. **Image Preprocessing**: Applies grayscale conversion, thresholding, and denoising
3. **OCR Text Extraction**: Uses Tesseract to extract text from preprocessed images
4. **Pattern Matching**: Identifies field names using regex patterns for common ACORD field formats
5. **Deduplication & Sorting**: Removes duplicates and sorts alphabetically
6. **Output Generation**: Saves results to a formatted text file

## Supported Field Patterns

The extractor recognizes these common ACORD field patterns:

| Pattern | Example | Description |
|---------|---------|-------------|
| Colon-based | `Policy Number:` | Field label ending with colon |
| Underscore-based | `Name _______` | Fill-in-the-blank style |
| Numbered | `1. Coverage Type` | Numbered field labels |
| Checkbox | `☐ Auto` | Checkbox options |
| Label-style | `INSURED: Name` | Capitalized labels with colons |

## Troubleshooting

### "Tesseract not found" error
- Ensure Tesseract OCR is installed and added to your system PATH
- On Linux: `which tesseract` should return a path
- On Windows: Add Tesseract installation directory to PATH environment variable

### "Poppler not found" error
- Install poppler-utils (Linux) or poppler (macOS/Windows)
- On Windows, ensure poppler's `bin` directory is in your PATH

### Poor OCR accuracy
- Try increasing the DPI: `--dpi 400` or `--dpi 600`
- Ensure the PDF is not heavily encrypted or image-based with low resolution
- Check that the PDF is an ACORD form (the patterns are optimized for ACORD formats)

### Missing fields
- Some fields may not match the expected patterns
- Consider adjusting the regex patterns in `identify_field_names()` method
- Increase DPI for better text recognition

## Limitations

- Optimized for standard ACORD forms; may require adjustments for custom forms
- OCR accuracy depends on PDF quality and resolution
- Handwritten text may not be recognized accurately
- Very complex layouts may cause some fields to be missed

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Author

Created for extracting field information from ACORD insurance forms.
