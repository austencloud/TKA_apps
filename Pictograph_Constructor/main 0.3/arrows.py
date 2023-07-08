from PyQt5.QtWidgets import QApplication, QGraphicsItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPainterPath, QCursor
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
import os

class Arrow_Logic(QGraphicsSvgItem):
    SVG_SCALE = 8.0
    def __init__(self, svg_file, artboard):
        super().__init__(svg_file)
        self.setAcceptDrops(True)
        self.svg_file = svg_file
        self.in_artboard = False
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.artboard = artboard
        self.grid = None
        self.dot = None

        if "_l_" in svg_file:
            self.orientation = "l"
        elif "_r_" in svg_file:
            self.orientation = "r"
        else:
            print("Unexpected svg_file:", svg_file)
            self.orientation = "r"

        if "grid" not in svg_file:
            self.setFlag(QGraphicsSvgItem.ItemIsMovable, True)
            self.setFlag(QGraphicsSvgItem.ItemIsSelectable, True)
            self.setTransformOriginPoint(self.boundingRect().center())
            
    def mousePressEvent(self, event):
        self.dragOffset = event.pos() - self.boundingRect().center()
        if self.in_artboard:
            super().mousePressEvent(event)
        elif event.button() == Qt.LeftButton:
            self.artboard_start_position = event.pos()

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
        if self.in_artboard:
            print("mouse_pos:", mouse_pos)
            super().mouseMoveEvent(event)
        elif not (event.buttons() & Qt.LeftButton):
            return
        elif (event.pos() - self.artboard_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        mouse_pos = self.artboard.mapToScene(self.artboard.mapFromGlobal(QCursor.pos()))
        artboard_rect = self.artboard.sceneRect()

        if artboard_rect.contains(mouse_pos):
            print("artboard contains mouse_pos")
            if mouse_pos.y() < artboard_rect.height() / 2:
                if mouse_pos.x() < artboard_rect.width() / 2:
                    quadrant = 'nw'
                else:
                    quadrant = 'ne'
            else:
                if mouse_pos.x() < artboard_rect.width() / 2:
                    quadrant = 'sw'
                else:
                    quadrant = 'se'

            # print the current quadrant whenever a mouse drags over it
            print(quadrant)
            base_name = os.path.basename(self.svg_file)

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
                new_svg = self.svg_file
        else:
            new_svg = self.svg_file

        new_renderer = QSvgRenderer(new_svg)

        if new_renderer.isValid():
            pixmap = QPixmap(self.boundingRect().size().toSize() * self.SVG_SCALE)
            painter = QPainter(pixmap)
            new_renderer.render(painter)
            painter.end()
            self.drag.setPixmap(pixmap)

        self.drag.exec_(Qt.CopyAction | Qt.MoveAction)







    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.renderer().boundsOnElement(self.elementId()))
        return path
