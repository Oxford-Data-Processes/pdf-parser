class CoordinateUtils:
    @staticmethod
    def convert_to_absolute(relative_coord, page_dimensions):
        """Converts relative coordinates to absolute positions."""
        absolute_x = relative_coord[0] * page_dimensions[0]
        absolute_y = relative_coord[1] * page_dimensions[1]
        return (absolute_x, absolute_y)

    @staticmethod
    def is_within_bounds(coord, bounds):
        """Checks if a coordinate lies within specified bounds."""
        return bounds[0] <= coord[0] <= bounds[2] and bounds[1] <= coord[1] <= bounds[3]


class PDFUtils:
    @staticmethod
    def merge_text_elements(text_elements):
        """Merges adjacent text elements, if necessary."""
        merged_text = []
        current_text = text_elements[0] if text_elements else ""

        for element in text_elements[1:]:
            if (
                element["y"] == current_text["y"]
            ):  # Assuming 'y' indicates vertical position
                current_text["text"] += " " + element["text"]
            else:
                merged_text.append(current_text)
                current_text = element

        merged_text.append(current_text)
        return merged_text

    @staticmethod
    def sort_lines(lines):
        """Sorts lines based on their positions on the page."""
        return sorted(
            lines, key=lambda line: line["y"]
        )  # Assuming 'y' indicates vertical position
