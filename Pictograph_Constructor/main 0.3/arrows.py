from PyQt5.QtWidgets import QApplication, QGraphicsItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPainterPath, QCursor
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
import os

class Arrow_Logic(QGraphicsSvgItem):
    def __init__(self, svg_file, artboard):
        super().__init__(svg_file)
        self.setAcceptDrops(True)
        self.svg_file = svg_file
        self.in_drop_frame = False
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Store the reference to the artboard
        self.artboard = artboard
        self.grid = None
        self.dot = None

        # Determine the initial orientation based on the SVG file path
        if "_l_" in svg_file:
            self.orientation = "l"
        elif "_r_" in svg_file:
            self.orientation = "r"
        else:
            print("Unexpected svg_file:", svg_file)
            self.orientation = "r"  # use "r" as a fallback

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
            # Determine the current mouse position relative to the artboard
            mouse_pos = self.artboard.mapToScene(self.artboard.mapFromGlobal(QCursor.pos()))

            # Determine the quadrant of the scene the arrow is in
            if mouse_pos.y() < self.artboard().height() / 2:
                if mouse_pos.x() < self.artboard().width() / 2:
                    quadrant = 'nw'
                else:
                    quadrant = 'ne'
            else:
                if mouse_pos.x() < self.artboard().width() / 2:
                    quadrant = 'sw'
                else:
                    quadrant = 'se'

            # Get the base name of the file path
            base_name = os.path.basename(self.svg_file)

            # Replace the arrow with the corresponding form
            if base_name.startswith('red_anti'):
                new_svg = f'images\\arrows\\red\\{self.orientation}\\anti\\red_anti_{self.orientation}_{quadrant}.svg'
            elif base_name.startswith('red_iso'):
                new_svg = f'images\\arrows\\red\\{self.orientation}\\iso\\red_iso_{self.orientation}_{quadrant}.svg'
            elif base_name.startswith('blue_anti'):
                new_svg = f'images\\arrows\\blue\\{self.orientation}\\anti\\blue_anti_{self.orientation}_{quadrant}.svg'
            elif base_name.startswith('blue_iso'):
                new_svg = f'images\\arrows\\blue\\{self.orientation}\\iso\\blue_iso_{self.orientation}_{quadrant}.svg'
            else:
                print(f"Unexpected svg_file: {self.svg_file}")
                new_svg = self.svg_file  # use the current svg file as a fallback

            # Create a new QSvgRenderer
            new_renderer = QSvgRenderer(new_svg)

            # Check if the new renderer is valid
            if new_renderer.isValid():
                # Create a new QPixmap and QPainter
                pixmap = QPixmap(self.drag.pixmap().size())
                painter = QPainter(pixmap)

                # Render the new SVG file onto the QPixmap
                new_renderer.render(painter)

                # End the QPainter operation
                painter.end()

                # Set the new QPixmap as the pixmap of the drag object
                self.drag.setPixmap(pixmap)

            self.drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.renderer().boundsOnElement(self.elementId()))
        return path
