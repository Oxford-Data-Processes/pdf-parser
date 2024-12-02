from PIL import Image
import numpy as np
import io
import os
from src.extractor import Extractor

pdf_path = os.path.join(
    "data", "bank_statements", "barclays_student", "pdf", "barclays_student_march.pdf"
)


def calculate_average_pixel_value(jpg_bytes, top_left, bottom_right):
    """Calculate the average pixel value in a specified region of an image."""
    image = Image.open(io.BytesIO(jpg_bytes)).convert("RGB")
    pixels = np.array(image)

    x_min, y_min = int(top_left["x"] * image.width), int(top_left["y"] * image.height)
    x_max, y_max = int(bottom_right["x"] * image.width), int(
        bottom_right["y"] * image.height
    )

    if x_min == x_max and y_min == y_max:
        raise ValueError("Invalid coordinates: both x and y values are the same.")

    region = pixels[y_min:y_max, x_min:x_max]
    average_pixel_value = np.mean(region, axis=(0, 1))
    average_pixel_code = tuple(map(int, average_pixel_value))

    return average_pixel_code, average_pixel_value, region


def create_average_color_image(average_pixel_value, size=(50, 50)):
    """Create an image filled with the average pixel color."""
    return Image.new("RGB", size, tuple(map(int, average_pixel_value)))


def main():
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    extractor = Extractor(pdf_bytes)
    pdf_jpg_files = extractor.convert_pdf_to_jpg_files(prefix="barclays_student_march")

    top_left = {"x": 0.729, "y": 0.361}
    bottom_right = {"x": 0.786, "y": 0.375}

    average_pixel_code, average_pixel_value, region = calculate_average_pixel_value(
        pdf_jpg_files["barclays_student_march_page_2.jpg"], top_left, bottom_right
    )
    print("Average Pixel Code:", average_pixel_code)

    average_color_image = create_average_color_image(average_pixel_value)

    combined_image = Image.new(
        "RGB",
        (
            region.shape[1] + average_color_image.width,
            max(region.shape[0], average_color_image.height),
        ),
    )
    region_image = Image.fromarray(region)
    combined_image.paste(region_image, (0, 0))
    combined_image.paste(average_color_image, (region.shape[1], 0))

    combined_image.show(title="Extracted Region and Average Color Image")


if __name__ == "__main__":
    main()
