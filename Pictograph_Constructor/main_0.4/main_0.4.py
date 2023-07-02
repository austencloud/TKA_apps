import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt
from sidebar import Objects_From_Sidebar
from drop_frame import Drop_Frame, Grid


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1400, 1000)  

        hbox = QHBoxLayout()
        svg_dir = 'images\\svgs'
        svgs = [os.path.join(svg_dir, svg) for svg in os.listdir(svg_dir) if svg.endswith('.svg')]

        scroll_area = QScrollArea(self)  
        scroll_widget = QWidget(self)
        scroll_layout = QVBoxLayout()

        # Create a QGraphicsScene
        scene = QGraphicsScene()

        for i, svg in enumerate(svgs):
            # Create a DraggableSvg instance
            svg_item = Objects_From_Sidebar(svg)
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

        # Create a Grid instance
        grid_svg = 'images\\svgs\\grid\\grid.svg'
        grid_item = Grid(grid_svg)
        grid_item.setZValue(1)
        grid_item.setScale(8.0)
        self.scene.addItem(grid_item)

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


app = QApplication(sys.argv)
ex = MainApp()
ex.setFocus()  
sys.exit(app.exec_())
