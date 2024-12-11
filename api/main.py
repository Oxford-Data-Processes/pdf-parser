from fastapi import FastAPI
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
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
    return jpg_image_original


@app.post("/parse-pdf/")
async def parse_pdf(template: str, pdf: bytes) -> JSONResponse:
    try:
        template_dict = json.loads(template)

        # Create the output directory if it doesn't exist
        output_dir = os.path.join("src", "outputs")
        os.makedirs(output_dir, exist_ok=True)

        template_name = template_dict["metadata"]["template_id"]
        identifier = "test"

        data_extractor = DataExtractor(pdf, template_name, identifier)
        pdf_data = data_extractor.extract_data()

        number_of_pages = pdf_data["number_of_pages"]
        jpg_bytes = []
        for page_number in range(1, number_of_pages + 1):
            jpg_image = create_jpg_image(pdf, page_number)
            jpg_bytes.append(jpg_image)

        output = Parser.parse_pdf(template_dict, pdf_data, jpg_bytes)
        return JSONResponse(status_code=200, content=json.loads(output))

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "details": str(e)},
        )
