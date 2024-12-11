import os
import json
import requests
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from api import app

# Create a test client
client = TestClient(app)


def test_parse_pdf():
    # Test data setup
    test_pdf_path = os.path.join("tests", "data", "sample.pdf")
    template_name = "monzo"

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
        print(response.json())

        with open(
            os.path.join("src", "outputs", f"{template_name}_test_output.json"),
            "w",
        ) as f:
            json.dump(response.json(), f, indent=4)


def main():
    """Run the test directly"""
    # Create test PDF if it doesn't exist
    test_data_dir = os.path.join("tests", "data")
    os.makedirs(test_data_dir, exist_ok=True)

    test_pdf_path = os.path.join(test_data_dir, "sample.pdf")
    if not os.path.exists(test_pdf_path):
        print(f"Please place a sample PDF file at: {test_pdf_path}")
        return

    # Run the test
    print("Running API test...")
    test_parse_pdf()
    print("Test completed successfully!")


if __name__ == "__main__":
    main()
