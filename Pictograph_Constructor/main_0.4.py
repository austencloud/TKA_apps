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

        for svg in svgs:
            svg_widget = QSvgWidget(svg)
            svg_widget.setFixedSize(200, 200)  # Set a fixed size for the SVG widget
            scroll_layout.addWidget(svg_widget)

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
    def __init__(self, svg_path: str):
        super().__init__(svg_path)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return
        if not (event.pos() - self.drag_start_position).manhattanLength() > QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.elementId())
        drag.setMimeData(mimedata)
        pixmap = QPixmap(self.boundingRect().size().toSize())
        self.render(QPainter(pixmap))
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos().toPoint())
        drag.exec_()

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
        self.setDragMode(QGraphicsView.NoDrag)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            svg_id = event.mimeData().text()
            for item in self.scene().items():
                if isinstance(item, DraggableSvg) and item.elementId() == svg_id:
                    item.setPos(self.mapToScene(event.pos()))
                    break


            id_text = event.mimeData().text()
            if ',' in id_text:  # NewArrow
                svg_path = event.mimeData().data('application/x-qabstractitemmodeldatalist').data().decode()
                item = Drag(svg_path)
                if item.drag_start_position is None:
                    item.drag_start_position = QPointF(0, 0)
                pos = self.mapToScene(event.pos()) - item.drag_start_position
                item.setPos(pos)
                self.scene().addItem(item)
            if id_text.isdigit():  # Drag
                item_id = int(id_text)
                for item in self.scene().items():
                    if isinstance(item, Drag) and item.id == item_id:
                        pos = self.mapToScene(event.pos()) - item.drag_start_position
                        item.setPos(pos)  # Move the existing item
                        item.setVisible(True)  # unhide original item
                        break
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
