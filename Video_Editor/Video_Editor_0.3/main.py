from PyQt5.QtWidgets import QApplication
import sys
import logging
from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtCore import pyqtSignal
from kaleidoscope import KaleidoscopeTab
from merge_tab import MergeFilesTab

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
        self.combiner_tab = MergeFilesTab()
        self.tab_widget.addTab(self.combiner_tab, "Combiner")

        self.kaleidoscope_tab = KaleidoscopeTab()
        self.tab_widget.addTab(self.kaleidoscope_tab, "Kaleidoscope")

if __name__ == "__main__":
        try:
            app = QApplication(sys.argv)
            logging.debug("Application starting")
            main_window = MainWindow()
            main_window.show()
            sys.exit(app.exec_())
        except Exception as e:
            logging.exception(f"Unhandled exception: {e}")
