import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QGraphicsEllipseItem, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform
from arrows import Arrow_Logic
from artboard import Artboard, Grid
from buttonhandlers import Button_Handlers



class Main_Window(QWidget):
    ARROW_DIR = 'images\\arrows'
    SVG_SCALE = 9.0
    SVG_POS_Y_INCREMENT = 200

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1800, 1400)  
        hbox = QHBoxLayout()

        arrow_box = self.initArrowBox()
        hbox.addWidget(arrow_box)

        self.view = self.initArtboard()
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

        svgs = [os.path.join(self.ARROW_DIR, svg) for svg in os.listdir(self.ARROW_DIR) if svg.endswith('.svg')]

        for i, svg in enumerate(svgs):
            # Create a DraggableSvg instance
            svg_item = Arrow_Logic(svg)
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
    
    def initArtboard(self):
        self.grid = Grid('images\\grid\\grid.svg')
        view = Artboard(self.artboard, self.grid)

        # Set the size of the artboard to a fixed amount
        view.setFixedSize(1000, 1000)

        # Calculate the center of the frame
        frame_center = QPointF(view.frameSize().width() / 2, view.frameSize().height() / 2)

        # Show a blue dot at the frame center
        center = QGraphicsEllipseItem(QRectF(frame_center.x(), frame_center.y(), 20, 20))
        center.setBrush(QBrush(QColor(0, 0, 255)))
        self.artboard.addItem(center)

        # Add the grid to the artboard
        self.artboard.addItem(self.grid)

        # Create a transformation matrix that translates the grid to the center of the frame and then scales it by a factor of 8
        transform = QTransform()
        transform.translate(frame_center.x() - 250, frame_center.y() - 250)

        # Apply the transformation matrix to the grid
        self.grid.setTransform(transform)

        # store the resulting grid location in a variable
        grid_location = self.grid.mapToScene(0, 0)
        print("grid location: ", grid_location)

        return view


    def initButtons(self, layout):
            handlers = Button_Handlers(self.artboard, self.view, self.grid, self.artboard)

            self.deleteButton = QPushButton("Delete Selected")
            self.deleteButton.clicked.connect(handlers.deleteArrow)
            layout.addWidget(self.deleteButton)

            self.rotateRightButton = QPushButton("Rotate Right")
            self.rotateRightButton.clicked.connect(lambda: handlers.rotateArrow(90)) # 90 degrees clockwise
            layout.addWidget(self.rotateRightButton)

            self.rotateLeftButton = QPushButton("Rotate Left")
            self.rotateLeftButton.clicked.connect(lambda: handlers.rotateArrow(-90)) # 90 degrees counterclockwise
            layout.addWidget(self.rotateLeftButton)

            self.mirrorHorizontallyButton = QPushButton("Mirror Horizontally")
            self.mirrorHorizontallyButton.clicked.connect(lambda: handlers.mirrorArrow(True)) # Mirror horizontally
            layout.addWidget(self.mirrorHorizontallyButton)

            self.mirrorVerticallyButton = QPushButton("Mirror Vertically")
            self.mirrorVerticallyButton.clicked.connect(lambda: handlers.mirrorArrow(False)) # Mirror vertically
            layout.addWidget(self.mirrorVerticallyButton)

            self.exportButton = QPushButton("Export to PNG")
            self.exportButton.clicked.connect(handlers.exportArtboard)
            layout.addWidget(self.exportButton)


app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

