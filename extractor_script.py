from PIL import Image, ImageDraw
import json
import numpy as np
import io
import os

from src.extractor import Extractor, ImageExtractor


template_name = "barclays_student"
identifier = "march"

pdf_path: str = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)


def draw_boxes(image, lines, color="red", width=2):
    """Draw boxes for lines."""
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    for line in lines:
        try:
            coords = line["decimal_coordinates"]

            # Convert decimal coordinates to pixel coordinates
            # Note: y coordinates are already inverted in the PDF data (1 - y)
            box_coords = (
                coords["top_left"]["x"] * image_width,
                coords["top_left"]["y"] * image_height,
                coords["bottom_right"]["x"] * image_width,
                coords["bottom_right"]["y"] * image_height,
            )

            # Draw the box
            draw.rectangle(box_coords, outline=color, width=width)

        except Exception as e:
            print(f"Error processing line: {e}")

    return image


# Read and process PDF
with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

# Extract text and lines
extractor = Extractor(pdf_bytes, template_name, identifier)
pdf_data = extractor.extract_data()

print(pdf_data)
