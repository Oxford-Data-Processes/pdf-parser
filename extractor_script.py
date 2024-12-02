from PIL import Image, ImageDraw
import numpy as np
import io
import os

from src.extractor import Extractor, ImageExtractor


template_name = "barclays_student"

identifier = "march"

pdf_path: str = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)


def create_average_color_image(average_pixel_value, size=(50, 50)):
    # Create an image filled with the average pixel color
    avg_color_image = Image.new("RGB", size, tuple(map(int, average_pixel_value)))
    return avg_color_image


def show_average_color_image(average_pixel_value, region, image, box_coords):

    # Draw a red box around the coordinates
    draw = ImageDraw.Draw(image)
    draw.rectangle(box_coords, outline="red", width=3)

    # Show the image with the red box
    image.show(title="JPEG File with Red Box")

    # Create an image of the average color
    average_color_image = create_average_color_image(average_pixel_value)

    # Display the original region and the average color image
    region_image = Image.fromarray(region)
    region_image.show(title="Extracted Region")
    average_color_image.show(title="Average Color Image")


with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

image_extractor = ImageExtractor(pdf_bytes)
pdf_jpg_files = image_extractor.convert_pdf_to_jpg_files(
    prefix=f"{template_name}_{identifier}"
)


with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

extractor = Extractor(pdf_bytes)

pdf_data = extractor.extract_text()


page_number = 2
lines = pdf_data["pages"][page_number]["lines"]

for line in lines[1:2]:

    coordinates = line["decimal_coordinates"]

    jpg_bytes = pdf_jpg_files[f"{template_name}_{identifier}_page_{page_number}.jpg"]

    print(coordinates)

    average_pixel_value, region, image, box_coords = (
        image_extractor.calculate_average_pixel_value(jpg_bytes, coordinates)
    )

    show_average_color_image(average_pixel_value, region, image, box_coords)
