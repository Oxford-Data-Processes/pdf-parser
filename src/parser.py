import json
import os
from typing import Dict, Any
from datetime import datetime


class PDFParser:
    def parse(
        self, template: Dict[str, Any], pdf_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass


template_path: str = os.path.join("src", "templates", "barclays_template.json")
pdf_data_path: str = os.path.join("src", "pdf_data", "barclays_pdf_data.json")

template: Dict[str, Any] = json.load(open(template_path))
pdf_data: Dict[str, Any] = json.load(open(pdf_data_path))

parser: PDFParser = PDFParser()
output: Dict[str, Any] = parser.parse(template, pdf_data)

print(output)

assert output == json.load(open("src/outputs/barclays_output.json"))
