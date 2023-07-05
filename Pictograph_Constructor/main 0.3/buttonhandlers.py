from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgRenderer
import os

class Button_Handlers:
    def __init__(self, artboard, view, grid, scene):
        self.artboard = artboard
        self.view = view
        self.grid = grid
        self.scene = scene

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteArrow()

    def rotateArrow(self, direction):
        for item in self.artboard.selectedItems():
            current_svg = item.svg_file
            base_name = os.path.basename(current_svg)
            color, type_, orientation, quadrant = base_name.split('_')[:4]
            print(color, type_, orientation, quadrant)
            quadrants = ['ne', 'se', 'sw', 'nw']
            quadrant = quadrant.replace('.svg', '')
            current_quadrant_index = quadrants.index(quadrant)
            if direction == "right":
                new_quadrant_index = (current_quadrant_index + 1) % 4
            elif direction == "left":
                new_quadrant_index = (current_quadrant_index - 1) % 4
            else:
                print("Unexpected direction:", direction)
                continue
            new_quadrant = quadrants[new_quadrant_index]
            new_svg = current_svg.replace(quadrant, new_quadrant)
            new_renderer = QSvgRenderer(new_svg)
            if new_renderer.isValid():
                item.setSharedRenderer(new_renderer)
                item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)

    def mirrorArrow(self):
        for item in self.artboard.selectedItems():
            current_svg = item.svg_file
            print(f"Current SVG: {current_svg}")  # Print the current SVG file path
            if item.orientation == "l":
                new_svg = current_svg.replace("_l_", "_r_").replace("\\l\\", "\\r\\")
                item.orientation = "r"
            elif item.orientation == "r":
                new_svg = current_svg.replace("_r_", "_l_").replace("\\r\\", "\\l\\")
                item.orientation = "l"
            else:
                print("Unexpected svg_file:", current_svg)
                continue
            print(f"New SVG: {new_svg}")  # Print the new SVG file path
            new_renderer = QSvgRenderer(new_svg)
            if new_renderer.isValid():
                item.setSharedRenderer(new_renderer)
                item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)

    def deleteArrow(self):
        for item in self.artboard.selectedItems():
            self.artboard.removeItem(item)

    def exportArtboard(self):
        selectedItems = self.artboard.selectedItems()
        image = QImage(self.view.size(), QImage.Format_ARGB32)
        painter = QPainter(image)

        for item in selectedItems:
            item.setSelected(False)

        self.view.render(painter)
        painter.end()
        image.save("export.png")

        for item in selectedItems:
            item.setSelected(True)

    def bringForward(self):
        for item in self.artboard.selectedItems():
            z = item.zValue()
            item.setZValue(z + 1)

#write a swapColors function which looks at all the svgs that are currently selected and changes the red to blue and blue to red
    def swapColors(self):
        for item in self.artboard.selectedItems():
            current_svg = item.svg_file
            base_name = os.path.basename(current_svg)
            color, type_, orientation, quadrant = base_name.split('_')[:4]
            print(color, type_, orientation, quadrant)
            if color == "red":
                new_color = "blue"
            elif color == "blue":
                new_color = "red"
            else:
                print("Unexpected color:", color)
                continue
            new_svg = current_svg.replace(color, new_color)
            new_renderer = QSvgRenderer(new_svg)
            if new_renderer.isValid():
                item.setSharedRenderer(new_renderer)
                item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)