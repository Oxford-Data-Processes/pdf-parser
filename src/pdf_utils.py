from pdf2image import convert_from_path
from PIL import ImageDraw
from typing import List, Dict, Any


class ImageDrawer:
    def __init__(self, image: Any, pdf_width: int, pdf_height: int) -> None:
        self.image = image
        self.pdf_width = pdf_width
        self.pdf_height = pdf_height

    @staticmethod
    def create_jpg_image(pdf_path: str, page_number: int) -> Any:
        """Convert the PDF page to a JPG."""
        images = convert_from_path(pdf_path)
        jpg_image_original = images[page_number - 1]

        return jpg_image_original

    def draw_coordinates(self, coordinates: List[Dict[str, Dict[str, float]]]) -> Any:
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

    def draw_horizontal_lines(self, pdf_lines_y_coordinates: List[float]) -> Any:
        """Draw the extracted PDF lines on the image."""
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)

        img_width, img_height = image_copy.size

        for y_coordinate in pdf_lines_y_coordinates:
            y = y_coordinate * img_height

            # Draw a line across the entire width of the image
            draw.line([(0, y), (img_width, y)], fill="red", width=2)

        print(f"Successfully drew {len(pdf_lines_y_coordinates)} lines")
        return image_copy

    def draw_lines_and_coordinates(
        self, coordinates: Dict[str, Dict[str, float]], lines_y_coordinates: List[float]
    ) -> Any:
        """Draw coordinates and horizontal lines on the image."""
        x0 = coordinates["top_left"]["x"]
        x1 = coordinates["bottom_right"]["x"]
        y0 = coordinates["top_left"]["y"]
        y1 = coordinates["bottom_right"]["y"]

        # Create a list of y coordinates within the range
        y_coordinates = [y for y in lines_y_coordinates if y0 <= y <= y1]

        # Generate new coordinate boxes
        new_coordinates = []
        for i in range(len(y_coordinates) + 1):
            top_left = {"x": x0, "y": y0 if i == 0 else y_coordinates[i - 1]}
            bottom_right = {
                "x": x1,
                "y": y1 if i == len(y_coordinates) else y_coordinates[i],
            }
            new_coordinates.append({"top_left": top_left, "bottom_right": bottom_right})

        modified_image = self.draw_coordinates(new_coordinates)
        return modified_image

    @staticmethod
    def draw_column_box_and_lines(
        pdf_path: str,
        lines_y_coordinates: List[float],
        coordinates: Dict[str, Dict[str, float]],
        page_number: int,
    ) -> Any:
        jpg_image = ImageDrawer.create_jpg_image(pdf_path, page_number)
        image_drawer = ImageDrawer(jpg_image, jpg_image.size[0], jpg_image.size[1])
        modified_image = image_drawer.draw_lines_and_coordinates(
            coordinates, lines_y_coordinates
        )

        return modified_image
