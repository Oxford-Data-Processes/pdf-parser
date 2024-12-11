class CoordinateUtils:
    @staticmethod
    def get_rule_from_id(rule_id, template):
        return [item for item in template["rules"] if item["rule_id"] == rule_id][0]

    @staticmethod
    def get_items_in_bounding_box(text_coordinates, box_coordinates, threshold=0.005):
        items_in_box = []
        for item in text_coordinates:
            bounding_box = item["bounding_box"]["decimal_coordinates"]
            if (
                bounding_box["top_left"]["x"]
                >= box_coordinates["top_left"]["x"] - threshold
                and bounding_box["top_left"]["y"]
                >= box_coordinates["top_left"]["y"] - threshold
                and bounding_box["bottom_right"]["x"]
                <= box_coordinates["bottom_right"]["x"] + threshold
                and bounding_box["bottom_right"]["y"]
                <= box_coordinates["bottom_right"]["y"] + threshold
            ):
                items_in_box.append(item)
        return items_in_box
