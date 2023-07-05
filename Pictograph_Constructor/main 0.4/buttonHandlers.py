from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtSvg import QSvgRenderer, QSvgGenerator
from PyQt5.QtWidgets import QFileDialog
import os


from arrows import Arrow_Logic

class Button_Handlers:
    def __init__(self, artboard, view, grid, scene, main_window):
        self.artboard = artboard
        self.view = view
        self.grid = grid
        self.scene = scene
        self.main_window = main_window

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteArrow()

    def rotateArrow(self, direction):
        if self.view.grid is not None:
            scene_center = QPointF(self.view.width() / 2, self.view.height() / 2)
            

            #fill in the red dot
            self.scene.addEllipse(scene_center.x() - 2, scene_center.y() - 2, 4, 4, Qt.red, Qt.red)


            for item in self.artboard.selectedItems():
                # Get the current position of the item relative to the scene center
                current_pos = item.pos() - scene_center
                item.setTransformOriginPoint(item.boundingRect().center())
                # Calculate the new position based on the rotation direction
                if direction == "right":
                    new_pos = QPointF(-current_pos.y(), current_pos.x())
                else:  # direction == "left"
                    new_pos = QPointF(current_pos.y(), -current_pos.x())

                # Move the item to the new position
                item.setPos(scene_center + new_pos)

                # Change the SVG file to match the new orientation
                base_name = os.path.basename(item.svg_file)
                color, type_, orientation, quadrant = base_name.split('_')[:4]
                quadrant = quadrant.replace('.svg', '')

                quadrants = ['ne', 'se', 'sw', 'nw']
                current_quadrant_index = quadrants.index(quadrant)
                if direction == "right":
                    new_quadrant_index = (current_quadrant_index + 1) % 4
                else:  # direction == "left"
                    new_quadrant_index = (current_quadrant_index - 1) % 4

                new_quadrant = quadrants[new_quadrant_index]
                new_svg = item.svg_file.replace(quadrant, new_quadrant)

                new_renderer = QSvgRenderer(new_svg)
                if new_renderer.isValid():
                    item.setSharedRenderer(new_renderer)
                    item.svg_file = new_svg
                else:
                    print("Failed to load SVG file:", new_svg)

    def mirrorArrow(self):
        for item in self.artboard.selectedItems():
            current_svg = item.svg_file

            if item.orientation == "l":
                new_svg = current_svg.replace("_l_", "_r_").replace("\\l\\", "\\r\\")
                item.orientation = "r"
            elif item.orientation == "r":
                new_svg = current_svg.replace("_r_", "_l_").replace("\\r\\", "\\l\\")
                item.orientation = "l"
            else:
                print("Unexpected svg_file:", current_svg)
                continue

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

    def swapColors(self):
        if len(self.artboard.selectedItems()) == 0:
            self.selectAll()
            for item in self.artboard.selectedItems():
                current_svg = item.svg_file
                base_name = os.path.basename(current_svg)
                color, type_, orientation, quadrant = base_name.split('_')[:4]
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
        elif len(self.artboard.selectedItems()) > 0:
            for item in self.artboard.selectedItems():
                current_svg = item.svg_file
                base_name = os.path.basename(current_svg)
                color, type_, orientation, quadrant = base_name.split('_')[:4]
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



    def selectAll(self):
        for item in self.artboard.items():
            item.setSelected(True)
    def deselectAll(self):
        for item in self.artboard.selectedItems():
            item.setSelected(False)

    def export_to_svg(self):
        generator = QSvgGenerator()
        generator.setFileName("output.svg")
        generator.setSize(self.artboard.sceneRect().size().toSize())
        generator.setViewBox(self.artboard.sceneRect())

        painter = QPainter(generator)
        self.artboard.render(painter)
        painter.end()
