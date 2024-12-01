import tabula
import pandas as pd
import json


class TableExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_with_lattice(self, page_number=1):
        """Extract tables that have visible lines/borders.

        Args:
            page_number: The page number to extract from (1-based)

        Returns:
            List of pandas DataFrames, one for each table found
        """
        print("\nExtracting tables with lattice mode (for tables with lines)...")
        tables = tabula.read_pdf(
            self.pdf_path,
            pages=page_number,
            lattice=True,  # Use lattice mode for tables with lines
            multiple_tables=True,
            pandas_options={"header": None},  # Don't assume first row is header
        )

        print(f"Found {len(tables)} tables in lattice mode")
        return tables

    def extract_with_stream(self, page_number=1):
        """Extract tables without visible lines using stream mode.

        Args:
            page_number: The page number to extract from (1-based)

        Returns:
            List of pandas DataFrames, one for each table found
        """
        print("\nExtracting tables with stream mode (for tables without lines)...")
        tables = tabula.read_pdf(
            self.pdf_path,
            pages=page_number,
            stream=True,  # Use stream mode for tables without lines
            multiple_tables=True,
            guess=True,  # Enable advanced table detection
            pandas_options={"header": None},  # Don't assume first row is header
        )

        print(f"Found {len(tables)} tables in stream mode")
        return tables

    def extract_with_template(self, template_path):
        """Extract tables using a predefined template.

        Args:
            template_path: Path to the JSON template file

        Returns:
            List of pandas DataFrames, one for each table found
        """
        print("\nExtracting tables using template...")
        # Load template
        with open(template_path) as f:
            template = json.load(f)

        # Extract using template
        tables = tabula.read_pdf(
            self.pdf_path,
            pages=template.get("page", 1),
            area=template.get("area"),  # [top, left, bottom, right] in points
            columns=template.get(
                "columns"
            ),  # List of x-coordinates for column boundaries
            pandas_options={"header": None},
        )

        print(f"Found {len(tables)} tables using template")
        return tables

    def save_tables(self, tables, output_prefix="table"):
        """Save extracted tables to CSV and JSON formats.

        Args:
            tables: List of pandas DataFrames
            output_prefix: Prefix for output filenames
        """
        for i, table in enumerate(tables):
            if table is not None and not table.empty:
                # Save as CSV
                csv_path = f"{output_prefix}_{i+1}.csv"
                table.to_csv(csv_path, index=False)
                print(f"Saved table {i+1} to {csv_path}")

                # Save as JSON
                json_path = f"{output_prefix}_{i+1}.json"
                table.to_json(json_path, orient="records", indent=2)
                print(f"Saved table {i+1} to {json_path}")

                # Print preview
                print(f"\nTable {i+1} preview:")
                print(table.head())
                print("\nShape:", table.shape)


def main():
    # PDF path - adjust as needed
    pdf_path = "data/bank_statements/barclays/pdf/barclays March 2.pdf"
    template_path = "src/templates/barclays_template.json"

    try:
        extractor = TableExtractor(pdf_path)

        # Try both lattice and stream modes
        lattice_tables = extractor.extract_with_lattice(page_number=2)
        extractor.save_tables(lattice_tables, output_prefix="lattice_table")

        stream_tables = extractor.extract_with_stream(page_number=2)
        extractor.save_tables(stream_tables, output_prefix="stream_table")

        # Try template-based extraction
        template_tables = extractor.extract_with_template(template_path)
        extractor.save_tables(template_tables, output_prefix="template_table")

        print("\nProcess completed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
