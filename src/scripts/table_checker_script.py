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


def process_table_data(
    table_rule: Dict,
    page_content: Dict,
    parser: Parser,
    delimiter_field_name: str,
    delimiter_type: str,
) -> List[Dict]:
    """Process a single table's data."""

    delimiter_coordinates = parser.get_delimiter_column_coordinates(
        template, delimiter_field_name
    )

    table_splitter = TableSplitter(template, parser)

    if delimiter_type == "line":

        filtered_lines = parser.filter_lines_by_pixel_value(page_content["lines"])

        lines_y_coordinates = sorted(
            set(
                [
                    line["decimal_coordinates"]["top_left"]["y"]
                    for line in filtered_lines
                ]
            )
        )

    if delimiter_type == "field":
        delimiter_coordinates = parser.get_delimiter_column_coordinates(
            template, delimiter_field_name
        )
        lines_y_coordinates = table_splitter.split_table(
            delimiter_type, page_content, delimiter_coordinates
        )

    if not delimiter_coordinates:
        raise ValueError("Delimiter coordinates not found")

    # Process each column
    processed_columns = []
    for column in table_rule["config"]["columns"]:
        processed_columns.append(
            {
                "field_name": column["field_name"],
                "coordinates": column["coordinates"],
                "lines_y_coordinates": lines_y_coordinates,
            }
        )

    return processed_columns


def process_tables(template: Dict, pdf_data: Dict) -> List[Dict]:
    """Process all tables according to template pages."""
    results = []
    parser = Parser()
    # Process each page rule
    for page_rule in template["pages"]:
        if "tables" not in page_rule or not page_rule["tables"]:
            continue

        # Get page indexes
        page_indexes = parser.page_number_converter(
            page_rule["page_numbers"], len(pdf_data["pages"])
        )

        # Process each page
        for page_index in page_indexes:
            page_content = pdf_data["pages"][page_index]

            # Process each table rule
            for rule_id in page_rule["tables"]:
                # Get table rule
                table_rule = parser.get_rule_from_id(rule_id, template)
                if not table_rule:
                    print(f"Warning: Table rule {rule_id} not found")
                    continue

                delimiter_field_name = table_rule["config"]["row_delimiter"][
                    "field_name"
                ]
                delimiter_type = table_rule["config"]["row_delimiter"]["type"]

                # Process table data
                processed_columns = process_table_data(
                    table_rule,
                    page_content,
                    parser,
                    delimiter_field_name,
                    delimiter_type,
                )

                if processed_columns and any(
                    col["lines_y_coordinates"] for col in processed_columns
                ):
                    results.append(
                        {
                            "rule_id": rule_id,
                            "page_number": page_index + 1,
                            "columns": processed_columns,
                        }
                    )
                    print(f"\nProcessed table {rule_id} on page {page_index + 1}")
                    print(
                        f"Found {len(processed_columns[0]['lines_y_coordinates'])} lines"
                    )

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
    results = process_tables(template, pdf_data)

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

        # Process and visualize tables
        results = process_tables(template, pdf_data)
        for result in results:
            visualize_table_data(result, pdf_path)

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
