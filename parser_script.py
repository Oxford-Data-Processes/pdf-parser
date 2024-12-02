import json
import os
from src.extractor import Extractor

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

with open(pdf_path, "rb") as pdf_file:
    text_extractor = Extractor(pdf_file.read(), template_name, identifier)
    extracted_data = text_extractor.extract_data()

    with open(pdf_data_path, "w") as f:
        json.dump(extracted_data, f)

template = json.load(open(template_path))
pdf_data = json.load(open(pdf_data_path))

output_data = json.load(open(output_path))


from src.parser import Parser, TableSplitter
from src.pdf_utils import ImageDrawer

parser = Parser()

page_number = 2

table_splitter = TableSplitter(template, parser)

page_content = pdf_data["pages"][page_number - 1]

template = json.load(open(template_path))


def get_column_data_by_field_name(table_rule, field_name):
    for column in table_rule["config"]["columns"]:
        if column["field_name"] == field_name:
            return column


for rule in template["rules"][-1:]:
    if rule["type"] == "table":
        table_rule = rule
        print(table_rule)
        for column in table_rule["config"]["columns"][1:2]:
            print(column)
            coordinates = column["coordinates"]
            delimiter_field_name = "description"

            delimiter_type = "line"

            if delimiter_type == "delimiter":

                column_data = get_column_data_by_field_name(
                    table_rule, delimiter_field_name
                )
                delimiter_coordinates = column_data["coordinates"]

                lines_y_coordinates = table_splitter.split_table(
                    delimiter_type, page_content, delimiter_coordinates
                )

            if delimiter_type == "line":

                pixel_maximum_value = (255, 255, 255)

                column_data = get_column_data_by_field_name(
                    table_rule, delimiter_field_name
                )
                delimiter_coordinates = column_data["coordinates"]

                lines_y_coordinates = table_splitter.split_table(
                    delimiter_type,
                    page_content,
                    delimiter_coordinates,
                    pixel_maximum_value,
                )
                print(lines_y_coordinates)

            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path, lines_y_coordinates, coordinates, page_number
            )
            image_with_lines.show()
