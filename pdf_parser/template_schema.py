import json

with open("schema/template_json_schema.json") as schema_file:
    TEMPLATE_JSON_SCHEMA = json.load(schema_file)
