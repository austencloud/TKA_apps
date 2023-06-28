import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QPushButton, QGraphicsItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QBuffer, QIODevice, QPointF, QPoint




class DraggablePixmapItem(QGraphicsPixmapItem):
    id_counter = 0

    def __init__(self, pixmap: QPixmap):
        super().__init__(pixmap)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.id = DraggablePixmapItem.id_counter
        DraggablePixmapItem.id_counter += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_offset = event.pos()
            drag = QDrag(event.widget())
            mimedata = QMimeData()

            pixmap = self.pixmap()
            mimedata.setImageData(pixmap.toImage())
            mimedata.setText(str(self.id))  # Add the id to the mime data

            drag.setMimeData(mimedata)
            pixmap_scaled = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            drag.setPixmap(pixmap_scaled)

            scale_x = pixmap_scaled.width() / pixmap.width()
            scale_y = pixmap_scaled.height() / pixmap.height()

            drag.setHotSpot(QPoint(int(self.drag_start_offset.x() * scale_x), int(self.drag_start_offset.y() * scale_y)))  # Adjust hotspot for scaled pixmap

            drag.exec_(Qt.CopyAction)
        super().mousePressEvent(event)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor(255, 255, 255))  # This sets the background to white.

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasImage():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            image = QImage(event.mimeData().imageData())
            pixmap = QPixmap.fromImage(image)

            id_text = event.mimeData().text()  # Get the id from the mime data
            if id_text:
                # If there's an id, find the item in the scene and move it
                item_id = int(id_text)
                for item in self.scene().items():
                    if isinstance(item, DraggablePixmapItem) and item.id == item_id:
                        pos = self.mapToScene(event.pos()) - item.drag_start_offset  # Adjust for the offset
                        item.setPos(pos)
                        break
            else:
                # If there's no id, this is a new item, so add it to the scene
                item = DraggablePixmapItem(pixmap)
                item.drag_start_offset = QPointF(pixmap.width() / 2, pixmap.height() / 2)  # Center of the pixmap
                pos = self.mapToScene(event.pos()) - item.drag_start_offset  # Adjust for the offset
                item.setPos(pos)
                self.scene().addItem(item)
        else:
            event.ignore()



class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1400, 1000)  

        hbox = QHBoxLayout()

        image_dir = 'D:\\CODE\\TKA_Apps\\Pictograph_Constructor\\images\\arrows\\base'
        images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]

        scroll_area = QScrollArea(self)  
        scroll_widget = QWidget(self)
        scroll_layout = QVBoxLayout()

        for image in images:
            lbl = DraggableLabel()
            lbl.setPixmap(QPixmap(image).scaled(200, 200, Qt.KeepAspectRatio))  # Changed scale to 200, 200
            lbl.show()
            lbl.setParent(scroll_widget)
            scroll_layout.addWidget(lbl)


        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        hbox.addWidget(scroll_area)

        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene)

        # in your Example.initUI() method, after initializing self.scene
        grid_pixmap = QPixmap('D:\\CODE\\TKA_Apps\\Pictograph_Constructor\\images\\grids\\grid.png')
        grid_item = QGraphicsPixmapItem(grid_pixmap)
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

        self.exportButton = QPushButton("Export to PNG")
        self.exportButton.clicked.connect(self.exportToPng)
        vbox.addWidget(self.exportButton)

        hbox.addLayout(vbox)

        self.setLayout(hbox)
        self.setWindowTitle('Drag & Drop')
        self.show()

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


class DraggableLabel(QLabel):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mimedata = QMimeData()

            pixmap = self.pixmap()
            mimedata.setImageData(pixmap.toImage())

            drag.setMimeData(mimedata)  # Set mimedata before setting pixmap

            pixmap_scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Changed scale to 200, 200
            drag.setPixmap(pixmap_scaled)

            drag.setHotSpot(QPoint(pixmap_scaled.width() // 2, pixmap_scaled.height() // 2))  # Hotspot set to center

            drag.exec_(Qt.CopyAction)



app = QApplication(sys.argv)
ex = Example()
ex.setFocus()  
sys.exit(app.exec_())
