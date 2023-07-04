from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QPointF
from xml.dom import minidom
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItemGroup

from PyQt5.QtSvg import QGraphicsSvgItem

from PyQt5.QtSvg import QGraphicsSvgItem

from PyQt5.QtSvg import QGraphicsSvgItem

class Grid(QGraphicsSvgItem):
    def __init__(self, grid_svg):
        super().__init__(grid_svg)

        # Parse the SVG file
        self.doc = minidom.parse(grid_svg)

        # Find all circle elements in the SVG file
        circles = self.doc.getElementsByTagName('circle')

        # Find the circle with the id "center_point"
        center_point_circle = None
        for circle in circles:
            if circle.getAttribute('id') == "center_point":
                center_point_circle = circle
                break

        if center_point_circle is None:
            raise ValueError("No circle with id 'center_point' found in SVG file")

        # Get the center point of the circle
        center_x = float(center_point_circle.getAttribute('cx'))
        center_y = float(center_point_circle.getAttribute('cy'))

        # Store the center point as an attribute
        self.center_point = QPointF(center_x * 8.0, center_y * 8.0)  # Multiply by the scale factor

        # Set the transformation origin point to the center point
        self.setTransformOriginPoint(self.center_point)




    def getCenter(self):
        return self.mapToScene(self.center_point)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass
