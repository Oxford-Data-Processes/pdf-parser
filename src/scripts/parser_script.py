import json
import os
from extractor import Extractor
from parser import Parser, TableSplitter
from pdf_utils import ImageDrawer

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


parser = Parser()

page_number = 2

table_splitter = TableSplitter(template, parser)

page_content = pdf_data["pages"][page_number - 1]

lines = page_content["lines"]

for rule in template["rules"][-1:]:
    if rule["type"] == "table":
        table_rule = rule
        print(table_rule)
        for column in table_rule["config"]["columns"]:
            print(column)
            coordinates = column["coordinates"]
            delimiter_field_name = "description"

            delimiter_type = "line"

            if delimiter_type == "field":
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
                filtered_lines = parser.filter_lines_by_pixel_value(
                    lines, max_pixel_value
                )

                # Extract only the y coordinates from the filtered lines
                lines_y_coordinates = [
                    line["decimal_coordinates"]["top_left"]["y"]
                    for line in filtered_lines
                ]

                print(lines_y_coordinates)

            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path, lines_y_coordinates, coordinates, page_number
            )
            image_with_lines.show()
