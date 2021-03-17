import subprocess
import threading
import time
import os
import csv
import numpy as np
import pandas as pd
import sys
import math
from helper.module_soiltriangle import *
from PyQt5 import QtSql, QtWebEngineWidgets, QtWebEngine
from PyQt5.QtWidgets import QWidget, QTabWidget, QDialog, QProgressBar, QLabel, QHBoxLayout, QListWidget, QLabel, QTableView, QTableWidget, QTableWidgetItem, \
                            QComboBox, QVBoxLayout, QFormLayout, QPushButton, QSpacerItem, QSizePolicy, QHeaderView, QRadioButton, QButtonGroup, \
                            QPlainTextEdit, QProgressDialog, QMenu
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, pyqtSignal, QCoreApplication, QBasicTimer
from PyQt5.QtGui import QPixmap
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
from subprocess import Popen
from os import path

global runpath1
global twodsoilexe
global createsoilexe
global rosettaexe
global app_dir
global repository_dir

#----------------------
# at some point in the future we will have to figure out a solution of alternative documents folders
#import  winreg as wr
#Registry = wr.ConnectRegistry(None, wr.HKEY_CURRENT_USER) # get a handle to the HKEY_CURRENT_USER branch in registry
#RawKey = wr.OpenKey(Registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") # get a handle to the key we need
#newPath=wr.QueryValueEx(RawKey,r"Personal")  # retrieve a tuple with the information for the value of 'Personal'
#gparent_dir=newPath[0]  #0 is the directory name
# this is gparent_dir
#----------------
gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
app_dir = os.path.join(gparent_dir,'crop_int')
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

global db
db = app_dir+'\\crop.db'

# Corn model executables
twodsoilexe = app_dir+'\\2dsoil.exe'
createsoilexe = app_dir+'\\createsoilfiles.exe'
rosettaexe = app_dir+'\\rosetta.exe'

# Potato model executable
soilexe = app_dir+'\\soil.exe'

run_dir = os.path.join(app_dir,'run')
if not os.path.exists(run_dir):
    os.makedirs(run_dir)

runpath1= run_dir
repository_dir = os.path.join(runpath1,'store')
weather_dir = os.path.join(runpath1,'weather')

## This should always be there
if not os.path.exists(repository_dir):
    print('RotationTab Error: Missing repository_dir')

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


class Rotation_Widget(QWidget):
    # Add a signal
    rotationsig = pyqtSignal(int)    
    changedValue = pyqtSignal(int)
    def __init__(self):
        super(Rotation_Widget,self).__init__()
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
        self.importfaq("general")              
        self.faqtree.header().resizeSection(1,200)       
        self.faqtree.setItemDelegate(ItemWordWrap(self.faqtree))
        self.faqtree.setVisible(False)

        self.tab_summary = QTextEdit("Pick individual entries to create your simulation.  You have the ability \
to run more than one simulation, to add or delete a simulation select the entire row and right click. It will \
open a dialog box with simple instructions. Once changes are done, please make sure to press the Run button to \
start your simulation.")        
        self.tab_summary.setReadOnly(True)        
        self.tab_summary.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.tab_summary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.tab_summary.setFrameShape(QtWidgets.QFrame.NoFrame) 
        self.tab_summary.setMaximumHeight(50) # need it     
        self.helpcheckbox = QCheckBox("Turn FAQ on?")
        self.helpcheckbox.setChecked(False)
        self.helpcheckbox.stateChanged.connect(self.controlfaq)

        self.vl1 = QVBoxLayout()
        self.hl1 = QHBoxLayout()
        self.mainlayout1 = QGridLayout()
        self.spacer = QSpacerItem(10,10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.hl1.addWidget(self.tab_summary)     
        self.hl1.setSpacing(0)   

        self.vl1.setContentsMargins(0,0,0,0)

        self.rgroupbox = QGroupBox("Simulator")
        self.siteCombo = QComboBox()
        self.soilCombo = QComboBox()
        self.stationTypeCombo = QComboBox()        
        self.weatherCombo = QComboBox()        
        self.cropCombo = QComboBox()          
        self.expTreatCombo = QComboBox()          
        self.comboWaterStress = QComboBox()          
        self.comboNitroStress = QComboBox()          

        sitelists = read_sitedetailsDB()
        self.siteCombo.addItem("Select from list")
        for item in sitelists: 
            self.siteCombo.addItem(item)
        self.siteCombo.currentIndexChanged.connect(self.showstationtypecombo)
        
        soillists = read_soilDB()
        self.soilCombo.addItem("Select from list")
        for key in sorted(soillists):            
            self.soilCombo.addItem(key)
        
        croplists = read_cropDB()
        self.cropCombo.addItem("Select from list")
        for val in sorted(croplists):
            self.cropCombo.addItem(val)
        self.cropCombo.currentIndexChanged.connect(self.showexperimentcombo)
                
        # Create and populate waterStress combo
        self.comboWaterStress.addItem("Yes") # val = 0
        self.comboWaterStress.addItem("No") # val = 1

        # Create and populate nitroStress combo
        self.comboNitroStress.addItem("Yes") # val = 0
        self.comboNitroStress.addItem("No") # val = 1
        
        self.tablebasket = QTableWidget()
        self.tablebasket.setVisible(True)        
        self.tablebasket.horizontalScrollBar().setStyleSheet("QScrollBar:: horizontal {border: 2px solid grey; background: lightgray; height: 15px; \
                                                             margin: 0px 20px 0 20px;} \
                                                             QScrollBar::handle:horizontal {background: #32CC99; min-width: 20px;} \
                                                             QScrollBar::add-line:horizontal {border: 2px solid grey; background: none; width: 20px; \
                                                             subcontrol-position: right; subcontrol-origin: margin;} \
                                                             QScrollBar::sub-line:horizontal {border: 2px solid grey; background: none; width: 20px; \
                                                             subcontrol-position: left; subcontrol-origin: margin;} \
                                                             QScrollBar::left-arrow:horizontal, {border: 2px solid grey; width: 3px; height: 3px; \
                                                             background: white;} \
                                                             QScrollBar::right-arrow:horizontal, {border: 2px solid grey; width: 3px; height: 3px; \
                                                             background: white;}")
        self.tablebasket.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablebasket.verticalHeader().customContextMenuRequested.connect(self.tableverticalheader_popup)
        self.tablebaskethheaderlabels = ["Site","Soil","Station Type","Weather","Crop","Experiment/Treatment", "StartYear","EndYear","WaterStress","NitrogenStress","Comments"]
        self.tablebasket.clear()
        self.tablebasket.setRowCount(0)
        self.tablebasket.setRowCount(1)
        self.tablebasket.setColumnCount(11)
        self.tablebasket.setAlternatingRowColors(True)
        self.tablebasket.setHorizontalHeaderLabels(self.tablebaskethheaderlabels)

        self.tablebasket.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(7,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(8,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(9,QHeaderView.ResizeToContents)
        self.tablebasket.horizontalHeader().setSectionResizeMode(10,QHeaderView.ResizeToContents)

        self.tablebasket.setCellWidget(0,0,self.siteCombo)
        self.tablebasket.setCellWidget(0,1,self.soilCombo)
        self.tablebasket.setCellWidget(0,2,self.stationTypeCombo)
        self.tablebasket.setCellWidget(0,3,self.weatherCombo)
        self.tablebasket.setCellWidget(0,4,self.cropCombo)
        self.tablebasket.setCellWidget(0,5,self.expTreatCombo)
        self.tablebasket.setCellWidget(0,8,self.comboWaterStress)
        self.tablebasket.setCellWidget(0,9,self.comboNitroStress)

        self.rlabel = QLabel("Simulator")
        self.buttonrun = QPushButton("Run")
        self.buttonrun.setObjectName("buttonrun")
        
        # Output hourly/daily
        self.step_hourly = QRadioButton("Hourly")
        self.step_daily = QRadioButton("Daily")
        self.step_hourly.setObjectName("step_hourly")
        self.step_daily.setObjectName("step_daily")
        self.step_g = QButtonGroup()

        self.step_hourly.setChecked(True)
        self.step_g.addButton(self.step_hourly,1)
        self.step_g.addButton(self.step_daily,2)

        self.subgrid1 = QGridLayout()
        self.subgrid1.addWidget(self.tablebasket,2,0,4,5)

        self.SimulationFlabel = QLabel("Simulation Output Interval")
        self.subgrid1.addWidget(self.SimulationFlabel,6,0)
        self.subgrid1.addWidget(self.step_hourly,6,1)
        self.subgrid1.addWidget(self.step_daily,6,2)
        
        self.SimulationFlabel.setObjectName("SimulationFlabel")

        self.subgrid1.addWidget(self.buttonrun,12,0)
        
        self.buttonrun.clicked.connect(self.buttonrunclicked)
        self.tablebasket.resizeColumnsToContents()
        self.tablebasket.resizeRowsToContents()  
              
        self.hl2 = QHBoxLayout()                
        self.rgroupbox.setLayout(self.subgrid1)
        self.hl2.addWidget(self.rgroupbox)
        
        self.vl1.addLayout(self.hl1)
        self.vl1.addWidget(self.helpcheckbox)
        self.vl1.addLayout(self.hl2)
        self.vl1.addStretch(1)
        self.mainlayout1.addLayout(self.vl1,0,0)
        self.mainlayout1.setColumnStretch(0,3)
        self.mainlayout1.addWidget(self.faqtree,0,4)
        self.setLayout(self.mainlayout1)
  

    def tableverticalheader_popup(self, pos):
        '''
        pop menu items will come here
        '''
        if (len(self.tablebasket.selectionModel().selectedRows()) !=1):
            return True

        menu = QMenu()
        insertrowbelowaction = menu.addAction("Insert row below")
        deletethisrowaction = menu.addAction("Delete this row")
        action = menu.exec_(QtGui.QCursor.pos())
        
        if action == insertrowbelowaction:
            self.insertrowbelow()

        if action == deletethisrowaction:
            self.deletethisrow()


    def deletethisrow(self):
        '''
        deletes the current row
        '''
        crow = self.tablebasket.currentRow()
        self.tablebasket.removeRow(crow)        
        howmanyrows = self.tablebasket.rowCount()
        if howmanyrows == 0:
            self.tablebasket.insertRow(howmanyrows)
            self.siteCombo = QComboBox()
            self.soilCombo = QComboBox()
            self.stationTypeCombo = QComboBox()        
            self.weatherCombo = QComboBox()        
            self.cropCombo = QComboBox()          
            self.expTreatCombo = QComboBox()          
            self.comboWaterStress = QComboBox()          
            self.comboNitroStress = QComboBox()          

            sitelists = read_sitedetailsDB()
            self.siteCombo.addItem("Select from list")
            for item in sitelists: 
               self.siteCombo.addItem(item)
            self.siteCombo.currentIndexChanged.connect(self.showstationtypecombo)
        
            self.soillists = read_soilDB()
            self.soilCombo.addItem("Select from list")
            for key in sorted(self.soillists):            
                self.soilCombo.addItem(key)
        
            stationtypelists = read_weather_metaDB()
            self.stationTypeCombo.addItem("Select from list")
            for key in sorted(stationtypelists):
                if stationtypelists[key] != "Add New Station Type":
                    self.stationTypeCombo.addItem(stationtypelists[key])
                
            croplists = read_cropDB()
            self.cropCombo.addItem("Select from list")
            for val in sorted(croplists):
                self.cropCombo.addItem(val)

            # Create and populate waterStress combo
            self.comboWaterStress.addItem("Yes") # val = 0
            self.comboWaterStress.addItem("No") # val = 1

            # Create and populate nitroStress combo
            self.comboNitroStress.addItem("Yes") # val = 0
            self.comboNitroStress.addItem("No") # val = 1
        
            self.tablebasket.setCellWidget(0,0,self.siteCombo)
            self.tablebasket.setCellWidget(0,1,self.soilCombo)
            self.tablebasket.setCellWidget(0,2,self.stationTypeCombo)
            self.tablebasket.setCellWidget(0,3,self.weatherCombo)
            self.tablebasket.setCellWidget(0,4,self.cropCombo)
            self.tablebasket.setCellWidget(0,5,self.expTreatCombo)
            self.tablebasket.setCellWidget(0,8,self.comboWaterStress)
            self.tablebasket.setCellWidget(0,9,self.comboNitroStress)


    def insertrowbelow(self):
        '''
        insert row below
        '''
        crow = self.tablebasket.currentRow()
        newrowindex = crow + 1

        self.tablebasket.insertRow(newrowindex)
        self.siteCombo = QComboBox()
        self.soilCombo = QComboBox()
        self.stationTypeCombo = QComboBox()        
        self.weatherCombo = QComboBox()        
        self.cropCombo = QComboBox()          
        self.expTreatCombo = QComboBox()          
        self.comboWaterStress = QComboBox()          
        self.comboNitroStress = QComboBox()          

        sitelists = read_sitedetailsDB()
        self.siteCombo.addItem("Select from list")
        for item in sitelists: 
           self.siteCombo.addItem(item)
        self.siteCombo.currentIndexChanged.connect(self.showstationtypecombo)
        
        self.soillists = read_soilDB()
        self.soilCombo.addItem("Select from list")
        for key in sorted(self.soillists):            
            self.soilCombo.addItem(key)
        
        stationtypelists = read_weather_metaDB()
        self.stationTypeCombo.addItem("Select from list")
        for key in sorted(stationtypelists):
            if stationtypelists[key] != "Add New Station Type":
                self.stationTypeCombo.addItem(stationtypelists[key])
                
        croplists = read_cropDB()
        self.cropCombo.addItem("Select from list")
        for val in sorted(croplists):
            self.cropCombo.addItem(val)
        self.cropCombo.currentIndexChanged.connect(self.showexperimentcombo)

        # Create and populate waterStress combo
        self.comboWaterStress.addItem("Yes") # val = 0
        self.comboWaterStress.addItem("No") # val = 1

        # Create and populate nitroStress combo
        self.comboNitroStress.addItem("Yes") # val = 0
        self.comboNitroStress.addItem("No") # val = 1
        
        self.tablebasket.setCellWidget(newrowindex,0,self.siteCombo)
        self.tablebasket.setCellWidget(newrowindex,1,self.soilCombo)
        self.tablebasket.setCellWidget(newrowindex,2,self.stationTypeCombo)
        self.tablebasket.setCellWidget(newrowindex,3,self.weatherCombo)
        self.tablebasket.setCellWidget(newrowindex,4,self.cropCombo)
        self.tablebasket.setCellWidget(newrowindex,5,self.expTreatCombo)
        self.tablebasket.setItem(newrowindex,6,QTableWidgetItem(""))
        self.tablebasket.setItem(newrowindex,7,QTableWidgetItem(""))
        self.tablebasket.setCellWidget(newrowindex,8,self.comboWaterStress)
        self.tablebasket.setCellWidget(newrowindex,9,self.comboNitroStress)
        self.tablebasket.setItem(newrowindex,10,QTableWidgetItem(""))


    def showstationtypecombo(self):
        site = self.siteCombo.currentText()
        crow = self.tablebasket.currentRow()
        if(crow == -1):
            crow = 0
        
        self.stationTypeCombo = QComboBox()        
        self.weatherCombo = QComboBox()        

        stationtypelists = read_weather_metaDBforsite(site)
        weather_id_lists = read_weather_id_forsite(site)
            
        self.weatherCombo.addItem("Select from list") 
        self.stationTypeCombo.addItem("Select from list") 
        for key in sorted(stationtypelists):
            if stationtypelists[key] != "Add New Station Type":
                self.stationTypeCombo.addItem(stationtypelists[key])

        for item in sorted(weather_id_lists):
            if item != "Add New Station Type":
                self.weatherCombo.addItem(item)

        self.tablebasket.setCellWidget(crow,2,self.stationTypeCombo)
        self.tablebasket.setCellWidget(crow,3,self.weatherCombo)
        return True


    def showexperimentcombo(self):
        crop = self.cropCombo.currentText()
        crow = self.tablebasket.currentRow()
        if(crow == -1):
            crow = 0
        
        self.expTreatCombo = QComboBox()          
        if crop != "Select from list":
            self.experimentlists = getExpTreatByCrop(crop)            
            self.expTreatCombo.addItem("Select from list") 
            for val in sorted(self.experimentlists):
                self.expTreatCombo.addItem(val)
        self.expTreatCombo.currentIndexChanged.connect(self.showtreatmentyear)
        self.tablebasket.setCellWidget(crow,5,self.expTreatCombo)
        return True


    def showtreatmentyear(self):
        currentrow = self.tablebasket.currentRow()
        if(currentrow == -1):
            currentrow = 0
        crop = self.cropCombo.currentText()
        experiment = self.expTreatCombo.currentText()
        if experiment == "Select from list":
            self.tablebasket.setItem(currentrow,6,QTableWidgetItem(""))
            self.tablebasket.setItem(currentrow,7,QTableWidgetItem(""))
        else:
            cropExperimentTreatment = crop + "/" +  experiment
            print("cropExperimentTreatment=",cropExperimentTreatment)
            # get weather years
            # site,weather_id
            weatheryears_list = read_weatheryears_fromtreatment(cropExperimentTreatment)
            syear = str(weatheryears_list[0])
            eyear = str(weatheryears_list[-1])
            self.tablebasket.setItem(currentrow,6,QTableWidgetItem(syear))
            self.tablebasket.setItem(currentrow,7,QTableWidgetItem(eyear))
            self.tablebasket.setItem(currentrow,10,QTableWidgetItem("here"))
        return True


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


    def controlfaq(self):                
        if self.helpcheckbox.isChecked():
            self.faqtree.setVisible(True)
        else:
            self.faqtree.setVisible(False)
        

    def copyFile(self,src,dest):
        '''
        Copy this way will make it wait for this command to finish first
        '''
        try:
            copyresult = subprocess.run(['copy',src,dest],stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        except len(copyresult.stderr) > 0:
            print('Error1 in Copy function: %s', copyresult.stderr)
        

    def buttonrunclicked(self):        
        rowcount = self.tablebasket.rowCount()
        self.saveQTextStream()


    def saveQTextStream(self):
        MAGIC_NUMBER=0X3051E
        FILE_VERSION=100
        CODEC="UTF-8"
        regexp_forwardslash = QtCore.QRegExp('[/]')       

        # Extracting user values from the FUNNEL
        for irow in range(0,self.tablebasket.rowCount()):
            lsitename = self.tablebasket.cellWidget(irow,0).currentText()
            lsoilname = self.tablebasket.cellWidget(irow,1).currentText()
            lstationtype = self.tablebasket.cellWidget(irow,2).currentText()
            lweather = self.tablebasket.cellWidget(irow,3).currentText()
            lcrop = self.tablebasket.cellWidget(irow,4).currentText()
            lexperiment = self.tablebasket.cellWidget(irow,5).currentText()
            lwaterstress = self.tablebasket.cellWidget(irow,8).currentText()
            if(lwaterstress == "Yes"):
                waterStressFlag = 0
            else:
                waterStressFlag = 1
            lnitrostress = self.tablebasket.cellWidget(irow,9).currentText()
            if(lnitrostress == "Yes"):
                nitroStressFlag = 0
            else:
                nitroStressFlag = 1

            # enter the record and get its ID
            if lsitename == "Select from list":
                messageUser("You need to select Site.")
                return False

            if lsoilname == "Select from list":
                messageUser("You need to select Soilname.")
                return False

            if lstationtype == "Select from list":
                messageUser("You need to select Station Type.")
                return False

            if lweather == "Select from list":
                messageUser("You need to select Weather.")
                return False

            if lcrop == "Select from list":
                messageUser("You need to select Crop.")
                return False

            if lexperiment == "Select from list":
                messageUser("You need to select Experiment/Treatment.")
                return False

            lstartyear = int(self.tablebasket.item(irow,6).text())
            lendyear = int(self.tablebasket.item(irow,7).text())
            lcomment = self.tablebasket.item(irow,10).text()

            cropTreatment = lcrop + "/" + lexperiment
            print("working on:",lsitename,cropTreatment,lstationtype,lweather,lsoilname,lstartyear,lendyear,waterStressFlag,nitroStressFlag)
                
            simulation_name = update_pastrunsDB(lsitename,cropTreatment,lstationtype,lweather,lsoilname,str(lstartyear),\
                                                str(lendyear),str(waterStressFlag),str(nitroStressFlag),lcomment) 
            print("Debug: simulation_name=",simulation_name)

            # this will execute the 2 exe's: uncomment it in final stage: 
            self.prepare_and_execute(simulation_name,irow,lstartyear,0,0)                

        
    def progressBar(self,field_path,field_name,sdate,edate,progressBar):
        # Total number of days
        numDays = edate - sdate
        
        # Check if file is being written
        fname = field_path+"\\"+field_name+".G03"
        tt = path.exists(fname)
        while not (path.exists(fname)):
            time.sleep(5)

        size = 0
        progressBar.setValue(0)
        time.sleep(3)
        size2 = os.stat(fname).st_size
        while(size2 > size):
            size = size2
            time.sleep(2)
            size2 = os.stat(fname).st_size
            with open(fname, 'r') as f:
                last_line = f.readlines()[-1]             
                x = last_line.split(",")
                date = datetime.strptime(x[1].strip(),'%m/%d/%Y')
                prog = int(((date-sdate)/numDays)*100)
                if prog > 100:
                    prog = 100
                progressBar.setValue(prog)
        #os.remove(fname)

        while(prog<=100):
            time.sleep(1)
            prog = prog + 5
            progressBar.setValue(prog)
        progressBar.hide()
        return True


    def prepare_and_execute(self,simulation_name,irow,theyear,delta_temp, delta_rain):
        """
        this will create input files, and execute both exe's
        """
        regexp_forwardslash = QtCore.QRegExp('[/]')       
        field_path = os.path.join(runpath1,str(simulation_name[0]))
        if not os.path.exists(field_path):
            os.makedirs(field_path)

        field_name= self.tablebasket.cellWidget(irow,0).currentText()  
        lsitename = self.tablebasket.cellWidget(irow,0).currentText()
        lsoilname = self.tablebasket.cellWidget(irow,1).currentText()
        lstationtype = self.tablebasket.cellWidget(irow,2).currentText()
        lweather = self.tablebasket.cellWidget(irow,3).currentText()
        lcrop = self.tablebasket.cellWidget(irow,4).currentText()
        lexperiment = self.tablebasket.cellWidget(irow,5).currentText().split('/')[0]
        ltreatmentname = self.tablebasket.cellWidget(irow,5).currentText().split('/')[1]
        lstartyear = int(self.tablebasket.item(irow,6).text())
        lendyear = int(self.tablebasket.item(irow,7).text())
        lwaterstress = self.tablebasket.cellWidget(irow,8).currentText()
        if(lwaterstress == "Yes"):
            waterStressFlag = 0
        else:
            waterStressFlag = 1
        lnitrostress = self.tablebasket.cellWidget(irow,9).currentText()
        if(lnitrostress == "Yes"):
            nitroStressFlag = 0
        else:
            nitroStressFlag = 1
        lcomment = self.tablebasket.item(irow,10).text()

        #copy weather file from store to runpath1
        src_file= weather_dir+'\\'+lstationtype + '.wea'                
        dest_file= field_path+'\\'+lstationtype + '.wea'   
        print("debug delta values:dtemp=",delta_temp)
        print("debug delta values:drain=",delta_rain)
        print("lwaterstress=",lwaterstress)
        print("lnitrostress=",lnitrostress)

        # getting weather data from sqlite
        conn = sqlite3.connect(db)  

        # get date range for treatment
        op_date_query = "select distinct odate from operations o, treatment t, experiment e where \
                         t.tid = o.o_t_exid and e.exid=t.t_exid and e.name=? and t.name = ?"
        df_op_date = pd.read_sql(op_date_query,conn,params=[lexperiment,ltreatmentname])
        df_op_date['odate'] = pd.to_datetime(df_op_date['odate'])
        #sdate = df_op_date['odate'].min()
        #edate = df_op_date['odate'].max()
        sdate = df_op_date['odate'].min() - timedelta(days=1)
        edate = df_op_date['odate'].max() + timedelta(days=1)
        diffInDays = (edate - sdate)/np.timedelta64(1,'D')
        
        weather_query = "select jday, date, hour, srad, tmax, tmin, temperature, rain, wind, rh, co2 from weather_data where site = ? and weather_id = ?" 
        df_weatherdata_orig = pd.read_sql(weather_query,conn,params=[lsitename,lweather])    
        # Convert date column to Date type
        df_weatherdata_orig['date'] = pd.to_datetime(df_weatherdata_orig['date'])
        firstDate = df_weatherdata_orig['date'].min()
        lastDate = df_weatherdata_orig['date'].max()
        df_weatherdata = df_weatherdata_orig.copy()
        mask = (df_weatherdata['date'] >= sdate) & (df_weatherdata['date'] <= edate)
        df_weatherdata = df_weatherdata.loc[mask]
        #Check if dataframe is empty
        if df_weatherdata.empty == True or (df_weatherdata.shape[0] + 1) < diffInDays:
            messageUser("Weather data is available for the data range of " + firstDate.strftime("%m/%d/%Y") + " and " + lastDate.strftime("%m/%d/%Y"))
            return False

        # Check if data is daily or hourly
        hourly_flag = 0
        weather_length = df_weatherdata['date'].max() - df_weatherdata['date'].min()
        num_records = len(df_weatherdata)
        #print(ltreatmentname)
        #print("weather_length=",weather_length.days," num_records=",num_records)
        if(num_records > (weather_length.days+1)):
            # header for hourly file
            df_weatherdata = df_weatherdata.drop(columns=['tmax','tmin'])
            weather_col_names = ["JDay", "Date", "hour", "Radiation", "temperature", "rain", "Wind", "rh", "CO2"] 
            hourly_flag = 1
            #print("Hourly")
        else:
            #print("bd",df_weatherdata)
            # header for daily file
            df_weatherdata = df_weatherdata.drop(columns=['hour','temperature'])
            weather_col_names = ["JDay", "Date", "Radiation", "Tmax","Tmin", "rain", "Wind", "rh", "CO2"] 
            #print("Daily")
            #print("ad",df_weatherdata)

        df_weatherdata['date'] = pd.to_datetime(df_weatherdata['date'],format='%Y-%m-%d').dt.strftime('%m/%d/%Y')
        df_weatherdata.columns = weather_col_names         

        rh_flag = 1
        if (df_weatherdata['rh'].isna().sum() > 0 or (df_weatherdata['rh'] == '').sum() > 0):
            df_weatherdata = df_weatherdata.drop(columns=['rh'])
            rh_flag = 0

        co2_flag = 1      
        if (df_weatherdata['CO2'].isna().sum() > 0 or (df_weatherdata['CO2'] == '').sum() > 0):
            df_weatherdata = df_weatherdata.drop(columns=['CO2'])
            co2_flag = 0

        rain_flag = 1
        if (df_weatherdata['rain'].isna().sum() > 0 or (df_weatherdata['rain'] == '').sum() > 0):
            df_weatherdata = df_weatherdata.drop(columns=['rain'])
            rain_flag = 0

        wind_flag = 1
        if (df_weatherdata['Wind'].isna().sum() > 0 or (df_weatherdata['Wind'] == '').sum() > 0):
            df_weatherdata = df_weatherdata.drop(columns=['Wind'])
            wind_flag = 0

        # the inputs for weather file comes from the weather flags. So we have to build that data stream 
        # and then write
        comment_value = ",".join(df_weatherdata.columns)
        #write the comment first
        with open(dest_file,'a') as ff:
            ff.write(comment_value)
            ff.write('\n')

        if delta_temp !=0:     #delta_temp is in absolute value
            df_weatherdata['Tmax'] = df_weatherdata['Tmax'] + delta_temp
            df_weatherdata['Tmin'] = df_weatherdata['Tmin'] + delta_temp
        if delta_rain !=0:  #delta_rain is in percentage
            df_weatherdata['rain'] = df_weatherdata['rain']*(1 + delta_rain/100.0)
                
        df_weatherdata.to_csv(dest_file,sep=' ',index=False,quotechar='"',quoting=csv.QUOTE_NONNUMERIC,mode='a')

        #copy water.dat file from store to runpath1
        src_file = repository_dir+'\\Water.DAT'
        dest_file = field_path+'\\Water.DAT'
        self.copyFile(src_file,dest_file)

        #copy water.dat file from store to runpath1
        src_file= repository_dir+'\\WaterBound.DAT'
        dest_file= field_path+'\\WatMovParam.dat'
        self.copyFile(src_file,dest_file)

        #copy MassBI.out file from store to runpath1
        src_file= repository_dir+'\\MassBl.out'
        dest_file= field_path+'\\MassBl.out'
        self.copyFile(src_file,dest_file)

        self.WriteBiologydefault(field_name,field_path)

        # Start
        #includes initial, management and fertilizer 
        rowSpacing, rootWeightPerSlab, cultivar = self.WriteIni(irow,field_name,field_path,theyear,theyear,waterStressFlag,nitroStressFlag) 
        #print("rowSpacing=",rowSpacing)
        self.WriteCropVariety(irow,lcrop,cultivar,field_name,field_path)
        self.WriteWeather(irow,lstationtype,field_name,field_path,hourly_flag,rh_flag,co2_flag,rain_flag,wind_flag)
        self.WriteSoluteFile(irow,lsoilname,field_name,field_path)
        self.WriteTimeFileData(irow,ltreatmentname,lexperiment,lcrop,lstationtype,field_name,field_path,hourly_flag)
        self.WriteNitData(irow,lsoilname,field_name,field_path,rowSpacing)
        self.WriteLayer(irow,lsoilname,field_name,field_path,rowSpacing,rootWeightPerSlab)
        self.WriteSoiData(irow,lsoilname,field_name,field_path)
        self.WriteRunFile(irow,lsoilname,field_name,cultivar,lstationtype,field_path,lstationtype)            
        src_file= field_path+"\\"+field_name+".lyr"                    
        layerdest_file= field_path+"\\"+field_name+".lyr"
        createsoil_opfile= lsoilname
        grid_name = field_name
        #print("Debug:soil name:",createsoil_opfile)
        #print("Debug:createsoil, layerdest_file:",layerdest_file)
        #print("Debug:createsoil, field_name:",field_name)
        #print("Debug:createsoil, createsoilexe:",createsoilexe)
        #print("Debug:cwd=app_dir:",app_dir)
        #print("Debug:createsoil_opfile: ",createsoil_opfile)
        #print("Debug:grid_name:",grid_name)
            
        pp = subprocess.Popen([createsoilexe,layerdest_file,"/GN",grid_name,"/SN",createsoil_opfile],cwd=app_dir)
        while pp.poll() is None:
            time.sleep(1)
        print("Process ended, ret code:", pp.returncode)
        print("Debug:3")
        #putting back the files created by CREATESOIL.EXE to the simulation directory
        dest_file= field_path+"\\"+field_name+".elm"
        src_file= app_dir+'\\'+field_name + '.elm'
        self.copyFile(src_file,dest_file)

        dest_file= field_path+"\\"+field_name+".nod"
        src_file= app_dir+'\\'+field_name + '.nod'
        self.copyFile(src_file,dest_file)

        dest_file= field_path+"\\"+field_name+".grd"
        src_file= app_dir+'\\'+field_name + '.grd'
        self.copyFile(src_file,dest_file)

        dest_file= field_path+"\\element_elm"
        src_file= app_dir+'\\element_elm'
        self.copyFile(src_file,dest_file)

        dest_file= field_path+"\\grid_bnd"
        src_file= app_dir+'\\grid_bnd'
        self.copyFile(src_file,dest_file)

        dest_file= field_path+"\\"+createsoil_opfile+".soi"
        src_file= app_dir+'\\'+createsoil_opfile + '.soi'
        self.copyFile(src_file,dest_file)

        progress = QtWidgets.QProgressDialog("Executing...", "", 0, 10000000, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setAutoReset(True)
        progress.setAutoClose(True)
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.resize(500,50)
        progress.setCancelButton(None)
        progress.setWindowTitle("Executing, Please Wait!")
        progress.show()
        progress.setValue(0)

        #print("Debug before subprocess 2dsoil")
        runname = field_path+"\\Run"+field_name+".dat"       
        #print("Debug:subprocess, runname:",runname)
        #endOpDate
        #sdate = sdate - timedelta(days=22)
        edate = edate + timedelta(days=22)
        try:
            QCoreApplication.processEvents()
            if(lcrop == "corn"):
                p = subprocess.Popen([twodsoilexe, runname],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                file_ext = ["g01","g02","G03","G04","G05","G06"]
            else:
                p = subprocess.Popen([soilexe, runname],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                file_ext = ["g01","G03","G04","G05","G06"]
            thread = threading.Thread(target=self.progressBar,kwargs=dict(field_path=field_path,field_name=field_name,sdate=sdate,edate=edate,progressBar=progress))
            thread.start()
            (out,err) = p.communicate()
            if p.returncode == 0:
                print("twosoil stage completed. %s",str(out))
            else:
                print("twosoil stage failed. Error =. %s",str(err))
        except OSError as e:
            sys.exit("failed to execute twodsoil program, %s", str(e))

        # Ingesting table  into cropOutput database
        for ext in file_ext:
            g_name = field_path+"\\"+field_name+"."+ext
            g_name2 = field_path+"\\\\"+field_name+"."+ext
            table_name = ext.lower()+"_"+lcrop
            print("Working on = ",table_name)
            ingestOutputFile(table_name,g_name2,str(simulation_name[0]))
            #if(ext != "G03"):
            #    os.remove(g_name)
            print("Work done")

        if lcrop == "potato":
            ingestOutputFile("nitrogen_potato",field_path+"\\\\nitrogen.crp",str(simulation_name[0]))
            ingestOutputFile("plantStress_potato",field_path+"\\\\plantstress.crp",str(simulation_name[0]))
            #os.remove(field_path+"\\\\nitrogen.crp")
            #os.remove(field_path+"\\\\plantstress.crp")
        elif lcrop == "corn":
            ingestOutputFile("plantStress_corn",field_path+"\\\\"+field_name+".sum",str(simulation_name[0]))
            #os.remove(field_path+"\\\\"+field_name+".sum")

        self.rotationsig.emit(int(simulation_name[0])) #emitting the simulation id (integer)
        #end of prepare_and_execute


    def WriteBiologydefault(self,field_name,field_path):
        '''
        writes to file: BiologyDefault.bio
        '''
        CODEC="UTF-8"        
        filename = field_path+"\\BiologyDefault.bio"              
        fh = QFile(filename)
        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:
            biolist = read_biologydefault()
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)
            fout<<"*** Example 12.3: Parameters of abiotic responce: file 'SetAbio.dat'"<<"\n"
            fout<<"Dehumification, mineralization, nitrification dependencies on moisture:"<<"\n"
            fout<<"dThH    dThL    es    Th_m"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f%-14.6f' %(biolist[0][0],biolist[0][1],biolist[0][2],biolist[0][3])<<"\n"
            fout<<"Dependencies of temperature"<<"\n"
            fout<<"tb     QT"<<"\n"
            fout<<'%-14.6f%-14.6f' %(biolist[0][4],biolist[0][5])<<"\n"
            fout<<"Denitrification dependencies on water content"<<"\n"
            fout<<"dThD   Th_d"<<"\n"
            fout<<'%-14.6f%-14.6f' %(biolist[0][6],biolist[0][7])<<"\n"

        fh.close()


    def WriteCropVariety(self,irow,crop,cultivar,field_name,field_path):
        hybridname = cultivar
        print("Debug: hybridname=",hybridname)
        hybridparameters = read_cultivar_DB_detailed(hybridname,crop) #returns a tuple
        CODEC="UTF-8"

        filename = field_path+"\\"+hybridname+".var"
        #print("filename=",filename)
        #print("hybridparameters=",hybridparameters)
        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:            
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)

            if(crop  == "corn"):
            #     0                  1              2          3              4            5       6     7    8    9    10   11   12
            #juvenileleaves, DaylengthSensitive, Rmax_LTAR, Rmax_LTIR, PhyllFrmTassel,StayGreen,LM_min,RRRM,RRRY,RVRL,ALPM,ALPY,RTWL,
            #      13        14   15    16      17     18    19   20   21     22         23     24       25        26      27       28    
            #RTMinWTperArea,EPSI,IUPW,CourMax,Diffx, Diffz,Velz,lsink,Rroot,Constl_M,ConstK_M,Cmin0_M,ConstI_Y,ConstK_Y,Cmin0_Y,hybridname
                fout<<"Corn growth simulation for variety "<<hybridname<<"\n"
                fout<<"Juvenile   Daylength   StayGreen  LM_Min Rmax_LTAR              Rmax_LTIR                Phyllochrons from "<<"\n"
                fout<<"leaves     Sensitive                     Leaf tip appearance   Leaf tip initiation       TassellInit"<<"\n"            
                fout<<'%-14.0f%-14.0f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f' %(hybridparameters[0],hybridparameters[1],hybridparameters[5],hybridparameters[6],\
                hybridparameters[2],hybridparameters[3],hybridparameters[4])<<"\n"
            else:
            # 0    1  2    3   4    5   6  7    8    9    10    11    12     13   14     15              16    17     18     19
            # A1, A6, A8, A9, A10, G1, G2, G3, G4, RRRM, RRRY, RVRL, ALPM, ALPY, RTWL, RTMinWTperArea, EPSI, IUPW, CourMax, Diffx,
            #  20     21     22     23       24        25        26       27        28     29
            # Diffz, Velz, lsink, Rroot, Constl_M, ConstK_M, Cmin0_M, ConstI_Y, ConstK_Y, Cmin0_Y
                a2 = (hybridparameters[0]-1)/10
                a3 = 100
                a4 = 1
                a5 = hybridparameters[1]-1
                a7 = hybridparameters[2]-1
                fout<<"*** EX4 Coefficient Calibration for Agmip 2017"<<"\n"
                fout<<hybridname<<"\n"
                fout<<"Genetic Coefficients"<<"\n"
                fout<<"A1(T1) A2(T2) A3(LAI) A4(Srad) A5(Tamp) A6(Tamp) A7(Pd) A8(Pd) A9(N) A10(N) G1(Det) G2(Exp) G3(TGR) G4(SLW)"<<"\n"
                fout<<'%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f' %(hybridparameters[0],a2,a3,a4,a5,\
                hybridparameters[1],a7,hybridparameters[2],hybridparameters[3],hybridparameters[4],hybridparameters[5],hybridparameters[6],hybridparameters[7],\
                hybridparameters[8])<<"\n"
            fout<<"[SoilRoot]"<<"\n"
            fout<<"*** WATER UPTAKE PARAMETER INFORMATION **************************"<<"\n"
            fout<<"RRRM       RRRY    RVRL"<<"\n"
            if(crop  == "corn"):
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[7],hybridparameters[8],hybridparameters[9])<<"\n"
                fout<<" ALPM    ALPY     RTWL    RtMinWtPerUnitArea"<<"\n"
                fout<<'%-14.8f%-14.8f%-14.8f%-14.8f' %(hybridparameters[10],hybridparameters[11],hybridparameters[12],hybridparameters[13])<<"\n"
                fout<<"[RootDiff]"<<"\n"
                fout<<"*** ROOT MOVER PARAMETER INFORMATION **************************"<<"\n"
                fout<<"EPSI        lUpW             CourMax"<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[14],hybridparameters[15],hybridparameters[16])<<"\n"
                fout<<"Diffusivity and geotropic velocity"<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[17],hybridparameters[18],hybridparameters[19])<<"\n"
                fout<<"[SoilNitrogen]"<<"\n"
                fout<<"*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************"<<"\n"
                fout<<"ISINK    Rroot         "<<"\n"
                fout<<'%-14.6f%-14.6f' %(hybridparameters[20],hybridparameters[21])<<"\n"
                fout<<"ConstI   Constk     Cmin0 "<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[22],hybridparameters[23],hybridparameters[24])<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[25],hybridparameters[26],hybridparameters[27])<<"\n"
            else:
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[9],hybridparameters[10],hybridparameters[11])<<"\n"
                fout<<" ALPM    ALPY     RTWL    RtMinWtPerUnitArea"<<"\n"
                fout<<'%-14.8f%-14.8f%-14.8f%-14.8f' %(hybridparameters[12],hybridparameters[13],hybridparameters[14],hybridparameters[15])<<"\n"
                fout<<"[RootDiff]"<<"\n"
                fout<<"*** ROOT MOVER PARAMETER INFORMATION **************************"<<"\n"
                fout<<"EPSI        lUpW             CourMax"<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[16],hybridparameters[17],hybridparameters[18])<<"\n"
                fout<<"Diffusivity and geotropic velocity"<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[19],hybridparameters[20],hybridparameters[21])<<"\n"
                fout<<"[SoilNitrogen]"<<"\n"
                fout<<"*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************"<<"\n"
                fout<<"ISINK    Rroot         "<<"\n"
                fout<<'%-14.6f%-14.6f' %(hybridparameters[22],hybridparameters[23])<<"\n"
                fout<<"ConstI   Constk     Cmin0 "<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[24],hybridparameters[25],hybridparameters[26])<<"\n"
                fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[27],hybridparameters[28],hybridparameters[29])<<"\n"
            fout<<"[Gas_Exchange Species Parameters] "<<"\n"
            fout<<"**** for photosynthesis calculations ***"<<"\n"
            fout<<"EaVp    EaVc    Eaj     Hj      Sj     Vpm25   Vcm25    Jm25    Rd25    Ear       g0    g1"<<"\n"
            fout<<"75100   55900   32800   220000  702.6   70      50       300    2       39800   0.017   4.53"<<"\n"
            fout<<"*** Second set of parameters for Photosynthesis ****"<<"\n"
            fout<<"f (spec_correct)     scatt  Kc25    Ko25    Kp25    gbs         gi      gamma1"<<"\n"
            fout<<"0.15                 0.15   650      450    80      0.003       1       0.193"<<"\n"
            fout<<"**** Third set of photosynthesis parameters ****"<<"\n"
            fout<<"Gamma_gsw  sensitivity (sf) Reference_Potential_(phyla, bars) stomaRatio widthFact lfWidth (m)"<<"\n"
            fout<<"  10.0        2.3               -1.2                             1.0        0.72   0.050"<<"\n"
            fout<<"**** Secondary parameters for miscelanious equations ****"<<"\n"
            fout<<"internal_CO2_Ratio   SC_param      BLC_param"<<"\n"
            fout<<"0.7                   1.57           1.36"<<"\n"
            if(crop  == "corn"):
                fout<<"***** Q10 parameters for respiration and leaf senescence"<<"\n"
                fout<<"Q10MR            Q10LeafSenescense"<<"\n"
                fout<<"2.0                     2.0"<<"\n"
                fout<<"**** parameters for calculating the rank of the largest leaf and potential length of the leaf based on rank"<<"\n"
                fout<<"leafNumberFactor_a1 leafNumberFactor_b1 leafNumberFactor_a2 leafNumberFactor_b2"<<"\n"
                fout<<"-10.61                   0.25                   -5.99           0.27"<<"\n"
                fout<<"**************Leaf Morphology Factors *************"<<"\n"
                fout<<"LAF        WLRATIO         A_LW"<<"\n"
                fout<<" 1.37          0.106           0.75"<<"\n"
                fout<<"*******************Temperature factors for growth *****************************"<<"\n"
                fout<<"T_base                 T_opt            t_ceil  t_opt_GDD"<<"\n"
                fout<<"8.0                   32.1              43.7       34.0"<<"\n"
            fout<<"\n"
        fh.close()
            

    def WriteIni(self,irow,field_name,field_path,lstartyear,lendyear,waterStressFlag,nitroStressFlag):
        '''
        Get data from operation, soil_long
        '''
        searchlist = ['Simulation Start', 'Sowing','Fertilizer-N','Harvest','Simulation End','Initial Field Values','Emergence']
        searchdict = {"Simulation Start":0, "Sowing":0,"Fertilizer-N":0,"Harvest":0,"Simulation End":0,"Initial Field Values":0,\
                      "Emergence":0}
        autoirrigation=0
        rowangle=0
        xseed=0
        yseed=5
        cec=0.65
        eomult=0.5
        pop=6.5
        fertCount=0
        BeginDate=0
        SowingDate=0
        EndDate=0
        toriginal_date= 0                         
        date_tt1=0
        date_tt2=0

        #get management tree                    
        cropname = self.tablebasket.cellWidget(irow,4).currentText()
        experiment = self.tablebasket.cellWidget(irow,5).currentText().split('/')[0]
        treatmentname = self.tablebasket.cellWidget(irow,5).currentText().split('/')[1]

        #find cropid
        #use crop to find exid in eperiment table
        #use exid and treatmentname to find tid from treatment table
        # use tid(o_t_exid) to find all the operations
        operationList = []
        fertilizerList = []
        exid = read_experimentDB_id(cropname,experiment)
        tid = read_treatmentDB_id(exid,treatmentname)
        operationList = read_operationsDB_id(tid) #gets all the operations

        print("fertCount=",fertCount)
        for ii,jj in enumerate(operationList):
            print(jj[0])
            if "Fertilizer-N" in jj[0]:   
                fertilizerList.append((jj[0],jj[13],jj[2],jj[3]))   #adding a tuple of (name, depth,quantity, date) to the fertilizerList                    
                fertCount=fertCount+1
        print("fertCount=",fertCount)
        for searchrecord in searchlist:
            for ii,jj in enumerate(operationList):
                if searchrecord in jj:
                    searchdict[searchrecord]= jj[1]  #depth                          
                    if searchrecord in 'Initial Field Values': #'Cultivar':
                        #0      1      2        3     4        5         6       7      8    9    10        11       12       13       14
                        #name, depth, quantity,odate,pop,autoirrigation,rowangle,xseed,yseed,cec,eomult,rowSpacing,cultivar,fDepth,seedpieceMass
                        depth = int(jj[8])
                        length = int(jj[8])
                        pop = jj[4]
                        autoirrigation = jj[5]
                        rowangle = jj[6]
                        xseed = jj[7]
                        yseed = int(jj[8])
                        cec = jj[9]
                        eomult = jj[10]
                        rowSpacing = jj[11]
                        seedpieceMass = jj[14]
                        cultivar = jj[12]

                    if searchrecord in 'Simulation Start':
                        BeginDate=jj[3] #month/day/year
                 
                    if searchrecord in 'Sowing':                            
                        SowingDate=jj[3] #month/day/year

                    if searchrecord in 'Emergence':                            
                        EmergenceDate=jj[3] #month/day/year

                    if searchrecord in 'Simulation End':                            
                        EndDate=jj[3] #month/day/year
            
        site = self.tablebasket.cellWidget(irow,0).currentText()
        soil = self.tablebasket.cellWidget(irow,1).currentText()
        tsite_tuple = extract_sitedetails(site)   
        #maximum profile depth     
        maxSoilDepth=read_soillongDB_maxdepth(soil)
        #print("Debug: maxSoilDepth=",maxSoilDepth)

        RowSP = rowSpacing

        # get list of Y values at surface to examine the depth intervals
        gridratio_list = read_soilgridratioDB(soil)
        #read tuple value from list
        aux2 = 0
        ydim=[0.0]*62
        j=1    
        for ii in range(1,61):
            aux2 = aux2 + gridratio_list[0][2]*gridratio_list[0][1]**(ii-1)
            distance = maxSoilDepth-aux2
            if aux2 <=3:   # Dennis change: 10/26/2018: old value was 1:
                ydim[j]=aux2  #ydim.append(aux2)
                j=j+1

        YCnt = j-1
        if YCnt >5:
            YCnt = 5 # Original logic: 5 is the maximum line we probably need

############### Write *.MAN file
        CODEC="UTF-8"
        filename = field_path+"\\"+field_name+".man"                
        fh = QFile(filename)
        placeholder = 0

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)
            fout<<"****Script for chemical application module  *******mg/cm2= kg/ha* 0.01*rwsp*eomult*100"<<"\n"
            fout<<"Number of Fertilizer applications (max=25) mappl is in total mg N applied to grid (1 kg/ha = 1 mg/m2/width of application) application divided by width of grid in cm is kg ha-1"<<"\n"                    
            fout<<'%-14d' %(fertCount)<<"\n"
            fout<<"tAppl(i)  AmtAppl(i)  depth(i)  mAppl_Carb(i)  mAppl_N(i)  (repeat these 3 lines for the number of fertilizer applications)"<<"\n"

            for kk in range(0,fertCount):
                factor= 0.01*(rowSpacing/2)/100
                amount=fertilizerList[kk][2]*factor/10000 *1000000
                fDepth = fertilizerList[kk][1]
                fout<<"'"<<fertilizerList[kk][3]<<"' "<<'%-14.6f%-14.6f' %(amount,fDepth)<<"0   0\n"
            fh.close()

############### Write INI file
        PopRow= rowSpacing/100 * pop 
     
        filename = field_path+"\\"+field_name+".ini"
        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:
            yseed = maxSoilDepth - yseed
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)
            fout<<"***Initialization data for location"<<"\n"
            fout<<"POPROW  ROWSP  Plant Density      ROWANG  xSeed  ySeed         CEC    EOMult"<<"\n"                    
            fout<<'%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f' %(PopRow,RowSP,pop,rowangle,xseed,yseed,cec,eomult)<<"\n"
            fout<<"Latitude longitude altitude"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(tsite_tuple[1],tsite_tuple[2],tsite_tuple[3])<<"\n"
            if(cropname == "corn"):
                fout<<"AutoIrrigate"<<"\n"
                fout<<'%d' %(autoirrigation)<<"\n"
                fout<<"Sowing      end         timestep"<<"\n"
                fout<<"'%-10s'  '%-10s'  %d" %(SowingDate,EndDate,60)<<"\n"
                rootWeightPerSlab = 0
            else:
                fout<<"Seed  Depth  Length  Bigleaf"<<"\n"
                fout<<"%-14.6f%-14.6f%-14.6f%d" %(seedpieceMass,depth,length,1)<<"\n"
                fout<<"Planting          Emergence          End	TimeStep(m)"<<"\n"
                fout<<"'%-10s'  '%-10s'  '%-10s'  %d" %(SowingDate,EmergenceDate, EndDate,60)<<"\n"
                fout<<"AutoIrrigate"<<"\n"
                fout<<'%d' %(autoirrigation)<<"\n"
                fout<<"Stresses (Nitrogen, Water stress: 1-nonlimiting, 2-limiting): Simulation Type (1-meteorological, 2-physiological)"<<"\n"
                fout<<" Nstressoff  Wstressoff  Water-stress-simulation-method"<<"\n"
                fout<<"%d    %d    %d" %(waterStressFlag,nitroStressFlag,0)<<"\n"
                rootWeightPerSlab = seedpieceMass * pop  * 0.25 * RowSP / 100 * 0.5 * 0.01
            fout<<"output soils data (g03, g04, g05 and g06 files) 1 if true"<<"\n"
            fout<<"                          no soil files        output soil files"<<"\n"
            fout<<"    0                     1  "<<"\n"
                
        fh.close()

############### Write DRP file
        filename = field_path+"\\"+field_name+".drp"
        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)
            fout<<"*****Script for Drip application module ***** mAppl is cm water per hour to a 45 x 30 cm area"<<"\n"                    
            fout<<"Number of Drip irrigations(max=25)"<<"\n"                    
            fout<<0<<"\n"
            fout<<"No drip irrigation"<<"\n"                
            fh.close()
 
        return RowSP, rootWeightPerSlab, cultivar


    def WriteWeather(self,irow,stationtype,field_name,field_path,hourly_flag,rh_flag,co2_flag,rain_flag,wind_flag):
        '''
        Extracts weather information from the weather_meta table and write the text file.       
        '''
        weatherparameters = read_weatherlongDB(stationtype) #returns a tuple
        CODEC="UTF-8"
        extension=".cli"
        filename = field_path+"\\"+stationtype+".cli"
        hourlyWeather = 0

#        print("Debug: weatherparameters=",weatherparameters)
#        print("Debug: filename=",filename)
        fh = QFile(filename) 
        header = ""
        val = ""
        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:            
            if(wind_flag == 0):
                header = "wind"
                val = str(weatherparameters[7])
            if(hourly_flag == 0):
                header = header + "    irav"
                val = val + "    " + str(weatherparameters[8])
            header = header + "    ChemConc"
            val =  val + "    " + str(weatherparameters[9])
            if(co2_flag == 0):
                header = header + "    Co2"
                val =  val + "    " + str(weatherparameters[10])
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)
            #    0        1         2       3      4      5     6      7          8          9       10        11         12
            #Latitude, Longitude, Bsolar, Btemp, Atemp, BWInd, BIR, AvgWind, AvgRainRate, ChemCOnc, AvgCO2, stationtype, site
            fout<<"***STANDARD METEOROLOGICAL DATA  Header fle for "<<stationtype<<"\n"
            fout<<"Latitude Longitude"<<"\n"
            fout<<'%-14.6f%-14.6f' %(weatherparameters[0],weatherparameters[1])<<"\n"
            fout<<"^Daily Bulb T(1) ^Daily Wind(2) ^RainIntensity(3) ^Daily Conc^(4) ^Furrow(5) ^Rel_humid(6) ^CO2(7)"<<"\n"
            fout<<'%-14d%-14d%-14d%-14d%-14d%-14d%-14d' %(0,wind_flag,hourly_flag,0,0,rh_flag,co2_flag)<<"\n"
            fout<<"Parameters for changing of units: BSOLAR BTEMP ATEMP ERAIN BWIND BIR "<<"\n"
            fout<<"BSOLAR is 1e6/3600 to go from j m-2 h-1 to wm-2"<<"\n"
            fout<<'%-14.1f%-14.1f%-14.4f%-14.1f%-14.1f%-14.1f' %(weatherparameters[2],weatherparameters[3],weatherparameters[4],0.1,weatherparameters[5],weatherparameters[6])<<"\n"
            fout<<"Average values for the site"<<"\n"
            fout<<header<<"\n"
            fout<<val<<"\n"            
        fh.close()


    def WriteSoluteFile(self,irow,soilname,field_name,field_path):
        '''
        Writes the SOLUTE FILE
        '''
        CODEC="UTF-8"
        filename = field_path+"\\NitrogenDefault.sol"        
        fh = QFile(filename)
        
        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:            
            soiltexture_list = read_soiltextureDB(soilname) #read soil file content 
            # 1 is the default solute record. Output type= tuple.
            # read solute file content
            solute_tuple = read_soluteDB(1)
            TextureCl=[] #empty list
            for irow in soiltexture_list:
                texture = soiltriangle.what_texture(irow[0],irow[2]).tostring().strip().decode('utf-8')
                textures = list(filter(str.strip,texture.split("/")))
                if len(textures) >= 1:
                    # Assumption: we won't have more than 2 textures, but choose the second one in that 
                    # case. -1 will give last entry
                    TextureCl.append(textures[-1])          

            #get dispersivity texture pairs
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)
            
            fout<<"*** SOLUTE MOVER PARAMETER INFORMATION ***"<<"\n"
            fout<<"Number of solutes"<<"\n"
            fout<<"1"<<"\n"
            fout<<"Computational parameters "<<"\n"
            fout<<"EPSI        lUpW             CourMax"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(solute_tuple[1],solute_tuple[2],solute_tuple[3])<<"\n"
            fout<<"Material Information"<<"\n"
            fout<<"Solute#, Ionic/molecular diffusion coefficients of solutes "<<"\n"
            fout<<'%-14.6f%-14.6f' %(1,solute_tuple[4])<<"\n"
            fout<<"Solute#, Layer#, Lingitudinal Dispersivity, Transversal Dispersivity (units are cm)"<<"\n"
            
            for counter in range(0,len(TextureCl)):
                dispersivity = read_dispersivityDB(TextureCl[counter])
                fout<<'%-14.6f%-14.6f%-14.6f%-14.6f' %(1,counter,dispersivity,dispersivity/2)<<"\n"
            fout<<"\n"                
        fh.close()


    def WriteTimeFileData(self,irow,treatmentname,experimentname,cropname,stationtype,field_name,field_path,hourly_flag):
        '''
        Writes the Time information into *.tim FILE
        '''
        startdate ='Blank'
        enddate ='Blank'
        dt=0.0001
        dtMin=0.0000001
        DMul1 = 1.3
        DMul2 = 0.3
        CODEC="UTF-8"
        filename = field_path+'\\'+field_name + '.tim'
        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:      
            startdate = read_operation_timeDB2('Simulation Start',treatmentname, experimentname ,cropname)                 
            enddate = read_operation_timeDB2('Simulation End', treatmentname, experimentname ,cropname)   
            
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)            
            fout<<"*** SYNCHRONIZER INFORMATION *****************************"<<"\n"
            fout<<"Initial time       dt       dtMin     DMul1    DMul2    tFin"<<"\n"
            #fout<<"'%-16s'%-14.4f%-14.4f%-14.4f%-14.4f%-16s" %(startdate,dt,dtMin,DMul1,DMul2,enddate)<<"\n"
            fout<<"'%-10s'  %-14.4f%-14.10f%-14.4f%-14.4f'%-10s'" %(startdate,dt,dtMin,DMul1,DMul2,enddate)<<"\n"
            hourlyFlag = 1 if self.step_hourly.isChecked() else 0
            fout<<"Output variables, 1 if true  Daily    Hourly"<<"\n"
            fout<<'%-16d%-14d' %(1-hourlyFlag,hourlyFlag)<<"\n"
            fout<<"Daily Hourly Weather data frequency. if daily enter 1   0; if hourly enter 0  1"<<"\n"
            fout<<'%-16d%-14d' %(1-hourly_flag, hourly_flag)<<"\n\n"

        fh.close()


    def WriteNitData(self,irow,soilname,field_name,field_path,rowSpacing):
        '''
        Writes Soil Nitrogen parameters into *.nit FILE
        '''
        # Nitrogen data from the soil
        soilnitrogen_list = read_soilnitrogenDB(soilname)
        NCount = len(soilnitrogen_list)        
        #maximum width of grid
        #get horizontal coordinates where fertilizer will be applied
        MaxX = rowSpacing/2

        CODEC="UTF-8"
        filename = field_path+"\\"+field_name+".nit"      
        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:                  
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)            
            fout<<" *** SoilNit parameters for location"<<"***\n"  #prefix details comes here.
            fout<<"ROW SPACING (m)"<<"\n"
            fout<<MaxX<<"\n"
            fout<<"                             Potential rate constants:       Ratios and fractions:"<<"\n"
            fout<<"m      kh     kL       km       kn        kd             fe   fh    r0   rL    rm   fa    nq   cs"<<"\n"
            for rrow in range(0,NCount):
                record_tuple=soilnitrogen_list[rrow]
                fout<<'%-14d%-14.5f%-14.3f%-14.6f%-14.1f%-14.5f%-14.1f%-14.1f%-14d%-14d%-14d%-14.1f%-14d%-14.5f' %(rrow+1,record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7],record_tuple[8],record_tuple[9],record_tuple[10],record_tuple[11],record_tuple[12])<<"\n"
        fh.close()


    def WriteSoiData(self,irow,soilname,field_name,field_path):
        '''
        Writes Soil data into *.soi FILE
        '''
        # hydrology data from the soil
        soil_hydrology_list = read_soilhydroDB(soilname)   

        NCount = len(soil_hydrology_list)               
        CODEC="UTF-8"        
        #field_path = os.path.join(runpath1,field_name)
        filename = field_path+'\\'+soilname + '.soi'        
        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:                  
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)            
            fout<<"           *** Material information ****                                                                   g/g  \n"  #prefix details comes here.
            fout<<"   thr       ths         tha       th      Alfa      n        Ks         Kk       thk       BulkD     OM    Sand    Silt\n"
            for rrow in range(0,NCount):
                record_tuple=soil_hydrology_list[rrow]
                record_tuple = [float(i) for i in record_tuple]
                fout<<'%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7],record_tuple[8],record_tuple[9],record_tuple[10],record_tuple[11],record_tuple[12])<<"\n"

        fh.close()
        filename = field_path+'\\'+field_name + '.dat'        
        fh = QFile(filename)

        soil_OM_list = read_soilOMDB(soilname)     
        NCount = len(soil_OM_list)
        #print("debug:soil texture",soil_OM_list,"\n")
        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:                  
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)            
            fout<<" Matnum      sand     silt    clay     bd     om   TH33       TH1500 \n"  #prefix details comes here.           
            for rrow in range(0,NCount):
                record_tuple=soil_OM_list[rrow]
                #print("debug:soil texture",record_tuple,"\n")
                fout<<'%-5d%-8.3f%-8.3f%-8.3f%-8.3f%-8.3f%-8.3f%-8.3f' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7])<<"\n"

        fh.close()


    def WriteLayer(self,irow,soilname,field_name,field_path,rowSpacing,rootWeightPerSlab):
        '''
        Writes Layer file (*.lyr)
        '''
        # get Grid Ratio for the soil
        gridratio_list =read_soilgridratioDB(soilname)
        NumObs = len(gridratio_list)
        CODEC="UTF-8"
        # read rowSpacing
        filename = field_path+"\\"+field_name+".lyr"             
        fh = QFile(filename)
        print("Debug: gridratio_list=",gridratio_list)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:                  
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)  
            fout<<"surface ratio    internal ratio: ratio of the distance between two neighboring nodes"<<"\n"
            for rrow in range(0,NumObs):
                record_tuple=gridratio_list[rrow]
                fout<<'%-14.3f%-14.3f%-14.3f%-14.3f' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3])<<"\n"

            fout<<"RowSpacing"<<"\n"
            fout<<'%-6.1f' %(rowSpacing)

            fout<<"\n"<<" Planting Depth	  X limit for roots	root weight per slab (seedpiece * plant_density  * 0.25 * row_spacing / 100 * 0.5 *0.01)"<<"\n"
            for rrow in range(0,len(gridratio_list)):
                record_tuple=gridratio_list[rrow]
                fout<<'%-14.3f%-14.3f%-14.3f\n' %(record_tuple[4],record_tuple[5],rootWeightPerSlab)

            fout<<" Boundary code for bottom layer (for all bottom nodes) 1 constant -2 seepage face \n"
            for rrow in range(0,len(gridratio_list)):
                record_tuple=gridratio_list[rrow]
                fout<<'%-14d\n' %(record_tuple[6])

            fout<<"Bottom depth   Init Type    OM (%/100)    no3(ppm)    NH4         hNew      Tmpr    Sand     Silt    Clay     BD     \
                   TH33     TH1500           thr	ths	tha	th	Alfa	n	Ks	Kk	thk"<<"\n"
            print("soilname=",soilname)
            soilgrid_list = read_soilshortDB(soilname)
            for rrow in range(0,len(soilgrid_list)):
                record_tuple = soilgrid_list[rrow]
                record_tuple = [float(i) for i in record_tuple]
                if(record_tuple[1] == 1):
                    initType = "'m'"
                else:
                    initType = "'w'"
                fout<<'%-14d%-6s%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f\
                       %-14.3f%-14.3f%-14.3f' %(record_tuple[0],initType,record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],\
                       record_tuple[7]/100,record_tuple[8]/100,record_tuple[9]/100,record_tuple[10],record_tuple[11],record_tuple[12],record_tuple[13],\
                       record_tuple[14],record_tuple[15],record_tuple[16],record_tuple[17],record_tuple[18],record_tuple[19],record_tuple[20],record_tuple[21])<<"\n"
        fout<<"\n"
        fh.close()


    def WriteRunFile(self,irow,soilname,field_name,cultivar,weather,field_path,stationtype):
        '''
        Writes Run file with input data file names
        '''
        CODEC="UTF-8"        
        filename = field_path+"\\Run"+field_name+".dat"             
        fh = QFile(filename)
        hybridname = cultivar
        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:                  
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)            
            fout<<field_path<<"\\"<<stationtype<<".wea\n"
            fout<<field_path<<"\\"<<field_name<<".tim\n"
            fout<<field_path<<"\\"<<"BiologyDefault.bio\n"            
            fout<<field_path<<"\\"<<stationtype<<".cli\n"
            fout<<field_path<<"\\"<<field_name<<".nit\n"
            fout<<field_path<<"\\"<<"NitrogenDefault.sol\n"
            fout<<field_path<<"\\"<<soilname<<".soi\n"
            fout<<field_path<<"\\"<<field_name<<".man\n"
            fout<<field_path<<"\\"<<field_name<<".drp\n"
            fout<<field_path<<"\\"<<"Water.DAT\n"
            fout<<field_path<<"\\"<<"WatMovParam.dat\n"
            fout<<field_path<<"\\"<<field_name<<".ini\n"
            fout<<field_path<<"\\"<<hybridname<<".var\n"
            fout<<field_path<<"\\"<<field_name<<".grd\n"
            fout<<field_path<<"\\"<<field_name<<".nod\n"
            fout<<field_path<<"\\"<<"MassBI.dat\n"
            fout<<field_path<<"\\"<<field_name<<".g01\n"
            fout<<field_path<<"\\"<<field_name<<".g02\n"
            fout<<field_path<<"\\"<<field_name<<".G03\n"
            fout<<field_path<<"\\"<<field_name<<".G04\n"
            fout<<field_path<<"\\"<<field_name<<".G05\n"
            fout<<field_path<<"\\"<<field_name<<".G06\n"
            fout<<field_path<<"\\"<<"MassBI.out\n"
            fout<<field_path<<"\\"<<"runoffmassbl.txt\n"
            fh.close()


    def SaveRunInfo(self,sitename,managementname,stationtype,soilname,field_name):
        '''
        Save the RUN information into the database
        '''
        # get Grid Ratio for the soil
        gridratio_list =read_soilgridratioDB(soilname)
        CODEC="UTF-8"
        field_path = os.path.join(runpath1,field_name)
        filename = field_path+"\\"+field_name+".lyr"

        fh = QFile(filename)

        if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
            print("Could not open file")
        else:                  
            fout = QTextStream(fh)            
            fout.setCodec(CODEC)  
            #prefix details comes here.          
            fout<<"Put NoSoil or Soil here to have the program generate soils data"<<"\n"  
            fout<<"Soil"<<"\n"
            fout<<"If you want to generate a new grid put a file name after the Grid Gen:"<<"\n"
            fout<<"Grid Gen: dataGen2.dat"<<"\n"
            fout<<"surface ratio    internal ratio: ratio of the distance between two neighboring nodes"<<"\n"
            for rrow in range(0,len(gridratio_list)):
                record_tuple=gridratio_list[rrow]
                fout<<'%-14.1f%-14.6f%-14.6f%-14d' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3])<<"\n"

            fout<<"\n"<<" Planting Depth  X limit for roots "<<"\n"
            for rrow in range(1,len(gridratio_list)):
                record_tuple=gridratio_list[rrow]
                fout<<'%-14d%-14d%' %(record_tuple[4],record_tuple[5])<<"\n"

            fout<<"Bottom depth   OM (%/100)    no3(ppm)    NH4         hNew      Tmpr    Sand     Silt    Clay     BD     TH33     TH1500  "<<"\n"
            soilgrid_list = read_soilshortDB(soilname)
            for rrow in range(1,len(soilgrid_list)):
                record_tuple= soilgrid_list[rrow]
                fout<<'%-14d%-14.7f%-14.1f%-14.1f%-14d%-14d%-14.3f%-14.3f%-14.3f%-14.6f%-14.7f%-14.7f' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7],record_tuple[8],record_tuple[9],record_tuple[10],record_tuple[11])<<"\n"
        fout<<"\n"
        fh.close()