import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem
from PyQt5.QtGui import QImage, QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from sidebar import Objects_From_Sidebar
from drop_frame import Drop_Frame
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QBrush, QColor

class Make_Circle(QGraphicsEllipseItem):
    def __init__(self, center, radius, parent=None):
        super().__init__(parent)
        self.setRect(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

        # Set the brush to solid black
        self.setBrush(QBrush(QColor(0, 0, 0)))

        # Set the pen to no pen (i.e., no stroke)
        self.setPen(QPen(Qt.NoPen))


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1800, 1400)  

        hbox = QHBoxLayout()
        svg_dir = 'images\\arrows'
        svgs = [os.path.join(svg_dir, svg) for svg in os.listdir(svg_dir) if svg.endswith('.svg')]

        scroll_area = QScrollArea(self)  
        scroll_widget = QWidget(self)
        scroll_layout = QVBoxLayout()

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        # Create a new QGraphicsScene for the QGraphicsView in the scroll area
        scroll_scene = QGraphicsScene()
        # Parse the SVG file
        tree = ET.parse('images\\grid\\grid.svg')
        root = tree.getroot()

        # Define the SVG namespace
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}

        # Find all circle elements in the SVG file
        circles = root.findall('.//svg:circle', namespaces)

        # Create a CircleItem for each circle and add it to the scene
        for circle in circles:
            # Get the center and radius of the circle
            center = QPointF(float(circle.get('cx')), float(circle.get('cy')))
            radius = float(circle.get('r'))

            item = Make_Circle(center, radius)
            item.setScale(8.0)  
            item.setZValue(-1)
            self.scene.addItem(item)

        # Create a pen and brush
        pen = QPen(QColor(0, 0, 0))  # Black pen
        brush = QBrush(QColor(255, 0, 0))  # Red brush

        # Create a CircleItem
        item = Make_Circle(center, radius)

        # Set the item's pen and brush
        item.setPen(pen)
        item.setBrush(brush)

        # Add the item to the scene
        self.scene.addItem(item)

        for i, svg in enumerate(svgs):
            # Create a DraggableSvg instance
            svg_item = Objects_From_Sidebar(svg)
            svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            # Scale the SVG item
            svg_item.setScale(8.0)  # Adjust this value as needed
            # Position the SVG item
            svg_item.setPos(0, i * 200)  # Adjust the y-coordinate as needed
            # Add the arrows to the scroll_scene instead of self.scene
            scroll_scene.addItem(svg_item)

        # Use scroll_scene for the QGraphicsView in the scroll area
        view = QGraphicsView(scroll_scene)

        # Add the QGraphicsView to the layout
        scroll_layout.addWidget(view)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        hbox.addWidget(scroll_area)

        self.view = Drop_Frame(self.scene)

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
                # Flip horizontally by applying a horizontal flip matrix
                item.setTransform(item.transform().scale(-1, 1))
            else:
                # Flip vertically by applying a vertical flip matrix
                item.setTransform(item.transform().scale(1, -1))

    def deleteSelected(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

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

app = QApplication(sys.argv)
ex = MainApp()
ex.setFocus()  
sys.exit(app.exec_())
