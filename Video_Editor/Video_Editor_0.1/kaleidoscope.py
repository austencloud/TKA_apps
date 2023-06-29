import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl


class VideoWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Video Player")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.openButton = QPushButton("Open Video")
        self.openButton.clicked.connect(self.open_file)

        layout = QVBoxLayout()
        layout.addWidget(self.openButton)
        layout.addWidget(self.videoWidget)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.process_and_play(filename)

    def process_and_play(self, filename):
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        name, ext = os.path.splitext(basename)
        processed_name = f'{name}_mirrored{ext}'
        processed_filename = os.path.join(dirname, processed_name)
        temp_filename = os.path.join(dirname, 'processed_temp.mp4')
        crop_filename = os.path.join(dirname, 'crop.mp4')

        # Detect the crop values
        command = [
            'ffmpeg',
            '-i', filename,
            '-vf', 'cropdetect=24:16:0',
            '-f', 'null', '-'
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        crop_line = [line for line in result.stderr.split('\n') if 'crop=' in line]
        crop_values = crop_line[-1][crop_line[-1].index('crop='):].split(' ')[0]

        # Crop the video
        command = [
            'ffmpeg',
            '-i', filename,
            '-vf', crop_values,
            '-c:v', 'libx264',
            '-c:a', 'copy',
            crop_filename
        ]
        subprocess.run(command, check=True)
        # Create the mirrored video (right side)
        command = [
            'ffmpeg',
            '-i', crop_filename,
            '-filter_complex', '[0:v]split[m][a];[a]hflip[b];[m][b]hstack',
            '-c:v', 'libx264',
            '-c:a', 'copy',
            temp_filename
        ]
        subprocess.run(command, check=True)

        # Create the mirrored video (top side)
        command = [
            'ffmpeg',
            '-i', temp_filename,
            '-filter_complex', '[0:v]split[m][a];[a]vflip[b];[m][b]vstack',
            '-c:v', 'libx264',
            '-c:a', 'copy',
            processed_filename
        ]
        subprocess.run(command, check=True)

        # Clean up the temporary files
        os.remove(temp_filename)
        os.remove(crop_filename)

        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(processed_filename)))
        self.mediaPlayer.play()



app = QApplication(sys.argv)

window = VideoWindow()
window.show()

sys.exit(app.exec_())