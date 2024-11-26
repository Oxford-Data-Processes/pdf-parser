class FormParser:
    def get_items_in_bounding_box(self, page_data, coordinates):
        items_in_box = []
        for item in page_data:
            bounding_box = item["bounding_box"]["decimal_coordinates"]
            if (
                bounding_box["top_left"]["x"] >= coordinates["top_left"]["x"]
                and bounding_box["top_left"]["y"] >= coordinates["top_left"]["y"]
                and bounding_box["bottom_right"]["x"]
                <= coordinates["bottom_right"]["x"]
                and bounding_box["bottom_right"]["y"]
                <= coordinates["bottom_right"]["y"]
            ):
                items_in_box.append(item)
        return items_in_box

    def get_text_from_items(self, items):
        return "".join([item["text"] for item in items])

    def get_text_from_page(self, page_content, coordinates):
        items_within_coordinates = self.get_items_in_bounding_box(
            page_content, coordinates
        )
        return self.get_text_from_items(items_within_coordinates)

    def get_output_data_for_rule(self, form_rule, page_number, pdf_data):
        coordinates = form_rule["config"]["coordinates"]
        page_content = pdf_data["pages"][page_number - 1]["content"]
        return {
            form_rule["config"]["field_name"]: self.get_text_from_page(
                page_content, coordinates
            )
        }
