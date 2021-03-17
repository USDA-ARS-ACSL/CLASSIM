import sys
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import shutil
import time
from datetime import date, timedelta, datetime
from time import mktime
from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWebEngine, QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QProgressBar, QLabel, QHBoxLayout, QListWidget, QTableWidget, QTableWidgetItem, QComboBox, QVBoxLayout, \
                            QPushButton, QSpacerItem, QSizePolicy, QHeaderView, QSlider, QPlainTextEdit, QRadioButton, QButtonGroup, QBoxLayout, QApplication, \
                            QMainWindow, QFrame, QFormLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSlot, QUrl, QPropertyAnimation
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
from matplotlib import cm, ticker
import matplotlib.animation as animation
matplotlib.use('TkAgg') #backend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

global app_dir
global index

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
app_dir = os.path.join(gparent_dir,'crop_int')
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

run_dir = os.path.join(app_dir,'run')
if not os.path.exists(run_dir):
    os.makedirs(run_dir)

'''
Contains 2 classes.
1). Class ItemWordWrap is to assist the text wrap features. You will find this class at the top of all the tab classes. 
    In future,we can centralize it. Lower priority.

2). Class Output_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget. It handles 
    all the features of OUTPUT Tab on the interface. It has signal slot mechanism. It does interact with the 
    DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets

    It has few extra imports like for ANIMATION support. Like JSAnimation for spatial and movie for G03 outputs. 
    PANDA dataframe for grid processes.
    It also has sub-tabs. Idea is to have G[0,1,2,3,4,5,6] output files shown in individual sub-tabs.

    We are also working idea of comparing 2 (or more) simulations. Currently focusing on G01,G03 outputs. But this 
    idea can easily be spread to cover other output types.
    Dr.Dennis is working on consolidating some of the other output files.
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
class Output2_Widget(QWidget):
    # Add a signal    
    def __init__(self):
        super(Output2_Widget,self).__init__()
        self.init_ui()


    def init_ui(self):
        self.setGeometry(QtCore.QRect(10,20,700,700))
        self.setAccessibleName("output2")
        self.setFont(QtGui.QFont("Calibri",10)) 
        self.faqtree = QtWidgets.QTreeWidget(self)   
        self.faqtree.setHeaderLabel('FAQ')     
        self.faqtree.setUniformRowHeights(False)
        self.faqtree.setWordWrap(True)
        self.faqtree.setFont(QtGui.QFont("Calibri",10))        
        self.importfaq("output")              
        self.faqtree.header().resizeSection(1,200)       
        self.faqtree.setItemDelegate(ItemWordWrap(self.faqtree))
        self.status2 = QTextEdit("Status.")        
        self.status2.setReadOnly(True) 
        self.status2.setVisible(False)
        self.status2.setFrameShape(QtWidgets.QFrame.NoFrame)

        script_dir = os.path.dirname(os.path.dirname(__file__)) # give parent path                

        self.tab_summary = QTextEdit("Choose simulation by checking from the list box. Simulation outputs are \
categorized into 5 types and are displayed individually in bottom tabbed panel.")                
        self.tab_summary.setReadOnly(True)        
        # no scroll bars
        self.tab_summary.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) 
        self.tab_summary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)         
        self.tab_summary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum) # horizontal, vertical
        self.tab_summary.setFrameShape(QtWidgets.QFrame.NoFrame)      
        self.tab_summary.setMaximumHeight(40) # need it
        self.helpcheckbox = QCheckBox("Turn FAQ on?")
        self.helpcheckbox.setChecked(False)
        self.helpcheckbox.stateChanged.connect(self.controlfaq)
        self.faqtree.setVisible(False)

        self.vl1 = QVBoxLayout()
        self.hl1 = QHBoxLayout()
        self.vl1.setAlignment(QtCore.Qt.AlignTop)        
        self.mainlayout1 = QGridLayout()
        self.spacer = QSpacerItem(10,10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vl1.setContentsMargins(0,0,0,0)
        self.vl1.setSpacing(1)
        self.vl1.addWidget(self.tab_summary)
        self.vl1.addWidget(self.helpcheckbox)
        self.table2 = QTableWidget()

        self.plotoutput = QPushButton("Select Simulation")
        self.deleteSim = QPushButton("Delete Simulation")
        self.buttonhlayout = QVBoxLayout()
        self.buttonhlayout.addWidget(self.plotoutput)
        self.buttonhlayout.addWidget(self.deleteSim)
        self.buttonhlayout.addStretch(1)
        self.display1 = QTabWidget()
        self.statistic_toollist = ['hourly','daily'] 

        self.table2.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table2.setFixedHeight(75)     
        self.table2.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table2.setAlternatingRowColors(True)
        self.error_tuplelist = []
        self.populate()
        self.table2.setHorizontalHeaderLabels(['SimID','Site','Treatment','Station Type','Weather','Soil','Year'])
        self.table2.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)
        self.table2.verticalHeader().hide()       
        self.table2.resizeColumnsToContents()  
        self.plotoutput.clicked.connect(self.on_click_table_widget)
        self.deleteSim.clicked.connect(self.on_deletebuttonclick)

        self.hl1.addWidget(self.table2)
        self.hl1.addLayout(self.buttonhlayout)
        self.vl1.addLayout(self.hl1)
        self.vl1.addWidget(self.display1)
        self.vl1.addStretch(1)
        self.display1.setVisible(False)
        self.mainlayout1.addLayout(self.vl1,0,0)
        self.mainlayout1.setColumnStretch(0,3)
        self.mainlayout1.addWidget(self.faqtree,0,4)
        
        #add a scroll bar to window
        self.scrollArea = QtWidgets.QScrollArea() # self.centralWidget)
        self.scrollContent = QtWidgets.QWidget(self.scrollArea)
        self.scrollContent.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.scrollContent.setLayout(self.mainlayout1)
        self.scrollArea.setLayout(self.mainlayout1)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)


    def make_connection(self,rotation_object):
        rotation_object.rotationsig.connect(self.populate)


    def populate(self):
        rlist = extract_pastrunsidDB()
        # When setRowCount is set to 0, the table gets refreshed.
        self.table2.setRowCount(0)
        self.table2.setRowCount(len(rlist))
        self.table2.setColumnCount(7)
        self.table2.simGrp = QButtonGroup()
        for row1 in range(len(rlist)): 
            i = 0
            for col in range(len(rlist[row1])):
                if i == 0:
                    radioitem = QRadioButton(str(rlist[row1][col]))
                    self.table2.simGrp.addButton(radioitem,i)
                    self.table2.setCellWidget(row1,col,radioitem)
                else:
                    self.table2.setItem(row1,col,QTableWidgetItem(str(rlist[row1][col])))
                i = i + 1


    def on_click_plotPlantTab(self):
        checkedVar = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                checkedVar.append(checkbox.text())

       # Create dictionary to hold dataframes
        df_collection = {}
        print("Debug: Outputtab:plantTab_plot1, self.simulationID=",self.simulationID)          
        t4 = extract_cropOutputData(self.g01Tablename,self.simulationID)
        tableID = self.g01Tablename + "_id"
        if(self.cropname == "corn"):
            t4.drop(columns=[tableID,'jday','Note'], inplace=True)
        else:
            t4.drop(columns=[tableID,'jday'], inplace=True)

        new_df = t4['Date_Time'].str.split(' ', n=1, expand=True)
        t4['Date'] = new_df[0]
        t4['Date'] = pd.to_datetime(t4['Date'])
        t4_grouped = t4.groupby(['Date'], as_index=False).agg(self.varFuncDict)
        t4_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        t4_grouped['Date_Time'] = pd.to_datetime(t4_grouped['Date_Time'])

        self.plantTab.fig.clear()
        self.plantTab.canvas.flush_events()
        self.plantTab.ax = self.plantTab.fig.add_subplot(111)
        self.plantTab.ax.cla()
        for var in checkedVar:
            self.plantTab.ax.plot(t4_grouped['Date_Time'], t4_grouped[var], label=var)

        self.plantTab.ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), ncol=2, borderaxespad=0)
        self.plantTab.fig.subplots_adjust(right=0.55)
        self.plantTab.canvas.draw()


    def on_click_plotSoilTab(self):
        self.varFuncSoilDict = {'hNew':'mean','thNew':'mean','ConcN':'mean','Temp':'mean'}
        self.varSoilDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)","ConcN":"Nitrogen Concentration\n(mg/L)",\
                               "Temp":"Temperature\n(oC)"}

        date = self.comboDate.currentText()
        df_collection = {}
        t3 = extract_cropOutputData(self.g03Tablename,self.simulationID)
        tableID = self.g03Tablename + "_id"
        t3.drop(columns={tableID}, inplace=True)
        new_df = t3['Date_Time'].str.split(' ', n=1, expand=True)
        t3['Date'] = new_df[0]
        t3_grouped = t3.groupby(['Date','X','Y'], as_index=False).agg(self.varFuncSoilDict)
        t3_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        df_collection = t3_grouped.loc[t3_grouped['Date_Time'] == date].filter(['hNew','thNew','ConcN','Temp','X','Y'],axis=1)

        rows = 1
        columns = 4
        param = ["hNew", "thNew", "ConcN", "Temp"]
  
        ## Create image
        self.soilwhnTab.fig.clear()
        self.soilwhnTab.canvas.flush_events()
        for var, i in zip(param, range(1,5)):
            title = self.varSoilDict[var]
            #title, unit = self.varSoilDict[var]
            new_df = df_collection.filter(['X','Y',var],axis=1)
            new_arr = new_df.values
            colorMap = "cool"
            if var == "hNew":
                colorMap = "cool_r"
                new_df[var] = new_df[var].abs()
            nx = new_df['X'].nunique()
            ny = new_df['Y'].nunique()
            x = new_arr[:,0].reshape(nx,ny)
            y = new_arr[:,1].reshape(nx,ny)
            z = new_arr[:,2].reshape(nx,ny)
            maxY = max(map(max, y))
            y = maxY - y
            self.soilwhnTab.ax = self.soilwhnTab.fig.add_subplot(rows, columns, i)
            self.soilwhnTab.ax.invert_yaxis()
            levels = MaxNLocator(nbins=15).tick_values(z.min(), z.max())
            norm = BoundaryNorm(levels, ncolors=colorMap, clip=True)
            if var == "hNew":
                cf = self.soilwhnTab.ax.contourf(x, y, z, locator=ticker.LogLocator(), cmap=colorMap)   
            else:
                cf = self.soilwhnTab.ax.contourf(x, y, z, levels=levels, cmap=colorMap)   
            cb = self.soilwhnTab.fig.colorbar(cf, ax=self.soilwhnTab.ax,  shrink=0.9)
            if var == "hNew":
                cb.ax.invert_yaxis()
            cb.ax.tick_params(labelsize=7)
            self.soilwhnTab.ax.set_title(title, size="medium")
            self.soilwhnTab.ax.set_ylabel('Depth (cm)')
            if i > 1:
                self.soilwhnTab.ax.get_yaxis().set_visible(False)
            plt.tight_layout()
            self.soilwhnTab.canvas.draw()
            plt.tight_layout()


    def on_click_rootTab(self):
        self.varFuncRootDict = {'RDenT':'max','RMassT':'max'}
        self.varRootDict = {"RDenT":"Root Density Total (g/cm2)","RMassT":"Root Mass Total (g/cm2)"}

        date = self.comboDateRoot.currentText()
        df_collection = {}
        t4 = extract_cropOutputData(self.g04Tablename,self.simulationID)
        tableID = self.g04Tablename + "_id"
        t4.drop(columns={tableID}, inplace=True)
        new_df = t4['Date_Time'].str.split(' ', n=1, expand=True)
        t4['Date'] = new_df[0]
        # Creating RDenT and RMassT variables
        t4['RDenT'] = t4['RDenM'] + t4['RDenY']
        t4['RMassT'] = t4['RMassM'] + t4['RMassY']
        t4_grouped = t4.groupby(['Date','X','Y'], as_index=False).agg(self.varFuncRootDict)
        t4_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        df_collection = t4_grouped.loc[t4_grouped['Date_Time'] == date].filter(['RDenT','RMassT','X','Y'],axis=1)

        rows = 1
        columns = 2
        param = ['RDenT','RMassT']
  
        ## Create image
        self.rootTab.fig.clear()
        self.rootTab.canvas.flush_events()
        for var, i in zip(param, range(1,5)):
            title = self.varRootDict[var]
            new_df = df_collection.filter(['X','Y',var],axis=1)
            new_arr = new_df.values
            colorMap = "cool"
            nx = new_df['X'].nunique()
            ny = new_df['Y'].nunique()
            x = new_arr[:,0].reshape(nx,ny)
            y = new_arr[:,1].reshape(nx,ny)
            z = new_arr[:,2].reshape(nx,ny)
            maxY = max(map(max, y))
            y = maxY - y
            self.rootTab.ax = self.rootTab.fig.add_subplot(rows, columns, i)
            self.rootTab.ax.invert_yaxis()
            levels = MaxNLocator(nbins=15).tick_values(z.min(), z.max())
            norm = BoundaryNorm(levels, ncolors=colorMap, clip=True)
            cf = self.rootTab.ax.contourf(x, y, z, levels=levels, cmap=colorMap)   
            cb = self.rootTab.fig.colorbar(cf, ax=self.rootTab.ax,  shrink=0.9)
            cb.ax.tick_params(labelsize=7)
            self.rootTab.ax.set_title(title, size="medium")
            self.rootTab.ax.set_ylabel('Depth (cm)')
            if i > 1:
                self.rootTab.ax.get_yaxis().set_visible(False)
            plt.tight_layout()
            self.rootTab.canvas.draw()
            plt.tight_layout()


    def on_click_plotSurfChaTab(self):
        self.surfChaVarDict = {'PSoilEvap':'Potential Soil Evaporation','ASoilEVap':'Actual Soil Evaporation','PE_T_int':'Potential Transpiration','transp':'Actual Tranpiration',\
                               'SeasPTran':'Cumulative Potential Transpiration','SeasATran':'Cumulative Actual Transpiration','SeasRain':'Cumulative Rain','SeasInfil':'Infiltration',\
                               'Runoff':'Runoff'}

        checkedVar = []
        for i, checkbox in enumerate(self.surfChaCheckboxes):
            if checkbox.isChecked():
                checkedVar.append(checkbox.text())

       # Create dictionary to hold dataframes
        df_collection = {}
        t5 = extract_cropOutputData(self.g05Tablename,self.simulationID)
        tableID = self.g05Tablename + "_id"

        new_df = t5['Date_Time'].str.split(' ', n=1, expand=True)
        t5['Date'] = new_df[0]
        t5_grouped = t5.groupby(['Date'], as_index=False).agg(self.surfChaVarFuncDict)
        t5_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        t5_grouped['Date_Time'] = pd.to_datetime(t5_grouped['Date_Time'])

        self.surfChaTab.ax = self.surfChaTab.fig.add_subplot(111)
        self.surfChaTab.ax.cla()
        for var in checkedVar:
            # Convert to cm of water/cm2
            t5_grouped[var] = t5_grouped[var] * self.plantDensity / 10000
            self.surfChaTab.ax.plot(t5_grouped['Date_Time'], t5_grouped[var], label=var)

        self.surfChaTab.ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), ncol=2, borderaxespad=0)
        self.surfChaTab.fig.subplots_adjust(right=0.55)
        self.surfChaTab.canvas.draw()

 
    def on_deletebuttonclick(self):
        '''
        This function gets called when user chooses to delete a simulation. Simulations on cropOutput database tables and information on pastruns table on crop 
        database will be deleted and the simulation directory will be deleted as well.
        '''
        delete_flag = messageUserDelete("Are you sure you want to delete this simulation?")
        if delete_flag:
            self.rowNumChecked = [self.table2.simGrp.buttons()[x].isChecked() for x in range(len(self.table2.simGrp.buttons()))].index(True)
            self.simulationID = self.table2.simGrp.buttons()[self.rowNumChecked].text()
            self.cropname = self.table2.item(self.rowNumChecked,2).text().split('/')[0]   

            # First delete the directory that was creates with the simulation information
            sim_dir = os.path.join(run_dir,self.simulationID)
            shutil.rmtree(sim_dir, ignore_errors=True)

            # Delete simulation from pastruns
            delete_pastrunsDB(self.simulationID)

            # Delete simulations on the cropOutput database tables
            delete_cropOutputSim(self.simulationID,self.cropname)
            self.populate()


    def on_click_table_widget(self):
        '''
        This gets called when USER clicks one of the old simulation row/column. 
        It will plot the graph(s) for the selected simulation
        '''
        global img, data, i, updateTime, fps
        regexp_num = QtCore.QRegExp('\d+(\.\d+)?')
        validator_num = QtGui.QRegExpValidator(regexp_num)

        self.rowNumChecked = [self.table2.simGrp.buttons()[x].isChecked() for x in range(len(self.table2.simGrp.buttons()))].index(True)
        self.simulationID = self.table2.simGrp.buttons()[self.rowNumChecked].text()
        self.sitename = self.table2.item(self.rowNumChecked,1).text()    
        self.cropname = self.table2.item(self.rowNumChecked,2).text().split('/')[0]   
        self.experimentname = self.table2.item(self.rowNumChecked,2).text().split('/')[1]   
        self.treatmentname = self.table2.item(self.rowNumChecked,2).text().split('/')[2]   
        self.stationtypename = self.table2.item(self.rowNumChecked,3).text()    
        self.soilname = self.table2.item(self.rowNumChecked,4).text()    
        self.g01Tablename = "g01_" + self.cropname
        self.g03Tablename = "g03_" + self.cropname
        self.g04Tablename = "g04_" + self.cropname
        self.g05Tablename = "g05_" + self.cropname
        
        self.display1.clear()
        self.simTab = QWidget()
        self.plantTab = QWidget()
        self.soilwhnTab = QWidget()
        self.rootTab = QWidget()
        self.surfChaTab = QWidget()# g06 outputs

        ########## simTab ##########
        #add a scroll bar to window
        self.simTabWidget = QtWidgets.QWidget(self.simTab)
        self.simTab.mainlayout = QFormLayout(self.simTabWidget)
        self.simTabWidget.setLayout(self.simTab.mainlayout)
        self.simTab.setLayout(self.simTab.mainlayout)

        genInfoBox = QHBoxLayout()
 
        genInfoBoxSum = QVBoxLayout()
        genInfoBoxSumLabel = QLabel()
        genInfoBoxSum.addWidget(genInfoBoxSumLabel)
        genInfoBoxSum.setAlignment(Qt.AlignTop)

        genInfoBoxDates = QVBoxLayout()
        genInfoBoxDatesLabel = QLabel()
        genInfoBoxDates.addWidget(genInfoBoxDatesLabel)
        genInfoBoxDates.setAlignment(Qt.AlignTop)

        genInfoBoxAgroDates = QVBoxLayout()
        genInfoBoxAgroDatesLabel = QLabel()
        genInfoBoxAgroDates.addWidget(genInfoBoxAgroDatesLabel)
        genInfoBoxAgroDates.setAlignment(Qt.AlignTop)

        envInfoBoxData = QVBoxLayout()
        envInfoBoxDataLabel = QLabel()
        envInfoBoxData.addWidget(envInfoBoxDataLabel)
        envInfoBoxData.setAlignment(Qt.AlignTop)

        genInfoBox.addLayout(genInfoBoxSum)
        genInfoBox.addLayout(genInfoBoxDates)
        genInfoBox.addLayout(genInfoBoxAgroDates)
        genInfoBox.addLayout(envInfoBoxData)
        genInfoBox.setAlignment(Qt.AlignTop)

        self.simulationSumTable = QTableWidget()
        self.simTab.mainlayout.addRow(genInfoBox)
        self.simTab.mainlayout.addRow(self.simulationSumTable)
        searchlist = ['Initial Field Values','Simulation Start','Sowing','Fertilizer-N','Emergence','Harvest']

        exid = read_experimentDB_id(self.cropname,self.experimentname)
        tid = read_treatmentDB_id(exid,self.treatmentname)
        plantDensity = getPlantDensity(tid)
        operationList = read_operationsDB_id(tid) #gets all the operations
        FertilizerDateList = []
        for searchrecord in searchlist:
            for ii,jj in enumerate(operationList):
                if searchrecord in jj:
                    if searchrecord in 'Simulation Start':
                        BeginDate=jj[3] #month/day/year
                 
                    if searchrecord in 'Sowing':                            
                        SowingDate=jj[3] #month/day/year

                    if searchrecord in "Fertilizer-N":   
                        FertilizerDateList.append(jj[3])  #month/day/year                  

                    if searchrecord in 'Emergence':                            
                        EmergenceDate=jj[3] #month/day/year

                    if searchrecord in 'Harvest':                            
                        HarvestDate=jj[3] #month/day/year

                    if searchrecord in 'Initial Field Values':
                        self.cultivar = jj[12]
                        self.plantDensity = jj[4]

        FertilizerDate = ""
        if len(FertilizerDateList) >= 1:
            FertilizerDate = ", "
            FertilizerDate = FertilizerDate.join(FertilizerDateList) 

        self.simSummaryGen = "<i>General Information </i>"
        self.simSummaryGen += "<br><i>Site: </i>" + self.sitename
        self.simSummaryGen += "<br><i>Soil: </i>" + self.soilname
        self.simSummaryGen += "<br><i>Weather: </i>" + self.stationtypename
        self.simSummaryGen += "<br><i>Crop: </i>" + self.cropname
        self.simSummaryGen += "<br><i>Cultivar: </i>" + self.cultivar
        self.simSummaryGen += "<br><i>Experiment: </i>" + self.experimentname
        self.simSummaryGen += "<br><i>Treatment: </i>" + self.treatmentname
        genInfoBoxSumLabel.setText(self.simSummaryGen)
 
        self.simSummaryDates = "<i>Simulation Dates </i>"
        self.simSummaryDates += "<br><i>Start Date: </i>" + BeginDate
        self.simSummaryDates += "<br><i>Planting Date: </i>" + SowingDate
        self.simSummaryDates += "<br><i>Fertilization Date: </i>" + FertilizerDate
        if self.cropname == "potato":
            TuberInitDate = getTuberInitDate(self.simulationID)
            MaturityDate = getMaturityDate(self.simulationID)
            self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
            self.simSummaryDates += "<br><i>Tuber Initiation Date: </i>" + TuberInitDate
            self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
        elif self.cropname == "corn":
            EmergenceDate = getCornDateByDev(self.simulationID,"Emerged")
            TasseledDate = getCornDateByDev(self.simulationID,"Tasseled")
            SilkedDate = getCornDateByDev(self.simulationID,"Silked")
            MaturityDate = getCornDateByDev(self.simulationID,"Matured")
            self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
            self.simSummaryDates += "<br><i>Tasseled Date: </i>" + TasseledDate
            self.simSummaryDates += "<br><i>Silked Date: </i>" + SilkedDate
            self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
        self.simSummaryDates += "<br><i>Harvest Date: </i>" + HarvestDate
        genInfoBoxDatesLabel.setText(self.simSummaryDates)

        if self.cropname == "potato":
            agroDataTuple = getPotatoAgronomicData(self.simulationID, HarvestDate)
            NitrogenUptakeTuple = getPotatoNitrogenUptake(self.simulationID, HarvestDate)
            envDataTuple = getEnvironmentalData(self.simulationID, HarvestDate, self.cropname)
            self.envSummaryData = "<i>Simulation Environmental Data at <br>" + HarvestDate + " (harvest date)</i>"
            self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + HarvestDate + " (harvest date)</i>"
            self.simSummaryAgroDates += "<br><i>Yield: </i>" + '{:3.2f}'.format(agroDataTuple[0]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Total biomass: </i>" +  '{:3.2f}'.format(agroDataTuple[1]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Nitrogen Uptake: </i>" +  '{:3.2f}'.format(NitrogenUptakeTuple[0]*plantDensity/100) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Transpiration: </i>" +  '{:3.2f}'.format(agroDataTuple[2]*plantDensity/1000) + " mm"
        elif self.cropname == "corn":
            if(MaturityDate != "N/A"):
                agroDataTuple = getCornAgronomicData(self.simulationID, MaturityDate)
                envDataTuple = getEnvironmentalData(self.simulationID, MaturityDate, self.cropname)
                self.envSummaryData = "<i>Simulation Environmental Data at <br>" + MaturityDate + " (maturity date)</i>"
                self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + MaturityDate + " (maturity date)</i>"
            else:
                agroDataTuple = getCornAgronomicData(self.simulationID, HarvestDate)
                envDataTuple = getEnvironmentalData(self.simulationID, HarvestDate, self.cropname)
                self.envSummaryData = "<i>Simulation Environmental Data at <br>" + HarvestDate + " (harvest date)</i>"
                self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + HarvestDate + " (harvest date)</i>"
            self.simSummaryAgroDates += "<br><i>Yield: </i>" + '{:3.2f}'.format(agroDataTuple[0]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Total biomass: </i>" + '{:3.2f}'.format(agroDataTuple[1]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Nitrogen Uptake: </i>" +  '{:3.2f}'.format(agroDataTuple[2]*plantDensity*10) + " kg/ha"
        genInfoBoxAgroDatesLabel.setText(self.simSummaryAgroDates)
 
        self.envSummaryData += "<br><i>Total Potential Transpiration: </i>" + '{:3.2f}'.format(envDataTuple[0]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Actual Transpiration: </i>" + '{:3.2f}'.format(envDataTuple[1]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Potential Soil Evaporation: </i>" + '{:3.2f}'.format(envDataTuple[2]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Actual Soil Evaporation: </i>" + '{:3.2f}'.format(envDataTuple[3]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Drainage: </i>" + '{:3.2f}'.format(envDataTuple[4]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Infiltration: </i>" + '{:3.2f}'.format(envDataTuple[5]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Runoff: </i>" + '{:3.2f}'.format(envDataTuple[6]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Rain: </i>" + '{:3.2f}'.format(envDataTuple[7]*plantDensity/1000) + " mm"
        envInfoBoxDataLabel.setText(self.envSummaryData)

        if self.cropname == "potato":
            NitroWaterStressDatesTuple = getNitroWaterStressDates(self.simulationID)
            self.simulationSumTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.simulationSumTable.setFixedHeight(220)     
            self.simulationSumTable.setFixedWidth(510)     
            self.simulationSumTable.setRowCount(len(NitroWaterStressDatesTuple))
            self.simulationSumTable.setColumnCount(5)
            i = 0
            for record in NitroWaterStressDatesTuple:
                j = 0
                for col in record:
                    if j == 0:
                        date = dt.strptime(col, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
                        self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(date)))
                    else:
                        colFormat = '{:3.2f}'.format(col) 
                        if col <= 0.75:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                            self.simulationSumTable.item(i,j).setForeground(QColor(255, 0, 0))
                        else:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                        self.simulationSumTable.item(i,j).setTextAlignment(Qt.AlignHCenter)
                    j = j + 1
                i = i + 1
            self.simulationSumTable.setHorizontalHeaderLabels(['Date','Water stress on\nleaf expansion','Nitrogen stress on\nleaf expansion',\
                                                               'Water stress on\nleaf photosynthesis','Nitrogen stress on\nphotosynthesis'])
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
            self.simulationSumTable.verticalHeader().hide()       
            self.simulationSumTable.resizeColumnsToContents()  
        elif self.cropname == "corn":
            NitroWaterStressDatesTuple = getCornPlantStressDates(self.simulationID)
            self.simulationSumTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.simulationSumTable.setFixedHeight(220)     
            self.simulationSumTable.setFixedWidth(400)     
            self.simulationSumTable.setRowCount(len(NitroWaterStressDatesTuple))
            self.simulationSumTable.setColumnCount(5)
            i = 0
            for record in NitroWaterStressDatesTuple:
                j = 0
                for col in record:
                    if j == 0:
                        date = dt.strptime(col, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
                        self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(date)))
                    else:
                        colFormat = '{:3.2f}'.format(col) 
                        if col >= 0.75:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                            self.simulationSumTable.item(i,j).setForeground(QColor(255, 0, 0))
                        else:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                        self.simulationSumTable.item(i,j).setTextAlignment(Qt.AlignHCenter)
                    j = j + 1
                i = i + 1
            self.simulationSumTable.setHorizontalHeaderLabels(['Date','Water stress','Nitrogen stress','Carbon stress',
                                                               'Potential Area'])
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
            self.simulationSumTable.verticalHeader().hide()       
            self.simulationSumTable.resizeColumnsToContents()  

        self.simTab.setLayout(self.simTab.mainlayout)
     
        ########## plantTab ##########
        if(self.cropname == "corn"):
            self.varFuncDict = {'Leaves':'max','MaturLvs':'max','Dropped':'max','LA_pl':'max','LA_dead':'max','LAI':'max','RH':'mean','LeafWP':'mean','PFD':'sum','SolRad':'sum',
                                'SoilT':'mean','Tair':'mean','Tcan':'mean','ETdmd':'sum','ETsply':'sum','Pn':'sum','Pg':'sum','Respir':'sum','av_gs':'mean','VPD':'mean',
                                'Nitr':'mean','N_Dem':'sum','NUpt':'sum','LeafN':'max','PCRL':'max','totalDM':'max','shootDM':'max','earDM':'max','TotLeafDM':'max','DrpLfDM':'max',
                                'stemDM':'max','rootDM':'max','SoilRt':'max','MxRtDep':'max','AvailW':'max','solubleC':'max'}
        else:
            self.varFuncDict = {'LAI':'max','Tcan':'mean','Pgross':'sum','Rg+Rm':'sum','Tr-Pot':'sum','Tr-Act':'sum','Stage':'max','totalDM':'max','leafDM':'max','stemDM':'max',
                                'rootDM':'max','tuberDM':'max','deadDM':'max','LWPpd':'max','LWPave':'mean','gs_ave':'mean'}

        self.plantTab.fig = plt.figure()
        self.plantTab.canvas = FigureCanvas(self.plantTab.fig)
 
        self.plantTab.groupBox = QGroupBox("Select parameter to plot")
        self.plantTab.groupBox.setMaximumWidth(200)
        self.vboxLayout = QGridLayout()
 
        self.checkboxes = []
        i = 0
        for var in self.varFuncDict:
            checkbox = QtWidgets.QCheckBox(var)
            self.checkboxes.append(checkbox)
            j = i//2
            if i % 2 == 0:
                self.vboxLayout.addWidget(checkbox,j,0)
            else:
                self.vboxLayout.addWidget(checkbox,j,1)
            i+=1
        j+=1

        self.plotButtom = QPushButton("Plot")

        self.vboxLayout.addWidget(self.plotButtom,j,0,1,2)
        #self.vboxLayout.addStretch()
        self.plantTab.groupBox.setLayout(self.vboxLayout)
        self.plotButtom.clicked.connect(self.on_click_plotPlantTab)
 
        self.plantTab.mainlayout = QHBoxLayout()
        self.plantTab.mainlayout.addWidget(self.plantTab.groupBox)
        self.plantTab.mainlayout.addWidget(self.plantTab.canvas)
        self.plantTab.setLayout(self.plantTab.mainlayout)
     
        ########## Soil Water Heat Nitrogen components ##########
        self.soilwhnTab.fig = plt.figure()
        self.soilwhnTab.canvas = FigureCanvas(self.soilwhnTab.fig)
        self.soilwhnTab.groupBox = QGroupBox()

        # Create and populate date combo
        t3 = extract_cropOutputData(self.g03Tablename,self.simulationID)
        tableID = self.g03Tablename + "_id"
        t3.drop(columns={tableID}, inplace=True)
        new_df = t3['Date_Time'].str.split(' ', n=1, expand=True)
        t3['Date'] = new_df[0]
        dateList = t3['Date'].unique()

        self.comboDate = QComboBox() 
        for date in dateList:         
            self.comboDate.addItem(date)
 
        self.dateselectionlabel= QLabel("Select Date")
        self.hboxLayoutSoil = QHBoxLayout()
        self.hboxLayoutSoil.addWidget(self.dateselectionlabel)
        self.hboxLayoutSoil.addWidget(self.comboDate)

        self.plotButtomSoil = QPushButton("Plot")

        self.hboxLayoutSoil.addWidget(self.plotButtomSoil)
        self.hboxLayoutSoil.addStretch()
        self.soilwhnTab.groupBox.setLayout(self.hboxLayoutSoil)
        self.plotButtomSoil.clicked.connect(self.on_click_plotSoilTab)

        self.soilwhnTab.mainlayout = QVBoxLayout()
        self.soilwhnTab.mainlayout.addWidget(self.soilwhnTab.groupBox)
        self.soilwhnTab.mainlayout.addWidget(self.soilwhnTab.canvas)
        self.soilwhnTab.setLayout(self.soilwhnTab.mainlayout)
     
        ########## Root tab ##########
        self.rootTab.fig = plt.figure()
        self.rootTab.canvas = FigureCanvas(self.rootTab.fig)
        self.rootTab.groupBox = QGroupBox()

        t4 = extract_cropOutputData(self.g04Tablename,self.simulationID)
        tableID = self.g04Tablename + "_id"
        t4.drop(columns={tableID}, inplace=True)
        new_df = t4['Date_Time'].str.split(' ', n=1, expand=True)
        t4['Date'] = new_df[0]
        dateList = t4['Date'].unique()

        self.comboDateRoot = QComboBox() 
        for date in dateList:         
            self.comboDateRoot.addItem(date)
 
        self.dateselectionlabel= QLabel("Select Date")
        self.hboxLayoutRoot = QHBoxLayout()
        self.hboxLayoutRoot.addWidget(self.dateselectionlabel)
        self.hboxLayoutRoot.addWidget(self.comboDateRoot)

        self.plotButtomRoot = QPushButton("Plot")

        self.hboxLayoutRoot.addWidget(self.plotButtomRoot)
        self.hboxLayoutRoot.addStretch()
        self.rootTab.groupBox.setLayout(self.hboxLayoutRoot)
        self.plotButtomRoot.clicked.connect(self.on_click_rootTab)

        self.rootTab.mainlayout = QVBoxLayout()
        self.rootTab.mainlayout.addWidget(self.rootTab.groupBox)
        self.rootTab.mainlayout.addWidget(self.rootTab.canvas)
        self.rootTab.setLayout(self.rootTab.mainlayout)
     
        ### Surface Characteristics tab ###
        self.surfChaVarFuncDict = {'PSoilEvap':'max','ASoilEVap':'max','PE_T_int':'max','transp':'max','SeasPSoEv':'max',\
                                   'SeasASoEv':'max','SeasPTran':'max','SeasATran':'max','SeasRain':'max','SeasInfil':'max',\
                                   'Runoff':'max'}

        self.surfChaTab.fig = plt.figure()
        self.surfChaTab.canvas = FigureCanvas(self.surfChaTab.fig)
 
        self.surfChaTab.groupBox = QGroupBox("Select parameter to plot")
        self.surfChaTab.groupBox.setMaximumWidth(150)
        self.vboxSurfChaLayout = QVBoxLayout()
 
        self.surfChaCheckboxes = []
        for var in self.surfChaVarFuncDict:
            checkbox = QtWidgets.QCheckBox(var)
            self.surfChaCheckboxes.append(checkbox)
            self.vboxSurfChaLayout.addWidget(checkbox)

        self.surfChaPlotButtom = QPushButton("Plot")

        self.vboxSurfChaLayout.addWidget(self.surfChaPlotButtom)
        self.vboxSurfChaLayout.addStretch()
        self.surfChaTab.groupBox.setLayout(self.vboxSurfChaLayout)
        self.surfChaPlotButtom.clicked.connect(self.on_click_plotSurfChaTab)
 
        self.surfChaTab.mainlayout = QHBoxLayout()
        self.surfChaTab.mainlayout.addWidget(self.surfChaTab.groupBox)
        self.surfChaTab.mainlayout.addWidget(self.surfChaTab.canvas)
        self.surfChaTab.setLayout(self.surfChaTab.mainlayout)
        #################################################################################

        if self.simulationID != None:            
            self.display1.addTab(self.simTab,"Simulation Summary")
            self.display1.addTab(self.plantTab,"Plant")
            self.display1.addTab(self.soilwhnTab,"Soil Water Heat Nitrogen")            
            self.display1.addTab(self.rootTab,"Root Data")            
            self.display1.addTab(self.surfChaTab,"Surface Characteristics")
            self.display1.setVisible(True)

   
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