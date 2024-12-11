import json
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pdf_utils import ImageDrawer

template_name = "halifax"
identifier = "april"
# Load the PDF data
pdf_data_path = os.path.join(
    "src", "pdf_data", f"{template_name}_{identifier}_pdf_data.json"
)
with open(pdf_data_path, "r") as f:
    pdf_data = json.load(f)

# PDF path (assuming same naming convention)
pdf_path = os.path.join(
    "data", "bank_statements", template_name, "pdf", f"{template_name}_{identifier}.pdf"
)

# Process each page
for page_number, page_data in enumerate(pdf_data["pages"], start=1):
    print(f"\nProcessing page {page_number}...")

    # Extract line y-coordinates
    lines = page_data.get("lines", [])
    line_y_coords = []

    for line in lines:
        try:
            # Get decimal coordinates
            coords = line["decimal_coordinates"]
            y_coord = coords["top_left"]["y"]
            line_y_coords.append(y_coord)
        except (KeyError, TypeError) as e:
            print(f"Error processing line: {e}")
            continue

    print(f"Found {len(line_y_coords)} lines")

    # Create image with lines
    if line_y_coords:
        # Create a bounding box for the entire page
        coordinates = {"top_left": {"x": 0, "y": 0}, "bottom_right": {"x": 1, "y": 1}}

        # Draw lines on the page
        try:
            modified_image = ImageDrawer.draw_column_box_and_lines(
                pdf_path=pdf_path,
                lines_y_coordinates=sorted(line_y_coords),
                coordinates=coordinates,
                page_number=page_number,
            )

            # Save the modified image
            output_path = f"halifax_april_page_{page_number}_with_lines.jpg"
            # Display the image
            modified_image.show()

        except Exception as e:
            print(f"Error drawing lines on page {page_number}: {e}")
