from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QMessageBox, QTabWidget, QFileDialog, QCheckBox, QSlider
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from merge_files import MergeFiles
from preview_graphics_view import PreviewGraphicsView
from kaleidoscope import KaleidoscopeTab
from pathlib import Path
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import os
import subprocess

class MainWindow(QMainWindow):
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multifunctional Application")
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


class MergeFilesTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def cancel_merge(self):
        if self.merge_thread is not None:
            self.merge_thread.stop()

    def cleanup(self):
        if self.merge_thread.is_stopped():
            QMessageBox.information(self, "Merge cancelled", "The merge operation was cancelled.")
        else:
            QMessageBox.information(self, "Merge completed", "The merge operation completed successfully.")
        self.progress_bar.setValue(0)  # Clear the progress bar
        self.cancel_button.setEnabled(False)
        self.merge_button.setEnabled(True)  # Re-enable the merge button

    def setup_ui(self):
        # Set up the main layout
        layout = QVBoxLayout()

        # Set up the drop areas
        drop_area_layout = QHBoxLayout()

        # Image drop area with button
        image_layout = QVBoxLayout()
        self.browse_image_button = QPushButton("Browse Image")
        self.browse_image_button.clicked.connect(lambda: self.image_drop_area.process_dropped_path(self.image_drop_area.open_file_dialog()))
        self.image_drop_area = PreviewGraphicsView("Drop Image Here", self, "photo")
        self.image_drop_area.setGeometry(QtCore.QRect(70, 70, 200, 200))
        image_layout.addWidget(self.browse_image_button)
        image_layout.addWidget(self.image_drop_area)
        
        # Video drop area with button
        video_layout = QVBoxLayout()
        self.browse_video_button = QPushButton("Browse Video")
        self.browse_video_button.clicked.connect(lambda: self.video_drop_area.process_dropped_path(self.video_drop_area.open_file_dialog()))
        self.video_drop_area = PreviewGraphicsView("Drop Video Here", self, "video")
        self.video_drop_area.setGeometry(QtCore.QRect(330, 70, 200, 200))
        video_layout.addWidget(self.browse_video_button)
        video_layout.addWidget(self.video_drop_area)

        drop_area_layout.addLayout(image_layout)
        drop_area_layout.addLayout(video_layout)

        layout.addLayout(drop_area_layout)


        # Set up the Convert button and progress bar
        merge_layout = QHBoxLayout()
        
        self.merge_button = QPushButton("Merge")
        self.merge_button.setObjectName("merge_button")
        self.merge_button.setText("Merge")
        self.merge_button.clicked.connect(self.convert)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)  # Disable the cancel button initially
        
        self.progress_bar = QProgressBar()
        
        merge_layout.addWidget(self.merge_button, 0)  # Add the merge button with stretch factor of 0
        merge_layout.addWidget(self.cancel_button, 0)  # Add the cancel button with stretch factor of 0
        merge_layout.addWidget(self.progress_bar, 1)  # Add the progress bar with stretch factor of 1

        layout.addLayout(merge_layout)  # Add the merge layout to the main layout

        # Connect cancel button signal to slot
        self.cancel_button.clicked.connect(self.cancel_merge)

        # Set window properties
        self.setMinimumSize(QSize(640, 480))

        # Create the checkbox
        self.resize_checkbox = QCheckBox("Resize Image to Video Dimensions", self)
        # You can set the default state to be unchecked with
        # self.resize_checkbox.setChecked(False)
        self.resize_checkbox.setChecked(False)
        layout.addWidget(self.resize_checkbox)

        # Connect signals and slots
        self.image_drop_area.path_changed.connect(self.set_image_path)
        self.video_drop_area.path_changed.connect(self.set_video_path)
        self.progress_signal.connect(self.progress_bar.setValue)

        self.setLayout(layout)

    def set_image_path(self, path):
        self.image_path = path

    def set_video_path(self, path):
        self.video_path = path

    def cancel_merge(self):
        if self.merge_thread and self.merge_thread.isRunning():
            # Disconnect the cleanup function from the finished signal
            self.merge_thread.finished.disconnect(self.cleanup)

            # Stop the thread
            self.merge_thread.stop()

            def cleanup():
                QMessageBox.information(self, "Merge cancelled", "The merge operation was cancelled.")
                self.progress_bar.setValue(0)  # Clear the progress bar
                self.cancel_button.setEnabled(False)  # Disable the cancel button
                self.merge_button.setEnabled(True)  # Enable the merge button
                
                # Reconnect the cleanup function to the finished signal
                self.merge_thread.finished.connect(self.cleanup)

            # Connect the cleanup function to the stopped signal
            self.merge_thread.stopped.connect(cleanup)

    def convert(self):
        if self.image_path is not None and self.video_path is not None:
            # Set output path based on the input video path
            video_dir = os.path.dirname(self.video_path)
            video_basename = os.path.basename(self.video_path)
            video_name, video_ext = os.path.splitext(video_basename)
            self.output_path = os.path.join(video_dir, video_name + "_output" + video_ext)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select both a photo and a video before merging.")
            return
        if not hasattr(self, "image_path") or not hasattr(self, "video_path") or not hasattr(self, "output_path"):
            QMessageBox.critical(self, "Error", "Please choose an image, a video, and an output path.")
            return

        self.merge_button.setEnabled(False)
        self.cancel_button.setEnabled(True)  # Enable the cancel button
        self.progress_bar.setValue(0)
        print(f"Image Path: {self.image_path}")
        print(f"Video Path: {self.video_path}")
        print(f"Output Path: {self.output_path}")

        # Store the thread as an instance variable
        self.merge_thread = MergeFiles(self.image_path, self.video_path, self.output_path, preserve_aspect_ratio=self.resize_checkbox.isChecked())
        self.merge_thread.progress_signal.connect(self.progress_bar.setValue)
        self.merge_thread.finished.connect(self.cleanup)
        self.merge_thread.stopped.connect(self.cleanup)
        self.merge_thread.start()

