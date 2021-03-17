from PyQt5 import QtSql, QtCore, QtGui
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, \
                            QComboBox, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QRadioButton, QButtonGroup
from PyQt5.QtCore import pyqtSlot
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *

import re

'''
Contains 2 classes.
1). Class ItemWordWrap is to assist the text wrap features. You will find this class at the top of all the
    tab classes. In future,we can centralize it. Lower priority.

2). Class Cultivar_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget.
    It handles all the features of Cultivar Tab on the interface.  It has signal slot mechanism. It 
    interact with the DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets

    Tab screen is divided into 2 main panels.
    Left panel does the heavy lifting and interacts with user. 
    Right panel is mainly for frequently asked questions (FAQ) stored in sqlite table "Faq".
'''
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
        #Size should depend on number of lines wrapped
        text = index.model().data(index)
        document = QtGui.QTextDocument()
        document.setHtml(text) 
        width = index.model().data(index, QtCore.Qt.UserRole+1)
        if not width:
            width = 20
        document.setTextWidth(width) 
        return QtCore.QSize(document.idealWidth() + 10,  document.size().height())


#this is widget of type 1. It would be added to as a tab
class Cultivar_Widget(QWidget):
    def __init__(self):
        super(Cultivar_Widget,self).__init__()
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
        self.importfaq("cultivar")              
        self.faqtree.header().resizeSection(1,200)       
        self.faqtree.setItemDelegate(ItemWordWrap(self.faqtree))
        self.faqtree.setVisible(False)

        self.tab_summary = QTextEdit("")        
        self.tab_summary.setPlainText("CULITVAR means different varieties of a CROP. For example, CORN crop could be 90 or 120 maturity day crop. There are other specific parameters related to a crop variety. This tab allows to build a new crop variety from the default one and customize it further needs.") 
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
        self.croplistlabel = QLabel("Select Crop")        
        self.cropcombo = QComboBox()       
        self.croplistlabel.setBuddy(self.cropcombo)
        self.croplists = sorted(read_cropDB())        
        self.cropcombo.addItem("Select a crop") 
        for key in sorted(self.croplists):            
            self.cropcombo.addItem(key)
        self.cropcombo.currentIndexChanged.connect(self.showcultivarcombo,self.cropcombo.currentIndex())

        self.cultivarlistlabel = QLabel("Cultivar List")
        self.cultivarcombo = QComboBox()
        self.cultivarlistlabel.setBuddy(self.cultivarcombo)

        ###### Creating corn fields #####
        self.daylengthabel = QLabel("Daylength Sensitive")
        self.daylength_b1 = QRadioButton("Yes")
        self.daylength_b2 = QRadioButton("No")
        self.daylength_g = QButtonGroup()
        self.daylength_b1.setChecked(True)
        self.daylength_g.addButton(self.daylength_b1,1)
        self.daylength_g.addButton(self.daylength_b2,2)
        self.leaveslabel = QLabel("JuvenileLeaves")
        self.leavesedit = QLineEdit("")
        self.ltarlabel = QLabel("Rmax_LTAR")
        self.ltaredit = QLineEdit("0.46")
        self.ltirlabel = QLabel("Rmax_LTIR")
        self.ltiredit = QLineEdit("0.8")
        self.tassellabel = QLabel("PhyllFrmTassel")
        self.tasseledit = QLineEdit("4.0")
        self.staygreenlavel = QLabel("StayGreen")
        self.staygreenedit = QLineEdit("2.0")

        ###### Creating potato fields #####
        self.dailyAirTempEffectLabel = QLabel("Daily Air Temperature Effect")
        self.dailyAirTempEffectEdit = QLineEdit("")
        self.dailyAirTempAmpEffectLabel = QLabel("Daily Air Temperature Amplitude Effec")
        self.dailyAirTempAmpEffectEdit = QLineEdit("")
        self.photoEffectLabel = QLabel("Photoperiod Effect")
        self.photoEffectEdit = QLineEdit("")
        self.highNiEffectLabel = QLabel("High Nitrogen Effect")
        self.highNiEffectEdit = QLineEdit("")
        self.lowNiEffectLabel = QLabel("Low Nitrogen Effect")
        self.lowNiEffectEdit = QLineEdit("")
        self.determLabel = QLabel("Determinacy")
        self.determEdit = QLineEdit("")
        self.maxCanLeafExpRateLabel = QLabel("Maximum Canopy Leaf Expansion Rate")
        self.maxCanLeafExpRateEdit = QLineEdit("")
        self.maxTuberGrowthRateLabel = QLabel("Maximum Tuber Growth Rate")
        self.maxTuberGrowthRateEdit = QLineEdit("")
        self.specificLeafWeightLabel = QLabel("Specific Leaf Weight")
        self.specificLeafWeightEdit = QLineEdit("")

        self.cultivarnamelabel = QLabel("Cultivar Name")
        self.cultivarnameedit = QLineEdit("")
        self.cultivarbutton = QPushButton("Update")
        self.cultivardeletebutton = QPushButton("Delete")

        # Set main layout
        self.mainlayout.addLayout(self.vHeader,0,0,1,4)
        self.mainlayout.addWidget(self.faqtree,0,4,2,1)       
        self.mainlayout.addWidget(self.croplistlabel,1,0)
        self.mainlayout.addWidget(self.cropcombo,1,1,1,2)
        self.mainlayout.addWidget(self.cultivarlistlabel,2,0)
        self.mainlayout.addWidget(self.cultivarcombo,2,1,1,2)
 
        # Corn
        self.mainlayout.addWidget(self.daylengthabel,3,0)
        self.mainlayout.addWidget(self.daylength_b1,3,1)
        self.mainlayout.addWidget(self.daylength_b2,3,2)
        self.mainlayout.addWidget(self.leaveslabel,4,0)
        self.mainlayout.addWidget(self.leavesedit,4,1,1,2)
        self.mainlayout.addWidget(self.ltarlabel,5,0)
        self.mainlayout.addWidget(self.ltaredit,5,1,1,2)
        self.mainlayout.addWidget(self.ltirlabel,6,0)
        self.mainlayout.addWidget(self.ltiredit,6,1,1,2)
        self.mainlayout.addWidget(self.tassellabel,7,0)
        self.mainlayout.addWidget(self.tasseledit,7,1,1,2)
        self.mainlayout.addWidget(self.staygreenlavel,8,0)
        self.mainlayout.addWidget(self.staygreenedit,8,1,1,2)

        # Potato
        self.mainlayout.addWidget(self.dailyAirTempEffectLabel,9,0)
        self.mainlayout.addWidget(self.dailyAirTempEffectEdit,9,1,1,2)
        self.mainlayout.addWidget(self.dailyAirTempAmpEffectLabel,10,0)
        self.mainlayout.addWidget(self.dailyAirTempAmpEffectEdit,10,1,1,2)
        self.mainlayout.addWidget(self.photoEffectLabel,11,0)
        self.mainlayout.addWidget(self.photoEffectEdit,11,1,1,2)
        self.mainlayout.addWidget(self.highNiEffectLabel,12,0)
        self.mainlayout.addWidget(self.highNiEffectEdit,12,1,1,2)
        self.mainlayout.addWidget(self.lowNiEffectLabel,13,0)
        self.mainlayout.addWidget(self.lowNiEffectEdit,13,1,1,2)
        self.mainlayout.addWidget(self.determLabel,14,0)
        self.mainlayout.addWidget(self.determEdit,14,1,1,2)
        self.mainlayout.addWidget(self.maxCanLeafExpRateLabel,15,0)
        self.mainlayout.addWidget(self.maxCanLeafExpRateEdit,15,1,1,2)
        self.mainlayout.addWidget(self.maxTuberGrowthRateLabel,16,0)
        self.mainlayout.addWidget(self.maxTuberGrowthRateEdit,16,1,1,2)
        self.mainlayout.addWidget(self.specificLeafWeightLabel,17,0)
        self.mainlayout.addWidget(self.specificLeafWeightEdit,17,1,1,2)

        # Last line in the form
        self.mainlayout.addWidget(self.cultivarnamelabel,18,0)
        self.mainlayout.addWidget(self.cultivarnameedit,18,1,1,2)
        self.mainlayout.addWidget(self.cultivarbutton,18,3)
        self.mainlayout.addWidget(self.cultivardeletebutton,18,4)

        self.cultivarcombo.setVisible(False)
        self.cultivarlistlabel.setVisible(False)

        self.cornFieldSwitch(False)
        self.potatoFieldSwitch(False)

        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        
        self.setLayout(self.mainlayout) 

 
    def cornFieldSwitch(self, state):
        self.daylengthabel.setVisible(state)
        self.daylength_b1.setVisible(state)
        self.daylength_b2.setVisible(state)
        self.leaveslabel.setVisible(state)
        self.leavesedit.setVisible(state)
        self.ltarlabel.setVisible(state)
        self.ltaredit.setVisible(state)
        self.ltirlabel.setVisible(state)
        self.ltiredit.setVisible(state)
        self.tassellabel.setVisible(state)
        self.tasseledit.setVisible(state)
        self.staygreenlavel.setVisible(state)
        self.staygreenedit.setVisible(state)
        return True


    def potatoFieldSwitch(self,state):
        self.dailyAirTempEffectLabel.setVisible(state)
        self.dailyAirTempEffectEdit.setVisible(state)
        self.dailyAirTempAmpEffectLabel.setVisible(state)
        self.dailyAirTempAmpEffectEdit.setVisible(state)
        self.photoEffectLabel.setVisible(state)
        self.photoEffectEdit.setVisible(state)
        self.highNiEffectLabel.setVisible(state)
        self.highNiEffectEdit.setVisible(state)
        self.lowNiEffectLabel.setVisible(state)
        self.lowNiEffectEdit.setVisible(state)
        self.determLabel.setVisible(state)
        self.determEdit.setVisible(state)
        self.maxCanLeafExpRateLabel.setVisible(state)
        self.maxCanLeafExpRateEdit.setVisible(state)
        self.maxTuberGrowthRateLabel.setVisible(state)
        self.maxTuberGrowthRateEdit.setVisible(state)
        self.specificLeafWeightLabel.setVisible(state)
        self.specificLeafWeightEdit.setVisible(state)
        return True

    def showcultivarcombo(self,cropindex):
        cropname = self.cropcombo.currentText()

        self.cultivarcombo.setVisible(False)
        self.cultivarlistlabel.setVisible(False)

        self.cornFieldSwitch(False)
        self.potatoFieldSwitch(False)

        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        

        if cropname != "Select a crop":
            self.cultivarcombo.setVisible(True)
            self.cultivarlistlabel.setVisible(True)

            cultivarlists = read_cultivar_DB(cropname) 
            self.cultivarcombo.clear()
            self.cultivarcombo.addItem("Select from list")    
            self.cultivarcombo.addItem("Add New Cultivar ("+cropname+")") 
            for key in sorted(cultivarlists):
                key_aux = cropname + ":" + str(key)
                self.cultivarcombo.addItem(key_aux)   
                self.cultivarcombo.currentIndexChanged.connect(self.showcultivardetailscombo,cropindex)
        return True


    def showcultivardetailscombo(self,cropindex):
        cultivarname = self.cultivarcombo.currentText()

        self.cornFieldSwitch(False)
        self.potatoFieldSwitch(False)

        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        

        if cultivarname == "Select from list":  
            return True
        else:      
            if cultivarname.find(":") != -1:
                (crop,cultivar) = cultivarname.split(":")
                action = "Update"
                self.cultivardeletebutton.setVisible(True)   
                if crop == "corn":     
                    self.cultivardeletebutton.clicked.connect(lambda:self.on_corncultivardeletebuttonclick(cultivar))
                else:
                    self.cultivardeletebutton.clicked.connect(lambda:self.on_potatocultivardeletebuttonclick(cultivar))
            else:
                crop = self.cropcombo.currentText()
                cultivar = ""
                action = "SaveAs"
                self.cultivarnamelabel.setVisible(True)
                self.cultivarnameedit.setVisible(True)

            self.cultivarbutton.setText(action)
            self.cultivarbutton.setVisible(True)
            if crop == "corn":     
                self.cultivarbutton.clicked.connect(lambda:self.on_corncultivarbuttonsclick(cultivar))
            else:
                self.cultivarbutton.clicked.connect(lambda:self.on_potatocultivarbuttonsclick(cultivar))

        # Each cultivar has a different set of parameters, so this block of code will be specific for each crop corn
        if(crop == "corn"):
            self.cornFieldSwitch(True)

            ## putting 2 separate buttons for UPDATE and SAVEAS tasks
            if action == "SaveAs":
                self.leavesedit.setText("")
                self.ltaredit.setText("0.46")
                self.ltiredit.setText("0.8")
                self.tasseledit.setText("4.0")
                self.staygreenedit.setText("2.0")
            elif action == "Update":
                cultivartuple = read_cultivar_DB_detailed(cultivar,crop)  

                if cultivartuple[0] is not None:
                    self.leavesedit.setText(str(cultivartuple[0]))

                if cultivartuple[1] > 0:
                    self.daylength_b1.setChecked(True)
                else:
                    self.daylength_b2.setChecked(True)

                if cultivartuple[2] is not None:
                    self.ltaredit.setText(str(cultivartuple[2]))
                if cultivartuple[3] is not None:
                    self.ltiredit.setText(str(cultivartuple[3]))
                if cultivartuple[4] is not None:
                    self.tasseledit.setText(str(cultivartuple[4]))
                if cultivartuple[5] is not None:
                    self.staygreenedit.setText(str(cultivartuple[5]))
          
        # Potato
        if(crop == "potato"):
            self.potatoFieldSwitch(True)

            if action == "SaveAs":
                self.dailyAirTempEffectEdit.setText("")
                self.dailyAirTempAmpEffectEdit.setText("")
                self.photoEffectEdit.setText("")
                self.highNiEffectEdit.setText("")
                self.lowNiEffectEdit.setText("")
                self.determEdit.setText("")
                self.maxCanLeafExpRateEdit.setText("")
                self.maxTuberGrowthRateEdit.setText("")
                self.specificLeafWeightEdit.setText("")
            elif action == "Update":
                cultivartuple = read_cultivar_DB_detailed(cultivar,crop)  
                self.dailyAirTempEffectEdit.setText(str(cultivartuple[0]))
                self.dailyAirTempAmpEffectEdit.setText(str(cultivartuple[1]))
                self.photoEffectEdit.setText(str(cultivartuple[2]))
                self.highNiEffectEdit.setText(str(cultivartuple[3]))
                self.lowNiEffectEdit.setText(str(cultivartuple[4]))
                self.determEdit.setText(str(cultivartuple[5]))
                self.maxCanLeafExpRateEdit.setText(str(cultivartuple[6]))
                self.maxTuberGrowthRateEdit.setText(str(cultivartuple[7]))
                self.specificLeafWeightEdit.setText(str(cultivartuple[8]))
                   

    @pyqtSlot()    
    def on_corncultivarbuttonsclick(self, cultivar):
        print("Inside on_corncultivarbuttonsclick")
        '''
         Does some error checking.
         save/ update the changes to cultivar_corn table
        '''
        value=self.cultivarcombo.currentIndex()

        daylength_v = 1 if self.daylength_b1.isChecked() else 0        
        #how to pass crop link id
        lm_min = 100.0 
        rrrm = 166.7
        rrry = 31.3
        rvrl = 0.73
        alpm = 0.55
        alpy = 0.04
        rtwl = 0.000106
        rtminwt = 0.0002
        epsi = 1.0
        iupw = 1.0
        courmax = 1.0
        diffx = 2.4
        diffz = 2.9
        velz = 0.0
        lsink = 1.0
        rroot = 0.017
        constl_m = 35.0
        constk_m = 0.5
        cmin0_m = 0.01
        consti_y = 17.3
        constk_y = 0.75
        cmin0_y = 0.03
        
        if self.cultivarbutton.text() == "Update":
            print("Update")
            record_tuple = (cultivar, int(self.leavesedit.text()), daylength_v, float(self.ltaredit.text()), \
                            float(self.ltiredit.text()), float(self.tasseledit.text()), float(self.staygreenedit.text()), lm_min, \
                            rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, diffx, diffz, velz, lsink, rroot, constl_m, \
                            constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
            c1 = insertUpdateCultivarCorn(record_tuple,self.cultivarbutton.text())
            if c1:
                self.cultivarcombo.blockSignals(False)
                self.cultivarcombo.clear()
                cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
                self.cultivarcombo.addItem("Select Cultivar")    
                self.cultivarcombo.addItem("Add New Cultivar (corn)") 
                for key in sorted(cultivarlists):            
                    key_aux = "corn:" + str(key)
                    self.cultivarcombo.addItem(key_aux)   
                self.cultivarcombo.setVisible(False)
                self.cultivarlistlabel.setVisible(False)

                self.cornFieldSwitch(False)

                self.cultivarnamelabel.setVisible(False)
                self.cultivarnameedit.setVisible(False)
                self.cultivarbutton.setVisible(False)       
                self.cultivardeletebutton.setVisible(False)        
                self.cultivarbutton.setText("")
                self.cropcombo.setCurrentIndex(0)
                return True
            return False
        elif self.cultivarbutton.text() == "SaveAs":
            ## check if new name is empty
            if len(self.cultivarnameedit.text()) <= 0:
                messageUser("Cultivar name is empty, please provide a name.")
                return False
            else:
                matchedindex = self.cultivarcombo.findText("corn:"+self.cultivarnameedit.text())                
                if matchedindex > 0:
                    messageUser("Cultivar name exist, please use a different name.")
                    return False
                else:
                    #save the table        
                    cultivartuple = read_cultivar_DB_detailed(self.cultivarnameedit.text(),"corn")  
                    if cultivartuple:
                        return False
                    record_tuple = (self.cultivarnameedit.text(), int(self.leavesedit.text()), daylength_v, float(self.ltaredit.text()), \
                                    float(self.ltiredit.text()), float(self.tasseledit.text()), float(self.staygreenedit.text()), lm_min, \
                                    rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, diffx, diffz, velz, lsink, rroot, \
                                    constl_m, constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
                    print("Insert corn!")
                    c1 = insertUpdateCultivarCorn(record_tuple,self.cultivarbutton.text())
                    if c1:
                        self.cultivarcombo.blockSignals(False)
                        self.cultivarcombo.clear()
                        cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
                        self.cultivarcombo.addItem("Select Cultivar")    
                        self.cultivarcombo.addItem("Add New Cultivar (corn)") 
                        for key in sorted(cultivarlists):            
                            key_aux = "corn:" + str(key)
                            self.cultivarcombo.addItem(key_aux)   
                        self.cultivarcombo.setVisible(False)
                        self.cultivarlistlabel.setVisible(False)
                        self.cultivarnamelabel.setVisible(False)
                        self.cultivarnameedit.setVisible(False)
                        self.cultivarcombo.blockSignals(False)

                        self.cornFieldSwitch(False)

                        self.cultivarbutton.setVisible(False)       
                        self.cultivardeletebutton.setVisible(False)        
                        self.cultivarbutton.setText("")
                        self.cropcombo.setCurrentIndex(0)
                        return True
                return False


    @pyqtSlot()    
    def on_corncultivardeletebuttonclick(self, cultivar):
        '''
         Delete record on cultivar_corn table
        '''
        c1 = delete_cultivarCorn(cultivar)
        if c1:
            self.cultivarcombo.blockSignals(True)
            self.cultivarcombo.clear()
            cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
            self.cultivarcombo.addItem("Select Cultivar")    
            self.cultivarcombo.addItem("Add New Cultivar (corn)") 
            for key in sorted(cultivarlists):            
                key_aux = "corn:" + str(key)
                self.cultivarcombo.addItem(key_aux)   
            self.cultivarcombo.setVisible(False)
            self.cultivarlistlabel.setVisible(False)

            self.cornFieldSwitch(False)

            self.cultivarnamelabel.setVisible(False)
            self.cultivarnameedit.setVisible(False)
            self.cultivarbutton.setText("")
            self.cultivarbutton.setVisible(False)       
            self.cultivardeletebutton.setVisible(False)        
            self.cropcombo.setCurrentIndex(0)


    @pyqtSlot()    
    def on_potatocultivarbuttonsclick(self, buttonname):
        '''
         Does some error checking.
         save/ update the changes to cultivar_corn table
        '''
        value=self.cultivarcombo.currentIndex()
        rrrm = 166.7
        rrry = 31.3
        rvrl = 0.73
        alpm = 0.35
        alpy = 0.04
        rtwl = 0.000106
        rtminwt = 0.0002
        epsi = 1.0
        iupw = 1.0
        courmax = 1.0
        diffx = 0.5
        diffz = 0.5
        velz = 0.5
        lsink = 1.0
        rroot = 0.017
        constl_m = 35.0
        constk_m = 0.5
        cmin0_m = 0.01
        consti_y = 17.3
        constk_y = 0.75
        cmin0_y = 0.03
        
        if self.cultivarbutton.text() == "Update":
            record_tuple = (self.cultivarnameedit.text(), float(self.dailyAirTempEffectEdit.text()), float(self.dailyAirTempAmpEffectEdit.text()), \
                            float(self.photoEffectEdit.text()), float(self.highNiEffectEdit.text()), float(self.lowNiEffectEdit.text()), \
                            float(self.determEdit.text()), float(self.maxCanLeafExpRateEdit.text()), float(self.maxTuberGrowthRateEdit.text()), \
                            float(self.specificLeafWeightEdit.text()), rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, \
                            diffx, diffz, velz, lsink, rroot, constl_m, constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
            c1 = insertUpdateCultivarPotato(record_tuple,self.cultivarbutton.text())
            if c1:
                self.cultivarcombo.blockSignals(True)
                self.cultivarcombo.clear()
                cultivarlists = read_cultivar_DB(self.cropcombo.currentText())  #self.croplists[value-1]) 
                self.cultivarcombo.addItem("Select Cultivar")    
                self.cultivarcombo.addItem("Add New Cultivar (potato)") 
                for key in sorted(cultivarlists):            
                    key_aux = "potato:" + str(key)
                    self.cultivarcombo.addItem(key_aux)   
                    self.cultivarcombo.blockSignals(False)
                    self.cultivarcombo.setVisible(False)
                    self.cultivarlistlabel.setVisible(False)
                    self.cultivarcombo.blockSignals(False)

                    self.potatoFieldSwitch(False)

                    self.cultivarnamelabel.setVisible(False)
                    self.cultivarnameedit.setVisible(False)
                    self.cultivarbutton.setText("")
                    self.cultivarbutton.setVisible(False)       
                    self.cultivardeletebutton.setVisible(False)        
                    self.cropcombo.setCurrentIndex(0)
        elif self.cultivarbutton.text() == "SaveAs":
            ## check if new name is empty
            if len(self.cultivarnameedit.text()) <= 0:
                messageUser("Cultivar name is empty, please provide a name.")
                return False
            else:
                matchedindex = self.cultivarcombo.findText("potato:"+self.cultivarnameedit.text())                
                if matchedindex >0:
                    messageUser("Cultivar name exist, please use a different name.")
                    return False
                else:
                    #save the table        
                    record_tuple = (self.cultivarnameedit.text(), float(self.dailyAirTempEffectEdit.text()), float(self.dailyAirTempAmpEffectEdit.text()), \
                                    float(self.photoEffectEdit.text()), float(self.highNiEffectEdit.text()), float(self.lowNiEffectEdit.text()), \
                                    float(self.determEdit.text()), float(self.maxCanLeafExpRateEdit.text()), float(self.maxTuberGrowthRateEdit.text()), \
                                    float(self.specificLeafWeightEdit.text()), rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, diffx, \
                                    diffz, velz, lsink, rroot, constl_m, constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
                    c1 = insertUpdateCultivarPotato(record_tuple,self.cultivarbutton.text())
                    if c1:
                        self.cultivarcombo.blockSignals(True)
                        self.cultivarcombo.clear()
                        cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
                        self.cultivarcombo.addItem("Select Cultivar")    
                        for key in sorted(cultivarlists):            
                            key_aux = "potato:" + str(key)
                            self.cultivarcombo.addItem(key_aux)            
                        self.cultivarcombo.setVisible(False)
                        self.cultivarlistlabel.setVisible(False)
                        self.cultivarnamelabel.setVisible(False)
                        self.cultivarnameedit.setVisible(False)
                        self.cultivarcombo.blockSignals(False)

                        self.potatoFieldSwitch(False)

                        self.cultivarbutton.setVisible(False)       
                        self.cultivardeletebutton.setVisible(False)        
                        self.cultivarbutton.setText("")
                        self.cropcombo.setCurrentIndex(0)
                        return True


    @pyqtSlot()    
    def on_potatocultivardeletebuttonclick(self, cultivar):
        '''
         Delete record on cultivar_corn table
        '''
        c1 = delete_cultivarPotato(cultivar)
        if c1:
            self.cultivarcombo.blockSignals(True)
            self.cultivarcombo.clear()
            cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
            self.cultivarcombo.addItem("Select Cultivar")    
            self.cultivarcombo.addItem("Add New Cultivar (potato)") 
            for key in sorted(cultivarlists):            
                key_aux = "potato:" + str(key)
                self.cultivarcombo.addItem(key_aux)   
            self.cultivarcombo.setVisible(False)
            self.cultivarlistlabel.setVisible(False)
            self.cultivarcombo.blockSignals(False)

            self.potatoFieldSwitch(False)

            self.cultivarnamelabel.setVisible(False)
            self.cultivarnameedit.setVisible(False)
            self.cultivarbutton.setText("")
            self.cultivarbutton.setVisible(False)       
            self.cultivardeletebutton.setVisible(False)        
            self.cropcombo.setCurrentIndex(0)


    def importfaq(self, thetabname=None):        
        faqlist = read_FaqDB(thetabname) 
        faqcount=0
        
        for item in faqlist:
            roottreeitem = QTreeWidgetItem(self.faqtree)
            roottreeitem.setText(0,item[2])
            childtreeitem = QTreeWidgetItem()
            childtreeitem.setText(0,item[3])
            roottreeitem.addChild(childtreeitem)


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