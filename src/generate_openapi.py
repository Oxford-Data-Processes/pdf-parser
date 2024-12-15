from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Type
import json
from database.client import Client
import os

app = FastAPI()

# Ensure the schema directory exists
os.makedirs("schema", exist_ok=True)


def generate_openapi_schema(model: Type[BaseModel]) -> dict:
    return get_openapi(
        title="Custom Pydantic Model API",
        version="1.0.0",
        description="API documentation generated from a Pydantic model",
        routes=app.routes,
    )


def dump_schema_to_json(schema: dict, model_name: str):
    file_path = os.path.join("schema", f"{model_name}_schema.json")
    with open(file_path, "w") as f:
        json.dump(schema, f, indent=4)


class ExampleModel(BaseModel):
    name: str
    age: int


@app.get("/openapi-schema")
def openapi_schema():

    model_map = {
        "example": ExampleModel,
        "client": Client,
        # Add other models as needed
    }

    for model_name in model_map.keys():
        model = model_map.get(model_name)
        schema = generate_openapi_schema(model)
        dump_schema_to_json(schema, model_name)
