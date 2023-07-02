import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QMimeData, QPointF, QThread, pyqtSignal, QTimer, QByteArray
from PyQt5.QtSvg import QSvgRenderer, QSvgWidget, QGraphicsSvgItem

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1400, 1000)  

        hbox = QHBoxLayout()
        svg_dir = 'D:\\CODE\\TKA_Apps\\Pictograph_Constructor\\images\\svgs'
        svgs = [os.path.join(svg_dir, svg) for svg in os.listdir(svg_dir) if svg.endswith('.svg')]

        scroll_area = QScrollArea(self)  
        scroll_widget = QWidget(self)
        scroll_layout = QVBoxLayout()

        # Create a QGraphicsScene
        scene = QGraphicsScene()

        for i, svg in enumerate(svgs):
            # Create a DraggableSvg instance
            svg_item = DraggableSvg(svg)
            svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)

            # Scale the SVG item
            svg_item.setScale(8.0)  # Adjust this value as needed

            # Position the SVG item
            svg_item.setPos(0, i * 200)  # Adjust the y-coordinate as needed

            # Add the DraggableSvg instance to the scene
            scene.addItem(svg_item)

        # Create a QGraphicsView to display the scene
        view = QGraphicsView(scene)

        # Add the QGraphicsView to the layout
        scroll_layout.addWidget(view)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        hbox.addWidget(scroll_area)

        self.scene = QGraphicsScene()
        self.view = DropFrame(self.scene)

        # in your Example.initUI() method, after initializing self.scene
        grid_svg = 'D:\\\\CODE\\\\TKA_Apps\\\\Pictograph_Constructor\\\\images\\\\svgs\\\\grid\\\\grid.svg'
        grid_item = DraggableSvg(grid_svg)
        grid_item.setZValue(1)
        grid_item.setScale(8.0)
        self.scene.addItem(grid_item)


        vbox = QVBoxLayout()
        vbox.addWidget(self.view)

        self.deleteButton = QPushButton("Delete Selected")
        self.deleteButton.clicked.connect(self.deleteSelected)
        vbox.addWidget(self.deleteButton)

        self.rotateRightButton = QPushButton("Rotate Right")
        self.rotateRightButton.clicked.connect(lambda: self.rotateSelected(90)) # 90 degrees clockwise
        vbox.addWidget(self.rotateRightButton)

        self.rotateLeftButton = QPushButton("Rotate Left")
        self.rotateLeftButton.clicked.connect(lambda: self.rotateSelected(-90)) # 90 degrees counterclockwise
        vbox.addWidget(self.rotateLeftButton)

        self.mirrorHorizontallyButton = QPushButton("Mirror Horizontally")
        self.mirrorHorizontallyButton.clicked.connect(lambda: self.mirrorSelected(True)) # Mirror horizontally
        vbox.addWidget(self.mirrorHorizontallyButton)

        self.mirrorVerticallyButton = QPushButton("Mirror Vertically")
        self.mirrorVerticallyButton.clicked.connect(lambda: self.mirrorSelected(False)) # Mirror vertically
        vbox.addWidget(self.mirrorVerticallyButton)

        self.exportButton = QPushButton("Export to PNG")
        self.exportButton.clicked.connect(self.exportToPng)
        vbox.addWidget(self.exportButton)

        hbox.addLayout(vbox)

        self.setLayout(hbox)
        self.setWindowTitle('Drag & Drop')
        self.show()

    def rotateSelected(self, angle):
        for item in self.scene.selectedItems():
            # Compute the rotation center point
            center = item.boundingRect().center()
            # Adjust the transformation origin to the center
            item.setTransformOriginPoint(center)
            item.setRotation(item.rotation() + angle)

    def mirrorSelected(self, horizontal=True):
        for item in self.scene.selectedItems():
            if horizontal:
                item.setScale(-item.scale() if item.scale() < 0 else -1)  # Flip horizontally
            else:
                # Flip vertically by applying a vertical flip matrix
                item.setTransform(item.transform().scale(1, -1))

    def deleteSelected(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def rotateSelected(self, angle):
        for item in self.scene.selectedItems():
            item.setRotation(item.rotation() + angle)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()

    def exportToPng(self):
        # Create a QImage with the same dimensions as the QGraphicsView
        image = QImage(self.view.size(), QImage.Format_ARGB32)

        # Create a QPainter and draw the QGraphicsView's scene into the QImage
        painter = QPainter(image)
        self.view.render(painter)
        painter.end()

        # Save the QImage to a file
        image.save("export.png")

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

class DropFrame(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)

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
            svg_item = DraggableSvg(svg_file)
            svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)

            # Add the new DraggableSvg item to the scene at the drop location
            self.scene().addItem(svg_item)
            svg_item.setPos(self.mapToScene(event.pos()))
        else:
            event.ignore()


    def mousePressEvent(self, event):
        # find the item that we clicked
        items = self.items(event.pos())
        if items:
            # if we clicked on an item, select it
            item = items[0]
            item.setSelected(True)
        else:
            # if we didn't click on an item, clear the selection
            for item in self.scene().selectedItems():
                item.setSelected(False)




app = QApplication(sys.argv)
ex = MainApp()
ex.setFocus()  
sys.exit(app.exec_())
