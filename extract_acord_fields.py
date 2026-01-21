#!/usr/bin/env python3
"""
ACORD Form Field Extractor
Extracts field names from ACORD PDF forms using OCR
"""

import sys
import os
import re
from typing import List, Set
import argparse
from pathlib import Path

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)


class ACORDFieldExtractor:
    """Extract field names from ACORD forms using OCR"""

    def __init__(self, pdf_path: str, output_path: str = None, dpi: int = 300):
        """
        Initialize the ACORD field extractor

        Args:
            pdf_path: Path to the PDF file
            output_path: Path to save the output text file (default: same name as PDF with .txt extension)
            dpi: DPI for PDF to image conversion (higher = better quality but slower)
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if output_path:
            self.output_path = Path(output_path)
        else:
            self.output_path = self.pdf_path.with_suffix('.txt')

        self.dpi = dpi
        self.field_names: Set[str] = set()

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply thresholding to get better contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

        # Convert back to PIL Image
        return Image.fromarray(denoised)

    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from image using Tesseract OCR

        Args:
            image: PIL Image object

        Returns:
            Extracted text as string
        """
        # Preprocess the image
        preprocessed = self.preprocess_image(image)

        # Use Tesseract to extract text
        custom_config = r'--oem 3 --psm 6'  # PSM 6: Assume uniform block of text
        text = pytesseract.image_to_string(preprocessed, config=custom_config)

        return text

    def identify_field_names(self, text: str) -> List[str]:
        """
        Identify field names from extracted text

        ACORD forms typically have fields in these patterns:
        - "Field Name:" (colon-based)
        - "Field Name ___" (underscore-based)
        - "1. Field Name" (numbered)
        - "☐ Field Name" or "□ Field Name" (checkbox-based)

        Args:
            text: Extracted text from OCR

        Returns:
            List of identified field names
        """
        field_names = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Pattern 1: Field names ending with colon
            # e.g., "Named Insured:", "Policy Number:", "Effective Date:"
            colon_pattern = r'^([A-Z][A-Za-z\s&/\-,()]+):\s*$'
            match = re.search(colon_pattern, line)
            if match:
                field_name = match.group(1).strip()
                if len(field_name) > 3 and len(field_name) < 100:  # Filter out noise
                    field_names.append(field_name)
                continue

            # Pattern 2: Field names with underscores (fill-in-the-blank style)
            # e.g., "Name ________", "Address _______"
            underscore_pattern = r'^([A-Z][A-Za-z\s&/\-,()]+)\s+_{2,}'
            match = re.search(underscore_pattern, line)
            if match:
                field_name = match.group(1).strip()
                if len(field_name) > 3 and len(field_name) < 100:
                    field_names.append(field_name)
                continue

            # Pattern 3: Numbered fields
            # e.g., "1. Policy Holder", "2. Coverage Type"
            numbered_pattern = r'^\d+\.\s+([A-Z][A-Za-z\s&/\-,()]+)(?::|$)'
            match = re.search(numbered_pattern, line)
            if match:
                field_name = match.group(1).strip()
                if len(field_name) > 3 and len(field_name) < 100:
                    field_names.append(field_name)
                continue

            # Pattern 4: Checkbox fields
            # e.g., "☐ Yes", "□ No", "O Option"
            checkbox_pattern = r'^[☐□○◯O]\s+([A-Z][A-Za-z\s&/\-,()]+)'
            match = re.search(checkbox_pattern, line)
            if match:
                field_name = match.group(1).strip()
                if len(field_name) > 2 and len(field_name) < 100:
                    field_names.append(field_name)
                continue

            # Pattern 5: Label-like patterns (all caps or title case starting a line)
            # This is more lenient and catches other field labels
            if line and line[0].isupper() and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    field_name = parts[0].strip()
                    # Avoid sentences and long text
                    if len(field_name.split()) <= 8 and len(field_name) < 100:
                        field_names.append(field_name)

        return field_names

    def extract_fields(self) -> Set[str]:
        """
        Main method to extract all field names from the PDF

        Returns:
            Set of unique field names
        """
        print(f"Converting PDF to images (DPI: {self.dpi})...")
        try:
            images = convert_from_path(str(self.pdf_path), dpi=self.dpi)
        except Exception as e:
            print(f"Error converting PDF: {e}")
            print("Note: Make sure poppler-utils is installed on your system")
            sys.exit(1)

        print(f"Processing {len(images)} page(s)...")

        for i, image in enumerate(images, 1):
            print(f"  Processing page {i}/{len(images)}...")

            # Extract text from the image
            text = self.extract_text_from_image(image)

            # Identify field names
            fields = self.identify_field_names(text)

            # Add to the set (automatically handles duplicates)
            self.field_names.update(fields)

            print(f"    Found {len(fields)} field(s) on page {i}")

        return self.field_names

    def save_results(self):
        """Save extracted field names to a text file"""
        # Sort field names alphabetically
        sorted_fields = sorted(self.field_names)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write("ACORD Form Field Names\n")
            f.write("=" * 50 + "\n")
            f.write(f"Source: {self.pdf_path.name}\n")
            f.write(f"Total Fields Found: {len(sorted_fields)}\n")
            f.write("=" * 50 + "\n\n")

            for i, field in enumerate(sorted_fields, 1):
                f.write(f"{i}. {field}\n")

        print(f"\n✓ Results saved to: {self.output_path}")
        print(f"✓ Total unique fields found: {len(sorted_fields)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract field names from ACORD PDF forms using OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_acord_fields.py acord_form.pdf
  python extract_acord_fields.py acord_form.pdf -o fields.txt
  python extract_acord_fields.py acord_form.pdf --dpi 400
        """
    )

    parser.add_argument(
        'pdf_file',
        type=str,
        help='Path to the ACORD PDF file'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output text file path (default: same name as PDF with .txt extension)'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='DPI for PDF to image conversion (default: 300, higher = better quality but slower)'
    )

    args = parser.parse_args()

    try:
        # Create extractor instance
        extractor = ACORDFieldExtractor(
            pdf_path=args.pdf_file,
            output_path=args.output,
            dpi=args.dpi
        )

        # Extract fields
        print("\n" + "=" * 50)
        print("ACORD Field Extractor")
        print("=" * 50 + "\n")

        extractor.extract_fields()

        # Save results
        extractor.save_results()

        print("\n✓ Extraction complete!")

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
