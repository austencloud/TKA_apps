from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QMessageBox, QCheckBox
from PyQt5.QtCore import QSize, pyqtSignal
import os
from PyQt5 import QtCore
import os
import cv2
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QFont, QImageReader
from PyQt5.QtCore import Qt, pyqtSignal
import cv2
import random
from merge_files import MergeFiles
from pathlib import Path
import os
import logging


class MergeFilesTab(QWidget):
    progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.merge_thread = None
        self.image_path = None
        self.video_path = None

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
        self.image_drop_area = LoadMedia("Drop Image Here", self, "photo")
        self.image_drop_area.setGeometry(QtCore.QRect(70, 70, 200, 200))
        image_layout.addWidget(self.browse_image_button)
        image_layout.addWidget(self.image_drop_area)
        
                # Initialize media pairs
        self.media_pairs = []

        # Add button to create new image-video pair
        self.add_pair_button = QPushButton("Add Image-Video Pair")
        self.add_pair_button.clicked.connect(self.add_media_pair)
        layout.addWidget(self.add_pair_button)

        # Video drop area with button
        video_layout = QVBoxLayout()
        self.browse_video_button = QPushButton("Browse Video")
        self.video_drop_area = LoadMedia("Drop Video Here", self, "video")
        self.video_drop_area.setGeometry(QtCore.QRect(330, 70, 200, 200))
        video_layout.addWidget(self.browse_video_button)
        video_layout.addWidget(self.video_drop_area)

        self.browse_image_button.clicked.connect(self.image_drop_area.open_file_dialog)
        self.browse_video_button.clicked.connect(self.video_drop_area.open_file_dialog)



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

        # Create the checkbox
        self.resize_checkbox = QCheckBox("Resize Image to Video Dimensions", self)
        # You can set the default state to be unchecked with
        # self.resize_checkbox.setChecked(False)
        self.resize_checkbox.setChecked(False)
        layout.addWidget(self.resize_checkbox)

        # Add the drop areas to the main layout
        drop_area_layout.addLayout(image_layout)
        drop_area_layout.addLayout(video_layout)

        layout.addLayout(drop_area_layout)

        # Connect cancel button signal to slot
        self.cancel_button.clicked.connect(self.cancel_merge)

        # Set window properties
        self.setMinimumSize(QSize(640, 480))



        # Connect signals and slots
        self.image_drop_area.path_changed.connect(self.set_image_path)
        self.video_drop_area.path_changed.connect(self.set_video_path)

        self.progress_signal.connect(self.progress_bar.setValue)

        self.setLayout(layout)

    def add_media_pair(self):
        # Create image-video pair
        media_pair = MediaPair(self)
        self.media_pairs.append(media_pair)
        
        # Add pair to layout
        self.layout().addWidget(media_pair)

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
        
        outputs = []
        
        for media_pair in self.media_pairs:
            image_path = media_pair.get_image_path()
            video_path = media_pair.get_video_path()

            if image_path is None or video_path is None:
                QtWidgets.QMessageBox.warning(self, "Error", "Please select both a photo and a video for each pair before merging.")
                return
            
            video_dir = os.path.dirname(video_path)
            video_basename = os.path.basename(video_path)
            video_name, video_ext = os.path.splitext(video_basename)
            output_path = os.path.join(video_dir, video_name + "_output" + video_ext)


        self.merge_button.setEnabled(False)
        self.cancel_button.setEnabled(True)  # Enable the cancel button
        self.progress_bar.setValue(0)
        print(f"Image Path: {image_path}")
        print(f"Video Path: {video_path}")
        print(f"Output Path: {output_path}")

        # Store the thread as an instance variable
        self.merge_thread = MergeFiles(image_path, video_path, output_path, preserve_aspect_ratio=self.resize_checkbox.isChecked())
        self.merge_thread.progress_signal.connect(self.progress_bar.setValue)
        self.merge_thread.finished.connect(self.cleanup)
        self.merge_thread.stopped.connect(self.cleanup)
        self.merge_thread.start()


    
class LoadMedia(QGraphicsView):
    path_changed = pyqtSignal(str)  # Moved here

    def __init__(self, text, parent=None, file_type=None):
        logging.debug("Initializing MergeFilesUI")
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.pixmap = None
        self.text = text
        self.file_type = file_type  # Used file_type instead of path_type
        self.set_text(self.text)
        self.main_window = parent

    def update_progressbar(self, fraction):
        self.main_window.progress.setValue(fraction * 100)
        QApplication.processEvents()

    def get_path(self):
        return self.path

    def open_file_dialog(self):
        options = QFileDialog.Options()
        home_dir = str(Path.home())
        my_pictures = os.path.join(home_dir, 'Pictures')
        my_videos = os.path.join(home_dir, 'Videos')
        initial_dir = my_pictures if self.file_type == "image" else my_videos

        file_filter = "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)" if self.file_type == "image" else "Videos (*.mp4 *.avi *.mkv *.webm *.mov);;All Files (*)"
        file, _ = QFileDialog.getOpenFileName(None, "Open File", initial_dir, file_filter, options=options)
        if file:
            # If a file was selected in the dialog, process it
            self.process_dropped_path(file)



    def process_dropped_path(self, path):
        logging.debug(f"Processing dropped path: {path}")
        if self.file_type == "image":
            pixmap = load_image_without_exif_rotation(path)
            self.set_pixmap(pixmap)
        else:
            try:
                capture = cv2.VideoCapture(path)
                if not capture.isOpened():
                    raise ValueError("Unable to open the video file")

                frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                random_frame = random.randint(0, frame_count - 1)
                capture.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
                ret, frame = capture.read()
                if not ret:
                    raise ValueError("Unable to read a frame from the video file")

                capture.release()

                height, width, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                qimage = QImage(rgb_frame.data, width, height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                self.set_pixmap(pixmap)
                logging.debug(f"Releasing the video capture for {path}")
            except Exception as e:
                logging.exception(f"Error during video processing: {e}")

        self.path_changed.emit(path)

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.update_pixmap()

    def update_pixmap(self):
        if not self.pixmap:
            return
        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scene = QGraphicsScene(self)
        scene.setBackgroundBrush(Qt.transparent)
        scene.addPixmap(scaled_pixmap)
        self.setScene(scene)

    def dragMoveEvent(self, event):
        event.accept()


    def set_text(self, text):
        scene = QGraphicsScene()
        scene.addText(text, QFont("Arial", 14))
        self.setScene(scene)

    def dragEnterEvent(self, event):
        logging.debug("dragEnterEvent triggered")
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            url = event.mimeData().urls()[0]
            if url.isLocalFile():
                event.acceptProposedAction()
                logging.debug("Event accepted")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            path = url.toLocalFile()
            if os.path.isfile(path):
                try:
                    self.process_dropped_path(path)
                except Exception as e:
                    logging.exception(f"Error during drop event processing: {e}")
        event.acceptProposedAction()

    def resizeEvent(self, event):
        self.update_pixmap()
        super().resizeEvent(event)

    path_changed = pyqtSignal(str)
    
def load_image_without_exif_rotation(path):
    image_reader = QImageReader(path)
    image_reader.setAutoTransform(True)
    qimage = image_reader.read()

    if not qimage.isNull():
        pixmap = QPixmap.fromImage(qimage)
    else:
        pixmap = QPixmap(path)

    return pixmap

class MediaPair(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create layout
        layout = QHBoxLayout()

        # Image drop area with button
        image_layout = QVBoxLayout()
        self.browse_image_button = QPushButton("Browse Image")
        self.image_drop_area = LoadMedia("Drop Image Here", self, "image")  # Changed "photo" to "image"

        image_layout.addWidget(self.browse_image_button)
        image_layout.addWidget(self.image_drop_area)

        # Video drop area with button
        video_layout = QVBoxLayout()
        self.browse_video_button = QPushButton("Browse Video")
        self.video_drop_area = LoadMedia("Drop Video Here", self, "video")

        video_layout.addWidget(self.browse_video_button)
        video_layout.addWidget(self.video_drop_area)

        # connect the buttons to their media pairs
        self.browse_image_button.clicked.connect(self.image_drop_area.open_file_dialog)
        self.browse_video_button.clicked.connect(self.video_drop_area.open_file_dialog)

        # Add layouts to main layout
        layout.addLayout(image_layout)
        layout.addLayout(video_layout)
        self.setLayout(layout)

