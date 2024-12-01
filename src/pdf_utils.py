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

    def draw_coordinates(self, coordinates):
        """Draw the decimal coordinates on the image."""
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)

        img_width, img_height = image_copy.size

        for coordinate in coordinates:
            # Calculate the pixel coordinates from decimal coordinates
            top_left_x = coordinate["top_left"]["x"] * img_width
            top_left_y = coordinate["top_left"]["y"] * img_height
            bottom_right_x = coordinate["bottom_right"]["x"] * img_width
            bottom_right_y = coordinate["bottom_right"]["y"] * img_height

            print(
                f"top_left_x: {top_left_x}, top_left_y: {top_left_y}, bottom_right_x: {bottom_right_x}, bottom_right_y: {bottom_right_y}"
            )
            # Draw the rectangle using pixel coordinates
            draw.rectangle(
                [
                    top_left_x,
                    top_left_y,
                    bottom_right_x,
                    bottom_right_y,
                ],
                outline="red",
                width=2,
            )

        return image_copy

    def draw_horizontal_lines(self, pdf_lines_y_coordinates):
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
