from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from database.shared_models import Table, IdStr, PostcodeStr, NameStr


class TemplateMapping(BaseModel):
    """Mapping configuration for a template"""

    postcode_patterns: Optional[List[PostcodeStr]] = Field(
        default=None, description="List of postcode patterns this template maps to"
    )
    other_mappings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional mapping criteria (e.g. bank name, account type)",
    )


class Template(Table):
    """Template model for storing document processing templates with mappings"""

    name: NameStr = Field(description="Unique name of the template")
    template_data: Dict[str, Any] = Field(
        description="The actual template configuration stored as JSONB"
    )
    mappings: TemplateMapping = Field(
        description="Mapping rules for when to use this template"
    )
    is_default: bool = Field(
        default=False, description="Whether this is a default fallback template"
    )
    priority: int = Field(
        default=0,
        description="Priority of the template when multiple matches exist (higher = more priority)",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "lloyds_bank_statement",
                    "template_data": {
                        "metadata": {"template_name": "lloyds", "version": "1.0.0"},
                        "extraction_method": "ocr",
                        "rules": [],
                    },
                    "mappings": {
                        "postcode_patterns": ["SW1*", "EC1*"],
                        "other_mappings": {"bank_name": "Lloyds"},
                    },
                    "is_default": False,
                    "priority": 100,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "version": 1,
                    "is_active": True,
                }
            ]
        }
