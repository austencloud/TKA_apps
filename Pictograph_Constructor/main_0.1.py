import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QGraphicsScene, QFrame, QPushButton, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QDrag, QImage, QTransform
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QBuffer, QIODevice

class ImageLabel(QLabel):
    def __init__(self, pixmap, copy_allowed=True, selectable=True):
        super().__init__()
        self.setPixmap(pixmap)  
        self.copy_allowed = copy_allowed
        self.selectable = selectable
        self.selected = False

    def select(self):
        if self.selectable:  
            self.selected = True
            self.setStyleSheet("border: 2px solid blue;")

    def deselect(self):
        if self.selectable: 
            self.selected = False
            self.setStyleSheet("")

    def rotate(self, angle):
        pixmap = self.pixmap()
        transform = QTransform()
        transform.translate(pixmap.width()/2, pixmap.height()/2)  # Move the rotation point to the center of the pixmap
        transform.rotate(angle)
        transform.translate(-pixmap.width()/2, -pixmap.height()/2)  # Move the rotation point back to the top-left corner
        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.setPixmap(rotated_pixmap)
        self.setFixedSize(rotated_pixmap.size())  # adjust the size of QLabel


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            parent = self.parent()
            while parent is not None and not isinstance(parent, DropFrame):
                parent = parent.parent()
            if parent is not None:  
                for label in parent.findChildren(QLabel):
                    if isinstance(label, ImageLabel):
                        label.deselect()
            self.select()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimeData = QMimeData()

        image = self.pixmap().toImage()
        bytearray = QByteArray()
        buffer = QBuffer(bytearray)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, 'PNG')
        mimeData.setData('application/x-qt-image', bytearray)

        drag.setMimeData(mimeData)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(event.pos())
        
        if self.copy_allowed:
            drag.exec_(Qt.CopyAction | Qt.MoveAction)
        else:
            drag.exec_(Qt.MoveAction)
            self.close()  

class DropFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: white;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qt-image'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-qt-image'):
            for label in self.findChildren(QLabel):
                if isinstance(label, ImageLabel):
                    label.deselect()

            data = event.mimeData().data('application/x-qt-image')
            image = QImage.fromData(data)
            pixmap = QPixmap.fromImage(image)
            new_label = ImageLabel(pixmap, copy_allowed=False, selectable=True)
            position = event.pos() - event.source().drag_start_position
            new_label.move(position)
            new_label.setParent(self)  
            new_label.show()  
            new_label.select()  
            event.acceptProposedAction()
    

    
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
            lbl = ImageLabel(QPixmap(image), copy_allowed=True, selectable=False)
            lbl.show()
            lbl.setParent(scroll_widget)
            scroll_layout.addWidget(lbl)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        hbox.addWidget(scroll_area)

        right_layout = QVBoxLayout()
        right_view = DropFrame()
        right_view.setFrameShape(QFrame.StyledPanel)  
        right_view.setMinimumSize(800, 800)  
        right_layout.addWidget(right_view)

        self.setLayout(hbox)
        self.setWindowTitle('Drag & Drop')
        self.show()

        self.deleteButton = QPushButton("Delete Selected")
        self.deleteButton.clicked.connect(self.deleteSelected)
        right_layout.addWidget(self.deleteButton)

        self.rotateRightButton = QPushButton("Rotate Right")
        self.rotateRightButton.clicked.connect(lambda: self.rotateSelected(90)) # 90 degrees clockwise
        right_layout.addWidget(self.rotateRightButton)

        self.rotateLeftButton = QPushButton("Rotate Left")
        self.rotateLeftButton.clicked.connect(lambda: self.rotateSelected(-90)) # 90 degrees counterclockwise
        right_layout.addWidget(self.rotateLeftButton)

        hbox.addLayout(right_layout)

    def deleteSelected(self):
        for label in self.findChildren(QLabel):
            if isinstance(label, ImageLabel) and label.selected:
                label.deleteLater()

    def rotateSelected(self, angle):
        for label in self.findChildren(QLabel):
            if isinstance(label, ImageLabel) and label.selected:
                label.rotate(angle)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()

app = QApplication(sys.argv)
ex = Example()
ex.setFocus()  
sys.exit(app.exec_())
