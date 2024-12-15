import json
import os
from jsonschema import validate, ValidationError
from database.assessment import AssessmentRow
from database.client import Client
from database.documentmetadata import DocumentMetadata
from database.document import Document
from database.financialanalysis import FinancialAnalysis
from database.subscription import Subscription
from database.user import User


def load_json_file(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def validate_json_files():
    # Map file prefixes to their corresponding Pydantic models
    model_map = {
        "assessments": AssessmentRow,
        "clients": Client,
        "document_metadata": DocumentMetadata,
        "documents": Document,
        "financial_analysis": FinancialAnalysis,
        "subscriptions": Subscription,
        "users": User,
    }

    # Get all JSON files in the jsons directory
    json_dir = "jsons"
    json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]

    validation_results = []
    for json_file in json_files:
        file_path = os.path.join(json_dir, json_file)
        file_prefix = json_file.split("_")[0]

        if file_prefix not in model_map:
            print(f"Warning: No model mapping found for {json_file}")
            continue

        try:
            # Load JSON data
            json_data = load_json_file(file_path)

            # Get corresponding Pydantic model
            model = model_map[file_prefix]

            # Validate using Pydantic
            validated_data = model(**json_data)

            # Convert to dict to ensure all data is serializable
            validated_dict = validated_data.model_dump()

            validation_results.append(
                {
                    "file": json_file,
                    "status": "valid",
                    "model": model.__name__,
                }
            )
            print(f"✅ {json_file} is valid against {model.__name__}")

        except ValidationError as e:
            validation_results.append(
                {
                    "file": json_file,
                    "status": "invalid",
                    "model": model.__name__,
                    "errors": str(e),
                }
            )
            print(f"❌ {json_file} is invalid against {model.__name__}:")
            print(e)
        except Exception as e:
            validation_results.append(
                {
                    "file": json_file,
                    "status": "error",
                    "model": model.__name__,
                    "errors": str(e),
                }
            )
            print(f"❌ Error processing {json_file}:")
            print(e)

    # Save validation results
    with open("validation_results.json", "w") as f:
        json.dump(validation_results, f, indent=2)

    return validation_results


if __name__ == "__main__":
    validate_json_files()
