import os
import json
import requests
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from api import app

# Create a test client
client = TestClient(app)


def test_parse_pdf(test_pdf_path: str, template_name: str, identifier: str):

    # Ensure the template exists
    template_path = os.path.join("src", "templates", f"{template_name}_template.json")
    assert os.path.exists(template_path), f"Template file not found: {template_path}"

    with open(template_path, "r") as template_file:
        template = json.load(template_file)

    # Create test directories if they don't exist
    os.makedirs(os.path.join("src", "outputs"), exist_ok=True)

    # Open the PDF file
    with open(test_pdf_path, "rb") as pdf_file:
        # Create the files dictionary for the request
        files = {"pdf": ("sample.pdf", pdf_file, "application/pdf")}

        # Make the request to the API
        response = client.post(
            "/parse-pdf/", params={"template": json.dumps(template)}, files=files
        )

        assert response.status_code == 200

        with open(
            os.path.join("src", "outputs", f"{template_name}_{identifier}_output.json"),
            "w",
        ) as f:
            json.dump(response.json(), f, indent=4)


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

                import time

                # Run the test
                print(
                    f"Running API test for {document_type} {template_name} {identifier}"
                )
                start_time = time.time()  # Start timing
                test_parse_pdf(test_pdf_path, template_name, identifier)
                elapsed_time = time.time() - start_time  # Calculate elapsed time
                print(f"Test completed successfully in {elapsed_time:.2f} seconds!")


if __name__ == "__main__":
    main()
