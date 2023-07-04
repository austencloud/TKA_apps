from PyQt5.QtGui import QImage, QPainter, QBrush, QPen, QPolygonF, QPolygon, QColor
from PyQt5.QtCore import Qt

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
                grid_center_local = item.mapFromScene(grid_center_scene)

                #show a red dot at the center of the grid
                self.dot = self.scene.addEllipse(grid_center_scene.x() - 5, grid_center_scene.y() - 5, 10, 10, QPen(Qt.red), QBrush(Qt.red))
                #set the transform oigin around the center of the grid:
                item.setTransformOriginPoint(grid_center_local)
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

