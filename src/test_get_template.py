import os
import json
import requests
from pdf2image import convert_from_path
import io
from typing import List, Dict
from PIL import Image

api_url = "http://localhost:8000"


def create_jpg_bytes(pdf_bytes: bytes) -> List[bytes]:
    """Convert all PDF pages to JPG bytes."""
    with open("temp.pdf", "wb") as temp_pdf:
        temp_pdf.write(pdf_bytes)
    # Convert with higher DPI for better OCR
    images = convert_from_path("temp.pdf", dpi=300)
    jpg_bytes = convert_images_to_bytes(images)
    os.remove("temp.pdf")
    return jpg_bytes


def convert_images_to_bytes(images) -> List[bytes]:
    """Convert PIL Images to bytes with optimal settings for OCR."""
    jpg_bytes = []
    for image in images:
        # Convert to RGB mode to ensure compatibility
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize image if too small (helps OCR accuracy)
        min_size = 1800
        ratio = min_size / min(image.size)
        if ratio > 1:
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Save with high quality
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG", quality=95, optimize=False)
        jpg_bytes.append(img_byte_arr.getvalue())
    return jpg_bytes


def prepare_files(pdf_bytes: bytes, jpg_bytes: List[bytes]) -> List[tuple]:
    """Prepare files for the request."""
    files = [("pdf", ("temp.pdf", pdf_bytes, "application/pdf"))]

    # Add each image to the files list with the same field name 'images'
    for i, jpg in enumerate(jpg_bytes):
        files.append(("images", (f"image_{i}.jpg", jpg, "image/jpeg")))
    return files


def test_get_template(pdf_path: str):
    """Test the get-template endpoint."""
    print(f"\nTesting PDF: {pdf_path}")

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        jpg_bytes = create_jpg_bytes(pdf_bytes)
        files = prepare_files(pdf_bytes, jpg_bytes)

    try:
        response = requests.post(f"{api_url}/get-template/", files=files)

        result = response.json()
        response_data = {
            "pdf_plumber": result.get("pdf_plumber", []),
            "pytesseract": result.get("pytesseract", []),
        }

        document_type = (
            "bank_statements" if "bank_statements" in pdf_path else "payslips"
        )
        template_name = pdf_path.split("/")[-3]  # Extract template name from the path

        output_path = f"/Users/chrislittle/GitHub/pdf-parser/src/text_extraction/{document_type}/{template_name}/{template_name}_{identifier}"
        os.makedirs(output_path, exist_ok=True)

        with open(os.path.join(output_path, "response.json"), "w") as json_file:
            json.dump(response_data, json_file, indent=4)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error making request: {str(e)}")


if __name__ == "__main__":
    config = {
        "bank_statements": {
            "barclays_student": ["march", "april", "may"],
            "barclays": ["march", "april", "may"],
            "first_direct": ["march", "april", "may"],
            "halifax": ["march", "april", "may"],
            "lloyds": ["september"],
            "monzo": ["november", "3_months"],
        },
        "payslips": {
            "payslip": ["jake"],
        },
    }

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for document_type, templates_and_identifiers in config.items():
        for template_name, identifiers in templates_and_identifiers.items():
            for identifier in identifiers:
                test_pdf_path: str = os.path.join(
                    ROOT_DIR,
                    "data",
                    document_type,
                    template_name,
                    "pdf",
                    f"{template_name}_{identifier}.pdf",
                )
                test_get_template(test_pdf_path)
