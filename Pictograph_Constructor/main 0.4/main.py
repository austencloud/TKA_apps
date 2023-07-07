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
        main_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        self.label = QLabel(self)  # create a QLabel instance
        self.artboard = QGraphicsScene()
        self.setGeometry(300, 300, 1600, 1400)  

        self.infoTracker = InfoTracker(self.artboard, self.label)
        self.view = self.initArtboard() 
        self.view.arrowMoved.connect(self.infoTracker.update)  # connect the signal to the update method
        arrowbox = self.initArrowBox()
        main_layout.addWidget(arrowbox)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        self.setWindowTitle('Drag & Drop')
        self.show()

        right_layout.addWidget(self.view)
        button_layout = self.initButtons()  
        right_layout.addLayout(button_layout)
        right_layout.addWidget(self.label)  # add the label to the layout

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
                arrow_item = Arrow_Logic(svg, self.view, self.infoTracker)  # pass the QGraphicsView object here
                arrow_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                arrow_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                arrow_item.setScale(self.SVG_SCALE)
                arrow_item.setPos(0, svg_item_count * self.SVG_POS_Y)
                arrowbox_scene.addItem(arrow_item)  # use arrowbox_scene here
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
        artboard_view = Artboard_Events(self.artboard, self.grid, self.infoTracker)
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

        self.infoTracker = InfoTracker(self.artboard, self.label)
        self.artboard.changed.connect(self.infoTracker.update)


        return artboard_view


    def initButtons(self):
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


        self.infoTracker.update()

        #add a button to upload an svg
        self.uploadSVGButton = QPushButton("Upload SVG")
        self.uploadSVGButton.clicked.connect(handlers.upload_svg)
        masterbtnlayout.addWidget(self.uploadSVGButton)


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

        return masterbtnlayout

class InfoTracker:
    def __init__(self, artboard, label):
        self.artboard = artboard
        self.label = label
        self.previous_state = self.getCurrentState()
        #increase font size
        self.label.setFont(QFont('Helvetica', 14))
        #make it hug the top
        self.label.setAlignment(Qt.AlignTop)

    def getCurrentState(self):
        state = {}
        for item in self.artboard.items():
            if isinstance(item, Arrow_Logic):
                state[item] = item.get_attributes()
        return state

    def checkForChanges(self):
        current_state = self.getCurrentState()
        if current_state != self.previous_state:
            self.update()
            self.previous_state = current_state

    def update(self):
        text = ""
        for item in self.artboard.items():
            if isinstance(item, Arrow_Logic):
                attributes = item.get_attributes()
                color = attributes.get('color', 'N/A')
                text += f"Color: {color}\n"
                text += f"Quadrant: {attributes.get('quadrant', 'N/A').upper()}\n"
                text += f"Rotation: {attributes.get('rotation', 'N/A')}\n"
                text += f"Type: {attributes.get('type', 'N/A').capitalize()}\n"
                text += "\n"
                if color == 'red':
                    self.label.setStyleSheet("color: red")
                elif color == 'blue':
                    self.label.setStyleSheet("color: blue")
        self.label.setText(text)

app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

