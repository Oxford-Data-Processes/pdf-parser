from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import sys
import pdfplumber
import pytesseract
from typing import List
import io

# Add the parent directory to the system path
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


def extract_data_pdfplumber(pdf_bytes: bytes) -> List[str]:
    """Extract all text data from a PDF using pdfplumber."""
    extracted_text = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            extracted_text.append(page.extract_text())
    return extracted_text


def extract_data_pytesseract(jpg_bytes: List[bytes]) -> List[str]:
    """Extract all text data from images using pytesseract."""
    extracted_text = []
    for image in jpg_bytes:
        text = pytesseract.image_to_string(image)
        extracted_text.append(text)
    return extracted_text


@app.post("/get-template/")
async def get_template(
    pdf: UploadFile = File(...),
    images: list[UploadFile] = File(...),
) -> JSONResponse:
    print("Getting template")
    try:
        pdf_bytes = await pdf.read()
        jpg_bytes = [await image.read() for image in images]

        extracted_text_pdfplumber = extract_data_pdfplumber(pdf_bytes)

        print(extracted_text_pdfplumber)

        extracted_text_pytesseract = extract_data_pytesseract(jpg_bytes)

        return JSONResponse(
            status_code=200,
            content={
                "pdf_plumber": extracted_text_pdfplumber,
                "pytesseract": extracted_text_pytesseract,
            },
        )

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "details": str(e)},
        )


@app.post("/parse-pdf/")
async def parse_pdf(
    pdf: UploadFile = File(...),
    images: list[UploadFile] = File(...),
    template: str = Form(...),
) -> JSONResponse:
    try:
        print(f"Processing PDF: {pdf.filename}")
        template_dict = json.loads(template)

        # Read the PDF bytes
        pdf_bytes = await pdf.read()
        print(f"Read {len(pdf_bytes)} bytes from PDF")

        # Read the image bytes
        jpg_bytes = [await image.read() for image in images]
        print(f"Processed {len(jpg_bytes)} images")

        template_name = template_dict["metadata"]["template_id"]
        identifier = "test"

        print(f"Extracting data with template: {template_name}")
        data_extractor = DataExtractor(pdf_bytes, template_name, identifier)
        pdf_data = data_extractor.extract_data()

        pdf_data["number_of_pages"] = len(
            jpg_bytes
        )  # Use number of images instead of trying to read PDF
        print(f"Processing {pdf_data['number_of_pages']} pages")

        print("Parsing PDF with template")
        output = Parser.parse_pdf(template_dict, pdf_data, jpg_bytes)
        return JSONResponse(status_code=200, content=json.loads(output))

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "details": str(e)},
        )
