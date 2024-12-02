import unittest
import json
import os
from src.parser import Parser, TableSplitter


class TestTableSplitter(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.template_path = os.path.join(
            "src", "templates", "barclays_student_template.json"
        )
        self.pdf_data_path = os.path.join(
            "src", "pdf_data", "barclays_student_march_pdf_data.json"
        )

        with open(self.template_path) as f:
            self.template = json.load(f)
        with open(self.pdf_data_path) as f:
            self.pdf_data = json.load(f)

        self.table_splitter = TableSplitter(self.template, self.parser)
        self.page_content = self.pdf_data["pages"][1]  # Page 2

    def test_split_table_description_column(self):
        expected_coordinates = [
            0.475534,
            0.503682,
            0.54323,
            0.587767,
            0.63076,
            0.668765,
            0.67209,
            0.70677,
            0.749762,
            0.787767,
            0.825772,
            0.863777,
        ]

        # Get the table rule from template
        table_rule = None
        for rule in self.template["rules"]:
            if rule["type"] == "table":
                table_rule = rule
                break

        self.assertIsNotNone(table_rule, "Table rule not found in template")

        # Get description column coordinates
        description_coordinates = None
        for column in table_rule["config"]["columns"]:
            if column["field_name"] == "description":
                description_coordinates = column["coordinates"]
                break

        self.assertIsNotNone(
            description_coordinates, "Description column coordinates not found"
        )

        # Get the line coordinates
        lines_y_coordinates = self.table_splitter.split_table(
            "line", self.page_content, description_coordinates
        )

        # Test that we got the expected number of lines
        self.assertEqual(
            len(lines_y_coordinates),
            len(expected_coordinates),
            f"Expected {len(expected_coordinates)} lines, but got {len(lines_y_coordinates)}",
        )

        # Test each coordinate matches with a small tolerance for floating point differences
        for expected, actual in zip(expected_coordinates, lines_y_coordinates):
            self.assertAlmostEqual(
                expected,
                actual,
                places=6,
                msg=f"Expected y-coordinate {expected} but got {actual}",
            )


if __name__ == "__main__":
    unittest.main()
