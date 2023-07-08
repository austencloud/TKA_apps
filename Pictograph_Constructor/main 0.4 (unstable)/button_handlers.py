from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtSvg import QSvgRenderer, QSvgGenerator
from PyQt5.QtWidgets import QFileDialog, QGraphicsItem
import os
import xml.etree.ElementTree as ET
from svg_manager import SvgManager
from objects import Arrow

class Button_Handlers:
    SVG_SCALE = 10.0

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
            for item in self.artboard.selectedItems():
                current_pos = item.pos() - scene_center
                item.setTransformOriginPoint(item.boundingRect().center())
                if direction == "right":
                    new_pos = QPointF(-current_pos.y(), current_pos.x())
                else:
                    new_pos = QPointF(current_pos.y(), -current_pos.x())
                item.setPos(scene_center + new_pos)
                base_name = os.path.basename(item.svg_file)
                color, type_, rotation, quadrant = base_name.split('_')[:4]
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
        self.view.arrowMoved.emit()
        for item in self.artboard.selectedItems():
            current_svg = item.svg_file

            if item.rotation == "l":
                new_svg = current_svg.replace("_l_", "_r_").replace("\\l\\", "\\r\\")
                item.rotation = "r"
            elif item.rotation == "r":
                new_svg = current_svg.replace("_r_", "_l_").replace("\\r\\", "\\l\\")
                item.rotation = "l"
            else:
                print("Unexpected svg_file:", current_svg)
                continue

            new_renderer = QSvgRenderer(new_svg)
            if new_renderer.isValid():
                item.setSharedRenderer(new_renderer)
                item.svg_file = new_svg

                item.quadrant = item.quadrant.replace('.svg', '')
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
        arrow_items = [item for item in self.artboard.items() if isinstance(item, Arrow)]
        if len(arrow_items) >= 1:
            for item in arrow_items:
                current_svg = item.svg_file
                base_name = os.path.basename(current_svg)
                color, type_, rotation, quadrant = base_name.split('_')[:4]
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
                    item.color = new_color
                else:
                    print("Failed to load SVG file:", new_svg)
        else:
            print("Cannot swap colors with no arrows on the artboard.")

    def selectAll(self):
        for item in self.artboard.items():
            item.setSelected(True)
    def deselectAll(self):
        for item in self.artboard.selectedItems():
            item.setSelected(False)


    def export_to_svg(self):
        generator = QSvgGenerator()
        generator.setFileName('output.svg')
        generator.setSize(self.artboard.sceneRect().size().toSize())
        generator.setResolution(300)
        painter = QPainter(generator)
        renderer = QSvgRenderer()

        for item in self.artboard.items():
            renderer.load(item)
            renderer.render(painter)
        painter.end()

    def upload_svg(self):
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "Open SVG", "images\\arrows", "SVG Files (*.svg)")
        if file_path:
            svg_manager = SvgManager('images\\arrows')
            match = svg_manager.find_match(file_path)
            if match:
                print(f"Match found: {match}")
                arrow = Arrow(match, self.view)
                arrow.setFlag(QGraphicsItem.ItemIsMovable, True)
                arrow.setFlag(QGraphicsItem.ItemIsSelectable, True)
                arrow.setScale(self.SVG_SCALE)

                file_name = os.path.basename(match)
                compass_direction = file_name.split('_')[-1].split('.')[0]

                if compass_direction == 'ne':
                    arrow.setPos(530, 170)
                elif compass_direction == 'se':
                    arrow.setPos(530, 530)
                elif compass_direction == 'sw':
                    arrow.setPos(170, 530)
                elif compass_direction == 'nw':
                    arrow.setPos(170, 170)

                self.artboard.addItem(arrow)
            else:
                print("No match found")

    def parse_svg_file(file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for element in root.iter():
            print('tag:', element.tag)
            print('attributes:', element.attrib)

    def compare_svg_paths(file_path_1, file_path_2):

        tree_1 = ET.parse(file_path_1)
        root_1 = tree_1.getroot()

        tree_2 = ET.parse(file_path_2)
        root_2 = tree_2.getroot()

        path_data_1 = None
        for element in root_1.iter('{http://www.w3.org/2000/svg}path'):
            path_data_1 = element.attrib.get('d')
            break 

        path_data_2 = None
        for element in root_2.iter('{http://www.w3.org/2000/svg}path'):
            path_data_2 = element.attrib.get('d')
            break

        if path_data_1 == path_data_2:
            print('The SVG paths are identical.')
        else:
            print('The SVG paths are different.')
