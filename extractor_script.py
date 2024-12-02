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


def validate_line_box(image, box_coords, expected_color=(255, 0, 0), thickness=2):
    """
    Validate that a box was drawn correctly at the given coordinates.
    Returns True if the box is found with the expected color.
    """
    img_array = np.array(image)
    x_min, y_min, x_max, y_max = [int(coord) for coord in box_coords]

    # Check top and bottom horizontal lines
    for y in [y_min, y_max]:
        for x in range(
            max(0, x_min - thickness), min(img_array.shape[1], x_max + thickness)
        ):
            if not any(
                np.array_equal(img_array[y, x], expected_color)
                for y in range(
                    max(0, y - thickness), min(img_array.shape[0], y + thickness)
                )
            ):
                return False

    # Check left and right vertical lines
    for x in [x_min, x_max]:
        for y in range(
            max(0, y_min - thickness), min(img_array.shape[0], y_max + thickness)
        ):
            if not any(
                np.array_equal(img_array[y, x], expected_color)
                for x in range(
                    max(0, x - thickness), min(img_array.shape[1], x + thickness)
                )
            ):
                return False

    return True


def draw_and_validate_boxes(image, lines, color="red", width=2):
    """Draw boxes for lines and validate each box."""
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    validation_results = []

    for i, line in enumerate(lines):
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

            # Validate the box was drawn correctly
            is_valid = validate_line_box(image, box_coords)
            validation_results.append(
                {"line_index": i, "coords": box_coords, "is_valid": is_valid}
            )

            if not is_valid:
                print(f"Warning: Box validation failed for line {i}")
                print(f"Coordinates: {box_coords}")

        except Exception as e:
            print(f"Error processing line {i}: {e}")
            validation_results.append(
                {"line_index": i, "error": str(e), "is_valid": False}
            )

    return image, validation_results


# Read and process PDF
with open(pdf_path, "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

image_extractor = ImageExtractor(pdf_bytes)
pdf_jpg_files = image_extractor.convert_pdf_to_jpg_files(
    prefix=f"{template_name}_{identifier}"
)

extractor = Extractor(pdf_bytes)
pdf_data = extractor.extract_text()

# Process page 2
page_number = 2
lines = pdf_data["pages"][page_number - 1]["lines"]  # 0-based index
jpg_key = f"{template_name}_{identifier}_page_{page_number}.jpg"
jpg_bytes = pdf_jpg_files[jpg_key]

# Open image and draw boxes
image = Image.open(io.BytesIO(jpg_bytes))
image_with_boxes, validation_results = draw_and_validate_boxes(image, lines)

# Print validation summary
valid_boxes = sum(1 for result in validation_results if result["is_valid"])
print(f"\nValidation Summary:")
print(f"Total lines: {len(lines)}")
print(f"Valid boxes drawn: {valid_boxes}")
print(f"Invalid boxes: {len(lines) - valid_boxes}")

if valid_boxes == len(lines):
    print("\nAll boxes were drawn and validated successfully!")
else:
    print("\nSome boxes failed validation. Check the warnings above for details.")

# Save the image for inspection
output_path = f"output_{jpg_key}"
image_with_boxes.save(output_path)
print(f"\nSaved annotated image to: {output_path}")

# Show the image
image_with_boxes.show(title="PDF Page with Line Boxes")
