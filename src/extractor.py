class DataExtractor:
    def __init__(self, page, rules, lines):
        self.page = page
        self.rules = rules
        self.lines = lines
        self.forms = []  # Initialize empty structure for forms
        self.tables = []  # Initialize empty structure for tables

    def extract_data(self):
        for rule in self.rules:
            if rule.fields:
                self.extract_form_fields()
            if rule.coordinates:  # Assuming table extraction is based on coordinates
                self.extract_table()
        return PageData(
            self.page.page_number
        )  # Return PageData object with extracted forms and tables

    def extract_form_fields(self):
        for rule in self.rules:
            for field in rule.fields:
                # Use coordinates to define the extraction area
                extraction_area = field["coordinates"]  # Assuming field has coordinates
                extracted_text = self.extract_text_within_area(extraction_area)
                self.forms.append(
                    {field["name"]: extracted_text}
                )  # Map extracted text to field name

    def extract_table(self):
        table_areas = [
            rule.coordinates for rule in self.rules if rule.coordinates
        ]  # Identify table areas
        for area in table_areas:
            line_delimiters = self.identify_line_delimiters()
            self.parse_rows(line_delimiters)

    def identify_line_delimiters(self):
        line_positions = [
            line["doctop"] for line in self.lines if line["doctop"] is not None
        ]
        return sorted(line_positions)  # Return sorted list of line positions

    def parse_rows(self, line_delimiters):
        for start, end in zip(line_delimiters[:-1], line_delimiters[1:]):
            row_elements = [
                line for line in self.lines if start <= line["doctop"] <= end
            ]
            # Group text elements into columns based on coordinates
            self.tables.append(
                self.group_columns(row_elements)
            )  # Handle multi-line rows

    def extract_text_within_area(self, area):
        # Placeholder for text extraction logic within the specified area
        return "extracted_text"  # Replace with actual extraction logic

    def group_columns(self, row_elements):
        # Placeholder for logic to group text elements into columns
        return "grouped_columns"  # Replace with actual grouping logic
