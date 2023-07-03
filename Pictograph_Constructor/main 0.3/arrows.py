from PyQt5.QtWidgets import QApplication, QLabel, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QMimeData, QPointF, QByteArray
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem


class Objects_From_Sidebar(QGraphicsSvgItem):
    def __init__(self, svg_file):
        super().__init__(svg_file)
        self.setAcceptDrops(True)
        self.svg_file = svg_file
        self.in_drop_frame = False

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

            # Create a QDrag object
            self.drag = QDrag(self)
            mime_data = QMimeData()

            # Set the file path of the SVG file in the MIME data
            mime_data.setText(self.svg_file)
            self.drag.setMimeData(mime_data)

            # Create a QImage with the same dimensions as the item
            image = QImage(self.boundingRect().size().toSize() * 8, QImage.Format_RGB32)

            # Create a QPainter and draw the item into the QImage
            painter = QPainter(image)

            # Set the QPainter's render hint to antialiasing
            painter.setRenderHint(QPainter.Antialiasing)

            # Render the item using the QPainter
            renderer = QSvgRenderer(self.svg_file)
            if not renderer.isValid():
                print(f"Failed to load SVG file: {self.svg_file}")
                return
            renderer.render(painter)

            # End the QPainter
            painter.end()

            # Convert the QImage to a QPixmap
            pixmap = QPixmap.fromImage(image)

            # Set the pixmap for the drag
            self.drag.setPixmap(pixmap)

            # Set the hotspot to the center of the pixmap
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
    

