import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem
from PyQt5.QtCore import QRectF
from arrows import Objects_From_Sidebar
from artboard import Artboard, Grid
from buttonhandlers import Button_Handlers

class Main_Window(QWidget):
    SVG_DIR = 'images\\arrows'
    SVG_SCALE = 8.0
    SVG_POS_Y_INCREMENT = 200

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1800, 1400)  
        hbox = QHBoxLayout()

        arrow_box = self.initArrowBox()
        hbox.addWidget(arrow_box)

        self.view = self.init_artboard()
        vbox = QVBoxLayout()
        vbox.addWidget(self.view)

        self.initButtons(vbox)

        hbox.addLayout(vbox)

        self.setLayout(hbox)
        self.setWindowTitle('Drag & Drop')
        self.show()

    def initArrowBox(self):
        arrow_box = QScrollArea(self)  
        scroll_widget = QWidget(self)
        scroll_layout = QVBoxLayout()

        # Create a QGraphicsScene
        self.artboard = QGraphicsScene()
        # Create a new QGraphicsScene for the QGraphicsView in the scroll area
        scroll_scene = QGraphicsScene()

        svgs = [os.path.join(self.SVG_DIR, svg) for svg in os.listdir(self.SVG_DIR) if svg.endswith('.svg')]

        for i, svg in enumerate(svgs):
            # Create a DraggableSvg instance
            svg_item = Objects_From_Sidebar(svg)
            svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            # Scale the SVG item
            svg_item.setScale(self.SVG_SCALE)
            # Position the SVG item
            svg_item.setPos(0, i * self.SVG_POS_Y_INCREMENT)
            # Add the arrows to the scroll_scene instead of self.artboard
            scroll_scene.addItem(svg_item)

        # Use scroll_scene for the QGraphicsView in the scroll area
        view = QGraphicsView(scroll_scene)

        # Add the QGraphicsView to the layout
        scroll_layout.addWidget(view)

        scroll_widget.setLayout(scroll_layout)
        arrow_box.setWidget(scroll_widget)
        arrow_box.setWidgetResizable(True)

        return arrow_box

    def init_artboard(self):
        self.grid = Grid('images\\grid\\grid.svg')
        self.artboard.addItem(self.grid)
        view = Artboard(self.artboard)
        view.setSceneRect(QRectF(0, 0, view.width(), view.height()))
        return view

    def initButtons(self, layout):
        handlers = Button_Handlers(self.artboard)

        self.deleteButton = QPushButton("Delete Selected")
        self.deleteButton.clicked.connect(handlers.deleteSelected)
        layout.addWidget(self.deleteButton)

        self.rotateRightButton = QPushButton("Rotate Right")
        self.rotateRightButton.clicked.connect(lambda: handlers.rotateSelected(90)) # 90 degrees clockwise
        layout.addWidget(self.rotateRightButton)

        self.rotateLeftButton = QPushButton("Rotate Left")
        self.rotateLeftButton.clicked.connect(lambda: handlers.rotateSelected(-90)) # 90 degrees counterclockwise
        layout.addWidget(self.rotateLeftButton)

        self.mirrorHorizontallyButton = QPushButton("Mirror Horizontally")
        self.mirrorHorizontallyButton.clicked.connect(lambda: handlers.mirrorSelected(True)) # Mirror horizontally
        layout.addWidget(self.mirrorHorizontallyButton)

        self.mirrorVerticallyButton = QPushButton("Mirror Vertically")
        self.mirrorVerticallyButton.clicked.connect(lambda: handlers.mirrorSelected(False)) # Mirror vertically
        layout.addWidget(self.mirrorVerticallyButton)

        self.exportButton = QPushButton("Export to PNG")
        self.exportButton.clicked.connect(handlers.exportToPng)
        layout.addWidget(self.exportButton)


app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())
