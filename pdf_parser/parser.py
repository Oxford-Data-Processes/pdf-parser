import json
import os
import uuid
from jsonschema import validate
from datetime import datetime
from typing import Any, Dict, List, Optional

from pdf_parser.forms import FormProcessor
from pdf_parser.extractors import TextExtractor
from pdf_parser.coordinate_utils import CoordinateUtils
from pdf_parser.tables import TableProcessor, TableSplitter
from pdf_parser.pydantic_models import Document


class Parser:
    def __init__(self) -> None:
        self.coordinate_utils = CoordinateUtils()
        self.text_extractor = TextExtractor(self.coordinate_utils)

    def page_number_converter(
        self, page_numbers: str, number_of_pages: int
    ) -> List[int]:
        if ":" in page_numbers:
            left_index = int(page_numbers.split(":")[0])
            right_index = int(page_numbers.split(":")[1])
        else:
            index = int(page_numbers)
            if index >= 0:
                index = index - 1
            elif index < 0:
                index = number_of_pages + index
            return [index]

        if left_index > 0:
            left_index -= 1
        if right_index > 0:
            right_index -= 1

        if left_index < 0:
            left_index = number_of_pages + left_index + 1
        if right_index < 0:
            right_index = number_of_pages + right_index + 1

        if left_index == right_index:
            return [left_index]

        return list(range(left_index, right_index))

    def get_rule_from_id(
        self, rule_id: str, template: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self.coordinate_utils.get_rule_from_id(rule_id, template)

    def get_text_from_page(
        self,
        page_content: List[Dict[str, Any]],
        coordinates: Optional[Dict[str, Dict[str, float]]],
        extraction_method: str,
        jpg_bytes_page: bytes,
        search_type: Optional[str] = None,
        regex: Optional[str] = None,
    ) -> str:
        return self.text_extractor.get_text_from_page(
            page_content,
            coordinates,
            extraction_method,
            jpg_bytes_page,
            search_type=search_type,
            regex=regex,
        )

    def get_output_data_from_form_rule(
        self,
        form_rule_id: str,
        page_index: int,
        pdf_data: Dict[str, Any],
        template: Dict[str, Any],
        jpg_bytes: List[bytes],
    ) -> Dict[str, str]:
        form_processor = FormProcessor(self)
        return form_processor.get_output_data_from_form_rule(
            form_rule_id,
            page_index,
            pdf_data,
            template,
            jpg_bytes,
        )

    def get_output_data_from_table_rule(
        self,
        table_rule_id: str,
        page_index: int,
        pdf_data: Dict[str, Any],
        template: Dict[str, Any],
        jpg_bytes: List[bytes],
    ) -> List[Dict[str, Any]]:
        table_processor = TableProcessor(template)
        table_splitter = TableSplitter(template)
        table_rule = self.get_rule_from_id(table_rule_id, template)
        delimiter_field_name = table_rule["config"]["row_delimiter"]["field_name"]
        delimiter_type = table_rule["config"]["row_delimiter"]["type"]
        processed_columns = table_processor.process_table_data(
            table_rule,
            pdf_data["pages"][page_index],
            delimiter_field_name,
            delimiter_type,
        )

        data: Dict[int, Dict[str, str]] = {}

        jpg_bytes_page = jpg_bytes[page_index]

        extraction_method = template["extraction_method"]
        for column in processed_columns:
            split_boxes = table_splitter.split_bounding_box_by_lines(
                column["coordinates"], column["lines_y_coordinates"]
            )
            for row_index, box in enumerate(split_boxes):
                text_value = self.get_text_from_page(
                    pdf_data["pages"][page_index]["content"],
                    box,
                    extraction_method,
                    jpg_bytes_page,
                )
                if row_index not in data:
                    data[row_index] = {}
                data[row_index][column["field_name"]] = text_value

        # Convert the dictionary to a list of values ordered by row_index
        ordered_data = [data[row_index] for row_index in sorted(data.keys())]

        return ordered_data

    @staticmethod
    def parse_pdf(
        template: Dict[str, Any], pdf_data: Dict[str, Any], jpg_bytes: List[bytes]
    ) -> Dict[str, Any]:

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "schema",
            "template_json_schema.json",
        )

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path) as schema_file:
            template_json_schema = json.load(schema_file)

        validate(instance=template, schema=template_json_schema)

        forms = []
        tables = []
        number_of_pages = len(pdf_data["pages"])

        for page_rule in template["pages"]:
            page_indexes = Parser().page_number_converter(
                page_rule["page_numbers"], number_of_pages
            )
            for page_index in page_indexes:
                if "forms" in page_rule and len(page_rule["forms"]) > 0:
                    for rule_id in page_rule["forms"]:
                        try:
                            form = Parser().get_output_data_from_form_rule(
                                rule_id, page_index, pdf_data, template, jpg_bytes
                            )
                            forms.append(form)
                        except IndexError:
                            print(
                                f"Rule ID '{rule_id}' not found in template rules or page index '{page_index}' is out of range."
                            )
                if "tables" in page_rule and len(page_rule["tables"]) > 0:
                    for rule_id in page_rule["tables"]:
                        try:
                            table_data = Parser().get_output_data_from_table_rule(
                                rule_id, page_index, pdf_data, template, jpg_bytes
                            )

                            tables.append({"data": table_data})
                        except IndexError:
                            print(
                                f"Rule ID '{rule_id}' not found in template rules or page index '{page_index}' is out of range."
                            )

        output = {
            "metadata": {
                "document_id": str(uuid.uuid4()),
                "parsed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "number_of_pages": number_of_pages,
            },
            "pages": [{"forms": forms, "tables": tables}],
        }

        output_document = Document(**output)

        return output_document.model_dump_json()
