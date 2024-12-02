from PIL import Image
import numpy as np
import io
import os

from src.extractor import Extractor

pdf_path: str = os.path.join(
    "data", "bank_statements", "barclays_student", "pdf", "barclays_student_march.pdf"
)


def calculate_average_pixel_value(jpg_bytes, top_left, bottom_right):
    # Load the image from bytes
    image = Image.open(io.BytesIO(jpg_bytes)).convert("RGB")
    pixels = np.array(image)

    # Calculate the coordinates in pixel values
    x_min = int(top_left["x"] * image.width)
    y_min = int(top_left["y"] * image.height)
    x_max = int(bottom_right["x"] * image.width)
    y_max = int(bottom_right["y"] * image.height)

    # Check for invalid coordinates
    if x_min == x_max and y_min == y_max:
        raise ValueError("Invalid coordinates: both x and y values are the same.")

    # Extract the region of interest
    region = pixels[y_min:y_max, x_min:x_max]

    # Calculate the average pixel value
    average_pixel_value = np.mean(region, axis=(0, 1))
    average_pixel_code = tuple(map(int, average_pixel_value))

    return average_pixel_code, average_pixel_value, region


def create_average_color_image(average_pixel_value, size=(50, 50)):
    # Create an image filled with the average pixel color
    avg_color_image = Image.new("RGB", size, tuple(map(int, average_pixel_value)))
    return avg_color_image


with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

extractor = Extractor(pdf_bytes)
pdf_jpg_files = extractor.convert_pdf_to_jpg_files(prefix="barclays_student_march")

# Example coordinates
top_left = {"x": 0.729, "y": 0.361}
bottom_right = {"x": 0.786, "y": 0.375}


jpg_bytes = pdf_jpg_files["barclays_student_march_page_2.jpg"]
image = Image.open(io.BytesIO(jpg_bytes))
image.show(title="JPEG File")

# Calculate the average pixel value for the specified coordinates
average_pixel_code, average_pixel_value, region = calculate_average_pixel_value(
    jpg_bytes, top_left, bottom_right
)
print("Average Pixel Code:", average_pixel_code)


# Create an image of the average color
average_color_image = create_average_color_image(average_pixel_value)

# Display the original region and the average color image
region_image = Image.fromarray(region)
region_image.show(title="Extracted Region")
average_color_image.show(title="Average Color Image")
