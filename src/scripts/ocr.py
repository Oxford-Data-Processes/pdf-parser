from PIL import Image
import io
import pytesseract


class ImageExtractor:
    def __init__(self, jpg_bytes, decimal_coordinates):
        self.image = Image.open(io.BytesIO(jpg_bytes))
        self.coordinates = decimal_coordinates

    def extract_section(self):
        # Convert decimal coordinates to pixel values
        width, height = self.image.size
        top_left_x = int(self.coordinates["top_left"]["x"] * width)
        top_left_y = int(self.coordinates["top_left"]["y"] * height)
        bottom_right_x = int(self.coordinates["bottom_right"]["x"] * width)
        bottom_right_y = int(self.coordinates["bottom_right"]["y"] * height)

        # Crop the image to the specified coordinates
        return self.image.crop((top_left_x, top_left_y, bottom_right_x, bottom_right_y))

    def extract_text(self):
        section_image = self.extract_section()
        return pytesseract.image_to_string(section_image)
