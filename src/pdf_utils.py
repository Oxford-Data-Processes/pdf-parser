import json
from PIL import ImageDraw
from pdf2image import convert_from_path


class ImageDrawer:
    def __init__(self, image, pdf_width, pdf_height):
        self.image = image
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

    def draw_lines(self, pdf_lines_y_coordinates):
        """Draw the extracted PDF lines on the image."""
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)

        img_width, img_height = image_copy.size

        print(f"PDF lines: {pdf_lines_y_coordinates}")

        for i, y_coordinate in enumerate(pdf_lines_y_coordinates, 1):
            y = img_height - (y_coordinate * img_height)  # Flip y-coordinate

            # Draw a line across the entire width of the image
            draw.line([(0, y), (img_width, y)], fill="red", width=2)
            print(f"Drew line {i} at y: {y:.1f}")

        print(f"Successfully drew {len(pdf_lines_y_coordinates)} lines")
        return image_copy
