from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtSvg import QSvgRenderer, QSvgGenerator
from PyQt5.QtWidgets import QFileDialog
import os
import xml.etree.ElementTree as ET

from arrows import Arrow_Logic

class Button_Handlers:
    def __init__(self, artboard, view, grid, scene, main_window):
        self.artboard = artboard
        self.view = view
        self.grid = grid
        self.scene = scene
        self.main_window = main_window

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteArrow()

    def rotateArrow(self, direction):
        if self.view.grid is not None:
            scene_center = QPointF(self.view.width() / 2, self.view.height() / 2)
            

            #fill in the red dot
            self.scene.addEllipse(scene_center.x() - 2, scene_center.y() - 2, 4, 4, Qt.red, Qt.red)


            for item in self.artboard.selectedItems():
                # Get the current position of the item relative to the scene center
                current_pos = item.pos() - scene_center
                item.setTransformOriginPoint(item.boundingRect().center())
                # Calculate the new position based on the rotation direction
                if direction == "right":
                    new_pos = QPointF(-current_pos.y(), current_pos.x())
                else:  # direction == "left"
                    new_pos = QPointF(current_pos.y(), -current_pos.x())

                # Move the item to the new position
                item.setPos(scene_center + new_pos)

                # Change the SVG file to match the new orientation
                base_name = os.path.basename(item.svg_file)
                color, type_, orientation, quadrant = base_name.split('_')[:4]
                quadrant = quadrant.replace('.svg', '')

                quadrants = ['ne', 'se', 'sw', 'nw']
                current_quadrant_index = quadrants.index(quadrant)
                if direction == "right":
                    new_quadrant_index = (current_quadrant_index + 1) % 4
                else:  # direction == "left"
                    new_quadrant_index = (current_quadrant_index - 1) % 4

                new_quadrant = quadrants[new_quadrant_index]
                new_svg = item.svg_file.replace(quadrant, new_quadrant)

                new_renderer = QSvgRenderer(new_svg)
                if new_renderer.isValid():
                    item.setSharedRenderer(new_renderer)
                    item.svg_file = new_svg
                else:
                    print("Failed to load SVG file:", new_svg)

    def mirrorArrow(self):
        for item in self.artboard.selectedItems():
            current_svg = item.svg_file

            if item.orientation == "l":
                new_svg = current_svg.replace("_l_", "_r_").replace("\\l\\", "\\r\\")
                item.orientation = "r"
            elif item.orientation == "r":
                new_svg = current_svg.replace("_r_", "_l_").replace("\\r\\", "\\l\\")
                item.orientation = "l"
            else:
                print("Unexpected svg_file:", current_svg)
                continue

            new_renderer = QSvgRenderer(new_svg)
            if new_renderer.isValid():
                item.setSharedRenderer(new_renderer)
                item.svg_file = new_svg
            else:
                print("Failed to load SVG file:", new_svg)

    def deleteArrow(self):
        for item in self.artboard.selectedItems():
            self.artboard.removeItem(item)

    def exportArtboard(self):
        selectedItems = self.artboard.selectedItems()
        image = QImage(self.view.size(), QImage.Format_ARGB32)
        painter = QPainter(image)

        for item in selectedItems:
            item.setSelected(False)

        self.view.render(painter)
        painter.end()
        image.save("export.png")

        for item in selectedItems:
            item.setSelected(True)

    def bringForward(self):
        for item in self.artboard.selectedItems():
            z = item.zValue()
            item.setZValue(z + 1)

    def swapColors(self):
        if len(self.artboard.selectedItems()) == 0:
            self.selectAll()
            for item in self.artboard.selectedItems():
                current_svg = item.svg_file
                base_name = os.path.basename(current_svg)
                color, type_, orientation, quadrant = base_name.split('_')[:4]
                if color == "red":
                    new_color = "blue"
                elif color == "blue":
                    new_color = "red"
                else:
                    print("Unexpected color:", color)
                    continue
                new_svg = current_svg.replace(color, new_color)
                new_renderer = QSvgRenderer(new_svg)
                if new_renderer.isValid():
                    item.setSharedRenderer(new_renderer)
                    item.svg_file = new_svg
                else:
                    print("Failed to load SVG file:", new_svg)
        elif len(self.artboard.selectedItems()) > 0:
            for item in self.artboard.selectedItems():
                current_svg = item.svg_file
                base_name = os.path.basename(current_svg)
                color, type_, orientation, quadrant = base_name.split('_')[:4]
                if color == "red":
                    new_color = "blue"
                elif color == "blue":
                    new_color = "red"
                else:
                    print("Unexpected color:", color)
                    continue
                new_svg = current_svg.replace(color, new_color)
                new_renderer = QSvgRenderer(new_svg)
                if new_renderer.isValid():
                    item.setSharedRenderer(new_renderer)
                    item.svg_file = new_svg
                else:
                    print("Failed to load SVG file:", new_svg)



    def selectAll(self):
        for item in self.artboard.items():
            item.setSelected(True)
    def deselectAll(self):
        for item in self.artboard.selectedItems():
            item.setSelected(False)




    def export_to_svg(self):
        generator = QSvgGenerator()
        generator.setFileName("output.svg")
        generator.setSize(self.artboard.sceneRect().size().toSize())
        generator.setViewBox(self.artboard.sceneRect())

        painter = QPainter(generator)
        self.artboard.render(painter)
        painter.end()

    def upload_svg(self):
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "Open SVG", "", "SVG Files (*.svg)")
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
        #print the svg data in the console
        print(ET.tostring(root, encoding='utf8').decode('utf8'))

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

        # Call the function with the path to your SVG file
    parse_svg_file('D:\CODE\TKA_Apps\Pictograph_Constructor\main 0.4\images\\arrows\\blue\\l\\anti\\blue_anti_l_ne.svg')

    def compare_svg_paths(file_path_1, file_path_2):
        # Parse the first SVG file
        tree_1 = ET.parse(file_path_1)
        root_1 = tree_1.getroot()

        # Parse the second SVG file
        tree_2 = ET.parse(file_path_2)
        root_2 = tree_2.getroot()

        # Get the 'd' attribute of the 'path' element in the first SVG file
        path_data_1 = None
        for element in root_1.iter('{http://www.w3.org/2000/svg}path'):
            path_data_1 = element.attrib.get('d')
            break  # Assume there's only one 'path' element

        # Get the 'd' attribute of the 'path' element in the second SVG file
        path_data_2 = None
        for element in root_2.iter('{http://www.w3.org/2000/svg}path'):
            path_data_2 = element.attrib.get('d')
            break  # Assume there's only one 'path' element

        # Compare the two SVG paths
        if path_data_1 == path_data_2:
            print('The SVG paths are identical.')
        else:
            print('The SVG paths are different.')
