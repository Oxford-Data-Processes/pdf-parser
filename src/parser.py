import pdfplumber
from src.extractor import DataExtractor
from src.models import PageData


class PDFParser:
    def __init__(self, pdf_file_path, template):
        self.pdf_file_path = pdf_file_path
        self.template = template
        self.document = None

    def load_pdf(self):
        try:
            with pdfplumber.open(self.pdf_file_path) as pdf:
                self.document = pdf
        except Exception as e:
            print(f"Error loading PDF: {e}")

    def parse_document(self):
        if self.document is None:
            self.load_pdf()

        for page_number, page in enumerate(self.document.pages):
            rules = self.template.get_rules_for_page(page_number)
            if any(rule.ignore_page for rule in rules):
                continue
            self.parse_page(page_number, page, rules)

    def parse_page(self, page_number, page, rules):
        lines = self.get_lines(page)
        extractor = DataExtractor(page, rules, lines)
        extractor.extract_data()
        return PageData(page_number)

    def get_lines(self, page):
        return [line for line in page.lines if line["doctop"] is not None]
