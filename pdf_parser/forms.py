from typing import Dict, List, Any
from pdf_parser.coordinate_utils import CoordinateUtils
from pdf_parser.extractors import TextExtractor


class FormProcessor:
    def __init__(self, text_extractor: TextExtractor) -> None:
        self.text_extractor = text_extractor
        self.coordinate_utils = CoordinateUtils()

    def get_output_data_from_form_rule(
        self,
        form_rule_id: str,
        page_index: int,
        pdf_data: Dict[str, Any],
        template: Dict[str, Any],
        jpg_bytes: List[bytes],
    ) -> Dict[str, str]:
        form_rule = self.coordinate_utils.get_rule_from_id(form_rule_id, template)
        config = form_rule["config"]
        coordinates = config.get("coordinates")
        page_content = pdf_data["pages"][page_index]["content"]
        extraction_method = template["extraction_method"]
        jpg_bytes_page = jpg_bytes[page_index]
        search_type = config.get("search_type")
        regex = config.get("regex")

        return {
            config["field_name"]: self.text_extractor.get_text_from_page(
                page_content,
                coordinates,
                extraction_method,
                jpg_bytes_page,
                search_type=search_type,
                regex=regex,
            )
        }
