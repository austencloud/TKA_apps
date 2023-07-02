
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem
from sidebar import Objects_From_Sidebar

class Drop_Frame(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        self.dragging = None

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
            svg_file = event.mimeData().text()

            # Create a new DraggableSvg item
            if "grid" in svg_file:
                svg_item = Grid(svg_file)
            else:
                svg_item = Objects_From_Sidebar(svg_file)

            svg_item.setScale(8.0)

            # Add the new DraggableSvg item to the scene at the drop location
            self.scene().addItem(svg_item)
            svg_item.setPos(self.mapToScene(event.pos()))
        else:
            event.ignore()


    def mousePressEvent(self, event):

        items = self.items(event.pos())
        if items and items[0].flags() & QGraphicsItem.ItemIsMovable:
            self.dragging = items[0]
            self.dragOffset = self.mapToScene(event.pos()) - self.dragging.pos()
            self.dragging.setSelected(True)
        else:
            for item in self.scene().selectedItems():
                item.setSelected(False)
            self.dragging = None    

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.dragging.setPos(self.mapToScene(event.pos()) - self.dragOffset)

    def mouseReleaseEvent(self, event):
        self.dragging = None

class Drop_Frame_Objects(QGraphicsPixmapItem):
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
        self.id = Drop_Frame_Objects.id_counter
        Drop_Frame_Objects.id_counter += 1
        self.Drop_Frame_Objects_start_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setVisible(False)  # hide original item
            views = self.scene().views()
            
            if views:
                if self.Drop_Frame_Objects_start_position is None:  # this is for Drop_Frame_Objectsging copied items
                    self.Drop_Frame_Objects_start_position = event.pos() - self.boundingRect().topLeft()
                
                Drop_Frame_Objects = Drop_Frame_Objects(views[0])  # Use the first QGraphicsView as the parent
                Drop_Frame_Objects.setHotSpot(self.Drop_Frame_Objects_start_position.toPoint())
                mimedata = QMimeData()

                pixmap = self.pixmap()
                mimedata.setImageData(pixmap.toImage())
                mimedata.setText(str(self.id))

                Drop_Frame_Objects.setMimeData(mimedata)

                pixmap_scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                Drop_Frame_Objects.setPixmap(pixmap_scaled)

                self.Drop_Frame_Objects_start_position = event.pos() - self.boundingRect().topLeft()
                Drop_Frame_Objects.setHotSpot(self.Drop_Frame_Objects_start_position.toPoint())

                Drop_Frame_Objects.exec_(Qt.CopyAction)  # Execute the Drop_Frame_Objects action
            else:
                return  # Do nothing if there are no views
                items = self.items(event.pos())
                


    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        if self.isSelected():
            pen = QPen(Qt.red, 3, Qt.DashDotLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

class Grid(QGraphicsSvgItem):
    def __init__(self, svg_file):
        super().__init__(svg_file)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

