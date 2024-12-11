from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json
import os
from parser import Parser
from extractors import DataExtractor
from pdf_utils import ImageDrawer

app = FastAPI()


@app.post("/parse-pdf/")
async def parse_pdf(template: str, pdf: UploadFile = File(...)) -> JSONResponse:

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("src", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Save the uploaded PDF file
    pdf_path = os.path.join(output_dir, pdf.filename)
    with open(pdf_path, "wb") as buffer:
        buffer.write(await pdf.read())

    print(template)
    print(type(template))
    template_dict = json.loads(template)
    print(template_dict)
    print(type(template_dict))

    template_name = template_dict["metadata"]["template_id"]

    identifier = "test"

    data_extractor = DataExtractor(buffer.read(), template_name, identifier)
    pdf_data = data_extractor.extract_data()

    jpg_bytes = []
    for page_number in pdf_data["page_numbers"]:
        jpg_image = ImageDrawer.create_jpg_image(pdf_path, page_number)
        jpg_bytes.append(jpg_image)

    output = Parser.parse_pdf(template, pdf_data, jpg_bytes)

    return JSONResponse(status_code=200, content=output)
