import pdfplumber
from PIL import ImageDraw
from pdf2image import convert_from_path


pdf_path = "data/bank_statements/barclays/pdf/barclays March 2.pdf"


def create_jpg_image(pdf_path):
    # Convert the PDF page to a JPG
    images = convert_from_path(pdf_path)
    jpg_image_original = images[1]  # Get the second page as a JPG

    # Open the PDF and get the second page
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[1]

    # Save the JPG image
    jpg_image_original.save("barclays_march_2.jpeg", "JPEG")

    return jpg_image_original, page


jpg_image_original, page = create_jpg_image(pdf_path)

# Open the PDF file
with pdfplumber.open(pdf_path) as pdf:
    # Get the second page
    second_page = pdf.pages[1]
    # Extract the lines from the second page
    lines = second_page.lines

    # Create a copy of the original image to draw on
    jpg_image_original_copy = jpg_image_original.copy()
    draw = ImageDraw.Draw(jpg_image_original_copy)

    # Get the dimensions of the original image
    img_width, img_height = jpg_image_original_copy.size

    # Draw the lines on the image with scaling
    for line in lines:
        # Check if the line has valid coordinates
        if "x0" in line and "y0" in line and "x1" in line and "y1" in line:
            # Scale the coordinates based on the image dimensions
            scaled_x0 = line["x0"] * img_width
            scaled_y0 = line["y0"] * img_height
            scaled_x1 = line["x1"] * img_width
            scaled_y1 = line["y1"] * img_height
            draw.line(
                [(scaled_x0, scaled_y0), (scaled_x1, scaled_y1)], fill="red", width=5
            )

# Show the modified image
jpg_image_original_copy.show()
