import os
import json
import requests
import base64
from pdf2image import convert_from_path
from typing import List
import io

api_url = "http://localhost:8000"


def create_jpg_bytes(pdf_bytes: bytes) -> List[str]:
    """Convert all PDF pages to JPG bytes and encode as base64."""
    with open("temp.pdf", "wb") as temp_pdf:
        temp_pdf.write(pdf_bytes)
    images = convert_from_path("temp.pdf")

    # Convert PIL Images to base64 encoded strings
    jpg_bytes = []
    for image in images:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
        base64_encoded = base64.b64encode(img_byte_arr).decode("utf-8")
        jpg_bytes.append(base64_encoded)

    os.remove("temp.pdf")
    return jpg_bytes


def test_parse_pdf(test_pdf_path: str, template_name: str, identifier: str):
    print(f"\nTesting PDF: {test_pdf_path}")
    print(f"Template: {template_name}")

    # Ensure the template exists
    template_path = os.path.join("src", "templates", f"{template_name}_template.json")
    assert os.path.exists(template_path), f"Template file not found: {template_path}"
    print(f"Using template: {template_path}")

    with open(template_path, "r") as template_file:
        template = json.load(template_file)

    # Create test directories if they don't exist
    os.makedirs(os.path.join("src", "outputs"), exist_ok=True)

    # Open the PDF file
    with open(test_pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        jpg_bytes = create_jpg_bytes(pdf_bytes)

        files = {
            "pdf": (os.path.basename(test_pdf_path), pdf_file, "application/pdf"),
            **{
                f"image_{i}": (
                    f"image_{i}.jpg",
                    io.BytesIO(base64.b64decode(image)),
                    "image/jpeg",
                )
                for i, image in enumerate(jpg_bytes)
            },
        }

        # Make the request to the API
        response = requests.post(
            f"{api_url}/parse-pdf/",
            params={"template": json.dumps(template)},
            files=files,
        )

        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")

        assert response.status_code == 200, f"API request failed: {response.text}"

        # Save the output
        output_path = os.path.join(
            "src", "outputs", f"{template_name}_{identifier}_output.json"
        )
        with open(output_path, "w") as f:
            json.dump(response.json(), f, indent=4)
            print(f"Output saved to: {output_path}")


def main():
    """Run the test directly"""

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
