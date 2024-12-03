import json
from jsonschema import validate

template_name = "barclays_student"
identifier = "march"

template = json.load(open(f"src/templates/{template_name}_template.json"))


output_path = f"src/outputs/{template_name}_{identifier}_output.json"
with open("template_json_schema.json") as schema_file:
    schema = json.load(schema_file)

validate(instance=template, schema=schema)

generated_output = json.load(open(output_path))

from pydantic_models import Document

Document(**generated_output)
