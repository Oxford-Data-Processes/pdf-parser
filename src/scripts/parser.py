from typing import List, Dict, Any
from forms import FormProcessor
from tables import TableProcessor, TableSplitter
from datetime import datetime
import uuid
from ocr import ImageExtractor


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

    def get_text_from_ocr(self, jpg_bytes_page, coordinates):
        image_extractor = ImageExtractor(jpg_bytes_page, coordinates)
        return image_extractor.extract_text()

    def get_text_from_page(
        self, page_content, coordinates, extraction_method, jpg_bytes_page
    ):
        if extraction_method == "extraction":
            items_within_coordinates = self.get_items_in_bounding_box(
                page_content, coordinates
            )
            return self.get_text_from_items(items_within_coordinates)
        elif extraction_method == "ocr":
            import os

            # Create a directory for storing images if it doesn't exist
            output_dir = "extracted_images"
            os.makedirs(output_dir, exist_ok=True)

            # Generate a filename based on the coordinates
            coordinates_str = f"{coordinates['top_left']['x']}_{coordinates['top_left']['y']}_{coordinates['bottom_right']['x']}_{coordinates['bottom_right']['y']}"
            file_path = os.path.join(output_dir, f"{coordinates_str}.jpg")

            image_extractor = ImageExtractor(jpg_bytes_page, coordinates)

            # Save only the section of the jpg specified by coordinates
            section_image = image_extractor.extract_section()
            section_image.save(file_path, "JPEG")

            return self.get_text_from_ocr(jpg_bytes_page, coordinates)

    def get_output_data_from_form_rule(
        self, form_rule_id, page_index, pdf_data, template, jpg_bytes
    ):
        form_processor = FormProcessor(self)
        return form_processor.get_output_data_from_form_rule(
            form_rule_id,
            page_index,
            pdf_data,
            template,
            jpg_bytes,
        )

    def get_output_data_from_table_rule(
        self, table_rule_id, page_index, pdf_data, template, jpg_bytes
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

        jpg_bytes_page = jpg_bytes[page_index]

        extraction_method = template["extraction_method"]
        for column in processed_columns:
            split_boxes = table_splitter.split_bounding_box_by_lines(
                column["coordinates"], column["lines_y_coordinates"]
            )
            for row_index, box in enumerate(split_boxes):
                text_value = self.get_text_from_page(
                    pdf_data["pages"][page_index]["content"],
                    box,
                    extraction_method,
                    jpg_bytes_page,
                )
                if row_index not in data:
                    data[row_index] = {}
                data[row_index][column["field_name"]] = text_value

        # Convert the dictionary to a list of values ordered by row_index
        ordered_data = [data[row_index] for row_index in sorted(data.keys())]

        return ordered_data

    @staticmethod
    def parse_pdf(
        template: Dict[str, Any], pdf_data: Dict[str, Any], jpg_bytes: List[bytes]
    ) -> Dict[str, Any]:

        forms = []
        tables = []
        number_of_pages = len(pdf_data["pages"])

        for page_rule in template["pages"]:
            page_indexes = Parser().page_number_converter(
                page_rule["page_numbers"], number_of_pages
            )
            for page_index in page_indexes:
                if "forms" in page_rule and len(page_rule["forms"]) > 0:
                    for rule_id in page_rule["forms"]:
                        try:
                            form = Parser().get_output_data_from_form_rule(
                                rule_id, page_index, pdf_data, template, jpg_bytes
                            )
                            forms.append(form)
                        except IndexError:
                            print(
                                f"Rule ID '{rule_id}' not found in template rules or page index '{page_index}' is out of range."
                            )
                if "tables" in page_rule and len(page_rule["tables"]) > 0:
                    for rule_id in page_rule["tables"]:
                        try:
                            table_data = Parser().get_output_data_from_table_rule(
                                rule_id, page_index, pdf_data, template, jpg_bytes
                            )

                            tables.append({"data": table_data})
                        except IndexError:
                            print(
                                f"Rule ID '{rule_id}' not found in template rules or page index '{page_index}' is out of range."
                            )

        output = {
            "metadata": {
                "document_id": str(uuid.uuid4()),
                "parsed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "number_of_pages": number_of_pages,
            },
            "pages": [{"forms": forms, "tables": tables}],
        }

        return output
