import os

from pipeline import get_sort_code

if __name__ == "__main__":
    config = {
        "bank_statements": {
            "barclays_student": ["march", "april", "may"],
            "barclays": ["march", "april", "may"],
            "first_direct": ["march", "april", "may"],
            "halifax": ["march", "april", "may"],
            "lloyds": ["september"],
            "monzo": ["november", "3_months"],
        }
    }

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for document_type, templates_and_identifiers in config.items():
        for template_name, identifiers in templates_and_identifiers.items():
            for identifier in identifiers:
                test_pdf_path: str = os.path.join(
                    ROOT_DIR,
                    "data",
                    document_type,
                    template_name,
                    "pdf",
                    f"{template_name}_{identifier}.pdf",
                )
                sort_code = get_sort_code(test_pdf_path)
                print(sort_code)
