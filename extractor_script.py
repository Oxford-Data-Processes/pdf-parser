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


def draw_lines(image, lines, color="red", width=2):
    """Draw lines for each line in the data."""
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    for line in lines:
        try:
            coords = line["decimal_coordinates"]

            # Convert decimal coordinates to pixel coordinates
            line_coords = (
                coords["top_left"]["x"] * image_width,
                coords["top_left"]["y"] * image_height,
                coords["bottom_right"]["x"] * image_width,
                coords["bottom_right"]["y"] * image_height,
            )

            # Draw the line
            draw.line(line_coords[:2] + line_coords[2:], fill=color, width=width)

        except Exception as e:
            print(f"Error processing line: {e}")

    return image


# Read and process PDF
with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

# Extract text and lines
extractor = Extractor(pdf_bytes, template_name, identifier)
pdf_data = extractor.extract_data()

page_number = 2

lines = pdf_data["pages"][page_number - 1]["lines"]

max_pixel_value = (200, 200, 200)

filtered_lines = []
for line in lines:
    average_red = line["average_pixel_value"][0]
    average_green = line["average_pixel_value"][1]
    average_blue = line["average_pixel_value"][2]

    max_red = max_pixel_value[0]
    max_green = max_pixel_value[1]
    max_blue = max_pixel_value[2]

    if average_red < max_red and average_green < max_green and average_blue < max_blue:
        filtered_lines.append(line)

image_extractor = ImageExtractor(pdf_bytes)

pdf_bytes_dictionary = image_extractor.convert_pdf_to_jpg_files(
    prefix=f"{template_name}_{identifier}"
)

pdf_bytes = pdf_bytes_dictionary[f"{template_name}_{identifier}_page_{page_number}.jpg"]

image = Image.open(io.BytesIO(pdf_bytes))
image_with_lines = draw_lines(image, filtered_lines)
image_with_lines.show()
