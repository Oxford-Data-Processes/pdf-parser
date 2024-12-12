import requests
import json
from typing import List, Dict
from PIL import Image
from pdf2image import convert_from_path
import io
import os
import pandas as pd

api_url = "http://localhost:8000"


def get_sort_code_template_mapping() -> Dict[str, str]:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sort_code_template_mapping_path: str = os.path.join(
        ROOT_DIR, "src", "sort_code_template_mapping.csv"
    )
    mapping = pd.read_csv(sort_code_template_mapping_path)
    return mapping.set_index("sort_code")["template_id"].to_dict()


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
    """Convert PIL Images to bytes for OCR."""
    jpg_bytes = []
    for image in images:
        image = image.convert("RGB")  # Ensure RGB mode
        if min(image.size) < 1800:  # Resize if too small
            ratio = 1800 / min(image.size)
            image = image.resize(
                (int(dim * ratio) for dim in image.size), Image.Resampling.LANCZOS
            )
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG", quality=95)
        jpg_bytes.append(img_byte_arr.getvalue())
    return jpg_bytes


def get_sort_code(pdf_path: str) -> str:
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


def main(pdf_path: str):
    sort_code = get_sort_code(pdf_path)
    template_id = get_sort_code_template_mapping().get(sort_code)
    print(template_id)


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path: str = os.path.join(
        ROOT_DIR,
        "data",
        "bank_statements",
        "barclays",
        "pdf",
        "barclays_march.pdf",
    )
    main(pdf_path)
