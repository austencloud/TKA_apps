from PyQt5.QtWidgets import QApplication, QLabel
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

    def mousePressEvent(self, event):
        self.dragOffset = event.pos()
        if self.in_drop_frame:
            super().mousePressEvent(event)
        elif event.button() == Qt.LeftButton:
            self.Drop_Frame_Objects_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.in_drop_frame:
            super().mouseMoveEvent(event)
        elif not (event.buttons() & Qt.LeftButton):
            return
        elif (event.pos() - self.Drop_Frame_Objects_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        else:
            from drop_frame import Drop_Frame_Objects
            Drop_Frame_Objects = Drop_Frame_Objects(self)
            mime_data = QMimeData()

            # Set the file path of the SVG file in the MIME data
            mime_data.setText(self.svg_file)

            # Create a QDrag object
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(self.dragOffset.toPoint())

            pixmap = QPixmap(self.boundingRect().size().toSize() * 8)
            painter = QPainter(pixmap)

            # Use the renderer's render method
            self.renderer().render(painter)

            # End the QPainter
            painter.end()

            drag.setPixmap(pixmap)

            drag.exec_(Qt.CopyAction | Qt.MoveAction)


    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.renderer().boundsOnElement(self.elementId()))
        return path
    
class NewArrow(QLabel):
    def __init__(self, svg_path: str, parent=None):
        super().__init__(parent)
        self.svg_path = svg_path
        renderer = QSvgRenderer(svg_path)
        image = QImage(200, 200, QImage.Format_ARGB32)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()  # <-- End the painter's session
        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mimedata = QMimeData()

            pixmap = self.pixmap()
            mimedata.setImageData(pixmap.toImage())

            drag_start_position = QPointF(event.pos())
            mimedata.setText(','.join(map(str, [drag_start_position.x(), drag_start_position.y()])))
            
            mimedata.setData('application/x-qabstractitemmodeldatalist', QByteArray(self.svg_path.encode()))

            drag.setMimeData(mimedata)

            pixmap_scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            drag.setPixmap(pixmap_scaled)

            drag.setHotSpot(drag_start_position.toPoint())

            drag.exec_(Qt.CopyAction)
            self.setVisible(True)

