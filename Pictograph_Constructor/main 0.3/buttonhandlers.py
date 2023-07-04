from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt

class Button_Handlers:
    def __init__(self, artboard, view, grid):
        self.artboard = artboard
        self.view = view
        self.grid = grid


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteArrow()

    def rotateArrow(self, angle):
        print("rotateArrow")
        if self.grid is not None:
            # Get the center of the grid
            grid_center = self.grid.getCenter()

            for item in self.artboard.selectedItems():
                # Convert the center of the grid from scene coordinates to item coordinates
                local_grid_center = item.mapFromScene(grid_center)

                # Set the transformation origin point to the grid's center
                item.setTransformOriginPoint(local_grid_center)

                # Rotate the item by the specified angle
                item.setRotation(item.rotation() + angle)


    def mirrorArrow(self, horizontal=True):
        for item in self.artboard.selectedItems():
            if horizontal:
                # Flip horizontally by applying a horizontal flip matrix
                item.setTransform(item.transform().scale(-1, 1))
            else:
                # Flip vertically by applying a vertical flip matrix
                item.setTransform(item.transform().scale(1, -1))

    def deleteArrow(self):
        for item in self.artboard.selectedItems():
            self.artboard.removeItem(item)

    def exportArtboard(self):
        # Create a QImage with the same dimensions as the QGraphicsView
        image = QImage(self.view.size(), QImage.Format_ARGB32)

        # Create a QPainter and draw the QGraphicsView's artboard into the QImage
        painter = QPainter(image)
        self.view.render(painter)
        painter.end()

        # Save the QImage to a file
        image.save("export.png")

