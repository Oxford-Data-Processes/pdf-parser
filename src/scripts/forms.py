from typing import Dict


class FormProcessor:
    def __init__(self, parser):
        self.parser = parser

    def get_output_data_from_form_rule(
        self, form_rule_id: str, page_index: int, pdf_data: Dict, template: Dict
    ) -> Dict:
        form_rule = self.parser.get_rule_from_id(form_rule_id, template)
        coordinates = form_rule["config"]["coordinates"]
        page_content = pdf_data["pages"][page_index]["content"]
        return {
            form_rule["config"]["field_name"]: self.parser.get_text_from_page(
                page_content, coordinates
            )
        }
