from PyQt5.QtWidgets import QApplication, QGraphicsItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPainterPath, QBrush, QColor, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
from PyQt5.QtWidgets import QGraphicsEllipseItem


class Arrow_Logic(QGraphicsSvgItem):
    def __init__(self, svg_file):
        super().__init__(svg_file)
        self.setAcceptDrops(True)
        self.svg_file = svg_file
        self.in_drop_frame = False
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Define the grid and dot attributes
        self.grid = None
        self.dot = None

        if "grid" not in svg_file:
            self.setFlag(QGraphicsSvgItem.ItemIsMovable, True)
            self.setFlag(QGraphicsSvgItem.ItemIsSelectable, True)
            self.setTransformOriginPoint(self.boundingRect().center())


    def mousePressEvent(self, event):
        self.dragOffset = event.pos() - self.boundingRect().center()
        if self.in_drop_frame:
            super().mousePressEvent(event)
        elif event.button() == Qt.LeftButton:
            self.Drop_Frame_Objects_start_position = event.pos()

            self.drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.svg_file)
            self.drag.setMimeData(mime_data)
            image = QImage(self.boundingRect().size().toSize() * 8, QImage.Format_RGB32)
            painter = QPainter(image)

            painter.setRenderHint(QPainter.Antialiasing)
            renderer = QSvgRenderer(self.svg_file)
            if not renderer.isValid():
                print(f"Failed to load SVG file: {self.svg_file}")
                return
            renderer.render(painter)
            painter.end()
            pixmap = QPixmap.fromImage(image)
            self.drag.setPixmap(pixmap)
            self.drag.setHotSpot(pixmap.rect().center())

    def mouseMoveEvent(self, event):
        if self.in_drop_frame:
            super().mouseMoveEvent(event)
        elif not (event.buttons() & Qt.LeftButton):
            return
        elif (event.pos() - self.Drop_Frame_Objects_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        else:
            self.drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.renderer().boundsOnElement(self.elementId()))
        return path
    
    # need to modify this so it can access the svgs instead of usig pixmap

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.grid is not None:
            # Get the position of the arrow in the scene
            pos = self.scenePos()

            # Determine the quadrant of the grid the arrow is in
            if pos.y() < self.scene().height() / 2:
                if pos.x() < self.scene().width() / 2:
                    quadrant = 'nw'
                else:
                    quadrant = 'ne'
            else:
                if pos.x() < self.scene().width() / 2:
                    quadrant = 'sw'
                else:
                    quadrant = 'se'

            # Replace the arrow with the corresponding form
            if self.filename.startswith('red_anti'):
                new_svg = 'images\\arrows\\red_anti_r_' + quadrant + '.svg'
            elif self.filename.startswith('red_iso'):
                new_svg = 'images\\arrows\\red_iso_r_' + quadrant + '.svg'
            elif self.filename.startswith('blue_anti'):
                new_svg = 'images\\arrows\\blue_anti_r_' + quadrant + '.svg'
            elif self.filename.startswith('blue_iso'):
                new_svg = 'images\\arrows\\blue_iso_r_' + quadrant + '.svg'

            # Load the new SVG file and replace the current SVG item with a new one
            self.setSharedRenderer(QSvgRenderer(new_svg))

        return super().itemChange(change, value)

    def updateRedDot(self):
        # Remove the old red dot
        if self.dot is not None:
            self.scene().removeItem(self.dot)

        # Add a new red dot at the transformation origin point
        if self.grid is not None:

            # Get the transformation origin point in the local coordinates of the arrow
            local_origin = self.mapFromScene(self.transformOriginPoint())

            # Convert the transformation origin point to scene coordinates
            scene_origin = self.mapToScene(local_origin)

            # Create the red dot at the transformation origin point in scene coordinates
            self.dot = RedDot(scene_origin)


class RedDot(QGraphicsEllipseItem):
    def __init__(self, center, radius=5, parent=None):
        super().__init__(parent)
        self.setRect(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Set the brush to solid red
        self.setBrush(QBrush(QColor(255, 0, 0)))

        # Set the pen to no pen (i.e., no stroke)
        self.setPen(QPen(Qt.NoPen))
