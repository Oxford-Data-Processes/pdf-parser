import json

import fitz  # PyMuPDF
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


class PDFCoordinateFinder:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.current_page = 0
        self.first_point = None
        self.second_point = None
        self.rect = None
        self.first_point_marker = None
        self.preview_rect = None
        self.panning = False
        self.mode = "select"  # 'select' or 'pan'

        # Setup the plot
        self.fig, self.ax = plt.subplots(figsize=(12, 16))
        self.fig.canvas.manager.set_window_title("PDF Coordinate Finder")

        # Add navigation buttons
        plt.subplots_adjust(bottom=0.2)
        self.prev_button_ax = plt.axes([0.1, 0.05, 0.15, 0.075])
        self.next_button_ax = plt.axes([0.3, 0.05, 0.15, 0.075])
        self.zoom_in_ax = plt.axes([0.5, 0.05, 0.15, 0.075])
        self.zoom_out_ax = plt.axes([0.7, 0.05, 0.15, 0.075])
        self.mode_toggle_ax = plt.axes([0.1, 0.15, 0.15, 0.075])
        self.show_coords_ax = plt.axes([0.3, 0.15, 0.15, 0.075])

        self.prev_button = plt.Button(self.prev_button_ax, "Previous Page")
        self.next_button = plt.Button(self.next_button_ax, "Next Page")
        self.zoom_in_button = plt.Button(self.zoom_in_ax, "Zoom In")
        self.zoom_out_button = plt.Button(self.zoom_out_ax, "Zoom Out")
        self.mode_toggle = plt.Button(self.mode_toggle_ax, "Mode: Select")
        self.show_coords_button = plt.Button(self.show_coords_ax, "Show Coords")

        # Add field name display
        self.field_name_ax = plt.axes([0.5, 0.15, 0.4, 0.075])
        self.field_name_text = plt.text(
            0.5,
            0.5,
            "Last field: None",
            ha="center",
            va="center",
            transform=self.field_name_ax.transAxes,
        )
        self.field_name_ax.set_xticks([])
        self.field_name_ax.set_yticks([])

        # Connect events
        self.prev_button.on_clicked(self.prev_page)
        self.next_button.on_clicked(self.next_page)
        self.zoom_in_button.on_clicked(self.zoom_in)
        self.zoom_out_button.on_clicked(self.zoom_out)
        self.mode_toggle.on_clicked(self.toggle_mode)
        self.show_coords_button.on_clicked(self.show_coordinates)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

        # Load first page
        self.load_page()
        plt.show()

    def toggle_mode(self, event):
        if self.mode == "select":
            self.mode = "pan"
            self.mode_toggle.label.set_text("Mode: Pan")
        else:
            self.mode = "select"
            self.mode_toggle.label.set_text("Mode: Select")
        self.reset_points()
        plt.draw()

    def load_page(self):
        self.ax.clear()
        page = self.doc[self.current_page]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.page_width = pix.width
        self.page_height = pix.height
        self.ax.imshow(np.array(img))
        self.ax.set_title(
            f"Page {self.current_page + 1} of {len(self.doc)}\n"
            f"Current Mode: {self.mode.capitalize()}"
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        plt.draw()

    def on_mouse_move(self, event):
        if event.inaxes == self.ax:
            if self.panning and self.mode == "pan" and hasattr(self, "pan_start"):
                dx = event.xdata - self.pan_start[0]
                dy = event.ydata - self.pan_start[1]
                self.ax.set_xlim(self.pan_xlim - dx)
                self.ax.set_ylim(self.pan_ylim - dy)
                plt.draw()
            elif self.first_point and not self.second_point and self.mode == "select":
                if self.preview_rect:
                    self.preview_rect.remove()
                x = min(self.first_point[0], event.xdata)
                y = min(self.first_point[1], event.ydata)
                width = abs(event.xdata - self.first_point[0])
                height = abs(event.ydata - self.first_point[1])
                self.preview_rect = patches.Rectangle(
                    (x, y),
                    width,
                    height,
                    linewidth=1,
                    edgecolor="r",
                    facecolor="r",
                    alpha=0.2,
                )
                self.ax.add_patch(self.preview_rect)
                plt.draw()

    def calculate_coordinates(self):
        x1 = self.first_point[0] / self.page_width
        y1 = self.first_point[1] / self.page_height
        x2 = self.second_point[0] / self.page_width
        y2 = self.second_point[1] / self.page_height

        top_left = {"x": round(min(x1, x2), 3), "y": round(min(y1, y2), 3)}
        bottom_right = {"x": round(max(x1, x2), 3), "y": round(max(y1, y2), 3)}

        # Get field name from console instead of dialog
        print("\nEnter field name for this selection in the console:")
        field_name = input()

        if field_name:
            self.field_name_text.set_text(f"Last field: {field_name}")
            plt.draw()

            template_snippet = {
                "rule_id": field_name,
                "type": "form",
                "config": {
                    "field_name": field_name,
                    "coordinates": {"top_left": top_left, "bottom_right": bottom_right},
                    "type": "text",
                },
            }

            print(f"\nPage: {self.current_page + 1}")
            print(f"Field: {field_name}")
            print(f"top_left: {top_left}")
            print(f"bottom_right: {bottom_right}")
            print("\nTemplate JSON snippet:")
            print(json.dumps(template_snippet, indent=4))

    def on_click(self, event):
        if event.inaxes == self.ax:
            if self.mode == "pan":
                self.panning = True
                self.pan_start = (event.xdata, event.ydata)
                self.pan_xlim = self.ax.get_xlim()
                self.pan_ylim = self.ax.get_ylim()
            elif self.mode == "select":
                if self.first_point is None:
                    self.first_point = (event.xdata, event.ydata)
                    if self.first_point_marker:
                        self.first_point_marker.remove()
                    self.first_point_marker = self.ax.plot(
                        event.xdata, event.ydata, "ro", markersize=5
                    )[0]
                    print("\nFirst point selected")
                    plt.draw()
                else:
                    self.second_point = (event.xdata, event.ydata)
                    self.draw_rectangle()
                    self.calculate_coordinates()
                    self.reset_points()

    def on_release(self, event):
        self.panning = False

    def reset_points(self):
        self.first_point = None
        self.second_point = None
        if self.rect:
            self.rect.remove()
            self.rect = None
        if self.first_point_marker:
            self.first_point_marker.remove()
            self.first_point_marker = None
        if self.preview_rect:
            self.preview_rect.remove()
            self.preview_rect = None
        plt.draw()

    def draw_rectangle(self):
        if self.rect:
            self.rect.remove()
        x = min(self.first_point[0], self.second_point[0])
        y = min(self.first_point[1], self.second_point[1])
        width = abs(self.second_point[0] - self.first_point[0])
        height = abs(self.second_point[1] - self.first_point[1])
        self.rect = patches.Rectangle(
            (x, y), width, height, linewidth=1, edgecolor="r", facecolor="r", alpha=0.3
        )
        self.ax.add_patch(self.rect)
        plt.draw()

    def prev_page(self, event):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page()
            self.reset_points()

    def next_page(self, event):
        if self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.load_page()
            self.reset_points()

    def zoom_in(self, event):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 0.75, self.ax.get_xlim()[1] * 0.75)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 0.75, self.ax.get_ylim()[1] * 0.75)
        plt.draw()

    def zoom_out(self, event):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 1.25, self.ax.get_xlim()[1] * 1.25)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 1.25, self.ax.get_ylim()[1] * 1.25)
        plt.draw()

    def show_coordinates(self, event):
        print("\nEnter coordinates to visualize (as decimal values between 0-1):")
        try:
            top_left_x = float(input("Top left X: "))
            top_left_y = float(input("Top left Y: "))
            bottom_right_x = float(input("Bottom right X: "))
            bottom_right_y = float(input("Bottom right Y: "))

            # Convert relative coordinates to pixel coordinates
            x = top_left_x * self.page_width
            y = top_left_y * self.page_height
            width = (bottom_right_x - top_left_x) * self.page_width
            height = (bottom_right_y - top_left_y) * self.page_height

            # Remove existing rectangle if any
            if self.rect:
                self.rect.remove()

            # Draw new rectangle
            self.rect = patches.Rectangle(
                (x, y),
                width,
                height,
                linewidth=1,
                edgecolor="b",
                facecolor="b",
                alpha=0.3,
            )
            self.ax.add_patch(self.rect)

            # Center view on the rectangle
            self.ax.set_xlim(
                x - self.page_width * 0.1, x + width + self.page_width * 0.1
            )
            self.ax.set_ylim(
                y - self.page_height * 0.1, y + height + self.page_height * 0.1
            )

            plt.draw()

            print("\nCoordinates visualized in blue")

        except ValueError:
            print("Invalid input. Please enter numeric values.")


if __name__ == "__main__":
    document_type = "bank_statements"
    template_name = "monzo"
    identifier = "3_months"
    pdf_path = (
        f"data/{document_type}/{template_name}/pdf/{template_name}_{identifier}.pdf"
    )
    app = PDFCoordinateFinder(pdf_path)
