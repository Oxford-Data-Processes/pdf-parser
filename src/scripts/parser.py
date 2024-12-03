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
        results = table_processor.process_tables(pdf_data)

        table_header = results[0]["columns"][0]["field_name"]
        data = []
        for result in results:
            for column in result["columns"]:
                data.append(column["field_name"])

        return {"table_header": table_header, "data": data}


class TableProcessor:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

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

    def process_table_data(
        self,
        table_rule: Dict,
        page_content: Dict,
        delimiter_field_name: str,
        delimiter_type: str,
    ) -> List[Dict]:
        """Process a single table's data."""

        delimiter_coordinates = self.get_delimiter_column_coordinates(
            self.template, delimiter_field_name
        )

        table_splitter = TableSplitter(self.template, self.parser)

        if delimiter_type == "line":

            lines_y_coordinates = table_splitter.split_table(
                delimiter_type, page_content
            )

        if delimiter_type == "field":
            delimiter_coordinates = self.get_delimiter_column_coordinates(
                self.template, delimiter_field_name
            )
            lines_y_coordinates = table_splitter.split_table(
                delimiter_type, page_content, delimiter_coordinates
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

    def process_tables(self, pdf_data: Dict) -> List[Dict]:
        """Process all tables according to template pages."""
        results = []
        # Process each page rule
        for page_rule in self.template["pages"]:
            if "tables" not in page_rule or not page_rule["tables"]:
                continue

            # Get page indexes
            page_indexes = self.parser.page_number_converter(
                page_rule["page_numbers"], len(pdf_data["pages"])
            )

            # Process each page
            for page_index in page_indexes:
                page_content = pdf_data["pages"][page_index]
                results.extend(self.process_page_tables(page_rule, page_content))

        return results

    def process_page_tables(self, page_rule: Dict, page_content: Dict) -> List[Dict]:
        """Process tables for a specific page."""
        results = []
        # Process each table rule
        for rule_id in page_rule["tables"]:
            # Get table rule
            table_rule = self.parser.get_rule_from_id(rule_id, self.template)

            delimiter_field_name = table_rule["config"]["row_delimiter"]["field_name"]
            delimiter_type = table_rule["config"]["row_delimiter"]["type"]

            # Process table data
            processed_columns = self.process_table_data(
                table_rule,
                page_content,
                delimiter_field_name,
                delimiter_type,
            )

            if processed_columns and any(
                col["lines_y_coordinates"] for col in processed_columns
            ):
                results.append(
                    {
                        "rule_id": rule_id,
                        "page_number": page_content["page_number"],
                        "columns": processed_columns,
                    }
                )
        return results


class TableSplitter:
    def __init__(self, template, parser):
        self.template = template
        self.parser = parser

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

    def split_table_by_line(self, lines):

        filtered_lines = self.filter_lines_by_pixel_value(lines)

        lines_y_coordinates = [
            line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines
        ]

        return sorted(list(set(lines_y_coordinates)))

    def split_table(
        self,
        row_delimiter_type: str,
        page_content,
        delimiter_coordinates=None,
    ):
        if row_delimiter_type == "line":

            return self.split_table_by_line(page_content["lines"])
        elif row_delimiter_type == "field":
            return self.split_table_by_delimiter(page_content, delimiter_coordinates)
