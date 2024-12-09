import json
import os
from extractor import Extractor
from parser import Parser, TableProcessor
from pdf_utils import ImageDrawer
from typing import Dict, List, Optional

# Update paths to be relative to src directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(SRC_DIR)

FORMS_PAGE_NUMBER = 1

document_type = "bank_statements"
template_name: str = "first_direct"
identifier: str = "april"
template_path: str = os.path.join(
    SRC_DIR, "templates", f"{template_name}_template.json"
)
pdf_path: str = os.path.join(
    ROOT_DIR,
    "data",
    document_type,
    template_name,
    "pdf",
    f"{template_name}_{identifier}.pdf",
)

pdf_data_path: str = os.path.join(
    SRC_DIR, "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)


def extract_data_from_pdf(pdf_path: str, template_name: str, identifier: str) -> None:
    """Extract data from PDF and save to JSON."""
    print(f"Extracting data from PDF: {pdf_path}")

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(pdf_data_path), exist_ok=True)

    with open(pdf_path, "rb") as pdf_file:
        text_extractor = Extractor(pdf_file.read(), template_name, identifier)
        extracted_data = text_extractor.extract_data()
        with open(pdf_data_path, "w") as f:
            json.dump(extracted_data, f, indent=4, sort_keys=True)
    print(f"Data extracted and saved to: {pdf_data_path}")


def load_json_data(file_path: str) -> Dict:
    """Load JSON data from file."""
    print(f"Loading JSON data from: {file_path}")
    with open(file_path) as f:
        return json.load(f)


def process_tables(template: Dict, pdf_data: Dict) -> List[Dict]:
    """Process all tables in the PDF data."""
    results = []

    # Find all table rules
    table_rules = [rule for rule in template["rules"] if rule["type"] == "table"]

    # Process each table rule
    for table_rule in table_rules:
        try:
            # Get rule ID and configuration
            rule_id = table_rule.get("rule_id")
            if rule_id is None:
                print(f"Warning: Missing 'rule_id' in table rule: {table_rule}")
                continue

            delimiter_field_name = table_rule["config"]["row_delimiter"]["field_name"]
            delimiter_type = table_rule["config"]["row_delimiter"]["type"]

            page_number = None
            for page_rule in template["pages"]:
                if "tables" in page_rule and rule_id in page_rule["tables"]:
                    page_indexes = parser.page_number_converter(
                        page_rule["page_numbers"], len(pdf_data["pages"])
                    )
                    print("PAGE_INDEXES", page_indexes)
                    if page_indexes:
                        page_number = page_indexes[0] + 1
                        break

            if page_number is None or page_number > len(pdf_data["pages"]):
                print(f"Warning: Invalid page number {page_number} for rule {rule_id}")
                continue

            # Process the table
            page_content = pdf_data["pages"][page_number - 1]
            table_processor = TableProcessor(template, parser)
            processed_columns = table_processor.process_table_data(
                table_rule, page_content, delimiter_field_name, delimiter_type
            )

            if processed_columns:
                results.append(
                    {
                        "rule_id": rule_id,
                        "page_number": page_number,
                        "columns": processed_columns,
                    }
                )
                print(f"Successfully processed table {rule_id} on page {page_number}")

        except Exception as e:
            print(
                f"Error processing table {table_rule.get('rule_id', 'unknown')}: {str(e)}"
            )
            continue

    return results


def visualize_table_data(table_data: Dict, pdf_path: str) -> None:
    """Visualize table data by drawing boxes and lines."""
    print(
        f"\nVisualizing table {table_data['rule_id']} on page {table_data['page_number']}:"
    )

    # First, show the full table box
    try:
        # Get the overall table boundaries from all columns
        table_box = {
            "top_left": {
                "x": min(
                    col["coordinates"]["top_left"]["x"] for col in table_data["columns"]
                ),
                "y": min(
                    col["coordinates"]["top_left"]["y"] for col in table_data["columns"]
                ),
            },
            "bottom_right": {
                "x": max(
                    col["coordinates"]["bottom_right"]["x"]
                    for col in table_data["columns"]
                ),
                "y": max(
                    col["coordinates"]["bottom_right"]["y"]
                    for col in table_data["columns"]
                ),
            },
        }

        # Create image and draw the full table box
        jpg_image = ImageDrawer.create_jpg_image(pdf_path, table_data["page_number"])
        image_drawer = ImageDrawer(jpg_image, jpg_image.size[0], jpg_image.size[1])
        image_with_table = image_drawer.draw_coordinates([table_box])
        print("Showing full table boundary")
        image_with_table.show()
    except Exception as e:
        print(f"Error visualizing table boundary: {str(e)}")

    # Then process each column with its lines
    for column in table_data["columns"]:
        if not column.get("lines_y_coordinates"):
            print(f"No line coordinates for column: {column['field_name']}")
            continue

        try:
            # Draw the column box and its horizontal lines
            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path,
                column["lines_y_coordinates"],
                column["coordinates"],
                table_data["page_number"],
            )
            print(f"\nShowing visualization for column: {column['field_name']}")
            print(f"Column coordinates: {column['coordinates']}")
            print(f"Number of lines: {len(column['lines_y_coordinates'])}")
            print(f"Line y-coordinates: {column['lines_y_coordinates']}")
            image_with_lines.show()

        except Exception as e:
            print(f"Error visualizing column {column['field_name']}: {str(e)}")


def visualize_form_data(form_data: Dict, pdf_path: str, template: Dict) -> None:
    """Visualize form data by drawing boxes and lines."""
    print(
        f"\nVisualizing form {form_data['rule_id']} on page {form_data['page_number']}:"
    )

    # Get the coordinates for the form using the parser
    coordinates = Parser().get_rule_from_id(form_data["rule_id"], template)["config"][
        "coordinates"
    ]

    # Create a bounding box for the form
    form_box = {
        "top_left": coordinates["top_left"],
        "bottom_right": coordinates["bottom_right"],
    }

    # Create image and draw the form box
    jpg_image = ImageDrawer.create_jpg_image(pdf_path, form_data["page_number"])
    image_drawer = ImageDrawer(jpg_image, jpg_image.size[0], jpg_image.size[1])
    image_with_form = image_drawer.draw_coordinates([form_box])
    print("Showing form boundary")
    image_with_form.show()


if __name__ == "__main__":
    print("Starting table checker script...")
    print(f"Template path: {template_path}")
    print(f"PDF path: {pdf_path}")
    print(f"PDF data path: {pdf_data_path}")

    try:
        # Extract and load data
        extract_data_from_pdf(pdf_path, template_name, identifier)
        template = load_json_data(template_path)
        pdf_data = load_json_data(pdf_data_path)

        # Create parser
        parser = Parser()

        # Process tables
        print("\nProcessing tables...")
        results = process_tables(template, pdf_data)

        if not results:
            print("No tables were found in the PDF")

        print(f"Found {len(results)} tables")

        if len(results) > 0:
            # Visualize each table
            for result in results:
                visualize_table_data(result, pdf_path)

        # Visualize each form
        for form_rule in template["rules"]:

            if form_rule["type"] == "form":
                rule_id = form_rule.get("rule_id")
                print(form_rule)
                coordinates = form_rule["config"]["coordinates"]
                form_data = {
                    "rule_id": rule_id,
                    "page_number": FORMS_PAGE_NUMBER,
                    "coordinates": coordinates,
                }
                visualize_form_data(form_data, pdf_path, template)

    except FileNotFoundError as e:
        print(f"Error: File not found - {str(e)}")
        exit(1)
    except KeyError as e:
        print(f"Error: Missing key {str(e)} in the data")
        exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        exit(1)
