import pdfplumber
import numpy as np
from PIL import Image
import io
from pdf2image import convert_from_bytes
import os


class Extractor:
    def __init__(self, pdf_bytes: bytes, template_name: str, identifier: str):
        self.pdf_bytes = pdf_bytes
        self.template_name = template_name
        self.identifier = identifier

    def extract_data(self):
        """
        Extract text, bounding box information, and line coordinates from the PDF file.

        Returns:
            dict: Dictionary containing extracted text, bounding box information, line coordinates, number of pages, and dimensions.
        """
        prefix = f"{self.template_name}_{self.identifier}"
        pdf_jpg_files = ImageExtractor(self.pdf_bytes).convert_pdf_to_jpg_files(
            prefix=prefix
        )
        images_dir = os.path.join("src", "images", prefix)
        os.makedirs(images_dir, exist_ok=True)
        for jpg_file, jpg_bytes in pdf_jpg_files.items():
            with open(os.path.join(images_dir, jpg_file), "wb") as image_file:
                image_file.write(jpg_bytes)

        with pdfplumber.open(io.BytesIO(self.pdf_bytes)) as pdf:
            data = {
                "pages": [],
                "number_of_pages": len(pdf.pages),
                "dimensions": self.get_dimensions(pdf),
            }
            for page_num, page in enumerate(pdf.pages):
                page_data = self.extract_page_text_data(page)

                line_data = self.extract_page_line_data(
                    page, pdf_jpg_files[f"{prefix}_page_{page_num + 1}.jpg"]
                )

                data["pages"].append(
                    {
                        "page_number": page_num + 1,
                        "content": page_data,
                        "lines": line_data,
                    }
                )

            return data

    def get_dimensions(self, pdf):
        """Get the dimensions of the first page of the PDF."""
        return {
            "width": round(pdf.pages[0].width, 2),
            "height": round(pdf.pages[0].height, 2),
        }

    def extract_page_line_data(self, page, jpg_bytes):
        """Extract line data from a page."""
        image_extractor = ImageExtractor(self.pdf_bytes)
        line_data = []
        for line in page.lines:
            # Ensure line has the necessary keys before proceeding
            if "x0" in line and "y0" in line and "x1" in line and "y1" in line:
                coordinates = {
                    "top_left": {
                        "x": round(line["x0"] / page.width, 6),
                        "y": round(1 - (line["y0"] / page.height), 6),
                    },
                    "bottom_right": {
                        "x": round(line["x1"] / page.width, 6),
                        "y": round(1 - (line["y1"] / page.height), 6),
                    },
                }
                average_pixel_value, _, _, _ = (
                    image_extractor.calculate_average_pixel_value(
                        jpg_bytes,
                        coordinates,
                    )
                )
                line_data.append(
                    {
                        "decimal_coordinates": coordinates,
                        "average_pixel_value": average_pixel_value,
                    }
                )
        return line_data

    def extract_page_text_data(self, page):
        """Extract text and bounding box information from a page."""
        page_data = []
        for element in page.extract_words():
            text = element["text"]
            x0, y0, x1, y1 = (
                round(element["x0"], 2),
                round(element["top"], 2),
                round(element["x1"], 2),
                round(element["bottom"], 2),
            )
            page_data.append(
                {
                    "text": text,
                    "bounding_box": {
                        "coordinates": {
                            "top_left": {"x": x0, "y": y0},
                            "bottom_right": {"x": x1, "y": y1},
                        },
                        "decimal_coordinates": {
                            "top_left": {
                                "x": round((x0 / page.width), 6),
                                "y": round((y0 / page.height), 6),
                            },
                            "bottom_right": {
                                "x": round((x1 / page.width), 6),
                                "y": round((y1 / page.height), 6),
                            },
                        },
                    },
                }
            )
        return page_data


class ImageExtractor:
    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes

    def convert_pdf_to_jpg_files(self, prefix: str):
        """Convert the PDF into several JPG files, one for each page.

        Args:
            prefix (str): Optional prefix for the JPG file names.

        Returns:
            dict: Dictionary with file names as keys and JPEG bytes as values.
        """
        images = convert_from_bytes(self.pdf_bytes)
        jpg_files = {}
        for page_num, image in enumerate(images):
            jpg_file_name = f"{prefix}_page_{page_num + 1}.jpg"
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            jpg_files[jpg_file_name] = img_byte_arr.getvalue()
        return jpg_files

    def calculate_average_pixel_value(self, jpg_bytes, coordinates):
        # Load the image from bytes
        image = Image.open(io.BytesIO(jpg_bytes)).convert("RGB")
        pixels = np.array(image)

        # Calculate the coordinates in pixel values
        x_min = int(coordinates["top_left"]["x"] * image.width)
        y_min = int(coordinates["top_left"]["y"] * image.height)
        x_max = int(coordinates["bottom_right"]["x"] * image.width)
        y_max = int(coordinates["bottom_right"]["y"] * image.height)

        # Check for line coordinates
        if x_min == x_max:
            x_min = x_max = round(x_min)  # Round to the nearest whole pixel
            region = pixels[y_min:y_max, x_min : x_min + 1]  # Get the vertical line
        elif y_min == y_max:
            y_min = y_max = round(y_min)  # Round to the nearest whole pixel
            region = pixels[y_min : y_min + 1, x_min:x_max]  # Get the horizontal line
        else:
            # Extract the region of interest
            region = pixels[y_min:y_max, x_min:x_max]

        # Calculate the average pixel value
        average_pixel_value = list(
            np.round(np.mean(region, axis=(0, 1))).astype(int).tolist()
        )

        return (
            average_pixel_value,
            region,
            image,
            (round(x_min), round(y_min), round(x_max), round(y_max)),
        )
