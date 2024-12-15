import os
import json
from jsonschema import validate, ValidationError


def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".json")]


jsons = list_json_files("jsons")

for file in list_json_files("json_schemas"):
    schema_name = file.replace("_schema.json", "")
    for json_file in jsons:
        if schema_name == json_file.split("_")[0]:
            print(f"Schema {schema_name} is in {json_file}")

            with open(os.path.join("json_schemas", file)) as schema_file:
                schema = json.load(schema_file)

            with open(os.path.join("jsons", json_file)) as json_data_file:
                json_data = json.load(json_data_file)

            try:
                validate(instance=json_data, schema=schema)
                print(f"JSON file {json_file} is valid against schema {schema_name}.")
            except ValidationError as e:
                print(
                    f"JSON file {json_file} is invalid against schema {schema_name}: {e.message} ❌"
                )
                break  # Break the loop if invalid
