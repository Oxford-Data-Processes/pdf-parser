from pydantic import BaseModel
import json
import os

from database.clients import Client
from database.financial_analysis import FinancialAnalysis
from database.document_metadata import DocumentMetadata
from database.assessments import Assessment
from database.documents import Document
from database.subscriptions import Subscription
from database.users import User


def write_schema_to_json(model: BaseModel, output_dir: str = "json_schemas") -> None:
    json_schema_str = model.schema()

    with open(
        os.path.join(output_dir, f"{model.__name__.lower()}_schema.json"), "w"
    ) as f:
        json.dump(json_schema_str, f, indent=4)


if __name__ == "__main__":
    write_schema_to_json(Client)
    write_schema_to_json(FinancialAnalysis)
    write_schema_to_json(DocumentMetadata)
    write_schema_to_json(Assessment)
    write_schema_to_json(Document)
    write_schema_to_json(Subscription)
    write_schema_to_json(User)
