import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QGraphicsEllipseItem, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QBrush, QColor, QTransform, QFont
from arrows import Arrow_Logic
from artboardEvents import Artboard_Events
from buttonHandlers import Button_Handlers
from grid import Grid


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
        arrowbox = QGraphicsScene()

        # Get the full paths
        svgs_full_paths = []
        for dirpath, dirnames, filenames in os.walk(self.ARROW_DIR):
            svgs_full_paths.extend([os.path.join(dirpath, filename) for filename in filenames if filename.endswith('.svg')])

        # Get just the filenames
        svgs_filenames = [os.path.basename(svg) for svg in svgs_full_paths]

        # List of default arrow names
        default_arrows = ['red_anti_r_ne.svg', 'red_iso_r_ne.svg', 'blue_anti_r_sw.svg', 'blue_iso_r_sw.svg']

        # Counter for the number of SVG items added
        svg_item_count = 0

        for i, svg in enumerate(svgs_full_paths):
            file_name = os.path.basename(svg)
            if file_name in default_arrows:
                svg_item = Arrow_Logic(svg, arrowbox)
                svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                svg_item.setScale(self.SVG_SCALE)
                svg_item.setPos(0, svg_item_count * self.SVG_POS_Y)
                arrowbox.addItem(svg_item)
                svg_item_count += 1

        # Use arrowbox for the QGraphicsView in the scroll area
        view = QGraphicsView(arrowbox)

        # Add the QGraphicsView to the layout
        scroll_layout.addWidget(view)

        scroll_widget.setLayout(scroll_layout)
        arrow_box.setWidget(scroll_widget)
        arrow_box.setWidgetResizable(True)

        return arrow_box

    def initArtboard(self):
        self.grid = Grid('images\\grid\\grid.svg')
        view = Artboard_Events(self.artboard, self.grid)

        # Set the size of the artboard to a fixed amount
        view.setFixedSize(600, 600)

        # Calculate the center of the frame
        frame_center = QPointF(view.frameSize().width() / 2, view.frameSize().height() / 2)

        # Show a blue dot at the frame center
        # center = QGraphicsEllipseItem(QRectF(frame_center.x() - 10, frame_center.y() - 10, 20, 20))
        # center.setBrush(QBrush(QColor(0, 0, 255)))
        # self.artboard.addItem(center)
        # center.setZValue(1)

        # disable the scrollbars
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add the grid to the artboard
        self.artboard.addItem(self.grid)

        # Create a transformation matrix that translates the grid to the center of the frame and then scales it by a factor of 8
        transform = QTransform()
        transform.translate(frame_center.x() - 260, frame_center.y() - 260)

        # Apply the transformation matrix to the grid
        self.grid.setTransform(transform)

        # Add lines to demarcate the quadrants
        line_v = QGraphicsLineItem(view.frameSize().width() / 2, 0, view.frameSize().width() / 2, view.frameSize().height())
        line_h = QGraphicsLineItem(0, view.frameSize().height() / 2, view.frameSize().width(), view.frameSize().height() / 2)
        self.artboard.addItem(line_v)
        self.artboard.addItem(line_h)

        return view


    def initButtons(self, layout):
        masterbtnlayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        buttonstack1 = QVBoxLayout()
        buttonstack2 = QVBoxLayout()

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

        self.rotateRightButton = QPushButton("Rotate Right")
        self.rotateRightButton.clicked.connect(lambda: handlers.rotateArrow(90)) # 90 degrees clockwise
        buttonstack1.addWidget(self.rotateRightButton)

        self.rotateLeftButton = QPushButton("Rotate Left")
        self.rotateLeftButton.clicked.connect(lambda: handlers.rotateArrow(-90)) # 90 degrees counterclockwise
        buttonstack1.addWidget(self.rotateLeftButton)

        self.mirrorButton = QPushButton("Mirror")
        self.mirrorButton.clicked.connect(lambda: handlers.mirrorArrow()) # Mirror horizontally
        buttonstack2.addWidget(self.mirrorButton)

        self.bringForward = QPushButton("Bring Forward")
        self.bringForward.clicked.connect(handlers.bringForward)
        buttonstack2.addWidget(self.bringForward)

        self.exportButton = QPushButton("Export to PNG")
        self.exportButton.clicked.connect(handlers.exportArtboard)
        masterbtnlayout.addWidget(self.exportButton)

        self.deleteButton.setFont(QFont('Helvetica', 14))
        self.rotateRightButton.setFont(QFont('Helvetica', 14))
        self.rotateLeftButton.setFont(QFont('Helvetica', 14))
        self.mirrorButton.setFont(QFont('Helvetica', 14))
        self.bringForward.setFont(QFont('Helvetica', 14))
        self.exportButton.setFont(QFont('Helvetica', 14))

app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

