from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
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


def create_jpg_image(pdf_path: str, page_number: int) -> Any:
    """Convert the PDF page to a JPG."""
    images = convert_from_path(pdf_path)
    jpg_image_original = images[page_number - 1]

    return jpg_image_original


@app.post("/parse-pdf/")
async def parse_pdf(template: str, pdf: UploadFile = File(...)) -> JSONResponse:

    # Load the template schema for validation
    template_schema = json.load(open("src/schema/template_json_schema.json"))

    # Validate the incoming template against the schema
    try:
        validate(instance=json.loads(template), schema=template_schema)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": "Template validation failed", "details": str(e)},
        )

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("src", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Save the uploaded PDF file
    pdf_path = os.path.join(output_dir, pdf.filename)
    pdf_bytes = await pdf.read()  # Read the PDF bytes here
    with open(pdf_path, "wb") as buffer:
        buffer.write(pdf_bytes)

    template_dict = json.loads(template)

    template_name = template_dict["metadata"]["template_id"]

    identifier = "test"

    data_extractor = DataExtractor(pdf_bytes, template_name, identifier)
    pdf_data = data_extractor.extract_data()

    number_of_pages = pdf_data["number_of_pages"]
    jpg_bytes = []
    for page_number in range(1, number_of_pages + 1):
        jpg_image = create_jpg_image(pdf_path, page_number)
        jpg_bytes.append(jpg_image)

    output = Parser.parse_pdf(template_dict, pdf_data, jpg_bytes)
    return JSONResponse(status_code=200, content=output)
