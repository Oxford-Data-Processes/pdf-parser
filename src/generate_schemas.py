from pydantic import BaseModel
import json
import os

from database.clients import Client


def write_schema_to_json(model: BaseModel, output_dir: str = "json_schemas") -> None:
    json_schema_str = model.schema()

    with open(
        os.path.join(output_dir, f"{model.__name__.lower()}_schema.json"), "w"
    ) as f:
        json.dump(json_schema_str, f, indent=4)


if __name__ == "__main__":
    write_schema_to_json(Client)
