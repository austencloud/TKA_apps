from PyQt5.QtWidgets import QApplication, QGraphicsItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPainterPath, QCursor
from PyQt5.QtCore import Qt, QMimeData, QPointF
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
import os

class Arrow(QGraphicsSvgItem):
    SVG_SCALE = 10.0
    def __init__(self, svg_file, artboard, infoTracker):
        super().__init__(svg_file)
        self.setAcceptDrops(True)
        self.svg_file = svg_file
        self.in_artboard = False
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.artboard = artboard
        self.grid = None
        self.dot = None
        self.dragging = False
        self.drag = QDrag(self)
        self.dragged_item = None
        self.infoTracker = infoTracker
        self.parse_filename()

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
            self.dragging = True 
            self.dragged_item = self  # set dragged_item to self when the drag starts
            
            mime_data = QMimeData()
            mime_data.setText(self.svg_file)
            self.drag.setMimeData(mime_data)

            # Create a QImage to render the SVG to
            image = QImage(self.boundingRect().size().toSize() * 10, QImage.Format_ARGB32)
            image.fill(Qt.transparent)  # Fill with transparency to preserve SVG transparency

            # Create a QPainter to paint the SVG onto the QImage
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)

            # Create a QSvgRenderer with the SVG file and render it onto the QImage
            renderer = QSvgRenderer(self.svg_file)
            if not renderer.isValid():
                print(f"Failed to load SVG file: {self.svg_file}")
                return
            renderer.render(painter)

            # End the QPainter operation
            painter.end()

            # Convert the QImage to a QPixmap and set it as the drag pixmap
            pixmap = QPixmap.fromImage(image)
            self.drag.setPixmap(pixmap)
            self.drag.setHotSpot(pixmap.rect().center())

    def mouseMoveEvent(self, event):
        mouse_pos = self.artboard.mapToScene(self.artboard.mapFromGlobal(QCursor.pos()))
        movement = QPointF(0, 0)  # Add this line to assign a default value to movement

        if self.dragging:
            new_pos = self.mapToScene(event.pos()) - self.dragOffset
            movement = new_pos - self.dragged_item.pos()  # use self.dragged_item here
        for item in self.scene().selectedItems():
            item.setPos(item.pos() + movement)
        self.infoTracker.checkForChanges()
        if self.in_artboard:
            print("mouse_pos:", mouse_pos)
            super().mouseMoveEvent(event)
        elif not (event.buttons() & Qt.LeftButton):
            return
        elif (event.pos() - self.artboard_start_position).manhattanLength() < QApplication.startDragDistance():
            return

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
                new_svg = f'images\\arrows\\red\\anti\\{self.orientation}\\red_anti_{self.orientation}_{quadrant}.svg'
            elif base_name.startswith('red_iso'):
                new_svg = f'images\\arrows\\red\\iso\\{self.orientation}\\red_iso_{self.orientation}_{quadrant}.svg'
            elif base_name.startswith('blue_anti'):
                new_svg = f'images\\arrows\\blue\\anti\\{self.orientation}\\blue_anti_{self.orientation}_{quadrant}.svg'
            elif base_name.startswith('blue_iso'):
                new_svg = f'images\\arrows\\blue\\iso\\{self.orientation}\\blue_iso_{self.orientation}_{quadrant}.svg'
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
        self.dragging = False 
        self.dragged_item = None  # set dragged_item to None when the drag ends

    def shape(self):
        path = QPainterPath()
        path.addRect(self.renderer().boundsOnElement(self.elementId()))
        return path

    def parse_filename(self):
        # Assuming filenames are in the format 'color_type_r_quadrant.svg'
        parts = os.path.basename(self.svg_file).split('_')  # use self.svg_file here
        self.color = parts[0]
        self.type = parts[1]
        self.rotation = parts[2]
        self.quadrant = parts[3].split('.')[0]  # remove the '.svg' part

    def get_attributes(self):
        attributes = {
            'color': self.color,
            'quadrant': self.quadrant,
            'rotation': self.rotation,
            'type': self.type,
        }
        return attributes