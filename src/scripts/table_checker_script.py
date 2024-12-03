import json
import os
from extractor import Extractor
from parser import Parser, TableSplitter, TableProcessor
from pdf_utils import ImageDrawer
from typing import Dict, List, Optional

template_name: str = "barclays_student"
identifier: str = "may"
template_path: str = os.path.join("src", "templates", f"{template_name}_template.json")
pdf_path: str = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)
pdf_data_path: str = os.path.join(
    "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)


def extract_data_from_pdf(pdf_path: str, template_name: str, identifier: str) -> None:
    """Extract data from PDF and save to JSON."""
    with open(pdf_path, "rb") as pdf_file:
        text_extractor = Extractor(pdf_file.read(), template_name, identifier)
        extracted_data = text_extractor.extract_data()
        with open(pdf_data_path, "w") as f:
            json.dump(extracted_data, f, indent=4, sort_keys=True)


def load_json_data(file_path: str) -> Dict:
    """Load JSON data from file."""
    with open(file_path) as f:
        return json.load(f)


def process_table_rules(page_rule, page_index, pdf_data):
    """Process each table rule for the given page."""
    results = []
    for rule_id in page_rule["tables"]:
        try:
            delimiter_field_name = page_rule["delimiter_field_name"]
            delimiter_type = page_rule["delimiter_type"]
            table_data = get_table_data(
                rule_id, page_index, pdf_data, delimiter_field_name, delimiter_type
            )
            if table_data:
                results.append(table_data)
        except Exception:
            continue

    return results


def process_tables(pdf_data: Dict) -> List[Dict]:
    """Process all tables according to template pages."""
    results = []
    number_of_pages = len(pdf_data["pages"])

    for page_rule in template["pages"]:
        if "tables" not in page_rule:
            continue

        page_indexes = parser.page_number_converter(
            page_rule["page_numbers"], number_of_pages
        )

        for page_index in page_indexes:
            results.extend(process_table_rules(page_rule, page_index, pdf_data))

    return results


def visualize_table_data(table_data: Dict, pdf_path: str) -> None:
    """Visualize table data by drawing boxes and lines."""
    print(
        f"\nVisualizing table {table_data['rule_id']} on page {table_data['page_number']}:"
    )

    # Process each column
    for column in table_data["columns"]:
        if not column.get("lines_y_coordinates"):
            continue

        try:
            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path,
                column["lines_y_coordinates"],
                column["coordinates"],
                table_data["page_number"],
            )
            print(f"Showing visualization for column: {column['field_name']}")
            print(f"Number of lines: {len(column['lines_y_coordinates'])}")
            image_with_lines.show()

        except Exception as e:
            print(f"Error visualizing column {column['field_name']}: {str(e)}")


def run_tests(template: Dict, pdf_data: Dict) -> None:
    """Run tests to verify table processing."""
    print("\nRunning tests...")

    # Process tables
    results = process_tables(pdf_data)

    # Verify results
    assert results, "No tables were processed"

    for result in results:
        # Check required fields
        assert all(
            key in result for key in ["rule_id", "page_number", "columns"]
        ), "Missing required fields in result"

        # Check columns
        assert result["columns"], "No columns in result"

        # Check line coordinates
        for column in result["columns"]:
            assert column[
                "lines_y_coordinates"
            ], f"No line coordinates for column {column['field_name']}"

        print(
            f"\nTest passed for table {result['rule_id']} on page {result['page_number']}"
        )
        print(f"Found {len(result['columns'][0]['lines_y_coordinates'])} lines")
        print(f"All {len(result['columns'])} columns processed successfully")


if __name__ == "__main__":
    # Extract and load data
    extract_data_from_pdf(pdf_path, template_name, identifier)
    template = load_json_data(template_path)
    pdf_data = load_json_data(pdf_data_path)

    try:
        # Run tests
        run_tests(template, pdf_data)

        table_processor = TableProcessor(template, Parser())

        # Process and visualize tables
        results = table_processor.process_tables(pdf_data)
        for result in results:
            visualize_table_data(result, pdf_path)

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
