import os
import sys
sys.path.insert(0, './helper')
from module_soiltriangle import *
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTabWidget, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, \
                            QVBoxLayout, QSpacerItem, QSizePolicy, QHeaderView
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
from collections import deque
from pathlib import Path

global runpath1
global twodsoilexe
global createsoilexe
global rosettaexe
global app_dir
global repository_dir

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
app_dir = os.path.join(gparent_dir,'crop_int')
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

twodsoilexe= app_dir+'\\2dsoil.exe'
createsoilexe= app_dir+'\\createsoilfiles.exe'
rosettaexe= app_dir+'\\rosetta.exe'

run_dir = os.path.join(app_dir,'run')
if not os.path.exists(run_dir):
    os.makedirs(run_dir)

runpath1 = run_dir
repository_dir = os.path.join(runpath1,'store')

## This should always be there
if not os.path.exists(repository_dir):
    print('RotationTab Error: Missing repository_dir')

'''
Contains 2 classes.
1). Class ItemWordWrap is to assist the text wrap features. You will find this class at the top of all the tab classes. In future,we can centralize it. Lower priority.

2). Class Welcome_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget. It is acting like a index page of a book. It handles all the features of WELCOME Tab on the interface.
    It has signal slot mechanism. It does interact with the DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets
    
    Some of the GLOBALS defined above can be removed sequential after testing. 
    Check out the logic for images/icons.
'''

#this is widget of type 1. It would be added to as a tab
class ItemWordWrap(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.parent = parent


    def paint(self, painter, option, index):
        text = index.model().data(index) 
        #print("text=", text)
                
        document = QtGui.QTextDocument() 
        document.setHtml(text) 
        
        document.setTextWidth(option.rect.width())  #keeps text from spilling over into adjacent rect
        index.model().setData(index, option.rect.width(), QtCore.Qt.UserRole+1)
        painter.setPen(QtGui.QPen(Qt.blue))        
        painter.save() 
        painter.translate(option.rect.x(), option.rect.y())         
        document.drawContents(painter)  #draw the document with the painter        
        painter.restore() 


    def sizeHint(self, option, index):
        #Size should depend on number of lines wrapped
        text = index.model().data(index)
        document = QtGui.QTextDocument()
        document.setHtml(text) 
        width = index.model().data(index, QtCore.Qt.UserRole+1)
        if not width:
            width = 20
        document.setTextWidth(width) 
        return QtCore.QSize(document.idealWidth() + 10,  document.size().height())


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
        self.faqtree.setGeometry(500,200, 300, 500)
        self.faqtree.setUniformRowHeights(False)
        self.faqtree.setWordWrap(True)
        self.faqtree.setFont(QtGui.QFont("Calibri",10))
        self.importfaq("welcome")
        self.faqtree.header().resizeSection(1,200)
        self.faqtree.setItemDelegate(ItemWordWrap(self.faqtree))
        
        self.mainlayout1 = QHBoxLayout()  
        self.welcomeglayout1 = QVBoxLayout()  
        
        self.tab_label = QLabel("Welcome "+ gusername+ " !!")
        self.summary = '''
<p>Crop, Land And Soil SIMulation (CLASSIM) was developed to facilitate the execution of crop models like MAIZSIM and SPUDSIM.  
To run the simulation use the Rotation Builder tab.</p>
<>Before you proceed with the simulation, verify if the necessary information is already on the system otherwise you can add it going to the following tabs</p>
<ol>
    <li>Site</li>
    <li>Soil</li>
    <li>Weather</li>
    <li>Cultivar</li>
    <li>Management</li>
</ol>
<p>After the simulation is completed, go to Output tab to see the simulation summary and to plot graphics.</p>
'''
        self.tab_summary = QTextEdit(self.summary)
        self.tab_summary.setReadOnly(True)        
        # no scroll bars
        self.tab_summary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.tab_summary.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.ClassimGraph = QLabel()
        self.pixmap = QPixmap("./images/classim.png")
        self.ClassimGraph.setPixmap(self.pixmap)
 
        self.USDAGraph = QLabel()
        self.USDApixmap = QPixmap("./images/USDA_logo.png")
        self.USDAGraph.setPixmap(self.USDApixmap)
                      
        self.welcomeglayout1.addWidget(self.USDAGraph)
        self.welcomeglayout1.addWidget(self.tab_label)        
        self.welcomeglayout1.addWidget(self.tab_summary)
        self.welcomeglayout1.addWidget(self.ClassimGraph)
        self.welcomeglayout1.addStretch()

        self.mainlayout1.addLayout(self.welcomeglayout1)
        self.mainlayout1.addWidget(self.faqtree)
        self.setLayout(self.mainlayout1) 
        

    def importfaq(self, thetabname=None):        
        faqlist = read_FaqDB(thetabname) 
        faqcount=0
        
        for item in faqlist:
            roottreeitem = QTreeWidgetItem(self.faqtree)
            roottreeitem.setText(0,item[2])
            childtreeitem = QTreeWidgetItem()
            childtreeitem.setText(0,item[3])
            roottreeitem.addChild(childtreeitem)
