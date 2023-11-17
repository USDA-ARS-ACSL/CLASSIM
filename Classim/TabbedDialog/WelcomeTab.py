import os
from PyQt5.QtWidgets import QTreeWidgetItem, QTabWidget, QLabel, QHBoxLayout, QVBoxLayout, QHeaderView, QTextBrowser
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
#from TabbedDialog.VidTutorial import *
from collections import deque
from pathlib import Path

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDir, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QTextEdit,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QFrame)

global runpath1
global app_dir
global repository_dir

gusername = os.environ['username'] #windows. What about linux

'''
Contains 1 class
1). Class Welcome_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget. It is acting like a index page of a book. It handles all the features of WELCOME Tab on the interface.
    It has signal slot mechanism. It does interact with the DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets
    
    Some of the GLOBALS defined above can be removed sequential after testing. 
    Check out the logic for images/icons.
'''

class Welcome_Widget(QTabWidget):
    # Add a signal to notify parent tab that user has selected following tabindex#     
    welcomesig = pyqtSignal(int)

    def __init__(self):
        super(Welcome_Widget,self).__init__()
        self.init_ui()


    def init_ui(self):
        self.setGeometry(QtCore.QRect(10,20,700,700))
        self.setFont(QtGui.QFont("Calibri",10))
        self.faqtree = QtWidgets.QTreeWidget(self)   
        self.faqtree.setHeaderLabel('FAQ')     
      # self.faqtree.setGeometry(500,200, 300, 500)
        self.faqtree.setUniformRowHeights(False)
        self.faqtree.setWordWrap(True)
       #self.faqtree.setFont(QtGui.QFont("Calibri",10))        
        self.faqtree.header().setStretchLastSection(False)  
        self.faqtree.header().setSectionResizeMode(QHeaderView.ResizeToContents)  
        self.importfaq("welcome")

        
        self.mainlayout1 = QHBoxLayout()  
        self.welcomeglayout1 = QVBoxLayout()  

        self.tab_label = QLabel("Welcome "+ gusername+ " !!")
        self.summary = '''
<p>Crop, Land And Soil SIMulation (CLASSIM) was developed to facilitate the execution of crop models like GLYCIM (soybean), GOSSYM (cotton), MAIZSIM (maize) and SPUDSIM (potato).  
To run the simulation use the Seasonal Run tab or to build a rotation use the Rotation Builder tab.</p>
<p>Before you proceed with the simulation, verify if the necessary information is already on the system otherwise you can add it going to the following tabs</p>
<ol>
    <li>Site</li>
    <li>Soil</li>
    <li>Weather</li>
    <li>Cultivar</li>
    <li>Management</li>
</ol>
<p>The model output can be seen on Seasonal Output or Rotation Output tab.</p>
'''
        self.tab_summary = QTextEdit(self.summary)
        self.tab_summary.setReadOnly(True)        
        # no scroll bars
        self.tab_summary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.tab_summary.setFrameShape(QtWidgets.QFrame.NoFrame)

       
        
        urlLink="<a href=\"https://youtu.be/v22tXNg1vCg/\">Click here to watch \
        the Welcome Tab video tutorial. </a><br>"
        self.welcomeVidlabel=QLabel()
        self.welcomeVidlabel.setOpenExternalLinks(True)
        self.welcomeVidlabel.setText(urlLink)
        

        self.ClassimGraph = QLabel()
        self.pixmap = QPixmap("./images/classim.png")
        self.ClassimGraph.setPixmap(self.pixmap)
 
        self.USDAGraph = QLabel()
        self.USDApixmap = QPixmap("./images/USDA_logo.png")
        self.USDAGraph.setPixmap(self.USDApixmap)      

        self.welcomeglayout1.addWidget(self.USDAGraph)
        self.USDAGraph.resize(self.USDApixmap.width(),self.USDApixmap.height())
        self.welcomeglayout1.addWidget(self.tab_label)        
        self.welcomeglayout1.addWidget(self.tab_summary)
        self.welcomeglayout1.addWidget(self.welcomeVidlabel)
        self.welcomeglayout1.addWidget(self.ClassimGraph)
        self.ClassimGraph.resize(self.pixmap.width(),self.pixmap.height())
        self.welcomeglayout1.addStretch()

        self.mainlayout1.addLayout(self.welcomeglayout1)
        self.mainlayout1.addWidget(self.faqtree)
     
        self.setLayout(self.mainlayout1) 
        

    def importfaq(self, thetabname=None):        
        faqlist = read_FaqDB(thetabname,'') 
      

        for item in faqlist:
            roottreeitem = QTreeWidgetItem(self.faqtree)
            roottreeitem.setText(0,item[2])
            childtreeitem = QTreeWidgetItem()
            childtreeitem.setText(0,item[3])
            roottreeitem.addChild(childtreeitem)
