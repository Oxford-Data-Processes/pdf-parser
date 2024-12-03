import json
import os
from src.extractor import Extractor
from src.parser import Parser, TableSplitter
from src.pdf_utils import ImageDrawer

template_name: str = "barclays_student"
identifier: str = "march"
template_path: str = os.path.join("src", "templates", f"{template_name}_template.json")
pdf_path: str = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)
pdf_data_path: str = os.path.join(
    "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)
output_path: str = os.path.join(
    "src", "outputs", f"{template_name}_{identifier}_output.json"
)


def extract_data_from_pdf(pdf_path, template_name, identifier):
    with open(pdf_path, "rb") as pdf_file:
        text_extractor = Extractor(pdf_file.read(), template_name, identifier)
        extracted_data = text_extractor.extract_data()

        with open(pdf_data_path, "w") as f:
            json.dump(extracted_data, f)


def load_json_data(file_path):
    with open(file_path) as f:
        return json.load(f)


def process_table(template, pdf_data, page_number):
    parser = Parser()
    table_splitter = TableSplitter(template, parser)
    page_content = pdf_data["pages"][page_number - 1]
    lines = page_content["lines"]

    for rule in template["rules"]:
        if rule["type"] == "table":
            table_rule = rule
            print_table_rule(table_rule)
            process_columns(
                table_rule, parser, table_splitter, lines, pdf_data, page_content
            )


def print_table_rule(table_rule):
    print(table_rule)
    for column in table_rule["config"]["columns"]:
        print(column)


def process_columns(table_rule, parser, table_splitter, lines, pdf_data, page_content):
    delimiter_field_name = "date"
    delimiter_type = "delimiter"

    for column in table_rule["config"]["columns"]:
        coordinates = column["coordinates"]

        if delimiter_type == "delimiter":
            delimiter_coordinates = parser.get_delimiter_column_coordinates(
                template, delimiter_field_name
            )
            lines_y_coordinates = table_splitter.split_table(
                delimiter_type, page_content, delimiter_coordinates
            )

        if delimiter_type == "line":
            max_pixel_value = (100, 100, 100)
            delimiter_coordinates = parser.get_delimiter_column_coordinates(
                template, delimiter_field_name
            )
            filtered_lines = parser.filter_lines_by_pixel_value(lines, max_pixel_value)

            # Extract only the y coordinates from the filtered lines
            lines_y_coordinates = [
                line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines
            ]

            print(lines_y_coordinates)

        image_with_lines = ImageDrawer.draw_column_box_and_lines(
            pdf_path, lines_y_coordinates, coordinates, page_number
        )
        image_with_lines.show()


# Main execution
extract_data_from_pdf(pdf_path, template_name, identifier)
template = load_json_data(template_path)
pdf_data = load_json_data(pdf_data_path)
output_data = load_json_data(output_path)

page_number = 2
process_table(template, pdf_data, page_number)
