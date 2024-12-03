import json
import os
from extractor import Extractor
from parser import Parser, TableSplitter
from pdf_utils import ImageDrawer

template_name: str = "barclays_student"
identifier: str = "may"
template_path: str = os.path.join("src", "templates", f"{template_name}_template.json")
pdf_path: str = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)
pdf_data_path: str = os.path.join(
    "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)


def extract_data_from_pdf(pdf_path, template_name, identifier):
    with open(pdf_path, "rb") as pdf_file:
        text_extractor = Extractor(pdf_file.read(), template_name, identifier)
        extracted_data = text_extractor.extract_data()

        with open(pdf_data_path, "w") as f:
            json.dump(extracted_data, f, indent=4, sort_keys=True)


def load_json_data(file_path):
    with open(file_path) as f:
        return json.load(f)


def process_column(
    table_rule,
    parser,
    table_splitter,
    lines,
    page_content,
    delimiter_field_name,
    delimiter_type,
    max_pixel_value=(100, 100, 100),
):

    coordinates = column["coordinates"]

    if delimiter_type == "field":
        delimiter_coordinates = parser.get_delimiter_column_coordinates(
            template, delimiter_field_name
        )
        lines_y_coordinates = table_splitter.split_table(
            delimiter_type, page_content, delimiter_coordinates
        )

    elif delimiter_type == "line":
        delimiter_coordinates = parser.get_delimiter_column_coordinates(
            template, delimiter_field_name
        )
        filtered_lines = parser.filter_lines_by_pixel_value(lines, max_pixel_value)

        # Extract only the y coordinates from the filtered lines
        lines_y_coordinates = [
            line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines
        ]

    return lines_y_coordinates, coordinates


# Main execution
extract_data_from_pdf(pdf_path, template_name, identifier)
template = load_json_data(template_path)
pdf_data = load_json_data(pdf_data_path)


parser = Parser()
splitter = TableSplitter(template, parser)


for table_rule in template["rules"]:
    if table_rule["type"] == "table":
        if table_rule["rule_id"] == "transactions_first_page":
            page_number = 2
        elif table_rule["rule_id"] == "transactions_second_page_onwards":
            page_number = 3

        page_content = pdf_data["pages"][page_number - 1]
        lines = page_content["lines"]
        delimiter_field_name = "description"
        delimiter_type = "line"
        processed_columns = []

        for column in table_rule["config"]["columns"]:
            lines_y_coordinates, coordinates = process_column(
                table_rule,
                parser,
                splitter,
                lines,
                page_content,
                delimiter_field_name,
                delimiter_type,
            )

            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path, lines_y_coordinates, coordinates, page_number
            )
            image_with_lines.show()
