import os
import json
import requests
from pdf2image import convert_from_path
import io
from typing import List, Dict

api_url = "http://localhost:8000"


def create_jpg_bytes(pdf_bytes: bytes) -> List[bytes]:
    """Convert all PDF pages to JPG bytes."""
    with open("temp.pdf", "wb") as temp_pdf:
        temp_pdf.write(pdf_bytes)
    jpg_bytes = convert_images_to_bytes(convert_from_path("temp.pdf"))
    os.remove("temp.pdf")
    return jpg_bytes


def convert_images_to_bytes(images) -> List[bytes]:
    """Convert PIL Images to bytes."""
    jpg_bytes = []
    for image in images:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        jpg_bytes.append(img_byte_arr.getvalue())
    return jpg_bytes


def prepare_files(pdf_bytes: bytes, jpg_bytes: List[bytes]) -> Dict[str, bytes]:
    """Prepare files for the request."""
    files = {
        "pdf": ("temp.pdf", pdf_bytes, "application/pdf"),
    }
    for i, jpg in enumerate(jpg_bytes):
        files[f"images[{i}]"] = (f"image_{i}.jpg", jpg, "image/jpeg")
    return files


def test_get_template(pdf_path: str):
    """Test the get-template endpoint."""
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        jpg_bytes = create_jpg_bytes(
            pdf_bytes
        )  # Use the previous function to create JPG bytes
        files = prepare_files(
            pdf_bytes, jpg_bytes
        )  # Prepare files using the previous function

    response = requests.post(f"{api_url}/get-template/", files=files)

    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        print("Extracted text:", response.json())
    else:
        print(f"Error response: {response.text}")


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
