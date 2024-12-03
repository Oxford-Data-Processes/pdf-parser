from typing import List, Optional


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
        self, text_coordinates, box_coordinates, threshold=0.01
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

    def get_delimiter_column_coordinates(self, template, delimiter_field_name):
        """Get the coordinates of the description column from the template."""
        delimiter_coordinates = None
        for rule in template["rules"]:
            if rule["type"] == "table":
                for column in rule["config"]["columns"]:
                    if column["field_name"] == delimiter_field_name:
                        delimiter_coordinates = column["coordinates"]
                        break
                break

        if not delimiter_coordinates:
            raise ValueError("Description column coordinates not found in template")

        return delimiter_coordinates

    # Filter lines by pixel value
    def filter_lines_by_pixel_value(self, lines, max_pixel_value):
        """Filter lines based on their average pixel value."""
        filtered_lines = []
        for line in lines:
            if "average_pixel_value" in line:
                avg_red, avg_green, avg_blue = line["average_pixel_value"]
                max_red, max_green, max_blue = max_pixel_value

                if avg_red < max_red and avg_green < max_green and avg_blue < max_blue:
                    filtered_lines.append(line)
        return filtered_lines

    def get_output_data_from_form_rule(
        self, form_rule_id, page_index, pdf_data, template
    ):
        form_rule = self.get_rule_from_id(form_rule_id, template)
        coordinates = form_rule["config"]["coordinates"]
        page_content = pdf_data["pages"][page_index]["content"]
        return {
            form_rule["config"]["field_name"]: self.get_text_from_page(
                page_content, coordinates
            )
        }

    def get_output_data_from_table_rule(
        self, table_rule_id, page_index, pdf_data, template
    ):
        table_rule = self.get_rule_from_id(table_rule_id, template)
        return {"table_rule_id": table_rule_id}


class TableProcessor:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

    def process_table(template, page_content):
        parser = Parser()
        table_splitter = TableSplitter(template, parser)
        lines = page_content["lines"]

        for table_rule in template["rules"]:
            if table_rule["type"] == "table":
                process_columns(
                    table_rule, parser, table_splitter, lines, pdf_data, page_content
                )


class TableSplitter:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

    def split_table_by_delimiter(self, page_content, coordinates):

        text_coordinates = page_content["content"]
        items_within_coordinates = self.parser.get_items_in_bounding_box(
            text_coordinates, coordinates
        )

        line_separation_y_coordinates = {
            item["bounding_box"]["decimal_coordinates"]["top_left"]["y"]
            for item in items_within_coordinates
        }
        return sorted(list(set(line_separation_y_coordinates)))

    def split_table_by_line(
        self,
        lines,
        coordinates,
        pixel_maximum_value=None,
        threshold=0.01,
    ):

        min_y = coordinates["top_left"]["y"] - threshold
        max_y = coordinates["bottom_right"]["y"] + threshold

        min_x = coordinates["top_left"]["x"] - threshold
        max_x = coordinates["bottom_right"]["x"] + threshold

        line_separation_y_coordinates = []

        for line in lines:
            x0 = line["decimal_coordinates"]["top_left"]["x"]
            x1 = line["decimal_coordinates"]["bottom_right"]["x"]
            y0 = line["decimal_coordinates"]["top_left"]["y"]
            y1 = line["decimal_coordinates"]["bottom_right"]["y"]

            red, green, blue = line["average_pixel_value"]

            if (
                x0 >= min_x
                and x1 <= max_x
                and y0 >= min_y
                and y1 <= max_y
                and red < pixel_maximum_value[0]
                and green < pixel_maximum_value[1]
                and blue < pixel_maximum_value[2]
            ):
                line_separation_y_coordinates.append(y0)

        return sorted(list(set(line_separation_y_coordinates)))

    def split_table(
        self,
        row_delimiter_type: str,
        page_content,
        coordinates,
        pixel_maximum_value=None,
    ):
        if row_delimiter_type == "line":
            return self.split_table_by_line(
                page_content["lines"],
                coordinates,
                pixel_maximum_value,
            )
        elif row_delimiter_type == "delimiter":
            return self.split_table_by_delimiter(page_content, coordinates)
