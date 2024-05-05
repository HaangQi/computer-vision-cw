from PyQt5.QtCore import QThread, pyqtSignal
from panorama import panorama
class WorkerThread(QThread):
    finished = pyqtSignal(object)  # Used to pass processing results
    error = pyqtSignal(Exception)  # Used to pass errors

    def __init__(self, video_path, frame_step, filter_enable, sharp_enable):
        super().__init__()
        self.video_path = video_path
        self.frame_step = frame_step
        self.filter_enable = filter_enable
        self.sharp_enable = sharp_enable

    def run(self):
        try:
            panorama_creator = panorama(self.video_path, self.frame_step, self.filter_enable, self.sharp_enable)
            panorama_image = panorama_creator.create_panorama()
            if panorama_image is not None:
                self.finished.emit(panorama_image)
            else:
                raise ValueError("Panorama creation failed: No image returned.")
        except Exception as e:
            self.error.emit(e)


