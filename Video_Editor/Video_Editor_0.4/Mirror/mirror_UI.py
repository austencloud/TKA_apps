from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QFileDialog, QSlider
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt
from .mirror_thread import MirrorThread
import os

class MirrorTab(QWidget):
    def __init__(self, parent=None):
        super(MirrorTab, self).__init__(parent)
        
        self.setWindowTitle("PyQt Video Player")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.openButton = QPushButton("Open Video")
        self.openButton.clicked.connect(self.open_file)

        self.mirrorButton = QPushButton("Mirror")
        self.mirrorButton.clicked.connect(self.process_and_play)
        self.mirrorButton.setEnabled(False)

        self.playButton = QPushButton("Play")
        self.playButton.clicked.connect(self.play_pause)
        self.playButton.setEnabled(False)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.set_position)

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0)  # Indeterminate mode
        self.progressBar.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.openButton)
        layout.addWidget(self.mirrorButton)
        layout.addWidget(self.videoWidget)
        layout.addWidget(self.playButton)
        layout.addWidget(self.positionSlider)
        layout.addWidget(self.progressBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.update_play_button_text)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)
        self.mediaPlayer.mediaStatusChanged.connect(self.media_status_changed)

        self.worker = None


    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename != '':
            url = QUrl.fromUserInput(os.path.abspath(filename))
            self.mediaPlayer.setMedia(QMediaContent(url))
            self.filename = filename
            self.mirrorButton.setEnabled(True)
            self.videoWidget.show()
            self.mediaPlayer.setPosition(0)

    def process_and_play(self):
        import tempfile
        self.mediaPlayer.pause()
        self.mirrorButton.setEnabled(False)

        filename = self.filename

        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_filename = temp_file.name
        temp_file.close()

        self.worker = MirrorThread(filename, temp_filename)
        self.worker.progress_update.connect(self.update_progress_bar)
        self.worker.result_ready.connect(self.finalize_mirror)
        self.worker.start()

        self.progressBar.setRange(0, 100)  # Percent mode
        self.progressBar.show()  # Show the progress bar


    def update_progress_bar(self, progress):
        self.progressBar.setValue(progress)

    def finalize_mirror(self, processed_filename):
        self.progressBar.hide()  # Hide the progress bar
        url = QUrl.fromUserInput(os.path.abspath(processed_filename))
        self.mediaPlayer.setMedia(QMediaContent(url))
        self.playButton.setEnabled(True)
        self.mirrorButton.setEnabled(True)
        self.progressBar.setRange(0, 0)  # Reset to indeterminate mode


    def play_pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def media_status_changed(self, status):
        if status == QMediaPlayer.LoadedMedia:
            self.playButton.setEnabled(True)
            if self.mediaPlayer.position() == 0:  # check if it's the first time the media is being loaded
                self.mediaPlayer.pause()
                
    def update_play_button_text(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playButton.setText("Pause")
        else:
            self.playButton.setText("Play")
            
    def play_pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def position_changed(self, position):
        self.positionSlider.setValue(position)

    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)
