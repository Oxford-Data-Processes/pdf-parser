from typing import Dict, List


class FormProcessor:
    def __init__(self, parser):
        self.parser = parser

    def get_output_data_from_form_rule(
        self,
        form_rule_id: str,
        page_index: int,
        pdf_data: Dict,
        template: Dict,
        jpg_bytes: List[bytes],
    ) -> Dict:
        form_rule = self.parser.get_rule_from_id(form_rule_id, template)
        coordinates = form_rule["config"]["coordinates"]
        page_content = pdf_data["pages"][page_index]["content"]
        extraction_method = template["extraction_method"]
        jpg_bytes_page = jpg_bytes[page_index]

        return {
            form_rule["config"]["field_name"]: self.parser.get_text_from_page(
                page_content, coordinates, extraction_method, jpg_bytes_page
            )
        }
