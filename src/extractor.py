import pdfplumber
import io


class TextExtractor:
    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes

    def extract_text(self):
        """
        Extract text, bounding box information, and line coordinates from the PDF file.

        Returns:
            dict: Dictionary containing extracted text, bounding box information, line coordinates, number of pages, and dimensions.
        """
        with pdfplumber.open(io.BytesIO(self.pdf_bytes)) as pdf:
            data = {
                "pages": [],
                "number_of_pages": len(pdf.pages),
                "dimensions": self.get_dimensions(pdf),
            }
            for page_num, page in enumerate(pdf.pages):
                page_data = self.extract_page_data(page)
                line_coordinates = self.extract_line_coordinates(page.lines)

                data["pages"].append(
                    {
                        "page_number": page_num + 1,
                        "content": page_data,
                        "lines": line_coordinates,
                    }
                )

            return data

    def get_dimensions(self, pdf):
        """Get the dimensions of the first page of the PDF."""
        return {
            "width": pdf.pages[0].width,
            "height": pdf.pages[0].height,
        }

    def extract_page_data(self, page):
        """Extract text and bounding box information from a page."""
        page_data = []
        for element in page.extract_words():
            text = element["text"]
            x0, y0, x1, y1 = (
                element["x0"],
                element["top"],
                element["x1"],
                element["bottom"],
            )
            page_data.append(
                {
                    "text": text,
                    "bounding_box": {
                        "top_left": {"x": x0, "y": y0},
                        "bottom_right": {"x": x1, "y": y1},
                    },
                }
            )
        return page_data

    def extract_line_coordinates(self, lines):
        """Extract line coordinates from a list of lines."""
        line_coordinates = []
        for line in lines:
            line_coordinates.append(
                {
                    "x0": line["x0"],
                    "y0": line["y0"],
                    "x1": line["x1"],
                    "y1": line["y1"],
                }
            )
        return line_coordinates
