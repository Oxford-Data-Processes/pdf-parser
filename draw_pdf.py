import json
from PIL import ImageDraw
from pdf2image import convert_from_path


class ImageDrawer:
    def __init__(self, image, pdf_lines, pdf_width, pdf_height):
        self.image = image
        self.pdf_lines = pdf_lines
        self.pdf_width = pdf_width
        self.pdf_height = pdf_height

    def create_jpg_image(self, pdf_path):
        """Convert the PDF page to a JPG."""
        images = convert_from_path(pdf_path)
        jpg_image_original = images[1]  # Get the second page

        # Get dimensions
        img_width, img_height = jpg_image_original.size
        print(f"Image dimensions: {img_width}x{img_height}")

        # Save the JPG image
        jpg_image_original.save("output.jpeg", "JPEG")
        return jpg_image_original

    def draw_lines(self):
        """Draw the extracted PDF lines on the image."""
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)

        img_width, img_height = image_copy.size

        print(f"PDF lines: {self.pdf_lines}")

        for i, line in enumerate(self.pdf_lines, 1):
            x0 = float(line["decimal_coordinates"]["top_left"]["x"]) * img_width
            y0 = img_height - (
                float(line["decimal_coordinates"]["top_left"]["y"]) * img_height
            )  # Flip y-coordinate
            x1 = float(line["decimal_coordinates"]["bottom_right"]["x"]) * img_width
            y1 = img_height - (
                float(line["decimal_coordinates"]["bottom_right"]["y"]) * img_height
            )  # Flip y-coordinate

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
    pdf_data_path = "src/pdf_data/barclays_march_2_pdf_data.json"
    try:
        pdf_data = json.load(open(pdf_data_path))
        extracted_lines = pdf_data["pages"][1]["lines"]

        print(f"Extracted {len(extracted_lines)} lines from PDF")

        jpg_image = ImageDrawer(None, extracted_lines, None, None).create_jpg_image(
            pdf_path
        )

        print("\nDrawing lines...")
        image_drawer = ImageDrawer(
            jpg_image,
            extracted_lines,
            jpg_image.size[0],  # Use the image width
            jpg_image.size[1],  # Use the image height
        )
        modified_image = image_drawer.draw_lines()

        modified_image.save("output_with_lines.jpeg", "JPEG")
        modified_image.show()

        print("\nProcess completed successfully!")
        print("Check 'output_with_lines.jpeg' for the result")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
