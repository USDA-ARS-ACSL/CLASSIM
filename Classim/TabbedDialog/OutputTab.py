from math import factorial
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
                            QMainWindow, QFrame, QFormLayout, QFileDialog, QScrollArea
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSlot, QUrl, QPropertyAnimation
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
from CustomTool.genDictOutput import *
from matplotlib import cm, ticker
matplotlib.use('TkAgg') #backend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pandas.plotting import register_matplotlib_converters
from shutil import copyfile
register_matplotlib_converters()
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

global app_dir
global index

pd.options.mode.chained_assignment = None

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
app_dir = os.path.join(gparent_dir,'classim_v3')
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

run_dir = os.path.join(app_dir,'run')
if not os.path.exists(run_dir):
    os.makedirs(run_dir)

'''
Contains 3 classes.
1). Class ItemWordWrap is to assist the text wrap features. You will find this class at the top of all the tab classes. 
    In future,we can centralize it. Lower priority.

2). Class Output_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget. It handles 
    all the features of OUTPUT Tab on the interface. It has signal slot mechanism. It does interact with the 
    DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets

3). Class TimeAxisItem formats the date that is displayed on the x-axis.
   
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


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
 #       return [date.fromtimestamp(value).strftime('%m/%d/%y') for value in values]
        return [date.fromtimestamp(value).strftime('%m/%d') for value in values]


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
        self.table2.setHorizontalHeaderLabels(['SimID',"Site","Soil","Station Name","Weather","Crop/Experiment/Treatment", "StartYear","EndYear",
                                               "Water\nStress","Nitrogen\nStress","Temp\nVariance (oC)","Rain\nVariance (%)","CO2\nVariance (ppm)"])
        self.table2.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(6,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(7,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(8,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(9,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(10,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(11,QHeaderView.ResizeToContents)
        self.table2.horizontalHeader().setSectionResizeMode(12,QHeaderView.ResizeToContents)
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

        # Set graphic background to white and foreground to black
        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')


    def make_connection(self,rotation_object):
        rotation_object.rotationsig.connect(self.populate)


    def populate(self):
        rlist = extract_pastrunsidDB(0)
        # When setRowCount is set to 0, the table gets refreshed.
        self.table2.setRowCount(0)
        self.table2.setRowCount(len(rlist))
        self.table2.setColumnCount(13)
        self.table2.simGrp = QButtonGroup()
        for row1 in range(len(rlist)): 
            for col in range(len(rlist[row1])):
                if col == 0:
                    radioitem = QRadioButton(str(rlist[row1][col]))
                    self.table2.simGrp.addButton(radioitem,col)
                    self.table2.setCellWidget(row1,col,radioitem)
                if col > 1:
                    if col == 9 or col == 10:
                        if rlist[row1][col] == 0:
                            self.table2.setItem(row1,col-1,QTableWidgetItem("Yes"))
                        else:
                            self.table2.setItem(row1,col-1,QTableWidgetItem("No"))
                    elif col == 13:
                        if rlist[row1][col] == 0:
                            self.table2.setItem(row1,col-1,QTableWidgetItem("None"))
                        else:
                            self.table2.setItem(row1,col-1,QTableWidgetItem(str(rlist[row1][col])))
                    else:
                        self.table2.setItem(row1,col-1,QTableWidgetItem(str(rlist[row1][col])))


    def on_click_plotPlantTab(self):
        LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
        checkedVar = []
        for i, checkbox in enumerate(self.plantCheckboxes):
            if checkbox.isChecked():
                for key, value in self.varDescDict.items():
                    if checkbox.text() == value:
                         checkedVar.append(key)

        # Create dictionary to hold dataframes
        df_collection = {}
        #print("Debug: Outputtab:plantTab_plot1, self.simulationID=",self.simulationID)          
        t1 = extract_cropOutputData(self.g01Tablename,self.simulationID)
        tableID = self.g01Tablename + "_id"
        if self.cropname == "maize":
            t1.drop(columns=[tableID,'jday','Note'], inplace=True)
        elif self.cropname == "potato" or self.cropname == "soybean":
            t1.drop(columns=[tableID,'jday'], inplace=True)

        new_df = t1['Date_Time'].str.split(' ', n=1, expand=True)
        t1['Date'] = new_df[0]
        t1['Date'] = pd.to_datetime(t1['Date'])
        for key in self.varFuncDict:
            t1[key] = pd.to_numeric(t1[key],errors='coerce')
        t1 = t1.fillna(0)
        if self.cropname != "cotton":
            t1.loc[t1.SolRad <= 0,'SolRad'] = np.nan
            t1['PFD'] = (t1['PFD']*3600)/1000000
        t1_grouped = t1.groupby(['Date'], as_index=False).agg(self.varFuncDict)
        t1_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        t1_grouped['Date_Time'] = pd.to_datetime(t1_grouped['Date_Time'])
        tmstampArray = np.array([row['Date_Time'].timestamp() for index, row in t1_grouped.iterrows()])

        self.plantGraphWidget.clear()
        self.plantGraphWidget.setLabel("bottom", "Date")
        self.plantGraphWidget.showGrid(x=True, y=True)
        self.legend = self.plantGraphWidget.addLegend()
        
        i = 0
        maxY = 0
        for var in checkedVar:
            color = LINECOLORS[i]
            pen = pg.mkPen(color, width=3)
            if max(t1_grouped[var]) > maxY:
                maxY = max(t1_grouped[var])
            self.plantGraphWidget.plot(x=tmstampArray,y=np.array(t1_grouped[var]), name=self.varDescUnitDict[var], pen=pen)
            if i < 6:
                i = i + 1
            else:
                i = 0

        # set Y  and X range
        self.plantGraphWidget.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,maxY*1.05),padding=0)
        self.plantGraphWidget.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=maxY*1.05)
         

    def on_click_soilCNTab(self):
        LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
        checkedVar = []
        for i, checkbox in enumerate(self.soilCheckboxes):
            if checkbox.isChecked():
                for key, value in self.varSoilCNDescDict.items():
                    if checkbox.text() == value:
                         checkedVar.append(key)

       # Create dictionary to hold dataframes
        df_collection = {}
        #print("Debug: Outputtab:soilCNTab_plot1, self.simulationID=",self.simulationID)          
        t7 = extract_cropOutputData(self.g07Tablename,self.simulationID)
        new_df = t7['Date_Time'].str.split(' ', n=1, expand=True)
        # Get only date
        t7['Date'] = new_df[0]
        t7['Date'] = pd.to_datetime(t7['Date'])
        t7 = t7.drop(columns=[self.g07Tablename + "_id",'Date_Time'])

        # Read geometry table for this simulation
        geo_df = readGeometrySimID(self.simulationID)
        # Merge geo_df dataframe to t7 dataframe
        t7 = pd.merge(geo_df,t7, how='inner', left_on=['X','Y'], right_on=['X','Y'])
        for key in t7:
            if key != "Date":
                t7[key] = pd.to_numeric(t7[key],errors='coerce')
        t7 = t7.fillna(0)

        # Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth and the bottom
        # of the profile is 0, we have to reverse this for the layer file. Thus we subtract the max depth from all the Y's'
        maxY = max(t7['Y'])
        t7['Y'] = maxY-t7['Y']

        # First group every node by Date, X and Y
        # average the 24 hourly periods over each day
        t7 = t7.groupby(['Date','X','Y'], as_index=False).agg({'Area':['mean'],'Humus_N':['mean'],'Humus_C':['mean'],'Litter_N':['mean'],
                                                       'Litter_C':['mean'],'Manure_N':['mean'],'Manure_C':['mean'],
                                                       'Root_N':['mean'],'Root_C':['mean']})

        t7 = t7.drop(columns=["X","Y"])
        t7.columns = ["_".join(x) for x in t7.columns.ravel()]
        t7.rename(columns={'Date_':'Date'}, inplace=True)

        # Multiply by area to get total g in each node
        for key in t7:
            if (key != "Date" and key != "Area_mean"):
                t7[key] = t7[key]*t7['Area_mean']
        t7 = t7.drop(columns=["Area_mean"])

        # Group by Date adding all nodal values
        t7 = t7.groupby(['Date'], as_index=False).agg({'Humus_N_mean':['sum'],'Humus_C_mean':['sum'],'Litter_N_mean':['sum'],
                                                       'Litter_C_mean':['sum'],'Manure_N_mean':['sum'],'Manure_C_mean':['sum'],
                                                       'Root_N_mean':['sum'],'Root_C_mean':['sum']})
        t7.columns = ["_".join(x) for x in t7.columns.ravel()]
        t7.rename(columns={'Date_':'Date_Time'}, inplace=True)

        tmstampArray = np.array([row['Date_Time'].timestamp() for index, row in t7.iterrows()])
        #values are now total ugrams in the domain area (1/2 row spacing *1 cm), scale to kg/ha
        fact=1.0/(0.01*self.rowSP/100.0*self.eomult) # m2 area if the slab
        fact=fact*10000./1000./1000./1000.  #scale area
        for column in t7.columns:
          if column in ['Humus_N_mean_sum','Humus_C_mean_sum','Litter_N_mean_sum','Litter_C_mean_sum','Manure_N_mean_sum','Manure_C_mean_sum','Root_N_mean_sum','Root_C_mean_sum']:
              t7[column]=t7[column]*fact                                         
              
        self.soilCNWidget.clear()
        self.soilCNWidget.setLabel("bottom", "Date")
        self.soilCNWidget.showGrid(x=True, y=True)
        self.legend = self.soilCNWidget.addLegend()
        
        i = 0
        maxY = 0
        for var in checkedVar:
            color = LINECOLORS[i]
            pen = pg.mkPen(color, width=3)
            if max(t7[var+'_mean_sum']) > maxY:
                maxY = max(t7[var+'_mean_sum'])
            self.soilCNWidget.plot(x=tmstampArray,y=np.array(t7[var+'_mean_sum']), name=self.varSoilCNDescUnitDict[var], pen=pen)
            if i < 6:
                i = i + 1
            else:
                i = 0
        # set Y  and X range
        self.soilCNWidget.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,maxY*1.05),padding=0)
        self.soilCNWidget.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=maxY*1.05)


    def on_click_plotSoil2DTab(self):
        date = self.comboDate.currentText()
        df_collection = {}
        t3 = extract_cropOutputData(self.g03Tablename,self.simulationID)
        tableID = self.g03Tablename + "_id"
        t3.drop(columns={tableID}, inplace=True)
        new_df = t3['Date_Time'].str.split(' ', n=1, expand=True)
        t3['Date'] = new_df[0]
        for key in self.varSoilwhn2DDescUnitDict:
            t3[key] = pd.to_numeric(t3[key],errors='coerce')
        t3 = t3.fillna(0)
        t3_grouped = t3.groupby(['Date','X','Y'], as_index=False).agg(self.varSoilwhn2DFuncDict)
        t3_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        df_collection = t3_grouped.loc[t3_grouped['Date_Time'] == date].filter(['hNew','thNew','NO3N','Temp','X','Y'],axis=1)

        rows = 1
        columns = 4
  
        ## Create image
        self.soilwhn2DTab.fig.clear()
        self.soilwhn2DTab.canvas.flush_events()
        i = 1
        for var, desc in self.varSoilwhn2DDescUnitDict.items():
            title = desc
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
            self.soilwhn2DTab.ax = self.soilwhn2DTab.fig.add_subplot(rows, columns, i)
            self.soilwhn2DTab.ax.invert_yaxis()
            levels = np.linspace(z.min(), z.max(),10)
            cf = self.soilwhn2DTab.ax.contourf(x, y, z, levels=levels, cmap=colorMap)   
            cb = self.soilwhn2DTab.fig.colorbar(cf, ax=self.soilwhn2DTab.ax,  shrink=0.9)
            if var == "hNew":
                cb.ax.invert_yaxis()
            cb.ax.tick_params(labelsize=7)
            self.soilwhn2DTab.ax.set_title(title, size="medium")
            self.soilwhn2DTab.ax.set_ylabel('Depth (cm)')
            if i > 1:
                self.soilwhn2DTab.ax.get_yaxis().set_visible(False)
            plt.tight_layout()
            self.soilwhn2DTab.canvas.draw()
            plt.tight_layout()
            i = i + 1


    def on_click_rootTab(self):
        date = self.comboDateRoot.currentText()
        df_collection = {}
        t4 = extract_cropOutputData(self.g04Tablename,self.simulationID)
        tableID = self.g04Tablename + "_id"
        t4.drop(columns={tableID}, inplace=True)
        new_df = t4['Date_Time'].str.split(' ', n=1, expand=True)
        t4['Date'] = new_df[0]
        t4['RDenM'] = pd.to_numeric(t4['RDenM'],errors='coerce')
        t4['RDenY'] = pd.to_numeric(t4['RDenY'],errors='coerce')
        t4['RMassM'] = pd.to_numeric(t4['RMassM'],errors='coerce')
        t4['RMassY'] = pd.to_numeric(t4['RMassY'],errors='coerce')
        # Creating RDenT and RMassT variables
        t4['RDenT'] = t4['RDenM'] + t4['RDenY']
        t4['RMassT'] = t4['RMassM'] + t4['RMassY']
        t4_grouped = t4.groupby(['Date','X','Y'], as_index=False).agg(self.varRootFuncDict)
        t4_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        df_collection = t4_grouped.loc[t4_grouped['Date_Time'] == date].filter(['RDenT','RMassT','X','Y'],axis=1)

        rows = 1
        columns = 2
        i = 1
  
        ## Create image
        self.rootTab.fig.clear()
        self.rootTab.canvas.flush_events()
        for var, desc in self.varRootDescUnitDict.items():
            title = desc
            new_df = df_collection.filter(['X','Y',var],axis=1)
            new_arr = new_df.values
            colorMap = "cool"
            nx = new_df['X'].nunique()
            ny = new_df['Y'].nunique()
            y = new_arr[:,1].reshape(nx,ny)
            z = new_arr[:,2].reshape(nx,ny)
            maxY = max(map(max, y))
            x = new_arr[:,0].reshape(nx,ny)
            y = maxY - y
            self.rootTab.ax = self.rootTab.fig.add_subplot(rows, columns, i)
            self.rootTab.ax.invert_yaxis()
            levels = np.linspace(z.min(), z.max(),10)
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
            i = i + 1


    def on_click_plotSurfChaTab(self):
        checkedVar = []
        LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
        for i, checkbox in enumerate(self.surfChaCheckboxes):
            if checkbox.isChecked():
                for key, value in self.varSurfChaDescDict.items():
                    if checkbox.text() == value:
                         checkedVar.append(key)

        exid = read_experimentDB_id(self.cropname,self.experimentname)
        tid = read_treatmentDB_id(exid,self.treatmentname)
        plantDensity = getPlantDensity(tid)

       # Create dictionary to hold dataframes
        df_collection = {}
        t5 = extract_cropOutputData(self.g05Tablename,self.simulationID)
        tableID = self.g05Tablename + "_id"

        new_df = t5['Date_Time'].str.split(' ', n=1, expand=True)
        t5['Date'] = new_df[0]
        for key in self.varSurfChaFuncDict:
            t5[key] = pd.to_numeric(t5[key],errors='coerce')
        t5 = t5.fillna(0)
        t5_grouped = t5.groupby(['Date'], as_index=False).agg(self.varSurfChaFuncDict)
        t5_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        t5_grouped['Date_Time'] = pd.to_datetime(t5_grouped['Date_Time'])
        tmstampArray = np.array([row['Date_Time'].timestamp() for index, row in t5_grouped.iterrows()])

        self.surfChaGraphWidget.clear()
        self.surfChaGraphWidget.setLabel("bottom", "Date")
        self.surfChaGraphWidget.showGrid(x=True, y=True)
        self.legend = self.surfChaGraphWidget.addLegend()
        
        i = 0
        maxY = 0
        for var in checkedVar:
            color = LINECOLORS[i]
            pen = pg.mkPen(color, width=3)
            t5_grouped[var] = (t5_grouped[var] * plantDensity)/1000
            if max(t5_grouped[var]) > maxY:
                maxY = max(t5_grouped[var])
            self.surfChaGraphWidget.plot(x=tmstampArray,y=np.array(t5_grouped[var]), name=self.varSurfChaDescUnitDict[var],pen=pen)
            if i < 6:
                i = i + 1
            else:
                i = 0
        # set Y  and X range
        self.surfChaGraphWidget.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,maxY*1.05),padding=0)
        self.surfChaGraphWidget.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=maxY*1.05)

 
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
            delete_pastrunsDB(self.simulationID,self.cropname)
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
        self.cropname = self.table2.item(self.rowNumChecked,5).text().split('/')[0]   
        self.experimentname = self.table2.item(self.rowNumChecked,5).text().split('/')[1]   
        self.treatmentname = self.table2.item(self.rowNumChecked,5).text().split('/')[2]   
        self.stationtypename = self.table2.item(self.rowNumChecked,3).text()    
        self.soilname = self.table2.item(self.rowNumChecked,2).text()    
        self.g01Tablename = "g01_" + self.cropname
        self.g03Tablename = "g03_" + self.cropname
        self.g04Tablename = "g04_" + self.cropname
        self.g05Tablename = "g05_" + self.cropname
        self.g07Tablename = "g07_" + self.cropname
        
        self.display1.clear()
        scrollbar = QScrollArea(widgetResizable=True)
        self.simTab = QWidget()
        scrollbar.setWidget(self.simTab)
        self.plantTab = QWidget()
        self.soilCNTab = QWidget()
        self.soilTSTab = QWidget()
        self.soilwhn2DTab = QWidget()
        self.rootTab = QWidget()
        self.surfChaTab = QWidget()

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

        exid = read_experimentDB_id(self.cropname,self.experimentname)
        tid = read_treatmentDB_id(exid,self.treatmentname)
        plantDensity = getPlantDensity(tid)
        operationList = []
        operationList = read_operationsDB_id(tid) #gets all the operations
        FertilizerDateList = []
        PGRDateList = []

        for ii,jj in enumerate(operationList):
            if jj[1] == 'Simulation Start':
                BeginDate = jj[2] #month/day/year
 
                initCond = readOpDetails(jj[0],jj[1])
                self.plantDensity = initCond[0][3]
                self.eomult = initCond[0][8]
                self.rowSP = initCond[0][9]
                self.cultivar = initCond[0][10]

            if jj[1] == 'Sowing':                            
                SowingDate=jj[2]

            if jj[1] == 'Tillage':                            
                TillageDate=jj[2]

            if jj[1] in "Fertilizer":   
                FertilizerDateList.append(jj[2])       

            if jj[1] in "Plant Growth Regulator":   
                PGRDateList.append(jj[2])       

            if jj[1] == 'Emergence':                            
                EmergenceDate=jj[2]

            if jj[1] == 'Harvest':                            
                HarvestDate=jj[2] #month/day/year

        FertilizerDate = ""
        if len(FertilizerDateList) >= 1:
            FertilizerDate = ", "
            FertilizerDate = FertilizerDate.join(FertilizerDateList) 

        PGRDate = ""
        if len(PGRDateList) >= 1:
            PGRDate = ", "
            PGRDate = PGRDate.join(PGRDateList) 

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
        self.simSummaryDates += "<br><i>Tillage Date: </i>" + TillageDate
        if self.cropname != "fallow" and self.cropname != "cotton":
            self.simSummaryDates += "<br><i>Planting Date: </i>" + SowingDate
        if FertilizerDate != "":
            self.simSummaryDates += "<br><i>Fertilization Date: </i>" + FertilizerDate
        if PGRDate != "":
            self.simSummaryDates += "<br><i>Plant Growth Regulator Application Date: </i>" + PGRDate
        if self.cropname == "potato":
            TuberInitDate = getTuberInitDate(self.simulationID)
            MaturityDate = getMaturityDate(self.simulationID)
            self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
            self.simSummaryDates += "<br><i>Tuber Initiation Date: </i>" + TuberInitDate
            self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
        elif self.cropname == "maize":
            EmergenceDate = getMaizeDateByDev(self.simulationID,"Emerged")
            TasseledDate = getMaizeDateByDev(self.simulationID,"Tasseled")
            SilkedDate = getMaizeDateByDev(self.simulationID,"Silked")
            MaturityDate = getMaizeDateByDev(self.simulationID,"Matured")
            self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
            self.simSummaryDates += "<br><i>Tasseled Date: </i>" + TasseledDate
            self.simSummaryDates += "<br><i>Silked Date: </i>" + SilkedDate
            self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
        elif self.cropname == "soybean":
            FirstFlowerDate = getSoybeanDevDate(self.simulationID,1)
            PodInitDate = getSoybeanDevDate(self.simulationID,3)
            SeedInitDate = getSoybeanDevDate(self.simulationID,4)
            MaturityDate = getSoybeanDevDate(self.simulationID,7)
            self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
            self.simSummaryDates += "<br><i>First Flower Date: </i>" + FirstFlowerDate
            self.simSummaryDates += "<br><i>Pod Initiation Date: </i>" + PodInitDate
            self.simSummaryDates += "<br><i>Seed Initiation Date: </i>" + SeedInitDate
            self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
        elif self.cropname == "cotton":
            self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate

        if self.cropname != "fallow":
            self.simSummaryDates += "<br><i>Harvest Date: </i>" + HarvestDate
 
        genInfoBoxDatesLabel.setText(self.simSummaryDates)

        self.simSummaryAgroDates = ""
        if self.cropname == "potato" or self.cropname == "soybean":
            if self.cropname == "potato":
                agroDataTuple = getPotatoAgronomicData(self.simulationID, HarvestDate)
            else:
                agroDataTuple = getSoybeanAgronomicData(self.simulationID, HarvestDate)
            NitrogenUptakeTuple = getNitrogenUptake(self.simulationID, HarvestDate, self.cropname)
            envDataTuple = getEnvironmentalData(self.simulationID, HarvestDate, self.cropname)
            self.envSummaryData = "<i>Simulation Environmental Data at <br>" + HarvestDate + " (harvest date)</i>"
            self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + HarvestDate + " (harvest date)</i>"
            self.simSummaryAgroDates += "<br><i>Yield: </i>" + '{:3.2f}'.format(agroDataTuple[0]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Total biomass: </i>" +  '{:3.2f}'.format(agroDataTuple[1]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Nitrogen Uptake: </i>" +  '{:3.2f}'.format(NitrogenUptakeTuple[0]*plantDensity/10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Transpiration: </i>" +  '{:3.2f}'.format(agroDataTuple[2]*plantDensity/1000) + " mm"
        elif self.cropname == "maize":
            if(MaturityDate != "N/A"):
                agroDataTuple = getMaizeAgronomicData(self.simulationID, MaturityDate)
                envDataTuple = getEnvironmentalData(self.simulationID, MaturityDate, self.cropname)
                self.envSummaryData = "<i>Simulation Environmental Data at <br>" + MaturityDate + " (maturity date)</i>"
                self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + MaturityDate + " (maturity date)</i>"
            else:
                agroDataTuple = getMaizeAgronomicData(self.simulationID, HarvestDate)
                envDataTuple = getEnvironmentalData(self.simulationID, HarvestDate, self.cropname)
                self.envSummaryData = "<i>Simulation Environmental Data at <br>" + HarvestDate + " (harvest date)</i>"
                self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + HarvestDate + " (harvest date)</i>"
            self.simSummaryAgroDates += "<br><i>Yield: </i>" + '{:3.2f}'.format(agroDataTuple[0]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Total biomass: </i>" + '{:3.2f}'.format(agroDataTuple[1]*plantDensity*10) + " kg/ha"
            self.simSummaryAgroDates += "<br><i>Nitrogen Uptake: </i>" +  '{:3.2f}'.format(agroDataTuple[2]*plantDensity*10) + " kg/ha"
        elif self.cropname == "cotton":
            yieldDataTuple = getCottonYieldData(self.simulationID)
            yieldDate = dt.strptime(yieldDataTuple[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
            FirstSquareDate = getCottonDevDate(self.simulationID,"1stSquare")
            FirstBloomDate = getCottonDevDate(self.simulationID,"1stBloom")
            FirstOpenBollDate = getCottonDevDate(self.simulationID,"1stOpenBoll")
            envDataTuple = getEnvironmentalData(self.simulationID, HarvestDate, self.cropname)
            self.envSummaryData = "<i>Simulation Environmental Data </i>"
            self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + yieldDate + "</i>"
            self.simSummaryAgroDates += "<br><i>Date of first square: </i>" + FirstSquareDate
            self.simSummaryAgroDates += "<br><i>Date of first bloom: </i>" + FirstBloomDate
            self.simSummaryAgroDates += "<br><i>Date of first open boll: </i>" + FirstOpenBollDate
            self.simSummaryAgroDates += "<br><i>Yield: </i>" + '{:3.2f}'.format(yieldDataTuple[1]*1.12) + " kg/ha"
        elif self.cropname == "fallow":
            envDataTuple = getEnvironmentalData(self.simulationID, "", self.cropname)
            self.envSummaryData = "<i>Simulation Environmental Data </i>"
        genInfoBoxAgroDatesLabel.setText(self.simSummaryAgroDates)
        #print("env tuple=",envDataTuple)
 
        self.envSummaryData += "<br><i>Total Potential Transpiration: </i>" + '{:3.2f}'.format(envDataTuple[0]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Actual Transpiration: </i>" + '{:3.2f}'.format(envDataTuple[1]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Potential Soil Evaporation: </i>" + '{:3.2f}'.format(envDataTuple[3]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Actual Soil Evaporation: </i>" + '{:3.2f}'.format(envDataTuple[2]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Drainage: </i>" + '{:5.2f}'.format(envDataTuple[7]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Water From Deep Soil: </i>" + '{:5.2f}'.format(envDataTuple[8]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Infiltration: </i>" + '{:3.2f}'.format(envDataTuple[4]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Runoff: </i>" + '{:3.2f}'.format(envDataTuple[5]*plantDensity/1000) + " mm"
        self.envSummaryData += "<br><i>Total Rain: </i>" + '{:3.2f}'.format(envDataTuple[6]*plantDensity/1000) + " mm"
        envInfoBoxDataLabel.setText(self.envSummaryData)

        if self.cropname == "potato":
            NitroWaterStressDatesTuple = getNitroWaterStressDates(self.simulationID)
            self.simulationSumTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.simulationSumTable.setFixedHeight(250)     
            self.simulationSumTable.setFixedWidth(525)     
            self.simulationSumTable.setRowCount(len(NitroWaterStressDatesTuple))
            self.simulationSumTable.setColumnCount(5)
            i = 0
            for record in NitroWaterStressDatesTuple:
                j = 0
                for col in record:
                    if j == 0:
                        date = dt.strptime(col, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
                        self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(date)))
                    else:
                        colFormat = '{:3.3f}'.format(col) 
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
        elif self.cropname == "soybean":
            NitroWaterStressDatesTuple = getSoybeanPlantStressDates(self.simulationID)
            self.simulationSumTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.simulationSumTable.setFixedHeight(250)     
            self.simulationSumTable.setFixedWidth(525)     
            self.simulationSumTable.setRowCount(len(NitroWaterStressDatesTuple))
            self.simulationSumTable.setColumnCount(5)
            i = 0
            for record in NitroWaterStressDatesTuple:
                j = 0
                for col in record:
                    if j == 0:
                        date = dt.strptime(col, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
                        self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(date)))
                    elif j > 0 and j < 4:
                        colFormat = '{:3.3f}'.format(col) 
                        if col <= 0.75:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                            self.simulationSumTable.item(i,j).setForeground(QColor(255, 0, 0))
                        else:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                    else:
                        self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(col)))
                    self.simulationSumTable.item(i,j).setTextAlignment(Qt.AlignHCenter)
                    j = j + 1
                i = i + 1
            self.simulationSumTable.setHorizontalHeaderLabels(['Date','Water stress','Nitrogen stress','Carbon stress',
                                                               'Predominant factor\nlimiting growth'])
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
            self.simulationSumTable.verticalHeader().hide()       
            self.simulationSumTable.resizeColumnsToContents()  
        elif self.cropname == "maize":
            NitroWaterStressDatesTuple = getMaizePlantStressDates(self.simulationID)
            self.simulationSumTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.simulationSumTable.setFixedHeight(250)     
            self.simulationSumTable.setFixedWidth(440)     
            self.simulationSumTable.setRowCount(len(NitroWaterStressDatesTuple))
            self.simulationSumTable.setColumnCount(5)
            i = 0
            for record in NitroWaterStressDatesTuple:
                j = 0
                for col in record:
                    if j == 0:
                        date = dt.strptime(col, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
                        self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(date)))
                    else:
                        colFormat = '{:3.3f}'.format(col) 
                        if col <= 0.75:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                            self.simulationSumTable.item(i,j).setForeground(QColor(255, 0, 0))
                        else:
                            self.simulationSumTable.setItem(i,j,QTableWidgetItem(str(colFormat)))
                        self.simulationSumTable.item(i,j).setTextAlignment(Qt.AlignHCenter)
                    j = j + 1
                i = i + 1
            self.simulationSumTable.setHorizontalHeaderLabels(['Date','Water stress','Nitrogen stress','Carbon stress',
                                                               'Leaf Area Ratio'])
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
            self.simulationSumTable.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
            self.simulationSumTable.verticalHeader().hide()       
            self.simulationSumTable.resizeColumnsToContents()  

        self.simTab.setLayout(self.simTab.mainlayout)
        cropArr = [self.cropname]
    
        ########## plantTab ##########
        # Creates dictionaries based on crop type
        self.varDescDict, self.varDescUnitDict, self.varFuncDict = genDictOutput(cropArr,"plant",0)
        dateAxis = TimeAxisItem(orientation='bottom')
        self.plantGraphWidget = pg.PlotWidget(axisItems = {'bottom':dateAxis,'unitPrefix':None})
        if self.cropname != "fallow":
            self.plantTab.groupBox = QGroupBox("Select parameter to plot")
            self.leftBoxLayout = QGridLayout()
            self.plantCheckboxes = []
            i = 0
            for var in self.varDescDict:
                checkbox = QtWidgets.QCheckBox(self.varDescDict[var])
                self.plantCheckboxes.append(checkbox)
                j = i//2
                if i % 2 == 0:
                    self.leftBoxLayout.addWidget(checkbox,j,0)
                else:
                    self.leftBoxLayout.addWidget(checkbox,j,1)
                i+=1
            j+=1

            self.plotButtom = QPushButton("Plot")

            self.leftBoxLayout.addWidget(self.plotButtom,j,0,1,2)
            self.leftBoxLayout.addWidget(self.plantGraphWidget,0,2,j-1,4)
            self.plantTab.groupBox.setLayout(self.leftBoxLayout)
            self.plotButtom.clicked.connect(self.on_click_plotPlantTab)
 
            self.plantTab.mainlayout = QHBoxLayout()
            self.plantTab.mainlayout.addWidget(self.plantTab.groupBox)
            self.plantTab.setLayout(self.plantTab.mainlayout)
     
        ########## Soil Carbon Nitrogen tab ##########
        # Creates dictionaries based on crop type
        self.varSoilCNDescDict, self.varSoilCNDescUnitDict, self.varSoilCNFuncDict = genDictOutput(cropArr,"soilCN",0)

        dateAxis = TimeAxisItem(orientation='bottom')
        self.soilCNWidget = pg.PlotWidget(axisItems = {'bottom':dateAxis}) 
        self.soilCNTab.groupBox = QGroupBox("Select parameter to plot")
        self.leftBoxLayout = QGridLayout()
        self.soilCheckboxes = []
        i = 0
        for var in self.varSoilCNDescDict:
            checkbox = QtWidgets.QCheckBox(self.varSoilCNDescDict[var])
            self.soilCheckboxes.append(checkbox)
            j = i//2
            if i % 2 == 0:
                self.leftBoxLayout.addWidget(checkbox,j,0)
            else:
                self.leftBoxLayout.addWidget(checkbox,j,1)
            i+=1
        j+=1

        self.plotButtom = QPushButton("Plot")

        self.leftBoxLayout.addWidget(self.plotButtom,j,0,1,2)
        self.leftBoxLayout.addWidget(self.soilCNWidget,0,2,j-1,4)
        self.soilCNTab.groupBox.setLayout(self.leftBoxLayout)
        self.plotButtom.clicked.connect(self.on_click_soilCNTab)
 
        self.soilCNTab.mainlayout = QHBoxLayout()
        self.soilCNTab.mainlayout.addWidget(self.soilCNTab.groupBox)
        self.soilCNTab.setLayout(self.soilCNTab.mainlayout)
     
        ########## Soil Water Heat Nitrogen components 2D ##########
        # Creates dictionaries based on crop type
        self.varSoilwhn2DDescDict, self.varSoilwhn2DDescUnitDict, self.varSoilwhn2DFuncDict = genDictOutput(cropArr,"soilwhn2D",0)

        self.soilwhn2DTab.fig = plt.figure()
        self.soilwhn2DTab.canvas = FigureCanvas(self.soilwhn2DTab.fig)
        self.soilwhn2DTab.groupBox = QGroupBox()

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
        self.soilwhn2DTab.groupBox.setLayout(self.hboxLayoutSoil)
        self.plotButtomSoil.clicked.connect(self.on_click_plotSoil2DTab)

        self.soilwhn2DTab.mainlayout = QVBoxLayout()
        self.soilwhn2DTab.mainlayout.addWidget(self.soilwhn2DTab.groupBox)
        self.soilwhn2DTab.mainlayout.addWidget(self.soilwhn2DTab.canvas)
        self.soilwhn2DTab.setLayout(self.soilwhn2DTab.mainlayout)
     
        ########## Soil Time Series Tab ##########
        # Creates dictionaries based on crop type
        self.varSoilTSDescDict, self.varSoilTSDescUnitDict, self.varSoilTSFuncDict = genDictOutput(cropArr,"soilTS",0)

        self.SoilTSGraphWidget = pg.GraphicsLayoutWidget()

        dateAxisTotWatProf = TimeAxisItem(orientation='bottom')
        self.totWaterProfilePlot = self.SoilTSGraphWidget.addPlot(row=0,col=0,title="Total Water for Entire Profile (mm)",axisItems = {'bottom':dateAxisTotWatProf,'unitPrefix':None})

        dateAxisTotWatLayer = TimeAxisItem(orientation='bottom')
        self.totWaterLayerPlot = self.SoilTSGraphWidget.addPlot(row=0,col=1,title="Total Water by Layer (mm)",axisItems = {'bottom':dateAxisTotWatLayer,'unitPrefix':None})

        dateAxisWaterContLayer = TimeAxisItem(orientation='bottom')
        self.waterContentLayerPlot = self.SoilTSGraphWidget.addPlot(row=0,col=2,title="Water Conent by Layer (cm3/cm3)",axisItems = {'bottom':dateAxisWaterContLayer,'unitPrefix':None})

        dateAxisNNO3ConcProf = TimeAxisItem(orientation='bottom')
        self.NNO3ConcProfilePlot = self.SoilTSGraphWidget.addPlot(row=1,col=0,title="Total NNO3 as Nitrogen for Entire Profile (kg/ha)",axisItems = {'bottom':dateAxisNNO3ConcProf,'unitPrefix':None})

        dateAxisNNO3ConcLayer = TimeAxisItem(orientation='bottom')
        self.NNO3ConcLayerPlot = self.SoilTSGraphWidget.addPlot(row=1,col=1,title="Total NNO3 as Nitrogen by Layer (kg/ha)",axisItems = {'bottom':dateAxisNNO3ConcLayer,'unitPrefix':None})

        dateAxisTemp = TimeAxisItem(orientation='bottom')
        self.tempPlot = self.SoilTSGraphWidget.addPlot(row=1,col=2,title="Temperature by Layer (oC)",axisItems = {'bottom':dateAxisTemp,'unitPrefix':None})
       
        self.soilTSTab.mainlayout = QHBoxLayout()
        self.soilTSTab.mainlayout.addWidget(self.SoilTSGraphWidget)
        self.soilTSTab.setLayout(self.soilTSTab.mainlayout)
     
       # Create dictionary to hold dataframes
        df_collection = {}
        # Read geometry table for this simulation
        geo_df = readGeometrySimID(self.simulationID)
        # Read g03 table for this simulation
        t3 = extract_cropOutputData(self.g03Tablename,self.simulationID)
        new_df = t3['Date_Time'].str.split(' ', n=1, expand=True)
        # drop the id column
        t3 = t3.drop(columns=[self.g03Tablename + "_id"])
        # Get only date
        t3['Date'] = new_df[0]
        t3['Date'] = pd.to_datetime(t3['Date'])
        t3['Y'] = pd.to_numeric(t3['Y'],errors='coerce')
        for key in self.varSoilTSFuncDict:
            t3[key] = pd.to_numeric(t3[key],errors='coerce')
        t3 = t3.fillna(0)
        # Merge g03 table with geometry table
        t3 = pd.merge(geo_df,t3,how='inner',left_on=['X','Y'],right_on=['X','Y'])

        # Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth 
        # and the bottom of the profile is 0, we have to reverse this for the layer file. Thus we 
        # subtract the max depth from all the Y's'
        maxY = max(t3['Y'])
        t3['Y'] = maxY-t3['Y']

        t3['thNewArea'] = t3['thNew'] * t3['Area']
        t3['thNewNO3NArea'] = t3['thNew'] * t3['NO3N'] * t3['Area']

        # First, we need to group the data by day
        t3 = t3.groupby(['Date','X','Y'],as_index=False).mean()

        t3 = t3.drop(columns=["X","Q","NH4N","GasCon","hNew","Area"])

        LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']

        # Set total water profile plot x-axis label
        self.totWaterProfilePlot.clear()
        self.totWaterProfilePlot.setLabel("bottom", "Date")
        self.totWaterProfilePlot.showGrid(x=True, y=True)

        # Set total water by layer plot legend and x-axis label
        self.totWaterLayerPlot.clear()
        self.totWaterLayerPlot.setLabel("bottom", "Date")
        self.totWaterLayerPlot.showGrid(x=True, y=True)
        try:
            self.totWaterLayerPlotLegend.scene().removeItem(self.totWaterLayerPlotLegend)
        except Exception as e:
            print(e)
        self.totWaterLayerPlotLegend = self.totWaterLayerPlot.addLegend()

        # Set water content by layer plot legend and x-axis label
        self.waterContentLayerPlot.clear()
        self.waterContentLayerPlot.setLabel("bottom", "Date")
        self.waterContentLayerPlot.showGrid(x=True, y=True)
        try:
            self.waterContentLayerPlotLegend.scene().removeItem(self.waterContentLayerPlotLegend)
        except Exception as e:
            print(e)
        self.waterContentLayerPlotLegend = self.waterContentLayerPlot.addLegend()

        # Set NNO3 concentration for profile plot x-axis label
        self.NNO3ConcProfilePlot.clear()
        self.NNO3ConcProfilePlot.setLabel("bottom", "Date")
        self.NNO3ConcProfilePlot.showGrid(x=True, y=True)

        # Set NNO3 concentration by layer plot legend and x-axis label
        self.NNO3ConcLayerPlot.clear()
        self.NNO3ConcLayerPlot.setLabel("bottom", "Date")
        self.NNO3ConcLayerPlot.showGrid(x=True, y=True)
        try:
            self.NNO3ConcLayerPlotLegend.scene().removeItem(self.NNO3ConcLayerPlotLegend)
        except Exception as e:
            print(e)
        self.NNO3ConcLayerPlotLegend = self.NNO3ConcLayerPlot.addLegend()

        # Set Temp plot legend and x-axis label
        self.tempPlot.clear()
        self.tempPlot.setLabel("bottom", "Date")
        self.tempPlot.showGrid(x=True, y=True)
        try:
            self.tempPlotLegend.scene().removeItem(self.tempPlotLegend)
        except Exception as e:
            print(e)
        self.tempPlotLegend = self.tempPlot.addLegend()

        pen = pg.mkPen('r', width=3)

        # total water profile
        totWatProf = t3.groupby('Date',as_index=False)['thNewArea'].sum()
        # Get values for x-axis, these values will be used in all graphics on this tab.
        totWatProf['Date'] = pd.to_datetime(totWatProf['Date'])
        tmstampArray = np.array([row['Date'].timestamp() for index, row in totWatProf.iterrows()])
        totWatProf['totWatProf'] = totWatProf['thNewArea']/(self.eomult*self.rowSP)*10
        totWatProfMaxY = max(totWatProf['totWatProf'])
        self.totWaterProfilePlot.plot(x=tmstampArray,y=np.array(totWatProf['totWatProf']), pen=pen)
        # Set x-axis and y-axis
        self.totWaterProfilePlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,totWatProfMaxY*1.05),padding=0)
        self.totWaterProfilePlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=totWatProfMaxY*1.05)

        # NNO3 concentration profile
        NConcProf = t3.groupby('Date',as_index=False)['thNewNO3NArea'].sum()
        #N is ug/cm3 soil water. NNO3*10,000 cm2/m2 * 10,000 m2/ha * 1kg/1e9 ug/ (slab width) == kg/ha
        #NConcProf['NConcProf'] = NConcProf['thNewNO3N']*(14/64)*10000*10000/1000000000
        NConcProf['NConcProf'] = NConcProf['thNewNO3NArea']*(14/64)/10/(self.eomult*self.rowSP)
        NNO3ConcProfMaxY = max(NConcProf['NConcProf'])
        self.NNO3ConcProfilePlot.plot(x=tmstampArray,y=np.array(NConcProf['NConcProf']), pen=pen)
        # Set NNO3 concentration profile x-axis and y-axis
        self.NNO3ConcProfilePlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,NNO3ConcProfMaxY*1.05),padding=0)
        self.NNO3ConcProfilePlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=NNO3ConcProfMaxY*1.05)

        # Group by layer
        layers = t3.Layer.unique()
        i = 0
        totWatLayMaxY = 0
        watContLayMaxY = 0
        NNO3ConcLayMaxY = 0
        tempMaxY = 0

        for layer in layers:
            temp = t3.loc[t3['Layer']==layer]
            color = LINECOLORS[i]
            if i == 6:
                i = -1
            pen = pg.mkPen(color, width=3)

            depth = max(temp['Y'])
            # total water by layer
            totWatLay = temp.groupby(['Date','Layer'],as_index=False)['thNewArea'].sum()
            totWatLay['totWatLay'] = totWatLay['thNewArea']/(self.eomult*self.rowSP)*10
            if max(totWatLay['totWatLay']) > totWatLayMaxY:
                totWatLayMaxY = max(totWatLay['totWatLay'])
            self.totWaterLayerPlot.plot(x=tmstampArray,y=np.array(totWatLay['totWatLay']), name="Layer "+str(depth)+" cm", pen=pen)

            # water content by layer
            watContLay = temp.groupby(['Date','Layer'],as_index=False)['thNew'].mean()
            if max(watContLay['thNew']) > watContLayMaxY:
                watContLayMaxY = max(watContLay['thNew'])
            self.waterContentLayerPlot.plot(x=tmstampArray,y=np.array(watContLay['thNew']), name="Layer "+str(depth)+" cm", pen=pen)

            # NNO3 concentration by layer
            NConcLay = temp.groupby(['Date','Layer'],as_index=False)['thNewNO3NArea'].sum()
            #N is ug/cm3 soil water. NNO3*10,000 cm2/m2 * 10,000 m2/ha * 1kg/1e9 ug/ (slab width) == kg/ha
            #NConcProf['NConcProf'] = NConcProf['thNewNO3N']*(14/64)*10000*10000/1000000000
            NConcLay['NConcLay'] = NConcLay['thNewNO3NArea']*(14/64)/10/(self.eomult*self.rowSP)
            if max(NConcLay['NConcLay']) > NNO3ConcLayMaxY:
                NNO3ConcLayMaxY = max(NConcLay['NConcLay'])
            self.NNO3ConcLayerPlot.plot(x=tmstampArray,y=np.array(NConcLay['NConcLay']), name="Layer "+str(depth)+" cm", pen=pen)

            # temperature by layer
            tempLay = temp.groupby(['Date','Layer'],as_index=False)['Temp'].mean()
            if max(tempLay['Temp']) > tempMaxY:
                tempMaxY = max(tempLay['Temp'])
            self.tempPlot.plot(x=tmstampArray,y=np.array(tempLay['Temp']), name="Layer "+str(depth)+" cm", pen=pen)

            i = i + 1

        # Set total water by layer x-axis and y-axis
        self.totWaterLayerPlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,totWatLayMaxY*1.05),padding=0)
        self.totWaterLayerPlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=totWatLayMaxY*1.05)
        # Set water content by layer x-axis and y-axis
        self.waterContentLayerPlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,watContLayMaxY*1.05),padding=0)
        self.waterContentLayerPlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=watContLayMaxY*1.05)
        # Set NNO3 concentration by layer x-axis and y-axis
        self.NNO3ConcLayerPlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,NNO3ConcLayMaxY*1.05),padding=0)
        self.NNO3ConcLayerPlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=NNO3ConcLayMaxY*1.05)
        # Set temperature by layer x-axis and y-axis
        self.tempPlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,tempMaxY*1.05),padding=0)
        self.tempPlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=tempMaxY*1.05)


        ########## Root tab ##########
        if self.cropname != "fallow":
            # Creates dictionaries based on crop type
            self.varRootDescDict, self.varRootDescUnitDict, self.varRootFuncDict = genDictOutput(cropArr,"root",0)

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
        # Creates dictionaries based on crop type
        self.varSurfChaDescDict, self.varSurfChaDescUnitDict, self.varSurfChaFuncDict = genDictOutput(cropArr,"surfCha",0)

        dateAxis = TimeAxisItem(orientation='bottom')
        self.surfChaGraphWidget = pg.PlotWidget(axisItems = {'bottom':dateAxis}) 
 
        self.surfChaTab.groupBox = QGroupBox("Select parameter to plot")
        self.surfChaTab.groupBox.setMaximumWidth(270)
        self.vboxSurfChaLayout = QVBoxLayout()
 
        self.surfChaCheckboxes = []
        for var in self.varSurfChaDescDict:
            checkbox = QtWidgets.QCheckBox(self.varSurfChaDescDict[var])
            self.surfChaCheckboxes.append(checkbox)
            self.vboxSurfChaLayout.addWidget(checkbox)

        self.surfChaPlotButtom = QPushButton("Plot")

        self.vboxSurfChaLayout.addWidget(self.surfChaPlotButtom)
        self.vboxSurfChaLayout.addStretch()
        self.surfChaTab.groupBox.setLayout(self.vboxSurfChaLayout)
        self.surfChaPlotButtom.clicked.connect(self.on_click_plotSurfChaTab)
 
        self.surfChaTab.mainlayout = QGridLayout()
        self.surfChaTab.mainlayout.addWidget(self.surfChaTab.groupBox,0,0,2,1)
        self.surfChaTab.mainlayout.addWidget(self.surfChaGraphWidget,0,1)
        self.surfChaTab.setLayout(self.surfChaTab.mainlayout)
        #################################################################################

        if self.simulationID != None:            
            self.display1.addTab(scrollbar,"Simulation Summary")
            if self.cropname != "fallow":
                self.display1.addTab(self.plantTab,"Plant")
            self.display1.addTab(self.soilCNTab,"Soil Carbon Nitrogen")            
            self.display1.addTab(self.soilwhn2DTab,"2D Soil Water Heat Nitrogen")            
            self.display1.addTab(self.soilTSTab,"Soil Time Series")            
            if self.cropname != "fallow":
                self.display1.addTab(self.rootTab,"Root Data")            
            self.display1.addTab(self.surfChaTab,"Surface Characteristics")
            self.display1.setVisible(True)

   
    def importfaq(self, thetabname=None):        
        faqlist = read_FaqDB(thetabname,'') 
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
