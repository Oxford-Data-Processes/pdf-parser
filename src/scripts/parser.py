from typing import List, Dict


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


class TableProcessor:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

    def get_delimiter_column_coordinates(self, template, delimiter_field_name, rule_id):
        """Get the coordinates of the description column from the template."""

        delimiter_coordinates = None

        rule = self.parser.get_rule_from_id(rule_id, template)

        if rule["type"] == "table":
            for column in rule["config"]["columns"]:
                if column["field_name"] == delimiter_field_name:
                    delimiter_coordinates = column["coordinates"]
                    break

        return delimiter_coordinates

    def process_table_data(
        self,
        table_rule: Dict,
        page_content: Dict,
        delimiter_field_name: str,
        delimiter_type: str,
    ) -> List[Dict]:
        """Process a single table's data."""

        delimiter_coordinates = self.get_delimiter_column_coordinates(
            self.template, delimiter_field_name, table_rule["rule_id"]
        )

        table_splitter = TableSplitter(self.template, self.parser)

        if delimiter_type == "line":

            lines_y_coordinates = table_splitter.split_table(
                delimiter_type, page_content
            )

        if delimiter_type == "field":

            lines_y_coordinates = table_splitter.split_table(
                delimiter_type,
                page_content,
                delimiter_field_name,
                table_rule["rule_id"],
            )

        if not delimiter_coordinates:
            raise ValueError("Delimiter coordinates not found")

        # Process each column
        processed_columns = []
        for column in table_rule["config"]["columns"]:
            processed_columns.append(
                {
                    "field_name": column["field_name"],
                    "coordinates": column["coordinates"],
                    "lines_y_coordinates": lines_y_coordinates,
                }
            )

        return processed_columns


class TableSplitter:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

    def split_bounding_box_by_lines(
        self, bounding_box: Dict, lines_y_coordinates: List[float]
    ) -> List[Dict]:
        """Split a bounding box by given y-coordinates."""
        split_boxes = []
        top_left_y = bounding_box["top_left"]["y"]
        bottom_right_y = bounding_box["bottom_right"]["y"]

        # Add the top of the bounding box as the first coordinate
        previous_y = top_left_y

        for line_y in sorted(lines_y_coordinates):
            if top_left_y < line_y < bottom_right_y:
                # Create a new bounding box for the area above the line
                split_boxes.append(
                    {
                        "top_left": {
                            "x": bounding_box["top_left"]["x"],
                            "y": previous_y,
                        },
                        "bottom_right": {
                            "x": bounding_box["bottom_right"]["x"],
                            "y": line_y,
                        },
                    }
                )
                previous_y = line_y

        # Add the last segment from the last line to the bottom of the bounding box
        if previous_y < bottom_right_y:
            split_boxes.append(
                {
                    "top_left": {"x": bounding_box["top_left"]["x"], "y": previous_y},
                    "bottom_right": {
                        "x": bounding_box["bottom_right"]["x"],
                        "y": bottom_right_y,
                    },
                }
            )

        return split_boxes

    # Filter lines by pixel value
    def filter_lines_by_pixel_value(self, lines, max_pixel_value=(100, 100, 100)):
        """Filter lines based on their average pixel value."""
        filtered_lines = []
        for line in lines:
            if "average_pixel_value" in line:
                avg_red, avg_green, avg_blue = line["average_pixel_value"]
                max_red, max_green, max_blue = max_pixel_value

                if avg_red < max_red and avg_green < max_green and avg_blue < max_blue:
                    filtered_lines.append(line)
        return filtered_lines

    def split_table_by_field(self, page_content, delimiter_field_name, rule_id):
        text_coordinates = page_content["content"]

        table_processor = TableProcessor(self.template, self.parser)

        delimiter_coordinates = table_processor.get_delimiter_column_coordinates(
            self.template, delimiter_field_name, rule_id
        )

        items_within_coordinates = self.parser.get_items_in_bounding_box(
            text_coordinates, delimiter_coordinates
        )

        line_separation_y_coordinates = sorted(
            list(
                set(
                    item["bounding_box"]["decimal_coordinates"]["top_left"]["y"]
                    for item in items_within_coordinates
                )
            )
        )

        return self.average_y_coordinates(line_separation_y_coordinates)

    def average_y_coordinates(self, y_coordinates):
        threshold = 0.01
        averaged_y_coordinates = []
        while y_coordinates:
            current_value = y_coordinates.pop(0)
            close_values = [current_value]

            # Check for values within 0.01
            for value in y_coordinates:
                if abs(value - current_value) < threshold:
                    close_values.append(value)
                    y_coordinates.remove(value)

            # Calculate the average and add to the result
            averaged_y_coordinates.append(sum(close_values) / len(close_values))

        return averaged_y_coordinates

    def split_table_by_line(self, lines):

        filtered_lines = self.filter_lines_by_pixel_value(lines)

        lines_y_coordinates = [
            line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines
        ]

        print("LINE Y COORDINATES")
        print(lines_y_coordinates)
        print("\n")

        return sorted(list(set(lines_y_coordinates)))

    def split_table(
        self,
        row_delimiter_type: str,
        page_content,
        delimiter_field_name,
        rule_id,
    ):
        if row_delimiter_type == "line":
            return self.split_table_by_line(page_content["lines"])
        elif row_delimiter_type == "field":
            return self.split_table_by_field(
                page_content, delimiter_field_name, rule_id
            )
