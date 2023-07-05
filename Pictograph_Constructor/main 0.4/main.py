import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem, QGraphicsLineItem, QLabel, QFileDialog
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QTransform, QFont
from PyQt5.QtSvg import QSvgWidget
from arrows import Arrow_Logic
from artboardEvents import Artboard_Events, updateInfoTracker
from buttonHandlers import Button_Handlers
from grid import Grid
from PyQt5.QtWidgets import QFileDialog
import xml.etree.ElementTree as ET

class Main_Window(QWidget):
    ARROW_DIR = 'images\\arrows'
    SVG_SCALE = 10.0
    SVG_POS_Y = 250

    def __init__(self):
        super().__init__() 
        self.initUI()

    def loadSvg(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG files (*.svg)")
        if fileName:
            self.svgWidget.load(fileName)

    def initUI(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.artboard = QGraphicsScene()
        self.setGeometry(300, 300, 1800, 1400)  
        self.view = self.initArtboard()
        arrowbox = self.initArrowBox()
        vbox.addWidget(self.view)
        hbox.addWidget(arrowbox)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.setWindowTitle('Drag & Drop')
        self.show()
        self.initButtons(vbox)

    def initArrowBox(self):
        arrow_box = QScrollArea(self)
        scroll_widget = QWidget(self)
        scroll_layout = QVBoxLayout()
        arrowbox_scene = QGraphicsScene()  # Use a separate scene for the arrow box
        svgs_full_paths = []
        default_arrows = ['red_anti_r_ne.svg', 'red_iso_r_ne.svg', 'blue_anti_r_sw.svg', 'blue_iso_r_sw.svg']
        svg_item_count = 0

        for dirpath, dirnames, filenames in os.walk(self.ARROW_DIR):
            svgs_full_paths.extend([os.path.join(dirpath, filename) for filename in filenames if filename.endswith('.svg')])

        for i, svg in enumerate(svgs_full_paths):
            file_name = os.path.basename(svg)
            if file_name in default_arrows:
                svg_item = Arrow_Logic(svg, self.view)  # pass the QGraphicsView object here
                svg_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                svg_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                svg_item.setScale(self.SVG_SCALE)
                svg_item.setPos(0, svg_item_count * self.SVG_POS_Y)
                arrowbox_scene.addItem(svg_item)  # use arrowbox_scene here
                svg_item_count += 1

        view = QGraphicsView(arrowbox_scene)  # use arrowbox_scene here
        scroll_layout.addWidget(view)
        scroll_widget.setLayout(scroll_layout)
        arrow_box.setWidget(scroll_widget)
        arrow_box.setWidgetResizable(True)
        # set a fixed height and width
        arrow_box.setFixedWidth(800)
        arrow_box.setFixedHeight(1600)

        return arrow_box

    def initArtboard(self):
        #set grid_size to the height of the scaled svg by looking at the svg itself
        grid_size = 650
        
        self.grid = Grid('images\\grid\\grid.svg')
        artboard_view = Artboard_Events(self.artboard, self.grid)
        artboard_view.setFixedSize(700, 700)

        transform = QTransform()
        self.grid_center = QPointF(artboard_view.frameSize().width() / 2, artboard_view.frameSize().height() / 2)

        transform.translate(self.grid_center.x() - (grid_size / 2), self.grid_center.y() - (grid_size / 2))
        self.grid.setTransform(transform)

        line_v = QGraphicsLineItem(artboard_view.frameSize().width() / 2, 0, artboard_view.frameSize().width() / 2, artboard_view.frameSize().height())
        line_h = QGraphicsLineItem(0, artboard_view.frameSize().height() / 2, artboard_view.frameSize().width(), artboard_view.frameSize().height() / 2)

        artboard_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        artboard_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.artboard.addItem(self.grid)
        # self.artboard.addItem(line_v)
        # self.artboard.addItem(line_h)

        return artboard_view

    def initButtons(self, layout):
        handlers = Button_Handlers(self.artboard, self.view, self.grid, self.artboard, self)

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

        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(handlers.deleteArrow)
        buttonstack1.addWidget(self.deleteButton)

        self.rotateRightButton = QPushButton("Rotate Right")
        self.rotateRightButton.clicked.connect(lambda: handlers.rotateArrow("right"))
        buttonstack1.addWidget(self.rotateRightButton)

        self.rotateLeftButton = QPushButton("Rotate Left")
        self.rotateLeftButton.clicked.connect(lambda: handlers.rotateArrow("left"))
        buttonstack1.addWidget(self.rotateLeftButton)

        self.mirrorButton = QPushButton("Mirror")
        self.mirrorButton.clicked.connect(lambda: handlers.mirrorArrow())
        buttonstack2.addWidget(self.mirrorButton)

        self.bringForward = QPushButton("Bring Forward")
        self.bringForward.clicked.connect(handlers.bringForward)
        buttonstack2.addWidget(self.bringForward)

        self.swapColors = QPushButton("Swap Colors")
        self.swapColors.clicked.connect(handlers.swapColors)
        buttonstack2.addWidget(self.swapColors)

        self.exportAsPNGButton = QPushButton("Export to PNG")
        self.exportAsPNGButton.clicked.connect(handlers.exportArtboard)
        masterbtnlayout.addWidget(self.exportAsPNGButton)

        #add an export as svg button
        self.exportAsSVGButton = QPushButton("Export to SVG")
        self.exportAsSVGButton.clicked.connect(handlers.export_to_svg)
        masterbtnlayout.addWidget(self.exportAsSVGButton)

        #add a button to upload an svg
        self.uploadSVGButton = QPushButton("Upload SVG")
        self.uploadSVGButton.clicked.connect(self.upload_svg)
        masterbtnlayout.addWidget(self.uploadSVGButton)
        

        # # add text label for infotracker
        # self.infoTracker = QLabel("Info Tracker")
        # self.infoTracker.setFont(QFont('Helvetica', 14))
        # #connect to handler so it updates whenever the state of the artboard changes
        # self.artboard.changed.connect(updateInfoTracker.updateText())
        # masterbtnlayout.addWidget(self.infoTracker)

        self.deleteButton.setFont(QFont('Helvetica', 14))
        self.rotateRightButton.setFont(QFont('Helvetica', 14))
        self.rotateLeftButton.setFont(QFont('Helvetica', 14))
        self.mirrorButton.setFont(QFont('Helvetica', 14))
        self.bringForward.setFont(QFont('Helvetica', 14))
        self.swapColors.setFont(QFont('Helvetica', 14))
        self.exportAsPNGButton.setFont(QFont('Helvetica', 14))
        self.exportAsSVGButton.setFont(QFont('Helvetica', 14))
        self.uploadSVGButton.setFont(QFont('Helvetica', 14))


    def parse_svg_file(file_path):
        # Parse the SVG file
        tree = ET.parse(file_path)

        # Get the root element of the SVG file
        root = tree.getroot()

        # Iterate over all elements in the SVG file
        for element in root.iter():
            # Print the element's tag and attributes
            print('tag:', element.tag)
            print('attributes:', element.attrib)


    def upload_svg(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg)")
        if file_path:
            # Parse the SVG file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Iterate over all elements in the SVG file
            for element in root.iter():
                # If the element is a 'path', create a new Arrow_Logic object
                if element.tag == '{http://www.w3.org/2000/svg}path':
                    arrow = Arrow_Logic(file_path, self.view)  # replace 'self.view' with your QGraphicsView object
                    self.arrowbox_scene.addItem(arrow)  # replace 'self.artboard' with your QGraphicsScene object


        # Call the function with the path to your SVG file
    parse_svg_file('D:\CODE\TKA_Apps\Pictograph_Constructor\main 0.4\images\\arrows\\blue\\l\\anti\\blue_anti_l_ne.svg')

app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

