from typing import List, Dict


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
            max_pixel_value = table_rule["config"]["row_delimiter"].get(
                "max_pixel_value", 255
            )
            lines_y_coordinates = table_splitter.split_table(
                delimiter_type, page_content, max_pixel_value=max_pixel_value
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

    def filter_lines_by_pixel_value(self, lines, max_pixel_value=None):
        """Filter lines based on their average pixel value."""
        filtered_lines = []
        for line in lines:
            if "average_pixel_value" in line:
                avg_red, avg_green, avg_blue = line["average_pixel_value"]
                if (
                    avg_red <= max_pixel_value
                    and avg_green <= max_pixel_value
                    and avg_blue <= max_pixel_value
                ):
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

        line_separation_y_coordinates = self.average_y_coordinates(
            line_separation_y_coordinates
        )

        return line_separation_y_coordinates

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

    def split_table_by_line(self, lines, max_pixel_value=None):
        filtered_lines = self.filter_lines_by_pixel_value(lines, max_pixel_value)
        lines_y_coordinates = [
            line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines
        ]
        return sorted(list(set(lines_y_coordinates)))

    def split_table(
        self,
        row_delimiter_type: str,
        page_content,
        delimiter_field_name=None,
        rule_id=None,
        max_pixel_value=None,
    ):
        if row_delimiter_type == "line":
            return self.split_table_by_line(
                page_content["lines"], max_pixel_value=max_pixel_value
            )
        elif row_delimiter_type == "field":
            return self.split_table_by_field(
                page_content, delimiter_field_name, rule_id
            )
