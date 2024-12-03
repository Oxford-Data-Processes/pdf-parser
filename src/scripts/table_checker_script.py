import json
import os
from extractor import Extractor
from parser import Parser, TableSplitter
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


def get_table_data(
    rule_id: str,
    page_index: int,
    pdf_data: Dict,
    template: Dict,
    max_pixel_value: tuple = (100, 100, 100),
) -> Dict:
    """Get table data for a specific rule and page."""
    parser = Parser()
    table_splitter = TableSplitter(template, parser)

    # Get the table rule
    table_rule = parser.get_rule_from_id(rule_id, template)
    if not table_rule:
        raise ValueError(f"Table rule {rule_id} not found")

    # Get page content
    page_content = pdf_data["pages"][page_index]
    lines = page_content["lines"]

    # Get description column coordinates for line filtering
    description_coords = parser.get_delimiter_column_coordinates(
        template, "description"
    )
    if not description_coords:
        raise ValueError("Description column coordinates not found")

    # Filter lines by pixel value
    filtered_lines = parser.filter_lines_by_pixel_value(lines, max_pixel_value)

    # Get y-coordinates from filtered lines
    lines_y_coordinates = sorted(
        set(line["decimal_coordinates"]["top_left"]["y"] for line in filtered_lines)
    )

    if not lines_y_coordinates:
        print(
            f"Warning: No valid lines found for table {rule_id} on page {page_index + 1}"
        )
        return None

    # Process each column
    columns_data = []
    for column in table_rule["config"]["columns"]:
        column_data = {
            "field_name": column["field_name"],
            "coordinates": column["coordinates"],
            "lines_y_coordinates": lines_y_coordinates,  # Use same lines for all columns
        }
        columns_data.append(column_data)

    return {"rule_id": rule_id, "page_number": page_index + 1, "columns": columns_data}


def process_tables(template: Dict, pdf_data: Dict) -> List[Dict]:
    """Process all tables according to template pages."""
    results = []
    number_of_pages = len(pdf_data["pages"])
    parser = Parser()

    # Iterate through pages as defined in template
    for page_rule in template["pages"]:
        if "tables" not in page_rule:
            continue

        # Convert page numbers to indexes
        page_indexes = parser.page_number_converter(
            page_rule["page_numbers"], number_of_pages
        )

        # Process each page
        for page_index in page_indexes:
            # Process each table rule for this page
            for rule_id in page_rule["tables"]:
                try:
                    table_data = get_table_data(rule_id, page_index, pdf_data, template)
                    if table_data:
                        results.append(table_data)
                        print(f"\nProcessed table {rule_id} on page {page_index + 1}")
                        print(
                            f"Found {len(table_data['columns'][0]['lines_y_coordinates'])} lines"
                        )
                except Exception as e:
                    print(
                        f"Error processing table {rule_id} on page {page_index + 1}: {str(e)}"
                    )

    return results


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

    # Test 1: Check if we can process all pages
    results = process_tables(template, pdf_data)
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

    # Run tests
    try:
        run_tests(template, pdf_data)
    except AssertionError as e:
        print(f"Test failed: {str(e)}")
        exit(1)

    # Process tables
    results = process_tables(template, pdf_data)

    # Visualize results
    for table_data in results:
        visualize_table_data(table_data, pdf_path)
