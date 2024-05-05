import sys
import cv2
from PyQt5 import QtWidgets, QtCore, QtGui
from Ui_UI import Ui_MainWindow  
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMessageBox,QProgressDialog
from moviepy.editor import VideoFileClip
from thread import WorkerThread
import matplotlib.pyplot as plt


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)  # UI setting
        self.initUI()

    def initUI(self):
        self.setFixedSize(621, 386)
        self.pushButton.clicked.connect(self.on_click_file_button)
        self.pushButton_2.clicked.connect(self.on_click_run_button)
        self.listWidget.setIconSize(QtCore.QSize(128, 128))  
        self.listWidget.setAcceptDrops(True)
        self.listWidget.dragEnterEvent = self.dragEnterEvent
        self.listWidget.dropEvent = self.dropEvent

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.listWidget.clear()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')):
                        self.addVideoToList(file_path)
            event.acceptProposedAction()

    def addVideoToList(self, file_path):
        clip = VideoFileClip(file_path)
        frame = clip.get_frame(0)  # Get the first frame of the video
        clip.close()

        # Create QImage
        frame_image = QtGui.QImage(frame.tobytes(), frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        frame_image = frame_image.rgbSwapped()  

        # Create QPixmap
        pixmap = QPixmap.fromImage(frame_image)
        scaled_pixmap = pixmap.scaled(128, 128, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)  # Scaled

        # Add into listwidget
        item = QtWidgets.QListWidgetItem()
        item.setIcon(QIcon(scaled_pixmap)) 
        self.listWidget.addItem(item)
        self.lineEdit.setText(file_path)  # Update LineEdit 



    def on_click_file_button(self):
        filter = "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv)"
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Video File", "", filter)
        if file_name:
            self.listWidget.clear()
            self.addVideoToList(file_name)

    def on_click_run_button(self):
        video_path = self.lineEdit.text()
        if not video_path:
            QMessageBox.critical(self, "Error", "No video selected!")
            return

        frame_step = self.spinBox.value()
        filter_enable = self.checkBox_2.isChecked()
        sharp_enable = self.checkBox.isChecked()

        # Creating and displaying progress dialogs
        self.progressDialog = QProgressDialog("Processing the panorama, please wait...", None, 0, 0, self)
        self.progressDialog.setCancelButton(None) 
        self.progressDialog.setModal(True)  
        self.progressDialog.show()

        # Create thread
        self.thread = WorkerThread(video_path, frame_step, filter_enable, sharp_enable)
        self.thread.finished.connect(self.display_panorama)
        self.thread.error.connect(self.handle_error)
        self.thread.finished.connect(self.progressDialog.close)  
        self.thread.error.connect(self.progressDialog.close)  
        self.thread.start()  

    def display_panorama(self, panorama_image):
        
        rgb_image = cv2.cvtColor(panorama_image, cv2.COLOR_BGR2RGB)
        
        # Use Matplotlib
        plt.imshow(rgb_image)
        plt.axis('off') 
        plt.show()
        
    def handle_error(self, error):
        QMessageBox.critical(self, "Error", f"Failed to create panorama: {str(error)}")




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
