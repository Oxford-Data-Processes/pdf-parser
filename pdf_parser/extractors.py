import io
import os
import re
from typing import Dict, List, Tuple, Any, Optional, Union

import numpy as np
import pdfplumber
import pytesseract  # type: ignore
from pdf2image import convert_from_bytes
from PIL import Image


class DataExtractor:
    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes

    def extract_data(self) -> Dict[str, Any]:
        """
        Extract text, bounding box information, and line coordinates from the PDF file.

        Returns:
            dict: Dictionary containing extracted text, bounding box information, line coordinates, number of pages, and dimensions.
        """
        pdf_jpg_files = ImageExtractor(self.pdf_bytes).convert_pdf_to_jpg_files()

        with pdfplumber.open(io.BytesIO(self.pdf_bytes)) as pdf:
            data: Dict[str, Any] = {
                "pages": [],
                "number_of_pages": len(pdf.pages),
                "dimensions": self.get_dimensions(pdf),
            }
            for page_num, page in enumerate(pdf.pages):
                page_data = self.extract_page_text_data(page)

                line_data = self.extract_page_line_data(page, pdf_jpg_files[page_num])

                data["pages"].append(
                    {
                        "page_number": page_num + 1,
                        "content": page_data,
                        "lines": line_data,
                    }
                )
            return data

    def get_dimensions(self, pdf: Any) -> Dict[str, float]:
        """Get the dimensions of the first page of the PDF."""
        return {
            "width": round(pdf.pages[0].width, 2),
            "height": round(pdf.pages[0].height, 2),
        }

    def extract_page_line_data(
        self, page: Any, jpg_bytes: bytes
    ) -> List[Dict[str, Any]]:
        """Extract line data from a page."""
        image_extractor = ImageExtractor(self.pdf_bytes)
        line_data: List[Dict[str, Any]] = []
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
                (
                    average_pixel_value,
                    _,
                    _,
                    _,
                ) = image_extractor.calculate_average_pixel_value(
                    jpg_bytes,
                    coordinates,
                )
                line_data.append(
                    {
                        "decimal_coordinates": coordinates,
                        "average_pixel_value": average_pixel_value,
                    }
                )
        return line_data

    def extract_page_text_data(self, page: Any) -> List[Dict[str, Any]]:
        """Extract text and bounding box information from a page."""
        page_data: List[Dict[str, Any]] = []
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
    def __init__(self, image_data: Union[bytes, Image.Image]):
        self.image_data = image_data

    def get_image(self) -> Image.Image:
        """Get PIL Image object from the image data."""
        if isinstance(self.image_data, Image.Image):
            return self.image_data
        return Image.open(io.BytesIO(self.image_data)).convert("RGB")

    def convert_pdf_to_jpg_files(self) -> List[bytes]:
        """Convert the PDF into several JPG files, one for each page.

        Returns:
            list: List of JPEG bytes for each page.
        """
        if not isinstance(self.image_data, bytes):
            raise ValueError("PDF conversion requires bytes input")

        images = convert_from_bytes(self.image_data)
        jpg_files = []
        for image in images:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            jpg_files.append(img_byte_arr.getvalue())
        return jpg_files

    def extract_text_from_coordinates(self, coordinates: Dict[str, Any]) -> str:
        """Extract text from specific coordinates in an image using OCR."""
        image = self.get_image()
        x_min = int(coordinates["top_left"]["x"] * image.width)
        y_min = int(coordinates["top_left"]["y"] * image.height)
        x_max = int(coordinates["bottom_right"]["x"] * image.width)
        y_max = int(coordinates["bottom_right"]["y"] * image.height)
        cropped_image = image.crop((x_min, y_min, x_max, y_max))
        return pytesseract.image_to_string(cropped_image).strip()

    def calculate_average_pixel_value(
        self, jpg_bytes: bytes, coordinates: Dict[str, Dict[str, float]]
    ) -> Tuple[List[int], np.ndarray, Image.Image, Tuple[int, int, int, int]]:
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

        # Handle empty regions
        if region.size == 0:
            return ([0, 0, 0], np.array([]), image, (x_min, y_min, x_max, y_max))

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


class TextExtractor:
    def __init__(self, coordinate_utils):
        self.coordinate_utils = coordinate_utils

    def get_text_from_items(self, items: List[Dict[str, Any]]) -> str:
        return " ".join([item["text"] for item in items])

    def get_text_from_ocr(
        self, jpg_bytes_page: Union[bytes, Image.Image], coordinates: Dict[str, Any]
    ) -> str:
        image_extractor = ImageExtractor(jpg_bytes_page)
        return image_extractor.extract_text_from_coordinates(coordinates)

    def get_items_in_bounding_box(
        self,
        text_coordinates: List[Dict[str, Any]],
        box_coordinates: Dict[str, Dict[str, float]],
        threshold: float = 0.005,
    ) -> List[Dict[str, Any]]:
        return self.coordinate_utils.get_items_in_bounding_box(
            text_coordinates, box_coordinates, threshold
        )

    def get_text_from_page(
        self,
        page_content: List[Dict[str, Any]],
        coordinates: Optional[Dict[str, Dict[str, float]]],
        extraction_method: str,
        jpg_bytes_page: Union[bytes, Image.Image],
        search_type: Optional[str] = None,
        regex: Optional[str] = None,
    ) -> str:
        """Extract text using either coordinates, OCR, or regex"""
        if search_type == "regex" and regex:
            try:
                # Join all text from the page with spaces
                full_page_text = " ".join([item["text"] for item in page_content])

                # Use regex to find matches
                matches = re.findall(regex, full_page_text)

                # Handle different match types
                if matches:
                    if isinstance(matches[0], tuple):
                        # If regex has capture groups, return first group
                        return matches[0][0]
                    else:
                        # If no capture groups, return full match
                        return matches[0]
                return ""

            except re.error as e:
                print(f"Invalid regex pattern: {regex}")
                print(f"Error: {str(e)}")
                return ""
            except Exception as e:
                print(f"Error processing regex: {str(e)}")
                return ""

        if coordinates is None:
            return ""

        if extraction_method == "extraction":
            items_within_coordinates = self.get_items_in_bounding_box(
                page_content, coordinates
            )
            return self.get_text_from_items(items_within_coordinates)
        elif extraction_method == "ocr":
            return self.get_text_from_ocr(jpg_bytes_page, coordinates)
        return ""
