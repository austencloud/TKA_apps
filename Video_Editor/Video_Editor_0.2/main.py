from PyQt5.QtWidgets import QApplication
import sys
import logging
from merge_files import MergeFiles
from main_window import MainWindow

if __name__ == "__main__":
        try:
            app = QApplication(sys.argv)
            logging.debug("Application starting")
            main_window = MainWindow()
            main_window.show()
            sys.exit(app.exec_())
        except Exception as e:
            logging.exception(f"Unhandled exception: {e}")