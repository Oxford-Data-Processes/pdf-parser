import pdfplumber
from PIL import ImageDraw
from pdf2image import convert_from_path


class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_width = None
        self.pdf_height = None
        self.pdf_lines = None

    def extract_lines(self, page_number=1):
        """Extract lines from PDF using pdfplumber."""
        with pdfplumber.open(self.pdf_path) as pdf:
            page = pdf.pages[page_number]
            self.pdf_lines = page.lines
            self.pdf_width = page.width
            self.pdf_height = page.height
            print(f"PDF dimensions: {self.pdf_width}x{self.pdf_height}")

    def create_jpg_image(self):
        """Convert the PDF page to a JPG."""
        images = convert_from_path(self.pdf_path)
        jpg_image_original = images[1]  # Get the second page

        # Get dimensions
        img_width, img_height = jpg_image_original.size
        print(f"Image dimensions: {img_width}x{img_height}")

        # Save the JPG image
        jpg_image_original.save("output.jpeg", "JPEG")
        return jpg_image_original


class ImageDrawer:
    def __init__(self, image, pdf_lines, pdf_width, pdf_height):
        self.image = image
        self.pdf_lines = pdf_lines
        self.pdf_width = pdf_width
        self.pdf_height = pdf_height

    def draw_lines(self):
        """Draw the extracted PDF lines on the image."""
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)

        img_width, img_height = image_copy.size
        scale_x = img_width / self.pdf_width
        scale_y = img_height / self.pdf_height

        for i, line in enumerate(self.pdf_lines, 1):
            x0 = line["x0"] * scale_x
            y0 = (self.pdf_height - line["y0"]) * scale_y  # Flip y-coordinate
            x1 = line["x1"] * scale_x
            y1 = (self.pdf_height - line["y1"]) * scale_y  # Flip y-coordinate

            # Verify coordinates are within bounds
            assert 0 <= x0 <= img_width, f"Line {i}: x0 out of bounds"
            assert 0 <= y0 <= img_height, f"Line {i}: y0 out of bounds"
            assert 0 <= x1 <= img_width, f"Line {i}: x1 out of bounds"
            assert 0 <= y1 <= img_height, f"Line {i}: y1 out of bounds"

            draw.line([(x0, y0), (x1, y1)], fill="red", width=2)
            print(f"Drew line {i}: ({x0:.1f}, {y0:.1f}) to ({x1:.1f}, {y1:.1f})")

        print(f"Successfully drew {len(self.pdf_lines)} lines")
        return image_copy


def main():
    pdf_path = "data/bank_statements/barclays/pdf/barclays March 2.pdf"
    try:
        pdf_processor = PDFProcessor(pdf_path)
        print("Extracting lines from PDF...")
        pdf_processor.extract_lines()

        print("\nConverting PDF to JPG...")
        jpg_image = pdf_processor.create_jpg_image()

        print("\nDrawing lines...")
        image_drawer = ImageDrawer(
            jpg_image,
            pdf_processor.pdf_lines,
            pdf_processor.pdf_width,
            pdf_processor.pdf_height,
        )
        modified_image = image_drawer.draw_lines()

        modified_image.save("output_with_lines.jpeg", "JPEG")
        modified_image.show()

        print("\nProcess completed successfully!")
        print("Check 'output_with_lines.jpeg' for the result")

    except Exception as e:
        print(f"Error: {str(e)}")
