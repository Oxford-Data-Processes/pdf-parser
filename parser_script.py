import json
import os
from PIL import Image, ImageDraw
import io
from src.extractor import Extractor
from src.parser import Parser, TableSplitter
from src.pdf_utils import ImageDrawer

template_name: str = "barclays_student"
identifier: str = "march"
template_path: str = os.path.join("src", "templates", f"{template_name}_template.json")
pdf_path: str = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)
pdf_data_path: str = os.path.join(
    "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)
output_path: str = os.path.join(
    "src", "outputs", f"{template_name}_{identifier}_output.json"
)


def draw_lines(image, lines, coordinates, color="red", width=2):
    """Draw lines for each line in the data within the coordinates box."""
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    # Draw the description box
    box_coords = (
        coordinates["top_left"]["x"] * image_width,
        coordinates["top_left"]["y"] * image_height,
        coordinates["bottom_right"]["x"] * image_width,
        coordinates["bottom_right"]["y"] * image_height,
    )
    draw.rectangle(box_coords, outline=color, width=width)

    # Draw filtered lines that intersect with the box
    box_left = coordinates["top_left"]["x"] * image_width
    box_right = coordinates["bottom_right"]["x"] * image_width
    box_top = coordinates["top_left"]["y"] * image_height
    box_bottom = coordinates["bottom_right"]["y"] * image_height

    for line in lines:
        try:
            coords = line["decimal_coordinates"]
            y0 = coords["top_left"]["y"] * image_height

            # Check if line intersects with description box
            if box_top <= y0 <= box_bottom:
                # Draw line across the box width
                draw.line([(box_left, y0), (box_right, y0)], fill=color, width=width)

        except Exception as e:
            print(f"Error processing line: {e}")
            continue

    return image


# Read and process PDF
with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()
    text_extractor = Extractor(pdf_bytes, template_name, identifier)
    extracted_data = text_extractor.extract_data()

    with open(pdf_data_path, "w") as f:
        json.dump(extracted_data, f)

template = json.load(open(template_path))
pdf_data = json.load(open(pdf_data_path))

# Process page 2
page_number = 2
page_content = pdf_data["pages"][page_number - 1]

lines = page_content["lines"]

delimiter_field_name = "description"
max_pixel_value = (200, 200, 200)

from src.parser import Parser

parser = Parser()

delimiter_coordinates = parser.get_delimiter_column_coordinates(
    template, delimiter_field_name
)

filtered_lines = parser.filter_lines_by_pixel_value(lines, max_pixel_value)

print(filtered_lines)

# Convert PDF to image and draw lines
from src.extractor import ImageExtractor

image_extractor = ImageExtractor(pdf_bytes)
pdf_jpg_files = image_extractor.convert_pdf_to_jpg_files(
    prefix=f"{template_name}_{identifier}"
)

jpg_key = f"{template_name}_{identifier}_page_{page_number}.jpg"
jpg_bytes = pdf_jpg_files[jpg_key]

# Draw lines on the image
image = Image.open(io.BytesIO(jpg_bytes))
image_with_lines = draw_lines(image, filtered_lines, delimiter_coordinates)

# Save and show the result
output_image_path = f"output_{jpg_key}"
image_with_lines.save(output_image_path)
print(f"\nSaved output image to: {output_image_path}")
image_with_lines.show()
