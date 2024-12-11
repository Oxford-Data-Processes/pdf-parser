from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import json
import os
from pdf2image import convert_from_path
from jsonschema import validate

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pdf_parser.parser import Parser
from pdf_parser.extractors import DataExtractor

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs(os.path.join("src", "outputs"), exist_ok=True)
os.makedirs(os.path.join("src", "schema"), exist_ok=True)


def create_jpg_image(pdf_bytes: bytes, page_number: int) -> Any:
    """Convert the PDF page to a JPG."""
    with open("temp.pdf", "wb") as temp_pdf:
        temp_pdf.write(pdf_bytes)
    images = convert_from_path("temp.pdf")
    jpg_image_original = images[page_number - 1]
    os.remove("temp.pdf")  # Clean up temporary file
    return jpg_image_original


@app.post("/parse-pdf/")
async def parse_pdf(template: str, pdf: UploadFile = File(...)) -> JSONResponse:
    try:
        print(f"Processing PDF: {pdf.filename}")
        template_dict = json.loads(template)

        # Create the output directory if it doesn't exist
        output_dir = os.path.join("src", "outputs")
        os.makedirs(output_dir, exist_ok=True)

        # Read the PDF bytes
        pdf_bytes = await pdf.read()
        print(f"Read {len(pdf_bytes)} bytes from PDF")

        template_name = template_dict["metadata"]["template_id"]
        identifier = "test"

        print(f"Extracting data with template: {template_name}")
        data_extractor = DataExtractor(pdf_bytes, template_name, identifier)
        pdf_data = data_extractor.extract_data()

        number_of_pages = pdf_data["number_of_pages"]
        print(f"Processing {number_of_pages} pages")

        jpg_bytes = []
        for page_number in range(1, number_of_pages + 1):
            print(f"Converting page {page_number} to JPG")
            jpg_image = create_jpg_image(pdf_bytes, page_number)
            jpg_bytes.append(jpg_image)

        print("Parsing PDF with template")
        output = Parser.parse_pdf(template_dict, pdf_data, jpg_bytes)
        return JSONResponse(status_code=200, content=json.loads(output))

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "details": str(e)},
        )
