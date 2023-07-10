from PyQt5.QtWidgets import QApplication, QGraphicsItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPainterPath, QCursor
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
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
        self.dragged_item = None
        self.infoTracker = infoTracker
        self.parse_filename()
        self.start_position, self.end_position = self.arrow_positions.get(os.path.basename(svg_file), (None, None))


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
            image = QImage(self.boundingRect().size().toSize() * 8, QImage.Format_ARGB32)
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
        self.dragging = False 
        self.dragged_item = None 
        self.infoTracker.update() 



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
            'start_position': self.start_position,
            'end_position': self.end_position,
        }
        return attributes

    def update_positions(self):
        # Update the start and end positions
        self.start_position, self.end_position = self.arrow_positions.get(os.path.basename(self.svg_file), (None, None))



    def generate_arrow_positions(color):
        return {
            f"{color}_anti_l_ne.svg": ("n", "e"),
            f"{color}_anti_r_ne.svg": ("e", "n"),
            f"{color}_anti_l_nw.svg": ("w", "n"),
            f"{color}_anti_r_nw.svg": ("n", "w"),
            f"{color}_anti_l_se.svg": ("e", "s"),
            f"{color}_anti_r_se.svg": ("s", "e"),
            f"{color}_anti_l_sw.svg": ("s", "w"),
            f"{color}_anti_r_sw.svg": ("w", "s"),
            f"{color}_iso_l_ne.svg": ("e", "n"),
            f"{color}_iso_r_ne.svg": ("n", "e"),
            f"{color}_iso_l_nw.svg": ("n", "w"),
            f"{color}_iso_r_nw.svg": ("w", "n"),
            f"{color}_iso_l_se.svg": ("s", "e"),
            f"{color}_iso_r_se.svg": ("e", "s"),
            f"{color}_iso_l_sw.svg": ("w", "s"),
            f"{color}_iso_r_sw.svg": ("s", "w"),
        }
    
    arrow_positions = {**generate_arrow_positions("red"), **generate_arrow_positions("blue")}

    def get_arrow_start_position(arrow):
        # Assuming that the 'start_position' attribute of an arrow is a direction
        return arrow.get_attributes().get('start_position')

    def get_arrow_end_position(arrow):
        # Assuming that the 'end_position' attribute of an arrow is a direction
        return arrow.get_attributes().get('end_position')

    def get_position_from_directions(direction1, direction2):
        # Define the mapping from pairs of directions to positions
        directions_positions = {
            ("n", "s"): "alpha",
            ("s", "n"): "alpha",
            ("w", "e"): "alpha",
            ("e", "w"): "alpha",
            ("e", "e"): "beta",
            ("s", "s"): "beta",
            ("w", "w"): "beta",
            ("n", "n"): "beta",
            ("n", "e"): "gamma",
            ("e", "n"): "gamma",
            ("e", "s"): "gamma",
            ("s", "e"): "gamma",
            ("s", "w"): "gamma",
            ("w", "s"): "gamma",
            ("w", "n"): "gamma",
            ("n", "w"): "gamma",
        }

        # Return the position corresponding to the pair of directions
        return directions_positions.get((direction1, direction2))
    
    
    def update_quadrant(self):
        # Determine the quadrant based on the start and end positions
        if self.start_position == "n":
            if self.end_position == "e":
                self.quadrant = "ne"
            else:  # self.end_position == "w"
                self.quadrant = "nw"
        elif self.start_position == "s":
            if self.end_position == "e":
                self.quadrant = "se"
            else:  # self.end_position == "w"
                self.quadrant = "sw"
        elif self.start_position == "e":
            if self.end_position == "n":
                self.quadrant = "ne"
            else:
                self.quadrant = "se"
        elif self.start_position == "w":
            if self.end_position == "n":
                self.quadrant = "nw"
            else:
                self.quadrant = "sw"
