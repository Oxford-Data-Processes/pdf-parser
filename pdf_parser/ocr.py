import io
from typing import Dict, Any
import pytesseract  # type: ignore
from PIL import Image


class ImageExtractor:
    def __init__(self, jpg_bytes: bytes, coordinates: Dict[str, Any]) -> None:
        self.jpg_bytes = jpg_bytes
        self.coordinates = coordinates

    def extract_text(self) -> str:
        """Extract text from an image using OCR."""
        image = Image.open(io.BytesIO(self.jpg_bytes))
        x_min = int(self.coordinates["top_left"]["x"] * image.width)
        y_min = int(self.coordinates["top_left"]["y"] * image.height)
        x_max = int(self.coordinates["bottom_right"]["x"] * image.width)
        y_max = int(self.coordinates["bottom_right"]["y"] * image.height)
        cropped_image = image.crop((x_min, y_min, x_max, y_max))
        return pytesseract.image_to_string(cropped_image).strip()

    def extract_text_from_coordinates(self, coordinates: Dict[str, Any]) -> str:
        """Extract text from specific coordinates in an image using OCR."""
        image = Image.open(io.BytesIO(self.jpg_bytes))
        x_min = int(coordinates["top_left"]["x"] * image.width)
        y_min = int(coordinates["top_left"]["y"] * image.height)
        x_max = int(coordinates["bottom_right"]["x"] * image.width)
        y_max = int(coordinates["bottom_right"]["y"] * image.height)
        cropped_image = image.crop((x_min, y_min, x_max, y_max))
        return pytesseract.image_to_string(cropped_image).strip()
