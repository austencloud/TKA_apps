from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QFont, QImageReader
from PyQt5.QtCore import Qt, pyqtSignal
import cv2
import random

from pathlib import Path
import os
import logging

class PreviewGraphicsView(QGraphicsView):
    def update_progressbar(self, fraction):
        self.main_window.progress.setValue(fraction * 100)
        QApplication.processEvents()

    def __init__(self, text, parent=None, file_type=None):
        logging.debug("Initializing PreviewGraphicsView")
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.pixmap = None
        self.text = text
        self.file_type = "image" if text == "Drop Image Here" else "video"
        self.set_text(self.text)
        self.main_window = parent
        self.path_type = file_type 

    def open_file_dialog(self):
        options = QFileDialog.Options()
        home_dir = str(Path.home())
        my_pictures = os.path.join(home_dir, 'Pictures')
        my_videos = os.path.join(home_dir, 'Videos')
        initial_dir = my_pictures if self.file_type == "image" else my_videos

        file_filter = "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)" if self.file_type == "image" else "Videos (*.mp4 *.avi *.mkv *.webm *.mov);;All Files (*)"
        file, _ = QFileDialog.getOpenFileName(None, "Open File", initial_dir, file_filter, options=options)
        if file:
            return file

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
