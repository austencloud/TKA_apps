from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsPixmapItem, QAbstractItemView
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QMimeData, QPointF
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
from arrows import Objects_From_Sidebar
from xml.dom import minidom
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsItemGroup

class Artboard(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        self.dragging = None
        self.grid = None 

        # Set the drag mode to QGraphicsView::RubberBandDrag
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setStyleSheet("QGraphicsView { rubberBandColor: rgba(0, 0, 125, 25); }")

        # Set the QGraphicsView to interactive mode
        self.setInteractive(True)

        # Set a background for the QGraphicsScene
        scene.setBackgroundBrush(Qt.white)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.CopyAction)
            event.accept()

            # Get the SVG file from the MIME data
            grid_svg = event.mimeData().text()

            # Create a new DraggableSvg item
            if "grid" in grid_svg:
                grid_item = Grid(grid_svg)
                grid_item.setScale(8.0)

                # Add the new DraggableSvg item to the scene at the drop location
                self.scene().addItem(grid_item)
                grid_item.setPos(self.mapToScene(event.pos()))
            else:
                arrow_item = Objects_From_Sidebar(grid_svg)
                arrow_item.setScale(8.0)

                # Add the new DraggableSvg item to the scene at the drop location
                self.scene().addItem(arrow_item)
                arrow_item.setPos(self.mapToScene(event.pos()))

        
            arrow_item.setScale(8.0)

            # Add the new DraggableSvg item to the scene at the drop location
            self.scene().addItem(arrow_item)
            arrow_item.setPos(self.mapToScene(event.pos()))
        else:
            event.ignore()



    def mousePressEvent(self, event):
        items = self.items(event.pos())
        if items and items[0].flags() & QGraphicsItem.ItemIsMovable:
            if event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
                # If the Control key is pressed, toggle the selection of the item under the cursor
                items[0].setSelected(not items[0].isSelected())
            elif not items[0].isSelected():
                # If the item under the cursor is not already selected, select it and deselect all other items
                for item in self.scene().selectedItems():
                    item.setSelected(False)
                items[0].setSelected(True)
            self.dragging = items[0]
            self.dragOffset = self.mapToScene(event.pos()) - self.dragging.pos()
        else:
            # If there is no item under the cursor, deselect all items
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.dragging = None

        # Call the base class's mousePressEvent if the left button is pressed and there are no items under the cursor.
        if event.button() == Qt.LeftButton and not items:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Calculate the new position for the dragging item
            new_pos = self.mapToScene(event.pos()) - self.dragOffset

            # Calculate the movement vector
            movement = new_pos - self.dragging.pos()

            # Move all selected items by the movement vector
            for item in self.scene().selectedItems():
                item.setPos(item.pos() + movement)

    def mouseReleaseEvent(self, event):
        self.dragging = None
        # Clear the rubber band
        self.setRubberBandSelectionMode(Qt.ContainsItemShape)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        super().mouseReleaseEvent(event)

class Artboard_Objects(QGraphicsPixmapItem):
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
        self.id = Artboard_Objects.id_counter
        Artboard_Objects.id_counter += 1
        self.Artboard_Objects_start_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setVisible(False)  # hide original item
            views = self.scene().views()
            
            if views:
                if self.Artboard_Objects_start_position is None:  # this is for Artboard_Objectsging copied items
                    self.Artboard_Objects_start_position = event.pos() - self.boundingRect().topLeft()
                
                Artboard_Objects = Artboard_Objects(views[0])  # Use the first QGraphicsView as the parent
                Artboard_Objects.setHotSpot(self.Artboard_Objects_start_position.toPoint())
                mimedata = QMimeData()

                pixmap = self.pixmap()
                mimedata.setImageData(pixmap.toImage())
                mimedata.setText(str(self.id))

                Artboard_Objects.setMimeData(mimedata)

                pixmap_scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                Artboard_Objects.setPixmap(pixmap_scaled)

                self.Artboard_Objects_start_position = event.pos() - self.boundingRect().topLeft()
                Artboard_Objects.setHotSpot(self.Artboard_Objects_start_position.toPoint())

                Artboard_Objects.exec_(Qt.CopyAction)  # Execute the Artboard_Objects action
            else:
                return  # Do nothing if there are no views
                items = self.items(event.pos())
                


    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.isSelected():
            pen = QPen(Qt.red, 3, Qt.DashDotLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

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

        # Set the transformation origin point to the center point
        self.setTransformOriginPoint(center_x, center_y)

        # Create a CircleItem for each circle and add it to the group
        for circle in circles:
            # Get the center and radius of the circle
            center = QPointF(float(circle.getAttribute('cx')), float(circle.getAttribute('cy')))
            radius = float(circle.getAttribute('r'))

            item = Make_Circle(center, radius)
            item.setScale(8.0)  
            item.setZValue(-1)
            self.addToGroup(item)


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
