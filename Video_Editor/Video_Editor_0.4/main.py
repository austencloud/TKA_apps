from PyQt5.QtWidgets import QApplication
import sys
import logging
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtCore import pyqtSignal
from Mirror.mirror_UI import MirrorTab
from Combiner.combiner_UI import CombinerTab

class MainWindow(QMainWindow):
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Editor 0.3")
        self.resize(600, 600)
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.conversion_in_progress = False
        self.merge_thread = None

        # Setup tabs
        self.setup_ui()

    def setup_ui(self):
        # Set up the tab widget
        self.combiner_tab = CombinerTab()
        self.combiner_tab.media_pair_added.connect(self.resize_window)
        self.tab_widget.addTab(self.combiner_tab, "Combine")

        self.mirror_tab = MirrorTab()
        self.tab_widget.addTab(self.mirror_tab, "Mirror")

    def resize_window(self):
        media_pairs_height = len(self.combiner_tab.media_pairs) * 240  # height of each media pair + some margin
        new_height = max(600, 400 + media_pairs_height)  # minimum height is 600
        self.resize(self.width(), new_height)

if __name__ == "__main__":
        try:
            app = QApplication(sys.argv)
            logging.debug("Application starting")
            main_window = MainWindow()
            main_window.show()
            sys.exit(app.exec_())
        except Exception as e:
            logging.exception(f"Unhandled exception: {e}")
