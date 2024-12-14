from pydantic import BaseModel
import json
import os
from typing import Dict, Any, Set, Type
from enum import Enum

from database.clients import Client
from database.financial_analysis import FinancialAnalysis
from database.document_metadata import DocumentMetadata
from database.assessments import Assessment
from database.documents import Document
from database.subscriptions import Subscription
from database.users import User


def write_schema_to_json(
    model: type[BaseModel], output_dir: str = "json_schemas"
) -> None:
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate schema using the new Pydantic v2 method
    json_schema = model.model_json_schema(by_alias=True)

    # Write schema to file
    with open(
        os.path.join(output_dir, f"{model.__name__.lower()}_schema.json"), "w"
    ) as f:
        json.dump(json_schema, f, indent=4)


if __name__ == "__main__":
    # Define models to process
    models = [
        ("Client", Client),
        ("Financial Analysis", FinancialAnalysis),
        ("Document Metadata", DocumentMetadata),
        ("Assessment", Assessment),
        ("Document", Document),
        ("Subscription", Subscription),
        ("User", User),
    ]

    # Process each model
    for name, model in models:
        try:
            print(f"Generating schema for {name}...")
            write_schema_to_json(model)
            print(f"✓ {name} schema generated successfully")
        except Exception as e:
            print(f"✗ Error generating {name} schema: {str(e)}")
            raise  # Re-raise to see full traceback
