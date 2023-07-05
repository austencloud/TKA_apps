from PyQt5.QtGui import QImage, QPainter, QBrush, QPen, QPolygonF, QPolygon, QColor, QTransform
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
                # Get the grid's center in the item's local coordinate            
                grid_center_item = item.mapFromScene(grid_center_scene)

                # Set the transform origin point to the grid's center
                item.setTransformOriginPoint(grid_center_item)

                # Rotate the item
                item.setRotation(item.rotation() + angle)

    def mirrorArrow(self):
        for item in self.artboard.selectedItems():
            # Get the current SVG file name
            current_svg = item.svg_file

            # Determine the new SVG file name and orientation based on the current orientation
            if item.orientation == "l":
                new_svg = current_svg.replace("_l_", "_r_").replace("\\l\\", "\\r\\")
                item.orientation = "r"
            elif item.orientation == "r":
                new_svg = current_svg.replace("_r_", "_l_").replace("\\r\\", "\\l\\")
                item.orientation = "l"
            else:
                print("Unexpected svg_file:", current_svg)
                continue

            # Create a new QSvgRenderer
            new_renderer = QSvgRenderer(new_svg)

            # Check if the new renderer is valid
            if new_renderer.isValid():
                # If the new renderer is valid, set it as the shared renderer of the item
                item.setSharedRenderer(new_renderer)
                # Update the svg_file attribute of the item
                item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)

    def deleteArrow(self):
        for item in self.artboard.selectedItems():
            self.artboard.removeItem(item)

    def exportArtboard(self):
        #get a list of all selected items
        selectedItems = self.artboard.selectedItems()

        #deselect the items in that list
        for item in selectedItems:
            item.setSelected(False)

        # Create a QImage with the same dimensions as the QGraphicsView
        image = QImage(self.view.size(), QImage.Format_ARGB32)
        # Create a QPainter and draw the QGraphicsView's artboard into the QImage
        painter = QPainter(image)
        self.view.render(painter)
        painter.end()

        # Save the QImage to a file
        image.save("export.png")

        #reselect the items that were already selected
        for item in selectedItems:
            item.setSelected(True)

    def bringForward(self):
        for item in self.artboard.selectedItems():
            #get the current z value
            z = item.zValue()
            #increment that z value up by one
            item.setZValue(z + 1)
