import pytest
from parser import Parser


class TestParser:
    def test_page_number_converter(self):
        parser = Parser()

        # Test positive index
        assert parser.page_number_converter("1", 5) == [0]

        # Test negative index
        assert parser.page_number_converter("-1", 5) == [4]

        # Test range
        assert parser.page_number_converter("1:3", 5) == [0, 1, 2]

        # Test negative range
        assert parser.page_number_converter("-2:-1", 5) == [3, 4]

    def test_get_rule_from_id(self, sample_template):
        parser = Parser()
        rule = parser.get_rule_from_id("customer_name", sample_template)
        assert rule["type"] == "form"
        assert rule["config"]["field_name"] == "customer_name"

    def test_get_items_in_bounding_box(self, sample_pdf_data):
        parser = Parser()
        box_coordinates = {
            "top_left": {"x": 0.1, "y": 0.1},
            "bottom_right": {"x": 0.2, "y": 0.2},
        }
        items = parser.get_items_in_bounding_box(
            sample_pdf_data["pages"][0]["content"], box_coordinates
        )
        assert len(items) == 1
        assert items[0]["text"] == "John Doe"

    def test_get_text_from_page_coordinates(self, sample_pdf_data, sample_jpg_bytes):
        parser = Parser()
        coordinates = {
            "top_left": {"x": 0.1, "y": 0.1},
            "bottom_right": {"x": 0.2, "y": 0.2},
        }
        text = parser.get_text_from_page(
            sample_pdf_data["pages"][0]["content"],
            coordinates,
            "extraction",
            sample_jpg_bytes[0],
            search_type="coordinates",
        )
        assert text.strip() == "John Doe"

    def test_get_text_from_page_regex(self, sample_pdf_data, sample_jpg_bytes):
        parser = Parser()
        text = parser.get_text_from_page(
            sample_pdf_data["pages"][0]["content"],
            None,
            "extraction",
            sample_jpg_bytes[0],
            search_type="regex",
            regex=r"Account number: (\d+)",
        )
        assert text.strip() == "12345678"

    def test_parse_pdf(self, sample_template, sample_pdf_data, sample_jpg_bytes):
        output = Parser.parse_pdf(sample_template, sample_pdf_data, sample_jpg_bytes)

        assert "metadata" in output
        assert "pages" in output
        assert len(output["pages"]) == 1
        assert "forms" in output["pages"][0]

        forms = output["pages"][0]["forms"]
        assert len(forms) == 2

        # Check form values
        form_values = {
            form.get("customer_name", form.get("account_number")) for form in forms
        }
        assert "John Doe" in form_values
        assert "12345678" in form_values
