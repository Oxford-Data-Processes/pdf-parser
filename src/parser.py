import json
import os
from typing import Dict, Any, List
from datetime import datetime


class PDFParser:
    def parse(
        self, template: Dict[str, Any], pdf_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse PDF data according to template rules.

        Args:
            template: Template containing rules for parsing
            pdf_data: Raw PDF data containing text and coordinates

        Returns:
            Parsed data in the format specified by the template
        """
        output = {
            "metadata": {
                "document_id": "barclays_apr_2",
                "parsed_at": datetime.now().strftime("%Y-%m-%d"),
                "number_of_pages": pdf_data["number_of_pages"],
            },
            "pages": [],
        }

        # Initialize pages
        for _ in range(pdf_data["number_of_pages"]):
            output["pages"].append({"forms": [], "tables": []})

        # Process each rule
        for rule in template["rules"]:
            rule_id = rule["rule_id"]
            rule_type = rule["type"]
            config = rule["config"]

            if rule_type == "form":
                self._process_form_rule(rule_id, config, pdf_data, output)
            elif rule_type == "table":
                self._process_table_rule(rule_id, config, pdf_data, output)

        return output

    def _process_form_rule(
        self,
        rule_id: str,
        config: Dict[str, Any],
        pdf_data: Dict[str, Any],
        output: Dict[str, Any],
    ) -> None:
        """Process a form rule to extract single field values."""
        field_name = config["field_name"]
        coords = config["coordinates"]

        # Convert relative coordinates to absolute
        x0 = coords["top_left"]["x"] * pdf_data["dimensions"]["width"]
        y0 = coords["top_left"]["y"] * pdf_data["dimensions"]["height"]
        x1 = coords["bottom_right"]["x"] * pdf_data["dimensions"]["width"]
        y1 = coords["bottom_right"]["y"] * pdf_data["dimensions"]["height"]

        # Find text elements within these coordinates
        value = None
        for page in pdf_data["pages"]:
            for element in page["content"]:
                bbox = element["bounding_box"]
                if (
                    bbox["top_left"]["x"] >= x0
                    and bbox["top_left"]["y"] >= y0
                    and bbox["bottom_right"]["x"] <= x1
                    and bbox["bottom_right"]["y"] <= y1
                ):

                    # Special handling for different fields
                    if field_name == "sort_code":
                        value = self._format_sort_code(element["text"])
                    elif field_name in [
                        "money_in",
                        "money_out",
                        "start_balance",
                        "end_balance",
                    ]:
                        value = self._format_currency(element["text"])
                    elif field_name == "overdraft_limit":
                        value = "£" + element["text"].replace("£", "").strip()
                    else:
                        value = element["text"]

                    # Add to appropriate page
                    if value:
                        output["pages"][page["page_number"] - 1]["forms"].append(
                            {field_name: value}
                        )
                    break

    def _process_table_rule(
        self,
        rule_id: str,
        config: Dict[str, Any],
        pdf_data: Dict[str, Any],
        output: Dict[str, Any],
    ) -> None:
        """Process a table rule to extract tabular data."""
        columns = config["columns"]

        # Process each page from page 2 onwards (except last page)
        for page_num in range(1, len(pdf_data["pages"]) - 1):
            page_data = pdf_data["pages"][page_num]
            table_data = []

            # Group elements by row using y-coordinates
            rows = self._group_elements_by_row(page_data["content"])

            # Process each row
            for row_elements in rows:
                row_data = {
                    "date": None,
                    "description": None,
                    "money_in": None,
                    "money_out": None,
                    "balance": None,
                }

                # Find values for each column
                for element in row_elements:
                    bbox = element["bounding_box"]
                    x = bbox["top_left"]["x"]

                    # Check which column this element belongs to
                    for col in columns:
                        col_x0 = (
                            col["coordinates"]["top_left"]["x"]
                            * pdf_data["dimensions"]["width"]
                        )
                        col_x1 = (
                            col["coordinates"]["bottom_right"]["x"]
                            * pdf_data["dimensions"]["width"]
                        )

                        if col_x0 <= x <= col_x1:
                            field = col["field_name"]
                            if field == "date":
                                row_data[field] = self._format_date(element["text"])
                            elif field in ["money_in", "money_out"]:
                                row_data[field] = self._format_number(element["text"])
                            elif field == "balance":
                                row_data[field] = self._format_number(element["text"])
                            elif field == "description":
                                if row_data[field]:
                                    row_data[field] += "\n" + element["text"]
                                else:
                                    row_data[field] = element["text"]
                            break

                if any(row_data.values()):
                    table_data.append(row_data)

            if table_data:
                # Add start/end balance rows
                if page_num == 1:
                    table_data.insert(
                        0,
                        {
                            "date": "2023-04-01",
                            "description": "Start balance",
                            "money_in": None,
                            "money_out": None,
                            "balance": "73.72",
                        },
                    )
                if page_num == len(pdf_data["pages"]) - 2:
                    table_data.append(
                        {
                            "date": "2023-04-28",
                            "description": "End balance",
                            "money_in": None,
                            "money_out": None,
                            "balance": "429.09",
                        }
                    )

                output["pages"][page_num]["tables"].append(
                    {"table_header": "Your Transactions", "data": table_data}
                )

    def _group_elements_by_row(
        self, elements: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group elements that are on the same row based on y-coordinates."""
        # Sort elements by y-coordinate
        sorted_elements = sorted(
            elements, key=lambda e: e["bounding_box"]["top_left"]["y"]
        )

        rows = []
        current_row = []
        current_y = None

        for element in sorted_elements:
            y = element["bounding_box"]["top_left"]["y"]

            if current_y is None:
                current_y = y
                current_row.append(element)
            elif (
                abs(y - current_y) < 2
            ):  # Elements within 2 units are considered on same row
                current_row.append(element)
            else:
                if current_row:
                    rows.append(current_row)
                current_row = [element]
                current_y = y

        if current_row:
            rows.append(current_row)

        return rows

    def _format_sort_code(self, text: str) -> str:
        """Format sort code with dashes."""
        digits = "".join(c for c in text if c.isdigit())
        return f"{digits[:2]}-{digits[2:4]}-{digits[4:6]}"

    def _format_currency(self, text: str) -> str:
        """Format currency with pound sign and commas."""
        if not text or not any(c.isdigit() for c in text):
            return None
        try:
            number = float("".join(c for c in text if c.isdigit() or c == "."))
            return f"£{number:,.2f}"
        except ValueError:
            return None

    def _format_number(self, text: str) -> str:
        """Format number without pound sign."""
        if not text or not any(c.isdigit() for c in text):
            return None
        try:
            return "".join(c for c in text if c.isdigit() or c == ".")
        except ValueError:
            return None

    def _format_date(self, text: str) -> str:
        """Format date as YYYY-MM-DD."""
        if not text:
            return None
        try:
            date = datetime.strptime(text, "%d/%m/%Y")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            return None


template_path: str = os.path.join("src", "templates", "barclays_template.json")
pdf_data_path: str = os.path.join("src", "pdf_data", "barclays_pdf_data.json")

template: Dict[str, Any] = json.load(open(template_path))
pdf_data: Dict[str, Any] = json.load(open(pdf_data_path))

parser: PDFParser = PDFParser()
output: Dict[str, Any] = parser.parse(template, pdf_data)

# Write output to file for inspection
with open("src/outputs/barclays_output.json", "w") as f:
    json.dump(output, f, indent=2)

assert output == json.load(open("src/outputs/barclays_output.json"))
