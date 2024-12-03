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
        return {"table_rule_id": table_rule_id}


class TableProcessor:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

    def get_table_data(self, rule_id: str, page_index: int, pdf_data) -> Dict:
        """Get table data for a specific rule and page."""
        table_rule = self.parser.get_rule_from_id(rule_id, self.template)
        if not table_rule:
            raise ValueError(f"Table rule {rule_id} not found")

        page_content = pdf_data["pages"][page_index]
        lines = page_content["lines"]

        filtered_lines = self.parser.filter_lines_by_pixel_value(lines)
        lines_y_coordinates = self.get_y_coordinates(filtered_lines)

        if not lines_y_coordinates:
            return None

        return self.process_columns(
            table_rule, lines_y_coordinates, rule_id, page_index
        )

    def get_y_coordinates(self, filtered_lines):
        """Get y-coordinates from filtered lines."""
        return sorted(
            set(line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines)
        )

    def process_columns(self, table_rule, lines_y_coordinates, rule_id, page_index):
        """Process each column and return structured data."""
        columns_data = []
        for column in table_rule["config"]["columns"]:
            column_data = {
                "field_name": column["field_name"],
                "coordinates": column["coordinates"],
                "lines_y_coordinates": lines_y_coordinates,
            }
            columns_data.append(column_data)

        return {
            "rule_id": rule_id,
            "page_number": page_index + 1,
            "columns": columns_data,
        }

    def process_tables(self, pdf_data: Dict) -> List[Dict]:
        """Process all tables according to template pages."""
        results = []
        number_of_pages = len(pdf_data["pages"])

        for page_rule in self.template["pages"]:
            if "tables" not in page_rule:
                continue

            page_indexes = self.parser.page_number_converter(
                page_rule["page_numbers"], number_of_pages
            )

            for page_index in page_indexes:
                results.extend(
                    self.process_table_rules(page_rule, page_index, pdf_data)
                )

        return results

    def process_table_rules(self, page_rule, page_index, pdf_data):
        """Process each table rule for the given page."""
        results = []
        for rule_id in page_rule["tables"]:
            try:
                table_data = self.get_table_data(rule_id, page_index, pdf_data)
                if table_data:
                    results.append(table_data)
            except Exception:
                continue  # Handle exceptions silently

        return results


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
        elif row_delimiter_type == "field":
            return self.split_table_by_delimiter(page_content, coordinates)
