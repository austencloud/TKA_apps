import os
import xml.etree.ElementTree as ET

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
