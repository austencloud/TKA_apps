import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QFrame, QPushButton
from PyQt5.QtGui import QPixmap, QDrag, QImage, QTransform, QPainter
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QBuffer, QIODevice
from PyQt5.QtSvg import QSvgRenderer


class ImageLabel(QLabel):
    def __init__(self, pixmap, parent=None, copy_allowed=True, selectable=True):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.copy_allowed = copy_allowed
        self.selectable = selectable
        self.selected = False
        self.dragging = False
        self.drag_start_position = self.pos()
        self.setStyleSheet("background-color: transparent;")


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
        old_width = pixmap.width()
        old_height = pixmap.height()

        transform = QTransform()
        transform.translate(old_width/2, old_height/2)  # Move the rotation point to the center of the pixmap
        transform.rotate(angle)
        transform.translate(-old_width/2, -old_height/2)  # Move the rotation point back to the top-left corner

        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        new_width = rotated_pixmap.width()
        new_height = rotated_pixmap.height()

        # Adjust QLabel position to keep rotated image centered
        dx = (old_width - new_width) / 2
        dy = (old_height - new_height) / 2
        self.move(int(self.x() + dx), int(self.y() + dy))

        self.setPixmap(rotated_pixmap)
        self.setFixedSize(new_width, new_height)  # adjust the size of QLabel


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


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap())


    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimeData = QMimeData()

        image = self.pixmap().toImage()
        byteArray = QByteArray()
        buffer = QBuffer(byteArray)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, 'PNG')
        mimeData.setData('application/x-qt-image', byteArray)

        drag.setMimeData(mimeData)
        self.dragging = True
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.MoveAction)
        self.dragging = False


class DropFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: white;")

        svg_data = '''<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 65 65">
  <defs>
    <style>
      .cls-1 {
        fill: #231f20;
      }
    </style>
  </defs>
  <g id="Layer_1-2" data-name="Layer 1">
    <g>
      <path class="cls-1" d="m18.19,32.95c.58,0,.58-.9,0-.9s-.58.9,0,.9h0Z"/>
      <path class="cls-1" d="m32.5,47.26c.58,0,.58-.9,0-.9s-.58.9,0,.9h0Z"/>
      <path class="cls-1" d="m46.81,32.95c.58,0,.58-.9,0-.9s-.58.9,0,.9h0Z"/>
      <path class="cls-1" d="m32.5,18.64c.58,0,.58-.9,0-.9s-.58.9,0,.9h0Z"/>
      <circle class="cls-1" cx="32.5" cy="2.5" r="2.5"/>
      <circle class="cls-1" cx="62.5" cy="32.5" r="2.5"/>
      <circle class="cls-1" cx="32.5" cy="62.5" r="2.5"/>
      <circle class="cls-1" cx="2.5" cy="32.5" r="2.5"/>
      <circle class="cls-1" cx="46.81" cy="46.81" r=".87"/>
      <circle class="cls-1" cx="18.19" cy="46.81" r=".87"/>
      <circle class="cls-1" cx="18.19" cy="18.19" r=".87"/>
      <circle class="cls-1" cx="46.81" cy="18.19" r=".87"/>
      <circle class="cls-1" cx="32.5" cy="32.5" r="1.12"/>
    </g>
  </g>
</svg>'''  # add your SVG data here


        # Convert SVG to QPixmap
        svg_renderer = QSvgRenderer(QByteArray(svg_data.encode()))
        pixmap = QPixmap(500, 500)  # adjust the size as per your requirements
        pixmap.fill(Qt.transparent)  # make sure background is transparent
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        # Create QLabel to hold the pixmap
        self.grid_label = QLabel(self)
        self.grid_label.setPixmap(pixmap)
        self.grid_label.move(0, 0)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qt-image'):
            event.accept()

    def dropEvent(self, event):
        source = event.source()
        if isinstance(source, ImageLabel) and source.parent() == self:
            # If source is already child of this DropFrame, just move it
            pos = event.pos() - source.drag_start_position
            source.move(pos)
            source.select()  # Select the moved image
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            data = event.mimeData().data('application/x-qt-image')
            image = QImage()
            image.loadFromData(data)
            pixmap = QPixmap.fromImage(image)

            # Deselect all images in the frame
            for label in self.findChildren(ImageLabel):
                label.deselect()

            image_label = ImageLabel(pixmap, parent=self, copy_allowed=False)  # pass self as parent

            # Adjust position to align with where the mouse was clicked
            pos = event.pos() - image_label.drag_start_position
            image_label.move(pos)
            image_label.show()
            image_label.select()  # Select the new image

            event.setDropAction(Qt.CopyAction)
            event.accept()

    def resizeEvent(self, event):
        # Center the grid_label in the DropFrame
        self.grid_label.move((self.width() - self.grid_label.width()) // 2, (self.height() - self.grid_label.height()) // 2)

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
