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


def send_request(files: List[tuple], template: dict) -> requests.Response:
    """Send the request to the API."""
    response = requests.post(
        f"{api_url}/parse-pdf/",
        files=files,
        data={"template": json.dumps(template)},
    )
    return response


def test_get_sort_code(pdf_path: str):
    """Test the get-template endpoint."""
    print(f"\nTesting PDF: {pdf_path}")

    template = {
        "metadata": {"template_id": "sort_code", "version": "1.0.0"},
        "extraction_method": "extraction",
        "rules": [
            {
                "rule_id": "sort_code",
                "type": "form",
                "config": {
                    "field_name": "sort_code",
                    "search_type": "regex",
                    "regex": r"ode.*?(\d{2}-\d{2}-\d{2})",
                },
            }
        ],
        "pages": [{"page_numbers": "1:-1", "forms": ["sort_code"]}],
    }

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        jpg_bytes = create_jpg_bytes(pdf_bytes)
        files = prepare_files(pdf_bytes, jpg_bytes)

    try:
        response = send_request(files, template)
        if response.status_code == 200:
            sort_code = next(
                (
                    form["sort_code"]
                    for form in response.json()["pages"][0]["forms"]
                    if form["sort_code"]
                ),
                None,
            )
            return sort_code
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
        # "payslips": {
        #     "payslip": ["jake"],
        # },
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
                sort_code = test_get_sort_code(test_pdf_path)
                print(sort_code)
