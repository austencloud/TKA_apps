import os
import xml.etree.ElementTree as ET
import svgwrite

class SvgManager:
    def __init__(self, arrow_dir):
        self.arrow_dir = arrow_dir
        self.d_attributes = self.load_svg_files()

    def load_svg_files(self):
        svg_files = [os.path.join(root, file) for root, dirs, files in os.walk(self.arrow_dir) for file in files if file.endswith('.svg')]
        d_attributes = {}
        for svg_file in svg_files:
            tree = ET.parse(svg_file)
            root = tree.getroot()
            for element in root.iter('{http://www.w3.org/2000/svg}path'):
                d_attributes[svg_file] = element.attrib['d']
        return d_attributes

    def find_match(self, uploaded_file):
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        for element in root.iter('{http://www.w3.org/2000/svg}path'):
            uploaded_d = element.attrib['d']
            for svg_file, d in self.d_attributes.items():
                if d == uploaded_d:
                    return svg_file
        return None

class Make_Square_Bounding_Box_For_Arrows():

    # Load the original SVG
    original_svg = svgwrite.Drawing(filename='original.svg')

    # Determine the largest dimension
    largest_dimension = max(original_svg.width, original_svg.height)

    # Create a new SVG that's a square with the size of the largest dimension
    new_svg = svgwrite.Drawing(filename='new.svg', size=(largest_dimension, largest_dimension))

    # Calculate the translation needed to center the original SVG within the new SVG
    translation_x = (largest_dimension - original_svg.width) / 2
    translation_y = (largest_dimension - original_svg.height) / 2

    # Add the original SVG to the new SVG, translated to the center
    new_svg.add(original_svg.translate(translation_x, translation_y))

    # Save the new SVG
    new_svg.save()
