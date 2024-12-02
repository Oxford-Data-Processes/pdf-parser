from PIL import Image
import numpy as np
import io


def calculate_average_pixel_value(jpg_bytes, top_left, bottom_right):
    # Load the image from bytes
    image = Image.open(io.BytesIO(jpg_bytes))

    # Convert the image to RGB format
    image = image.convert("RGB")

    # Get the pixel values in the specified coordinates
    pixels = np.array(image)

    # Calculate the coordinates in pixel values
    x_min = int(top_left["x"] * image.width)
    y_min = int(top_left["y"] * image.height)
    x_max = int(bottom_right["x"] * image.width)
    y_max = int(bottom_right["y"] * image.height)

    # Check for invalid coordinates
    if x_min == x_max and y_min == y_max:
        raise ValueError("Invalid coordinates: both x and y values are the same.")

    # Extract the region of interest based on conditions
    if y_min == y_max:  # If y values are the same, average over x values
        region = pixels[y_min, x_min:x_max]
    elif x_min == x_max:  # If x values are the same, average over y values
        region = pixels[y_min:y_max, x_min]
    else:  # Normal case, extract the full region
        region = pixels[y_min:y_max, x_min:x_max]

    # Calculate the average pixel value
    average_pixel_value = np.mean(region, axis=(0, 1))

    # Convert to a 3-number code (R, G, B)
    average_pixel_code = tuple(map(int, average_pixel_value))

    return average_pixel_code


with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

extractor = Extractor(pdf_bytes)

pdf_jpg_files = extractor.convert_pdf_to_jpg_files(prefix="barclays_student_march")

# Example coordinates
top_left = {"x": 0.729, "y": 0.361}
bottom_right = {"x": 0.786, "y": 0.375}

# Calculate the average pixel value for the specified coordinates
average_pixel_code = calculate_average_pixel_value(
    pdf_jpg_files["barclays_student_march_page_2.jpg"], top_left, bottom_right
)
print("Average Pixel Code:", average_pixel_code)
