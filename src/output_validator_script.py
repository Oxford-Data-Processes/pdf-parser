import json

from jsonschema import validate

from pdf_parser.pydantic_models import Document

templates_and_identifiers = {
    "barclays_student": ["march", "april", "may"],
    "barclays": ["march", "april", "may"],
    "first_direct": ["march", "april", "may"],
    "halifax": ["march", "april", "may"],
    "lloyds": ["september"],
    "monzo": ["november", "3_months"],
    "payslip": ["jake"],
}

for template_name, identifiers in templates_and_identifiers.items():
    for identifier in identifiers:
        template = json.load(open(f"src/templates/{template_name}_template.json"))

        with open("src/schema/template_json_schema.json") as schema_file:
            schema = json.load(schema_file)

        print("TEMPLATE")
        print(template_name, identifier)

        try:
            validate(instance=template, schema=schema)
            print("VALID")
        except Exception as e:
            print(e)

        output_path = f"src/outputs/{template_name}_{identifier}_output.json"
        generated_output = json.load(open(output_path))

        Document(**generated_output)
