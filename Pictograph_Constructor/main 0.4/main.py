import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem, QGraphicsLineItem, QLabel, QFileDialog
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QTransform, QFont
from arrows import Arrow_Logic
from artboard_events import Artboard_Events
from button_handlers import Button_Handlers
from grid import Grid
from PyQt5.QtWidgets import QFileDialog

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
        self.setGeometry(300, 300, 1600, 1400)  
        self.view = self.initArtboard()
        arrowbox = self.initArrowBox()
        vbox.addWidget(self.view)
        hbox.addWidget(arrowbox)
        #set the arrow box to hug the left side of the window
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.setWindowTitle('Drag & Drop')
        self.show()
        self.coordinatesLabel = QLabel(self)
        self.coordinatesLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.initButtons(vbox)
        vbox.addWidget(self.coordinatesLabel)
        self.view.itemMoved.connect(self.updateInfoTracker)


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
        arrow_box.setFixedSize(800, 1600)
        arrow_box.setFixedHeight(1600)

        return arrow_box

    def initArtboard(self):
        grid_size = 650
        
        self.grid = Grid('images\\grid\\grid.svg')
        artboard_view = Artboard_Events(self.artboard, self.grid)
        artboard_view.setFixedSize(700, 700)

        transform = QTransform()
        self.grid_center = QPointF(artboard_view.frameSize().width() / 2, artboard_view.frameSize().height() / 2)

        transform.translate(self.grid_center.x() - (grid_size / 2), self.grid_center.y() - (grid_size / 2))
        self.grid.setTransform(transform)

        artboard_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        artboard_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.artboard.addItem(self.grid)

        line_v = QGraphicsLineItem(artboard_view.frameSize().width() / 2, 0, artboard_view.frameSize().width() / 2, artboard_view.frameSize().height())
        line_h = QGraphicsLineItem(0, artboard_view.frameSize().height() / 2, artboard_view.frameSize().width(), artboard_view.frameSize().height() / 2)
        self.artboard.addItem(line_v)
        self.artboard.addItem(line_h)

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
        self.uploadSVGButton.clicked.connect(handlers.upload_svg)
        masterbtnlayout.addWidget(self.uploadSVGButton)
        

        # # add text label for infotracker
        # self.infoTracker = QLabel("Info Tracker")
        # self.infoTracker.setFont(QFont('Helvetica', 14))
        # #connect to handler so it updates whenever the state of the artboard changes
        # self.artboard.changed.connect(updateInfoTracker.updateText())
        # masterbtnlayout.addWidget(self.infoTracker)

        button_font = QFont('Helvetica', 14)

        self.deleteButton.setFont(button_font)
        self.rotateRightButton.setFont(button_font)
        self.rotateLeftButton.setFont(button_font)
        self.mirrorButton.setFont(button_font)
        self.bringForward.setFont(button_font)
        self.swapColors.setFont(button_font)
        self.exportAsPNGButton.setFont(button_font)
        self.exportAsSVGButton.setFont(button_font)
        self.uploadSVGButton.setFont(button_font)



    def updateInfoTracker(self):
        selectedItems = self.view.scene().selectedItems()
        text = ""
        for item in selectedItems:
            pos = item.scenePos()
            rect = item.boundingRect()
            center_pos = pos + QPointF(rect.width() / 2, rect.height() / 2)
            text += f"Item at ({center_pos.x()}, {center_pos.y()})\n"
        self.coordinatesLabel.setText(text)






app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

