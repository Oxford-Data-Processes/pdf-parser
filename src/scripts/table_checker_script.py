import json
import os
from extractor import Extractor
from parser import Parser, TableProcessor
from pdf_utils import ImageDrawer
from typing import Dict, List

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


def visualize_table_data(table_data: Dict, pdf_path: str) -> None:
    """Visualize table data by drawing boxes and lines for all columns."""
    if not table_data:
        return

    print(
        f"\nVisualizing table {table_data['rule_id']} on page {table_data['page_number']}:"
    )

    # Group columns by their y-coordinates to avoid duplicate visualizations
    visualized_coords = set()

    for column in table_data["columns"]:
        if not column["lines_y_coordinates"]:
            continue

        # Create a unique key for this column's coordinates
        coord_key = (
            column["coordinates"]["top_left"]["x"],
            column["coordinates"]["top_left"]["y"],
            column["coordinates"]["bottom_right"]["x"],
            column["coordinates"]["bottom_right"]["y"],
        )

        if coord_key not in visualized_coords:
            visualized_coords.add(coord_key)

            image_with_lines = ImageDrawer.draw_column_box_and_lines(
                pdf_path,
                column["lines_y_coordinates"],
                column["coordinates"],
                table_data["page_number"],
            )
            print(f"Showing visualization for column: {column['field_name']}")
            print(f"Number of lines: {len(column['lines_y_coordinates'])}")
            image_with_lines.show()


def run_tests(template: Dict, pdf_data: Dict) -> None:
    """Run tests to verify table processing."""
    print("\nRunning tests...")

    table_processor = TableProcessor(template, Parser())

    # Test 1: Check if we can process all pages
    results = table_processor.process_tables(pdf_data)
    assert len(results) > 0, "No tables were processed"

    # Test 2: Check if each result has required fields
    for result in results:
        assert "rule_id" in result, "Missing rule_id in result"
        assert "page_number" in result, "Missing page_number in result"
        assert "columns" in result, "Missing columns in result"

        # Test 3: Check if all columns have line coordinates
        for column in result["columns"]:
            assert (
                "lines_y_coordinates" in column
            ), f"Missing lines_y_coordinates in {column['field_name']}"
            assert (
                column["lines_y_coordinates"] is not None
            ), f"No line coordinates found for {column['field_name']}"
            assert (
                len(column["lines_y_coordinates"]) > 0
            ), f"Empty line coordinates for {column['field_name']}"

        print(
            f"\nTest passed for table {result['rule_id']} on page {result['page_number']}"
        )
        print(f"Found {len(result['columns'][0]['lines_y_coordinates'])} lines")
        print(f"All {len(result['columns'])} columns have valid line coordinates")


if __name__ == "__main__":

    # Extract and load data
    extract_data_from_pdf(pdf_path, template_name, identifier)
    template = load_json_data(template_path)
    pdf_data = load_json_data(pdf_data_path)
    table_processor = TableProcessor(template, Parser())

    # Run tests
    try:
        run_tests(template, pdf_data)
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
        exit(1)

    # Process tables
    results = table_processor.process_tables(pdf_data)

    # Visualize results
    for table_data in results:
        visualize_table_data(table_data, pdf_path)
