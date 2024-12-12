import os
import json
import requests
from pdf2image import convert_from_path
from typing import List
import io

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


def load_template(template_name: str) -> dict:
    """Load the template from a JSON file."""
    template_path = os.path.join("src", "templates", f"{template_name}_template.json")
    assert os.path.exists(template_path), f"Template file not found: {template_path}"
    with open(template_path, "r") as template_file:
        return json.load(template_file)


def prepare_files(pdf_bytes: bytes, jpg_bytes: List[bytes]) -> List[tuple]:
    """Prepare the files for the request."""
    files = [("pdf", ("pdf_file.pdf", pdf_bytes, "application/pdf"))]
    for i, image_bytes in enumerate(jpg_bytes):
        files.append(("images", (f"image_{i}.jpg", image_bytes, "image/jpeg")))
    return files


def send_request(files: List[tuple], template: dict) -> requests.Response:
    """Send the request to the API."""
    response = requests.post(
        f"{api_url}/parse-pdf/",
        files=files,
        data={"template": json.dumps(template)},
    )
    return response


def handle_response(response: requests.Response, template_name: str, identifier: str):
    """Handle the API response."""
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200, f"API request failed: {response.text}"

    output_path = os.path.join(
        "src", "outputs", f"{template_name}_{identifier}_output.json"
    )
    with open(output_path, "w") as f:
        json.dump(response.json(), f, indent=4)
        print(f"Output saved to: {output_path}")


def test_parse_pdf(test_pdf_path: str, template_name: str, identifier: str):
    print(f"\nTesting PDF: {test_pdf_path}")
    print(f"Template: {template_name}")

    template = load_template(template_name)
    os.makedirs(os.path.join("src", "outputs"), exist_ok=True)

    with open(test_pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        jpg_bytes = create_jpg_bytes(pdf_bytes)
        files = prepare_files(pdf_bytes, jpg_bytes)
        response = send_request(files, template)
        handle_response(response, template_name, identifier)


def main():
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

                print(
                    f"\nRunning API test for {document_type} {template_name} {identifier}"
                )
                print(f"PDF path: {test_pdf_path}")

                import time

                start_time = time.time()
                test_parse_pdf(test_pdf_path, template_name, identifier)
                elapsed_time = time.time() - start_time
                print(f"Test completed in {elapsed_time:.2f} seconds!")


if __name__ == "__main__":
    main()
