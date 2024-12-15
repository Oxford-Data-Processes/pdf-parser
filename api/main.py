from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import sys
from cleaner import PageCleaner

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


@app.post("/parse-pdf/")
async def parse_pdf(
    pdf: UploadFile = File(...),
    images: list[UploadFile] = File(...),
    template: str = Form(...),
) -> JSONResponse:
    try:
        template_dict = json.loads(template)

        # Read the PDF bytes
        pdf_bytes = await pdf.read()

        # Read the image bytes
        jpg_bytes = [await image.read() for image in images]

        data_extractor = DataExtractor(pdf_bytes)
        pdf_data = data_extractor.extract_data()

        pdf_data["number_of_pages"] = len(jpg_bytes)

        output = Parser.parse_pdf(template_dict, pdf_data, jpg_bytes)
        return JSONResponse(status_code=200, content=json.loads(output))

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "details": str(e)},
        )


def document_cleaner(document_data: dict, config: dict):
    cleaner = PageCleaner(config)
    cleaned_pages = []
    for page in document_data["pages"]:
        cleaned_page = cleaner.clean_page(page)
        cleaned_pages.append(cleaned_page)

    document_data["pages"] = cleaned_pages
    return document_data


@app.post("/clean-document/")
async def clean_document(
    document_data: dict = Body(...),
    template_name: str = Form(...),
) -> JSONResponse:
    try:
        config_path = os.path.join(
            os.path.dirname(__file__),
            "cleaner_configs",
            f"{template_name}_cleaner_config.json",
        )
        with open(config_path) as f:
            config = json.load(f)
        cleaned_document_data = document_cleaner(
            document_data, config
        )  # Clean the provided document data
        return JSONResponse(status_code=200, content=cleaned_document_data)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Processing failed", "details": str(e)},
        )
