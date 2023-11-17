# Install K-Lite http://www.codecguide.com/configuration_tips.htm?version=1766
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QTextEdit,QTabWidget,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QFrame)




class VideoPlayer(QWidget):

    def __init__(self, var, parent=None):
        #super(VideoPlayer, self).__init__(parent)
        super().__init__()

        self.setWindowTitle("Welcome Video")
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        btnSize = QSize(16, 16)
        self.videoWidget = QVideoWidget()
        
      #  self.openButton = QPushButton("Open Video")   
     #   self.openButton.setToolTip("Open Video File")
       # self.openButton.setStatusTip("Open Video File")
      #  self.openButton.setFixedHeight(24)
      #  self.openButton.setIconSize(btnSize)
      #  self.openButton.setFont(QFont("Noto Sans", 8))
      #  openButton.setIcon(QIcon.fromTheme("document-open", QIcon("D:/_Qt/img/open.png")))
    #    self.openButton.clicked.connect(self.abrir)

        #self.label = QLabel('Video')
        #self.label.setFixedSize(60, 30)
        #self.label.setStyleSheet('color: blue')


        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
     #   self.playutton.setCheckable(True)
      #  self.playButton.setToolTip("Open Video File")
      #  self.playButton.setStatusTip("Open Video File")
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playing = False
        self.playButton.clicked.connect(lambda: self.play(var))
        #self.playButton.clicked.connect(self.abrir)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 7))
        self.statusBar.setFixedHeight(14)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        #controlLayout.addWidget(self.openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    
        
    def play(self, var):
        if var == 'welcome':
            fileName = r".\video\welcome_tab_version1.avi"

        self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
        if self.playing:
            self.mediaPlayer.pause()
            self.playing = False
        else:
            self.mediaPlayer.play()
            self.playing = True

     #   self.mediaPlayer.play()

      #  self.playButton.clicked.connect(lambda: self.mediaPlayer.pause())
        

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())