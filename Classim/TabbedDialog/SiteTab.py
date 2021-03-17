import os
import math
from DatabaseSys.Databasesupport import extract_sitedetails
from PyQt5 import QtSql
from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QHBoxLayout, QTableWidgetItem, QComboBox, QVBoxLayout, \
                            QPushButton, QSpacerItem, QSizePolicy, QHeaderView
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from DatabaseSys.Databasesupport import *
from TabbedDialog.tableWithSignalSlot import *
from CustomTool.UI import *
global runpath1
global twodsoilexe
global createsoilexe
global rosettaexe
global app_dir
global repository_dir

'''F
Contains 2 classes and some GLOBALS. These GLOBALS can be refined and moved to centralized place, at the 
momemt lower priority.
1). Class ItemWordWrap is to assist the text wrap features. You will find this class at the top of all the
    tab classes. In future,we can centralize it. Lower priority.

2). Class Field_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget. 
    It handles all the features of SITE Tab on the interface.
    It has signal slot mechanism. It does interact with the DatabaseSys\Databasesupport.py for all the 
    databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets

    Tab screen is divided into 2 main panels.
    Left panel does the heavy lifting and interacts with user. 
    Right panel is mainly for frequently asked questions (FAQ) stored in sqlite table "Faq".
'''
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

runpath1= run_dir
repository_dir = os.path.join(runpath1,'store')

## This should always be there
if not os.path.exists(repository_dir):
    print('SiteTab Error: Missing repository_dir')

class ItemWordWrap(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.parent = parent


    def paint(self, painter, option, index):
        text = index.model().data(index) 
                
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
        text = index.model().data(index)
        document = QtGui.QTextDocument()
        document.setHtml(text) 
        width = index.model().data(index, QtCore.Qt.UserRole+1)
        if not width:
            width = 20
        document.setTextWidth(width) 
        return QtCore.QSize(document.idealWidth() + 10,  document.size().height())


class SiteWidget(QWidget):
    def __init__(self):
        super(SiteWidget,self).__init__()
        self.init_ui()


    def init_ui(self):
        self.setGeometry(QtCore.QRect(10,20,700,700))
        self.setFont(QtGui.QFont("Calibri",10))
        self.faqtree = QtWidgets.QTreeWidget(self)   
        self.faqtree.setHeaderLabel('FAQ')     
        self.faqtree.setGeometry(500,200, 400, 300)
        self.faqtree.setUniformRowHeights(False)
        self.faqtree.setWordWrap(True)
        self.faqtree.setFont(QtGui.QFont("Calibri",10))        
        self.importfaq("field")              
        self.faqtree.header().resizeSection(1,200)       
        self.faqtree.setItemDelegate(ItemWordWrap(self.faqtree))
        self.faqtree.setVisible(False)

        self.tab_summary = QTextEdit("")        
        self.tab_summary.setPlainText("Here we identify our agriculture SITE (for simulation purposes) with latitude, longitude and a name. From the LIST box underneath, we can define our SITE or update the existing SITE.") 
        self.tab_summary.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tab_summary.setReadOnly(True)  
        self.tab_summary.setMinimumHeight(10)    
        self.tab_summary.setAlignment(QtCore.Qt.AlignTop)
        # no scroll bars
        self.tab_summary.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.tab_summary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.tab_summary.setFrameShape(QtWidgets.QFrame.NoFrame)      
        self.helpcheckbox = QCheckBox("Turn FAQ on?")
        self.helpcheckbox.setChecked(False)
        self.helpcheckbox.stateChanged.connect(self.controlfaq)
       
        self.mainlayout = QGridLayout()
        self.spacer = QSpacerItem(10,10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vHeader = QVBoxLayout()
        self.vHeader.setContentsMargins(0,0,0,0)
        self.vHeader.addWidget(self.tab_summary)
        self.vHeader.addWidget(self.helpcheckbox)
        self.vHeader.setAlignment(QtCore.Qt.AlignTop)

        ## Setting up the form elements    
        self.sitelabel = QLabel("Site:")
        self.sitecombo = QComboBox()
        self.sitelabel.setBuddy(self.sitecombo)
        self.sitelists = sorted(read_sitedetailsDB())
        # this way we don't need this entry in database and it is always on the top of the combo
        self.sitecombo.addItem("Select from list") 
        self.sitecombo.addItem("Add New Site") 
        for item in sorted(self.sitelists):            
            self.sitecombo.addItem(item)
        self.sitecombo.currentIndexChanged.connect(self.showsitedetails)

        self.rlatlabel = QLabel("Latitude (deg)")
        self.rlatedit = QLineEdit("")
        self.rlonlabel = QLabel("Longitude (deg)")
        self.rlonedit = QLineEdit("")
        self.altlabel = QLabel("Altitude (m)")
        self.altedit = QLineEdit("")
        self.sitenamelabel = QLabel("Site Name")
        self.sitenameedit = QLineEdit("")
        self.savebutton = QPushButton("Update")        
        self.deletebutton = QPushButton("Delete")        

        self.mainlayout.addLayout(self.vHeader,0,0,1,4)
        self.mainlayout.addWidget(self.faqtree,0,4,2,1)       
        self.mainlayout.addWidget(self.sitelabel,1,0)
        self.mainlayout.addWidget(self.sitecombo,1,1)
        self.mainlayout.addWidget(self.rlatlabel,2,0)
        self.mainlayout.addWidget(self.rlatedit,2,1)
        self.mainlayout.addWidget(self.rlonlabel,3,0)
        self.mainlayout.addWidget(self.rlonedit,3,1)
        self.mainlayout.addWidget(self.altlabel,4,0)
        self.mainlayout.addWidget(self.altedit,4,1)
        self.mainlayout.addWidget(self.sitenamelabel,5,0)
        self.mainlayout.addWidget(self.sitenameedit,5,1)
        self.mainlayout.addWidget(self.savebutton,5,2)
        self.mainlayout.addWidget(self.deletebutton,5,3)
        self.rlatlabel.setVisible(False)
        self.rlatedit.setVisible(False)
        self.rlonlabel.setVisible(False)
        self.rlonedit.setVisible(False)
        self.altlabel.setVisible(False)
        self.altedit.setVisible(False)
        self.sitenamelabel.setVisible(False)
        self.sitenameedit.setVisible(False)
        self.savebutton.setVisible(False)       
        self.deletebutton.setVisible(False)        
        self.setLayout(self.mainlayout) 


    def showsitedetails(self,value):
        '''
        Prepare view for SITE related information.
        '''
        self.rlatlabel.setVisible(False)
        self.rlatedit.setVisible(False)
        self.rlonlabel.setVisible(False)
        self.rlonedit.setVisible(False)
        self.altlabel.setVisible(False)
        self.altedit.setVisible(False)
        self.sitenamelabel.setVisible(False)
        self.sitenameedit.setVisible(False)
        self.savebutton.setVisible(False)       
        self.deletebutton.setVisible(False)        

        sitename = str(self.sitecombo.currentText())
        if sitename == "Select from list":
            return True

        self.rlatlabel.setVisible(True)
        self.rlatedit.setVisible(True)
        self.rlonlabel.setVisible(True)
        self.rlonedit.setVisible(True)
        self.altlabel.setVisible(True)
        self.altedit.setVisible(True)
        self.sitenamelabel.setVisible(True)
        self.sitenameedit.setVisible(True)
        self.savebutton.setVisible(True)       

        if sitename == 'Add New Site':            
            self.rlatedit.setText("")
            self.rlonedit.setText("")
            self.altedit.setText("")
            self.sitenameedit.setText("")
            self.savebutton.setText("SaveAs")            
            self.deletebutton.setVisible(False)              
        else:
            site_tuple = extract_sitedetails(self.sitecombo.itemText(value))     
            self.rlatedit.setText(str(site_tuple[1]))
            self.rlonedit.setText(str(site_tuple[2]))
            self.altedit.setText(str(site_tuple[3]))
            self.sitenameedit.setText(self.sitecombo.itemText(value))            
            
            if self.sitenameedit.isReadOnly() == False:
                self.sitenameedit.setReadOnly(True)
  
            self.sitenamelabel.setVisible(False)
            self.sitenameedit.setVisible(False)      
            self.savebutton.setText("Update")
            self.deletebutton.setVisible(True)
       
        self.savebutton.clicked.connect(lambda:self.on_savebuttonclick(self.sitenameedit.text()))
        self.deletebutton.clicked.connect(lambda:self.on_deletebuttonclick(sitename))
        

    @pyqtSlot()
    def on_savebuttonclick(self,item1):
        '''
        aim: to save the SITE view data to field table
        '''
        #here table current_crop_simulation will be cleaned first and then filled with the values from all
        newSitename = str(self.sitenameedit.text())
        if(newSitename == ""):
            messageUser("Site Name is empty, please provide a name.")
            return False

        record_tuple=(newSitename,float(self.rlatedit.text()),float(self.rlonedit.text()),float(self.altedit.text()))

        c1=insert_update_sitedetails(record_tuple,self.savebutton.text())
        if c1:
            self.sitecombo.clear()
            self.sitelists = read_sitedetailsDB() 
            self.sitecombo.addItem("Select from list") 
            self.sitecombo.addItem("Add New Site") 
            for item in sorted(self.sitelists):            
                self.sitecombo.addItem(item)
        else:
            messageUser("Failed: Site exists. Change SITE name.")
            return False


    def importfaq(self, thetabname=None):        
        #faqlist = read_FaqDB() 
        faqlist = read_FaqDB(thetabname) 
        faqcount=0
        
        for item in faqlist:
            roottreeitem = QTreeWidgetItem(self.faqtree)
            roottreeitem.setText(0,item[2])
            childtreeitem = QTreeWidgetItem()
            childtreeitem.setText(0,item[3])
            roottreeitem.addChild(childtreeitem)


    @pyqtSlot()
    def on_deletebuttonclick(self,sitename):
        '''
        aim: delete the SITE data in field table
        '''
        delete_flag = messageUserDelete("Are you sure you want to delete this record?")
        if delete_flag:
            record_tuple=(str(sitename),)
            c1=delete_sitedetails(record_tuple)
            if c1:
                self.sitecombo.clear()
                self.sitelists = read_sitedetailsDB() #read_fieldDB()
                # this way we don't need this entry in database and it is always on the top of the combo                
                self.sitecombo.addItem("Select from list") 
                self.sitecombo.addItem("Add New Site") 
                for item in sorted(self.sitelists):            
                    self.sitecombo.addItem(item)


    def controlfaq(self):                
        if self.helpcheckbox.isChecked():
            self.faqtree.setVisible(True)
        else:
            self.faqtree.setVisible(False)

        
    def resource_path(self,relative_path):
        """
        Get absolute path to resource, works for dev and for PyInstaller 
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)            