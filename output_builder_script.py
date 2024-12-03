import json
import os
from typing import Dict, Any


template_name: str = "barclays_student"
identifier: str = "march"

template_path: str = os.path.join("src", "templates", f"{template_name}_template.json")
pdf_data_path: str = os.path.join(
    "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)

template: Dict[str, Any] = json.load(open(template_path))
pdf_data: Dict[str, Any] = json.load(open(pdf_data_path))

output_data_path: str = os.path.join(
    "src", "outputs", f"{template_name}_{identifier}_output.json"
)


from src.parser import Parser
from datetime import datetime
import uuid


def parse_pdf(template: Dict[str, Any], pdf_data: Dict[str, Any]) -> Dict[str, Any]:

    forms = []
    tables = []
    number_of_pages = len(pdf_data["pages"])

    for page_rule in template["pages"]:
        page_indexes = Parser().page_number_converter(
            page_rule["page_numbers"], number_of_pages
        )
        for page_index in page_indexes:
            if "forms" in page_rule and len(page_rule["forms"]) > 0:
                for rule_id in page_rule["forms"]:
                    try:
                        form = Parser().get_output_data_from_form_rule(
                            rule_id, page_index, pdf_data, template
                        )
                        forms.append(form)
                    except IndexError:
                        print(
                            f"Rule ID '{rule_id}' not found in template rules or page index '{page_index}' is out of range."
                        )
            if "tables" in page_rule and len(page_rule["tables"]) > 0:
                for rule_id in page_rule["tables"]:
                    try:
                        table = Parser().get_output_data_from_table_rule(
                            rule_id, page_index, pdf_data, template
                        )
                        tables.append(table)
                    except IndexError:
                        print(
                            f"Rule ID '{rule_id}' not found in template rules or page index '{page_index}' is out of range."
                        )

    output = {
        "metadata": {
            "document_id": str(uuid.uuid4()),
            "parsed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "number_of_pages": number_of_pages,
        },
        "pages": [{"forms": forms, "tables": tables}],
    }

    return output


output = parse_pdf(template, pdf_data)

with open(output_data_path, "w") as json_file:
    json.dump(output, json_file, indent=4)
