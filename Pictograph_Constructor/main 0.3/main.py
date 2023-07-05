import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QGraphicsEllipseItem, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPen, QBrush, QColor, QTransform, QFont
from arrows import Arrow_Logic
from artboard import Artboard, Grid
from buttonhandlers import Button_Handlers



class Main_Window(QWidget):
    ARROW_DIR = 'images\\arrows'
    SVG_SCALE = 9.0
    SVG_POS_Y = 225

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

        # Get the full paths
        svgs_full_paths = []
        for dirpath, dirnames, filenames in os.walk(self.ARROW_DIR):
            svgs_full_paths.extend([os.path.join(dirpath, filename) for filename in filenames if filename.endswith('.svg')])

        # Get just the filenames
        svgs_filenames = [os.path.basename(svg) for svg in svgs_full_paths]

        # List of default arrow names
        default_arrows = ['red_anti_r_ne.svg', 'red_iso_r_ne.svg', 'blue_anti_r_sw.svg', 'blue_iso_r_sw.svg']

        # print if the default_arrows were found in the arrow_dir
        print('Default arrows found: {}'.format([arrow for arrow in default_arrows if arrow in svgs_filenames]))

        # Counter for the number of SVG items added
        svg_item_count = 0

        for i, svg in enumerate(svgs_full_paths):
            # Extract the file name from the path
            file_name = os.path.basename(svg)
            # Only add the default arrows
            if file_name in default_arrows:
                # Create a DraggableSvg instance
                svg_item = Arrow_Logic(svg)
                svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                # Scale the SVG item
                svg_item.setScale(self.SVG_SCALE)
                # Position the SVG item using the svg_item_count instead of i
                svg_item.setPos(0, svg_item_count * self.SVG_POS_Y)
                # Add the arrows to the scroll_scene instead of self.artboard
                scroll_scene.addItem(svg_item)
                # Increment the counter
                svg_item_count += 1

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
        view.setFixedSize(1200, 1200)

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
       


        masterbtnlayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        buttonstack1 = QVBoxLayout()
        buttonstack2 = QVBoxLayout()

        #make the buttonstack1 and buttonstack2 hug the top of their frame
        buttonstack1.setAlignment(Qt.AlignTop)
        buttonstack2.setAlignment(Qt.AlignTop)
        masterbtnlayout.setAlignment(Qt.AlignTop)

        buttonlayout.addLayout(buttonstack1)
        buttonlayout.addLayout(buttonstack2)

        masterbtnlayout.addLayout(buttonlayout)
        layout.addLayout(masterbtnlayout)

        handlers = Button_Handlers(self.artboard, self.view, self.grid, self.artboard)

        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(handlers.deleteArrow)
        buttonstack1.addWidget(self.deleteButton)
        #set the button font


        self.rotateRightButton = QPushButton("Rotate Right")
        self.rotateRightButton.clicked.connect(lambda: handlers.rotateArrow(90)) # 90 degrees clockwise
        buttonstack1.addWidget(self.rotateRightButton)

        self.rotateLeftButton = QPushButton("Rotate Left")
        self.rotateLeftButton.clicked.connect(lambda: handlers.rotateArrow(-90)) # 90 degrees counterclockwise
        buttonstack1.addWidget(self.rotateLeftButton)

        self.mirrorHorizontallyButton = QPushButton("Mirror Horizontally")
        self.mirrorHorizontallyButton.clicked.connect(lambda: handlers.mirrorArrow(True)) # Mirror horizontally
        buttonstack2.addWidget(self.mirrorHorizontallyButton)

        self.mirrorVerticallyButton = QPushButton("Mirror Vertically")
        self.mirrorVerticallyButton.clicked.connect(lambda: handlers.mirrorArrow(False)) # Mirror vertically
        buttonstack2.addWidget(self.mirrorVerticallyButton)

        self.bringForward = QPushButton("Bring Forward")
        self.bringForward.clicked.connect(handlers.bringForward)
        buttonstack2.addWidget(self.bringForward)

        self.exportButton = QPushButton("Export to PNG")
        self.exportButton.clicked.connect(handlers.exportArtboard)
        masterbtnlayout.addWidget(self.exportButton)

        self.deleteButton.setFont(QFont('Helvetica', 14))
        self.rotateRightButton.setFont(QFont('Helvetica', 14))
        self.rotateLeftButton.setFont(QFont('Helvetica', 14))
        self.mirrorHorizontallyButton.setFont(QFont('Helvetica', 14))
        self.mirrorVerticallyButton.setFont(QFont('Helvetica', 14))
        self.bringForward.setFont(QFont('Helvetica', 14))
        self.exportButton.setFont(QFont('Helvetica', 14))

app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

