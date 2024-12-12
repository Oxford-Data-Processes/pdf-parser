import pdfplumber
import pytesseract
from typing import List
import io


def extract_data_pdfplumber(pdf_bytes: bytes) -> List[str]:
    """Extract all text data from a PDF using pdfplumber."""
    extracted_text = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            extracted_text.append(page.extract_text())
    return extracted_text


def extract_data_pytesseract(jpg_bytes: List[bytes]) -> List[str]:
    """Extract all text data from images using pytesseract."""
    extracted_text = []
    for image in jpg_bytes:
        text = pytesseract.image_to_string(image)
        extracted_text.append(text)
    return extracted_text
