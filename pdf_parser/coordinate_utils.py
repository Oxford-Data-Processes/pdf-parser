from typing import Dict, List, Any


class CoordinateUtils:
    @staticmethod
    def get_rule_from_id(rule_id: str, template: Dict[str, Any]) -> Dict[str, Any]:
        return [item for item in template["rules"] if item["rule_id"] == rule_id][0]

    @staticmethod
    def get_items_in_bounding_box(
        text_coordinates: List[Dict[str, Any]],
        box_coordinates: Dict[str, Dict[str, float]],
        threshold: float = 0.005,
    ) -> List[Dict[str, Any]]:
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
