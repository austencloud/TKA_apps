import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter
from PyQt5.QtCore import Qt, QMimeData, QPointF, QByteArray
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem

class DraggableSvg(QGraphicsSvgItem):
    def __init__(self, svg_file):
        super().__init__(svg_file)
        self.setAcceptDrops(True)
        self.svg_file = svg_file

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        # Set the file path of the SVG file in the MIME data
        mime_data.setText(self.svg_file)

        drag.setMimeData(mime_data)
        drag.setHotSpot(event.pos().toPoint())

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

class Drag(QGraphicsPixmapItem):
    id_counter = 0

    def __init__(self, svg_path: str):
        self.svg_path = svg_path
        self.svg_renderer = QSvgRenderer(svg_path)
        self.highlighted_svg_renderer = QSvgRenderer(svg_path)

        original_size = self.svg_renderer.defaultSize()
        scale_factor = min(200 / original_size.width(), 200 / original_size.height())

        # Create the original pixmap
        image = QImage(int(original_size.width() * scale_factor), int(original_size.height() * scale_factor), QImage.Format_ARGB32)
        painter = QPainter(image)
        self.svg_renderer.render(painter)
        painter.end()
        pixmap = QPixmap.fromImage(image)
        super().__init__(pixmap)


        # Create the highlighted pixmap
        highlighted_image = QImage(200, 200, QImage.Format_ARGB32)
        highlighted_painter = QPainter(highlighted_image)
        self.highlighted_svg_renderer.render(highlighted_painter)
        highlighted_painter.end()  # <-- End the highlighted painter's session
        self.highlighted_pixmap = QPixmap.fromImage(highlighted_image)
        super().__init__(pixmap)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.id = Drag.id_counter
        Drag.id_counter += 1
        self.drag_start_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setVisible(False)  # hide original item
            views = self.scene().views()
            
            if views:
                if self.drag_start_position is None:  # this is for dragging copied items
                    self.drag_start_position = event.pos() - self.boundingRect().topLeft()
                
                drag = QDrag(views[0])  # Use the first QGraphicsView as the parent
                drag.setHotSpot(self.drag_start_position.toPoint())
                mimedata = QMimeData()

                pixmap = self.pixmap()
                mimedata.setImageData(pixmap.toImage())
                mimedata.setText(str(self.id))

                drag.setMimeData(mimedata)

                pixmap_scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                drag.setPixmap(pixmap_scaled)

                self.drag_start_position = event.pos() - self.boundingRect().topLeft()
                drag.setHotSpot(self.drag_start_position.toPoint())

                drag.exec_(Qt.CopyAction)  # Execute the drag action
            else:
                return  # Do nothing if there are no views
            

    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.drawPixmap(self.boundingRect(), self.highlighted_pixmap, self.boundingRect())
        else:
            super().paint(painter, option, widget)
