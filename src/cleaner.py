from typing import Any, Dict
from datetime import datetime
import re
import json


class ProcessorRegistry:
    def __init__(self):
        self.processors = {
            "clean_text": self.clean_text,
            "clean_numbers": self.clean_numbers,
            "clean_currency": self.clean_currency,
            "clean_date": self.clean_date,
        }

    def clean_text(self, value: str, options: Dict[str, Any]) -> str:
        if not value:
            return value

        result = value.strip()

        if options.get("uppercase", False):
            result = result.upper()

        if options.get("remove_titles", False):
            titles = ["Mr", "Mrs", "Ms", "Dr", "Prof"]
            for title in titles:
                result = result.replace(title, "").strip()

        if "max_length" in options:
            result = result[: options["max_length"]]

        return result

    def clean_numbers(self, value: str, options: Dict[str, Any]) -> str:
        if not value:
            return value

        allowed = options.get("allow_chars", "")
        pattern = f"[^0-9{re.escape(allowed)}]"
        result = re.sub(pattern, "", value)

        if "format" in options:
            format_str = options["format"]
            current_pos = 0
            formatted = ""
            for char in format_str:
                if char == "#":
                    if current_pos < len(result):
                        formatted += result[current_pos]
                        current_pos += 1
                else:
                    formatted += char
            result = formatted

        return result

    def clean_currency(self, value: str, options: Dict[str, Any]) -> str:
        if not value:
            return value

        # Remove specified currency symbols
        for symbol in options.get("remove_symbols", []):
            value = value.replace(symbol, "")

        # Remove any remaining non-numeric chars except decimal point
        result = re.sub(r"[^0-9.]", "", value)

        # Format to specified decimal places
        try:
            decimal_places = options.get("decimal_places", 2)
            result = f"{float(result):.{decimal_places}f}"
        except ValueError:
            return value

        return result

    def clean_date(self, value: str, options: Dict[str, Any]) -> str:
        if not value:
            return value

        try:
            date_obj = datetime.strptime(value, options["input_format"])
            return date_obj.strftime(options["output_format"])
        except ValueError:
            return value

    def get_processor(self, name: str):
        return self.processors.get(name)


class DocumentCleaner:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
        self.processor_registry = ProcessorRegistry()

    def clean_value(self, value: Any, cleaning_rule: Dict) -> Any:
        if cleaning_rule is None:
            return value

        processor_name = cleaning_rule.get("processor")
        if not processor_name:
            return value

        processor = self.processor_registry.get_processor(processor_name)
        if not processor:
            return value

        options = cleaning_rule.get("options", {})
        return processor(value, options)

    def clean_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        from copy import deepcopy

        page_copy = deepcopy(page)
        # Clean forms
        for form in page_copy["forms"]:
            for key, value in form.items():
                form[key] = self.clean_value(value, self.config["forms"][key])

        # Clean tables
        for table in page_copy.get("tables", []):
            for row in table["data"]:
                for key, value in row.items():
                    row[key] = self.clean_value(
                        value, self.config["tables"]["data"][key]
                    )

        return page_copy