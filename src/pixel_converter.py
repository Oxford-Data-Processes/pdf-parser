pixels = {
    "length": 2480,
    "width": 3509,
    "forms": {
        "sort_code": {
            "page": 1,
            "bounding_box": {
                "top_left": {"x": 1596, "y": 1501},
                "box_size": {"width": 141, "height": 31},
            },
        },
        "account_number": {
            "page": 1,
            "bounding_box": {
                "top_left": {"x": 1931, "y": 1499},
                "box_size": {"width": 183, "height": 39},
            },
        },
        "customer_name": {
            "page": 1,
            "bounding_box": {
                "top_left": {"x": 1448, "y": 1686},
                "box_size": {"width": 483, "height": 45},
            },
        },
        "start_balance": {
            "page": 2,
            "bounding_box": {
                "top_left": {"x": 2150, "y": 664},
                "box_size": {"width": 170, "height": 40},
            },
        },
        "money_in": {
            "page": 2,
            "bounding_box": {
                "top_left": {"x": 2150, "y": 732},
                "box_size": {"width": 198, "height": 44},
            },
        },
        "money_out": {
            "page": 2,
            "bounding_box": {
                "top_left": {"x": 2150, "y": 795},
                "box_size": {"width": 198, "height": 44},
            },
        },
        "end_balance": {
            "page": 2,
            "bounding_box": {
                "top_left": {"x": 2150, "y": 859},
                "box_size": {"width": 170, "height": 40},
            },
        },
        "overdraft_limit": {
            "page": 2,
            "bounding_box": {
                "top_left": {"x": 2200, "y": 1045},
                "box_size": {"width": 145, "height": 42},
            },
        },
    },
    "tables": [
        {
            "date": {
                "page": 2,
                "bounding_box": {
                    "top_left": {"x": 232, "y": 1712},
                    "box_size": {"width": 132, "height": 1679},
                },
            },
            "description": {
                "page": 2,
                "bounding_box": {
                    "top_left": {"x": 451, "y": 1712},
                    "box_size": {"width": 602, "height": 1679},
                },
            },
            "money_in": {
                "page": 2,
                "bounding_box": {
                    "top_left": {"x": 1080, "y": 1712},
                    "box_size": {"width": 132, "height": 1679},
                },
            },
            "money_out": {
                "page": 2,
                "bounding_box": {
                    "top_left": {"x": 1280, "y": 1712},
                    "box_size": {"width": 132, "height": 1679},
                },
            },
            "balance": {
                "page": 2,
                "bounding_box": {
                    "top_left": {"x": 1500, "y": 1712},
                    "box_size": {"width": 132, "height": 1679},
                },
            },
        },
        {
            "date": {
                "page": 3,
                "bounding_box": {
                    "top_left": {"x": 232, "y": 330},
                    "box_size": {"width": 131, "height": 2130},
                },
            },
            "description": {
                "page": 3,
                "bounding_box": {
                    "top_left": {"x": 451, "y": 330},
                    "box_size": {"width": 602, "height": 2215},
                },
            },
            "money_in": {
                "page": 3,
                "bounding_box": {
                    "top_left": {"x": 1080, "y": 330},
                    "box_size": {"width": 132, "height": 2215},
                },
            },
            "money_out": {
                "page": 3,
                "bounding_box": {
                    "top_left": {"x": 1280, "y": 330},
                    "box_size": {"width": 132, "height": 2215},
                },
            },
            "balance": {
                "page": 3,
                "bounding_box": {
                    "top_left": {"x": 1500, "y": 330},
                    "box_size": {"width": 132, "height": 2215},
                },
            },
        },
    ],
}


def calculate_percentage_coordinates(pixels):
    length = pixels["length"]
    width = pixels["width"]

    for form, details in pixels["forms"].items():
        top_left = details["bounding_box"]["top_left"]
        box_size = details["bounding_box"]["box_size"]
        bottom_right = {
            "x": top_left["x"] + box_size["width"],
            "y": top_left["y"] + box_size["height"],
        }
        details["bounding_box"]["top_left_percentage"] = {
            "x": round(top_left["x"] / width, 6),
            "y": round(top_left["y"] / length, 6),
        }
        details["bounding_box"]["bottom_right_percentage"] = {
            "x": round(bottom_right["x"] / width, 6),
            "y": round(bottom_right["y"] / length, 6),
        }

    for table in pixels["tables"]:
        for key, details in table.items():
            top_left = details["bounding_box"]["top_left"]
            box_size = details["bounding_box"]["box_size"]
            bottom_right = {
                "x": top_left["x"] + box_size["width"],
                "y": top_left["y"] + box_size["height"],
            }
            details["bounding_box"]["top_left_percentage"] = {
                "x": round(top_left["x"] / width, 6),
                "y": round(top_left["y"] / length, 6),
            }
            details["bounding_box"]["bottom_right_percentage"] = {
                "x": round(bottom_right["x"] / width, 6),
                "y": round(bottom_right["y"] / length, 6),
            }

    return pixels
