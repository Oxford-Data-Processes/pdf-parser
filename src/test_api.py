import os
import time
from pipeline import parse_pdf


def main():
    config = {
        "bank_statements": {
            "barclays_student": ["march", "april", "may"],
            "barclays": ["march", "april", "may"],
            "first_direct": ["march", "april", "may"],
            "halifax": ["march", "april", "may"],
            "lloyds": ["september"],
            "monzo": ["november", "3_months"],
        },
        "payslips": {
            "payslip": ["jake"],
        },
    }

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for doc_type, templates in config.items():
        for template, identifiers in templates.items():
            for identifier in identifiers:
                pdf_path = os.path.join(
                    root_dir,
                    "data",
                    doc_type,
                    template,
                    "pdf",
                    f"{template}_{identifier}.pdf",
                )

                print(f"\nRunning API test for {doc_type} - {template} - {identifier}")
                print(f"PDF path: {pdf_path}")

                start_time = time.time()
                parse_pdf(pdf_path, template, identifier)
                elapsed_time = time.time() - start_time
                print(f"Test completed in {elapsed_time:.2f} seconds!")


if __name__ == "__main__":
    main()
