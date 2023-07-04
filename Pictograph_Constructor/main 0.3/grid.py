from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QPointF
from xml.dom import minidom
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItemGroup

class Grid(QGraphicsItemGroup):
    def __init__(self, grid_svg):
        super().__init__()

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

        # Create a CircleItem for each circle and add it to the group
        for circle in circles:
            # Get the center and radius of the circle
            center = QPointF(float(circle.getAttribute('cx')), float(circle.getAttribute('cy')))
            radius = float(circle.getAttribute('r'))

            item = Make_Circle(center, radius)
            item.setScale(8.0)  
            item.setZValue(-1)
            self.addToGroup(item)

        # Set the transformation origin point to the center point
        self.setTransformOriginPoint(center_x * 8.0, center_y * 8.0)  # Multiply by the scale factor

    def getCenter(self):
        return self.boundingRect().center()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

class Make_Circle(QGraphicsEllipseItem):
    def __init__(self, center, radius, parent=None):
        super().__init__(parent)
        self.setRect(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Set the brush to solid black
        self.setBrush(QBrush(QColor(0, 0, 0)))

        # Set the pen to no pen (i.e., no stroke)
        self.setPen(QPen(Qt.NoPen))
