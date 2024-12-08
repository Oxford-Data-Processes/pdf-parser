import json
import os
from typing import Dict, Any
from parser import Parser

templates_and_identifiers = {
    "barclays_student": ["march", "april", "may"],
    "barclays": ["march", "april", "may"],
    "first_direct": ["march", "april", "may"],
    "halifax": ["march", "april", "may"],
    "lloyds": ["september"],
    "monzo": ["november", "3_months"],
    "payslip": ["jake"],
}

# Loop through all templates and identifiers
for template_name, identifiers in templates_and_identifiers.items():
    for identifier in identifiers:
        template_path: str = os.path.join(
            "src", "templates", f"{template_name}_template.json"
        )
        pdf_data_path: str = os.path.join(
            "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
        )

        template: Dict[str, Any] = json.load(open(template_path))
        pdf_data: Dict[str, Any] = json.load(open(pdf_data_path))

        output_data_path: str = os.path.join(
            "src", "outputs", f"{template_name}_{identifier}_output.json"
        )

        output = Parser.parse_pdf(template, pdf_data)

        with open(output_data_path, "w") as json_file:
            json.dump(output, json_file, indent=4)
