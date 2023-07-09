import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QGraphicsScene, QGraphicsView, QPushButton, QGraphicsItem, QLabel, QFileDialog, QCheckBox, QLineEdit, QFrame
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QTransform, QFont
from objects import Arrow
from artboard_events import Artboard
from button_handlers import Button_Handlers
from grid import Grid
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from PyQt5.QtXml import QDomDocument
from upload_manager import UploadManager
from data import positions, compass_mapping, generate_variations
import json
from button_handlers import Button_Handlers

class Main_Window(QWidget):
    ARROW_DIR = 'images\\arrows'
    SVG_SCALE = 10.0
    SVG_POS_Y = 250

    def __init__(self):
        super().__init__() 
        self.initUI()
        self.scene = QGraphicsScene()  # Add this line
        self.handlers = Button_Handlers(self.artboard, self.view, self.grid, self.scene, self)
        self.letterCombinations = self.loadLetterCombinations()

    def initUI(self):
        main_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        self.label = QLabel(self)  # create a QLabel instance
        self.artboard = QGraphicsScene()
        self.setGeometry(300, 300, 1600, 1400)  

        self.infoTracker = Info_Tracker(self.artboard, self.label)
        self.view = self.initArtboard() 
        self.view.arrowMoved.connect(self.infoTracker.update)  # connect the signal to the update method
        arrowbox = self.initArrowBox()
        main_layout.addWidget(arrowbox)
        main_layout.setAlignment(arrowbox, Qt.AlignTop)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        self.setWindowTitle('Drag & Drop')
        self.show()
        self.grid = Grid('images\\grid\\grid.svg')
        right_layout.addWidget(self.view)
        button_layout = self.initButtons()  
        right_layout.addLayout(button_layout)
        # Add a text input field for entering a letter
        self.letterInput = QLineEdit(self)
        right_layout.addWidget(self.letterInput)

        # Add a button for assigning the entered letter to the selected combination of arrows
        self.assignLetterButton = QPushButton("Assign Letter", self)
        self.assignLetterButton.clicked.connect(self.assignLetter)
        right_layout.addWidget(self.assignLetterButton)
        self.checkbox_manager = Checkbox_Manager(self.view, self.grid)
        right_layout.addWidget(self.checkbox_manager.getCheckbox())

        right_layout.addWidget(self.label)  # add the label to the layout

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.handlers.deleteArrow()

    def loadLetterCombinations(self):
        try:
            with open('letterCombinations.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def saveLetterCombinations(self):
        with open('letterCombinations.json', 'w') as f:
            json.dump(self.letterCombinations, f)

    def assignLetter(self):
        letter = self.letterInput.text().upper()
        if letter not in positions:
            print(f"{letter} is not a valid letter.")
            return
        selected_items = self.artboard.selectedItems()
        if len(selected_items) != 2 or not all(isinstance(item, Arrow) for item in selected_items):
            print("Please select a combination of two arrows.")
            return
        letter_instance = Letter(selected_items[0], selected_items[1])
        letter_instance.assign_letter(letter)

        arrow_combination = [item.get_attributes() for item in selected_items]
        variations = generate_variations(arrow_combination)
        print(f"Generated {len(variations)} variations for the selected combination of arrows.")
        print(f"{variations}")
        if letter not in self.letterCombinations:
            self.letterCombinations[letter] = []
        for variation in variations:
            self.letterCombinations[letter].append(variation)

        self.saveLetterCombinations()

        print(f"Assigned {letter} to the selected combination of arrows and all its variations.")
        self.infoTracker.update()

    def loadSvg(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG files (*.svg)")
        if fileName:
            self.svgWidget.load(fileName)

    def initArrowBox(self):
        arrow_box = QScrollArea(self)
        arrowbox_scene = QGraphicsScene()  # Use a separate scene for the arrow box
        svgs_full_paths = []
        default_arrows = ['red_anti_r_ne.svg', 'red_iso_r_ne.svg', 'blue_anti_r_sw.svg', 'blue_iso_r_sw.svg']
        svg_item_count = 0

        for dirpath, dirnames, filenames in os.walk(self.ARROW_DIR):
            svgs_full_paths.extend([os.path.join(dirpath, filename) for filename in filenames if filename.endswith('.svg')])

        for i, svg in enumerate(svgs_full_paths):
            file_name = os.path.basename(svg)
            if file_name in default_arrows:
                arrow_item = Arrow(svg, self.view, self.infoTracker)  # pass the QGraphicsView object here
                arrow_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                arrow_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                arrow_item.setScale(self.SVG_SCALE)
                arrow_item.setPos(0, svg_item_count * self.SVG_POS_Y)
                arrowbox_scene.addItem(arrow_item)  # use arrowbox_scene here
                arrow_item.attributesChanged.connect(self.infoTracker.update)  # add this line
                svg_item_count += 1

        view = QGraphicsView(arrowbox_scene)  # use arrowbox_scene here
        view.setFrameShape(QFrame.NoFrame)  # remove the border
        arrow_box.setWidget(view)
        arrow_box.setWidgetResizable(True)
        # set a fixed height and width
        arrow_box.setFixedSize(500, 1100)

        return arrow_box

    def initArtboard(self):
        grid_size = 650
        
        self.grid = Grid('images\\grid\\grid.svg')
        artboard_view = Artboard(self.artboard, self.grid, self.infoTracker)
        artboard_view.setFixedSize(700, 700)

        transform = QTransform()
        self.grid_center = QPointF(artboard_view.frameSize().width() / 2, artboard_view.frameSize().height() / 2)

        transform.translate(self.grid_center.x() - (grid_size / 2), self.grid_center.y() - (grid_size / 2))
        self.grid.setTransform(transform)

        artboard_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        artboard_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.artboard.addItem(self.grid)



        self.infoTracker = Info_Tracker(self.artboard, self.label)
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

        self.exportAsSVGButton = QPushButton("Export to SVG")
        self.exportAsSVGButton.clicked.connect(handlers.export_to_svg)
        masterbtnlayout.addWidget(self.exportAsSVGButton)


        self.infoTracker.update()

        # add a button to upload an svg
        # self.uploadButton = QPushButton("Upload SVG")
        # self.uploadButton.clicked.connect(UploadManager.upload_svg)
        # masterbtnlayout.addWidget(self.uploadButton)


        button_font = QFont('Helvetica', 14)

        self.deleteButton.setFont(button_font)
        self.rotateRightButton.setFont(button_font)
        self.rotateLeftButton.setFont(button_font)
        self.mirrorButton.setFont(button_font)
        self.bringForward.setFont(button_font)
        self.swapColors.setFont(button_font)
        self.exportAsPNGButton.setFont(button_font)
        self.exportAsSVGButton.setFont(button_font)
        # self.uploadButton.setFont(button_font)

        return masterbtnlayout
        
    def assignLetter(self):
        letter = self.letterInput.text().upper()
        if letter not in positions:
            print(f"{letter} is not a valid letter.")
            return
        selected_items = self.artboard.selectedItems()
        if len(selected_items) != 2 or not all(isinstance(item, Arrow) for item in selected_items):
            print("Please select a combination of two arrows.")
            return
        letter_instance = Letter(selected_items[0], selected_items[1])
        letter_instance.assign_letter(letter)

        arrow_combination = [item.get_attributes() for item in selected_items]
        variations = generate_variations(arrow_combination)
        print(f"Generated {len(variations)} variations for the selected combination of arrows.")
        print(f"{variations}")
        if letter not in self.letterCombinations:
            self.letterCombinations[letter] = []
        for variation in variations:
            self.letterCombinations[letter].append(variation)

        self.saveLetterCombinations()

        print(f"Assigned {letter} to the selected combination of arrows and all its variations.")
        self.infoTracker.update()

class Checkbox_Manager():
    def __init__(self, artboard_view, grid):
        self.artboard_view = artboard_view
        self.lineCheckbox = QCheckBox("Show Lines")
        self.lineCheckbox.setFont(QFont('Helvetica', 14))
        self.lineCheckbox.setChecked(True)
        self.lineCheckbox.stateChanged.connect(self.toggleLines)
        self.lineCheckbox.move(0, 0)
        self.lineCheckbox.show()
        self.grid = grid

        # Load the SVG file
        self.grid_renderer = QSvgRenderer()
        self.grid_renderer.load('images\\grid\\grid.svg')

    def getCheckbox(self):
        return self.lineCheckbox
        
    def toggleLines(self, state):
        print("toggleLines")

        # Load the SVG file into a QDomDocument
        svg_doc = QDomDocument()
        with open('images\\grid\\grid.svg', 'r') as f:
            svg_doc.setContent(f.read())

        # Find all line elements
        lines = svg_doc.elementsByTagName('line')

        # Change the color of the lines
        for i in range(lines.length()):
            line = lines.item(i).toElement()  # Convert the QDomNode to a QDomElement
            if line.hasAttribute('class') and line.attribute('class') == 'lines':
                if state == Qt.Checked:
                    line.setAttribute('stroke', '#000000')  # Change to black
                else:
                    line.setAttribute('stroke', 'none')  # Make invisible

        # Update the QGraphicsSvgItem with the modified document
        self.grid_renderer.load(svg_doc.toByteArray())

        # Update the Grid object with the new SVG content
        self.grid.updateSvgContent(self.grid_renderer)
class Info_Tracker:
    def __init__(self, artboard, label):
        self.artboard = artboard
        self.label = label
        self.previous_state = self.getCurrentState()
        self.label.setFont(QFont('Helvetica', 14))
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.label.setAlignment(Qt.AlignTop)
        self.letterCombinations = self.loadLetterCombinations()

    def getCurrentState(self):
        state = {}
        for item in self.artboard.items():
            if isinstance(item, Arrow):
                state[item] = item.get_attributes()
        return state

    def checkForChanges(self):
        current_state = self.getCurrentState()
        if current_state != self.previous_state:
            self.update()
            self.previous_state = current_state
    
    def loadLetterCombinations(self):
        try:
            with open('letterCombinations.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_positional_relationship(self, start1, end1, start2, end2):
        start1_compass = Arrow.get_position_from_directions(start1, start1)
        end1_compass = Arrow.get_position_from_directions(end1, end1)
        start2_compass = Arrow.get_position_from_directions(start2, start2)
        end2_compass = Arrow.get_position_from_directions(end2, end2)

        # Determine the start position
        if set(start1_compass) == set(start2_compass):
            start_position = "beta"
        elif set(start1_compass) == set(["n", "s"]) or set(start1_compass) == set(["e", "w"]):
            start_position = "alpha"
        else:
            start_position = "gamma"

        # Determine the end position
        if set(end1_compass) == set(end2_compass):
            end_position = "beta"
        elif set(end1_compass) == set(["n", "s"]) or set(end1_compass) == set(["e", "w"]):
            end_position = "alpha"
        else:
            end_position = "gamma"

        return start_position + " to " + end_position
            
    def generate_arrow_positions():
        arrow_positions = {}
        for dirpath, dirnames, filenames in os.walk(Main_Window.ARROW_DIR):
            for filename in filenames:
                if filename.endswith('.svg'):
                    parts = filename.split('_')
                    arrow_type = parts[1]
                    rotation = parts[2]
                    quadrant = parts[3].split('.')[0]
                    if arrow_type == "anti":
                        if rotation == "l":
                            start_position, end_position = ("n", "s")
                        else:  # rotation == "r"
                            end_position, start_position = ("n", "s")
                    else:  # arrow_type == "iso"
                        if rotation == "l":
                            start_position, end_position = ("n", "s")
                        else:  # rotation == "r"
                            end_position, start_position = ("n", "s")
                    arrow_positions[filename] = (start_position, end_position)
        return arrow_positions
    
    def update(self):
        current_combination = []

        for item in self.artboard.items():
            if isinstance(item, Arrow):
                attributes = item.get_attributes()
                current_combination.append(attributes)

        current_combination = sorted(current_combination, key=lambda x: x['color'])

        self.letterCombinations = self.loadLetterCombinations()
        blue_text = "<h2>Left</h2>"
        red_text = "<h2>Right</h2>"
        letter_text = "<h2>Letter</h2>"

        for letter, combinations in self.letterCombinations.items():
            combinations = [sorted(combination, key=lambda x: x['color']) for combination in combinations]
            if current_combination in combinations:
                letter_text += f"<h3 style='font-size: 50px'>{letter}</h3>"

        for item in self.artboard.items():
            if isinstance(item, Arrow):
                attributes = item.get_attributes()
                current_combination.append(attributes)
                color = attributes.get('color', 'N/A')
                color_text = f"<font color='{color}'>Color: {color}</font>"
                if color == 'blue':
                    blue_text += f"{color_text}<br>"
                    blue_text += f"Quadrant: {attributes.get('quadrant', 'N/A').upper()}<br>"
                    blue_text += f"Rotation: {attributes.get('rotation', 'N/A')}<br>"
                    blue_text += f"Type: {attributes.get('type', 'N/A').capitalize()}<br>"
                    blue_text += f"Start position: {attributes.get('start_position', 'N/A').capitalize()}<br>"
                    blue_text += f"End position: {attributes.get('end_position', 'N/A').capitalize()}<br>"
                    blue_text += "<br>"
                elif color == 'red':
                    red_text += f"{color_text}<br>"
                    red_text += f"Quadrant: {attributes.get('quadrant', 'N/A').upper()}<br>"
                    red_text += f"Rotation: {attributes.get('rotation', 'N/A')}<br>"
                    red_text += f"Type: {attributes.get('type', 'N/A').capitalize()}<br>"
                    red_text += f"Start position: {attributes.get('start_position', 'N/A').capitalize()}<br>"
                    red_text += f"End position: {attributes.get('end_position', 'N/A').capitalize()}<br>"
                    red_text += "<br>"


        self.label.setText("<table><tr><td width=300>" + blue_text + "</td><td width=300>" + red_text + "</td><td width=100>" + letter_text + "</td></tr></table>")
       
class Letter:
    def __init__(self, arrow1, arrow2):
        self.arrow1 = arrow1
        self.arrow2 = arrow2
        self.letter = None  # Add an attribute for the letter

    def get_start_position(self):
        # Get the start positions of the two arrows
        start_position1 = Arrow.get_arrow_start_position(self.arrow1)
        start_position2 = Arrow.get_arrow_start_position(self.arrow2)

        # Return the position corresponding to the pair of start positions
        return Arrow.get_position_from_directions(start_position1, start_position2)

    def get_end_position(self):
        # Get the end positions of the two arrows
        end_position1 = Arrow.get_arrow_end_position(self.arrow1)
        end_position2 = Arrow.get_arrow_end_position(self.arrow2)

        # Return the position corresponding to the pair of end positions
        return Arrow.get_position_from_directions(end_position1, end_position2)

    def assign_letter(self, letter):
        # Check if the start and end positions match the positions for the letter
        if (self.get_start_position(), self.get_end_position()) == positions[letter]:
            self.letter = letter  # Assign the letter
        else:
            print(f"The start and end positions do not match the positions for {letter}.")

app = QApplication(sys.argv)
ex = Main_Window()
ex.setFocus()  
sys.exit(app.exec_())

