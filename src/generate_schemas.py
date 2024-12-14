from pydantic import BaseModel
import json
import os


class ExampleModel(BaseModel):
    name: str
    age: int


# Example usage
if __name__ == "__main__":
    # Replace FinancialAnalysis with any Pydantic model you want to generate a schema for
    json_schema_str = ExampleModel.schema()
    with open(os.path.join("schemas", "example_model_schema.json"), "w") as f:
        json.dump(json_schema_str, f, indent=4)
