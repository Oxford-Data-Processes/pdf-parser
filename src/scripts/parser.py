from typing import List, Dict
from forms import FormProcessor
from tables import TableProcessor, TableSplitter


class Parser:
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

    def get_rule_from_id(self, rule_id, template):
        return [item for item in template["rules"] if item["rule_id"] == rule_id][0]

    def get_items_in_bounding_box(
        self, text_coordinates, box_coordinates, threshold=0.005
    ):
        items_in_box = []
        for item in text_coordinates:
            bounding_box = item["bounding_box"]["decimal_coordinates"]
            if (
                bounding_box["top_left"]["x"]
                >= box_coordinates["top_left"]["x"] - threshold
                and bounding_box["top_left"]["y"]
                >= box_coordinates["top_left"]["y"] - threshold
                and bounding_box["bottom_right"]["x"]
                <= box_coordinates["bottom_right"]["x"] + threshold
                and bounding_box["bottom_right"]["y"]
                <= box_coordinates["bottom_right"]["y"] + threshold
            ):
                items_in_box.append(item)
        return items_in_box

    def get_text_from_items(self, items):
        return " ".join([item["text"] for item in items])

    def get_text_from_page(self, page_content, coordinates):
        items_within_coordinates = self.get_items_in_bounding_box(
            page_content, coordinates
        )
        return self.get_text_from_items(items_within_coordinates)

    def get_output_data_from_form_rule(
        self, form_rule_id, page_index, pdf_data, template
    ):
        form_processor = FormProcessor(self)
        return form_processor.get_output_data_from_form_rule(
            form_rule_id, page_index, pdf_data, template
        )

    def get_output_data_from_table_rule(
        self, table_rule_id, page_index, pdf_data, template
    ):
        table_processor = TableProcessor(template, self)
        table_splitter = TableSplitter(template, self)
        table_rule = self.get_rule_from_id(table_rule_id, template)
        delimiter_field_name = table_rule["config"]["row_delimiter"]["field_name"]
        delimiter_type = table_rule["config"]["row_delimiter"]["type"]
        processed_columns = table_processor.process_table_data(
            table_rule,
            pdf_data["pages"][page_index],
            delimiter_field_name,
            delimiter_type,
        )

        data = {}

        for column in processed_columns:
            split_boxes = table_splitter.split_bounding_box_by_lines(
                column["coordinates"], column["lines_y_coordinates"]
            )
            for row_index, box in enumerate(split_boxes):
                text_value = self.get_text_from_page(
                    pdf_data["pages"][page_index]["content"], box
                )
                if row_index not in data:
                    data[row_index] = {}
                data[row_index][column["field_name"]] = text_value

        # Convert the dictionary to a list of values ordered by row_index
        ordered_data = [data[row_index] for row_index in sorted(data.keys())]

        return ordered_data
