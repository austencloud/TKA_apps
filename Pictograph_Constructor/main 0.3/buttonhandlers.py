from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt

class Button_Handlers:
    def __init__(self, artboard):
        self.artboard = artboard

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()

    def rotateSelected(self, angle):
        if self.view.grid is not None:
            # Get the center of the grid
            grid_center = self.view.grid.getCenter()

            for item in self.artboard.selectedItems():
                # Set the transformation origin point to the grid's center
                item.setTransformOriginPoint(item.mapFromScene(grid_center))

                # Rotate the item by the specified angle
                item.setRotation(item.rotation() + angle)


    def mirrorSelected(self, horizontal=True):
        for item in self.artboard.selectedItems():
            if horizontal:
                # Flip horizontally by applying a horizontal flip matrix
                item.setTransform(item.transform().scale(-1, 1))
            else:
                # Flip vertically by applying a vertical flip matrix
                item.setTransform(item.transform().scale(1, -1))

    def deleteSelected(self):
        for item in self.artboard.selectedItems():
            self.artboard.removeItem(item)

    def exportToPng(self):
        # Create a QImage with the same dimensions as the QGraphicsView
        image = QImage(self.view.size(), QImage.Format_ARGB32)

        # Create a QPainter and draw the QGraphicsView's artboard into the QImage
        painter = QPainter(image)
        self.view.render(painter)
        painter.end()

        # Save the QImage to a file
        image.save("export.png")

