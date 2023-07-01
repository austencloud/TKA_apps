from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
import cv2
import numpy as np
import traceback
from PIL import Image

import cv2



def merge(image_path, video_path, output_path, preserve_aspect_ratio=True, progress_callback=None, stop_flag_callback=None):
    try:
        # Load the image
        image = Image.open(image_path)

        if image is None:
            raise ValueError(f"Failed to load the image from: {image_path}")
            
        image = np.array(image)
        # Change image color order from RGB to BGR (to make it compatible with OpenCV)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Obtain image dimensions
        image_height, image_width, _ = image.shape

        # Open the video
        video = cv2.VideoCapture(video_path)
        video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_fps = int(video.get(cv2.CAP_PROP_FPS))
        video_frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        if preserve_aspect_ratio:
            # Maintain aspect ratio, add black borders to make the image square
            max_dim = max(image_width, image_height)
            square_image = np.zeros((max_dim, max_dim, 3), dtype=np.uint8)

            y_offset = (max_dim - image_height) // 2
            x_offset = (max_dim - image_width) // 2
            square_image[y_offset:y_offset+image_height, x_offset:x_offset+image_width] = image

            # Now resize the square image to the video size
            resized_image = cv2.resize(square_image, (video_width, video_height), interpolation=cv2.INTER_LANCZOS4)
            new_image_width = video_width
        else:
            # Resize the image to match the video height while keeping the aspect ratio
            new_image_width = int(image_width * (video_height / image_height))
            resized_image = cv2.resize(image, (new_image_width, video_height), interpolation = cv2.INTER_LANCZOS4)
        
        # Set up the video writer with a new frame size to accommodate the image and video side by side
        combined_width = video_width + new_image_width
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output = cv2.VideoWriter(output_path, fourcc, video_fps, (combined_width, video_height))

        # Process the frames
        current_frame = 0
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break

            if frame is None:
                raise ValueError("Failed to read a frame from the video")

            # Check if a stop was requested
            if stop_flag_callback is not None and stop_flag_callback():
                print("Stopping the video merge process...")
                break

            # Combine the resized image and video frame side by side
            combined_frame = np.hstack((resized_image, frame))

            output.write(combined_frame)

            current_frame += 1
            if progress_callback:
                progress = int((current_frame / video_frame_count) * 100)
                progress_callback(progress)

        # Close the video files
        video.release()
        output.release()

    except Exception as e:
        print("Error in merge:", str(e))
        print(traceback.format_exc())

class MergeFiles(QThread):
    progress_signal = QtCore.pyqtSignal(int)
    stopped = QtCore.pyqtSignal()

    def is_stopped(self):
        return self.stop_flag

    def __init__(self, image_path=None, video_path=None, output_path=None, preserve_aspect_ratio=True):

        super().__init__()
        self.image_path = image_path
        self.video_path = video_path
        self.output_path = output_path
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.stop_flag = False
        

    def run(self):
        try:
            merge(self.image_path, self.video_path, self.output_path, 
                                    preserve_aspect_ratio=self.preserve_aspect_ratio, 
                                    progress_callback=self.progress_signal.emit, 
                                    stop_flag_callback=self.stop_requested)  
        except Exception as e:
            print("Error in ConvertThread:", str(e))
            print(traceback.format_exc())


    def stop(self):
        self.stop_flag = True
        self.stopped.emit() 

    def stop_requested(self):
        return self.stop_flag

    def __init__(self, parent=None):
        from merge_tab import LoadMedia
        super().__init__(parent)
        
        # Create layout
        layout = QHBoxLayout()
        
        # Image drop area with button
        image_layout = QVBoxLayout()
        self.browse_image_button = QPushButton("Browse Image")
        self.image_drop_area = LoadMedia("Drop Image Here", self, "photo")
        self.image_drop_area.path_changed.connect(self.image_drop_area.process_dropped_path)

        # ...
        image_layout.addWidget(self.browse_image_button)
        image_layout.addWidget(self.image_drop_area)
        
        # Video drop area with button
        video_layout = QVBoxLayout()
        self.browse_video_button = QPushButton("Browse Video")
        self.video_drop_area = LoadMedia("Drop Video Here", self, "video")
        self.video_drop_area.path_changed.connect(self.video_drop_area.process_dropped_path)

        # ...
        video_layout.addWidget(self.browse_video_button)
        video_layout.addWidget(self.video_drop_area)

        # connect the buttons to their media pairs
        self.browse_image_button.clicked.connect(self.image_drop_area.open_file_dialog)
        self.browse_video_button.clicked.connect(self.video_drop_area.open_file_dialog)
        
        #display the uploaded media in the appropriate frame
        self.image_drop_area.path_changed.connect(self.video_drop_area.process_dropped_path)
        self.video_drop_area.path_changed.connect(self.image_drop_area.process_dropped_path)

        # Add layouts to main layout
        layout.addLayout(image_layout)
        layout.addLayout(video_layout)
        self.setLayout(layout)
    
    def get_image_path(self):
        return self.image_drop_area.get_path()
    
    def get_video_path(self):
        return self.video_drop_area.get_path()