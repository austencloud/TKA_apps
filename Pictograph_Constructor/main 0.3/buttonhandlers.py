from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgRenderer

class Button_Handlers:
    def __init__(self, artboard, view, grid, scene):
        self.artboard = artboard
        self.view = view
        self.grid = grid
        self.scene = scene

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteArrow()

    def rotateArrow(self, angle):
        if self.view.grid is not None:
            grid_center_scene = self.view.grid.getCenter()
            for item in self.scene.selectedItems():         
                grid_center_item = item.mapFromScene(grid_center_scene)
                item.setTransformOriginPoint(grid_center_item)
                item.setRotation(item.rotation() + angle)

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
