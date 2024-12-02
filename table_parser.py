import json
import os
from src.extractor import TextExtractor
from src.parser import Parser, TableSplitter
from src.pdf_utils import ImageDrawer

template_path: str = os.path.join("src", "templates", "barclays_student_template.json")
pdf_path: str = os.path.join(
    "data", "bank_statements", "barclays_student", "pdf", "barclays_student_march.pdf"
)
pdf_data_path: str = os.path.join(
    "src", "pdf_data", "barclays_student_march_pdf_data.json"
)
output_path: str = os.path.join("src", "outputs", "barclays_student_march_output.json")

with open(pdf_path, "rb") as pdf_file:
    text_extractor = TextExtractor(pdf_file.read())
    extracted_data = text_extractor.extract_text()

    with open(pdf_data_path, "w") as f:
        json.dump(extracted_data, f)

template = json.load(open(template_path))
pdf_data = json.load(open(pdf_data_path))

output_data = json.load(open(output_path))


parser = Parser()

page_number = 2

table_splitter = TableSplitter(template, parser)

page_content = pdf_data["pages"][page_number - 1]

template = json.load(open(template_path))


def get_column_coordinates_by_field_name(table_rule, field_name):
    for column in table_rule["config"]["columns"]:
        if column["field_name"] == field_name:
            return column["coordinates"]


for rule in template["rules"][-1:]:
    if rule["type"] == "table":
        table_rule = rule
        print(table_rule)
        for column in table_rule["config"]["columns"][1:2]:
            print(column)
            coordinates = column["coordinates"]
            delimiter_field_name = "description"

            delimiter_type = "line"

            delimiter_coordinates = get_column_coordinates_by_field_name(
                table_rule, delimiter_field_name
            )

            lines_y_coordinates = table_splitter.split_table(
                delimiter_type, page_content, delimiter_coordinates
            )
            print(lines_y_coordinates)

            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path, lines_y_coordinates, coordinates, page_number
            )
            image_with_lines.show()
