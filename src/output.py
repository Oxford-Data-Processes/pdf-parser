import json


class JSONBuilder:
    def __init__(self):
        self.output = {}

    def build_metadata(self, document_id, parsed_at, number_of_pages):
        """Constructs the metadata dictionary."""
        self.output["metadata"] = {
            "document_id": document_id,
            "parsed_at": parsed_at,
            "number_of_pages": number_of_pages,
        }

    def build_pages(self, pages_data):
        """Iterates over pages_data (list of PageData objects) and converts each to a dictionary."""
        self.output["pages"] = [
            {
                "page_number": page.page_number,
                "forms": page.forms,
                "tables": page.tables,
            }
            for page in pages_data
        ]

    def build_json(self, metadata, pages):
        """Combines metadata and pages into the final JSON structure."""
        self.build_metadata(**metadata)
        self.build_pages(pages)

    def to_json(self):
        """Serializes the final JSON structure to a JSON string or returns as a dictionary."""
        return json.dumps(self.output, indent=4)
