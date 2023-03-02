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

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
app_dir = os.path.join(gparent_dir,'classim_v3')
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


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        #return [date.fromtimestamp(value).strftime('%m/%d/%y') for value in values]
        return [date.fromtimestamp(value).strftime('%m/%d') for value in values]


#this is widget of type 1. It would be added to as a tab
class RotOutput_Widget(QWidget):
    # Add a signal    
    def __init__(self):
        super(RotOutput_Widget,self).__init__()
        self.init_ui()


    def init_ui(self):
        self.setGeometry(QtCore.QRect(10,20,700,700))
        self.setAccessibleName("rotation_output")
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

        self.tab_summary = QTextEdit("Choose rotation by checking from the list box.")                
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

        self.plotoutput = QPushButton("Select Rotation")
        self.deleteSim = QPushButton("Delete Rotation")
        self.buttonhlayout = QVBoxLayout()
        self.buttonhlayout.addWidget(self.plotoutput)
        self.buttonhlayout.addWidget(self.deleteSim)
        self.buttonhlayout.addStretch(1)
        self.display1 = QTabWidget()
        self.statistic_toollist = ['hourly','daily'] 

        self.table2.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table2.setFixedHeight(100)     
        self.table2.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table2.setAlternatingRowColors(True)
        self.error_tuplelist = []
        self.populate()
        self.table2.setHorizontalHeaderLabels(['RotID','Site','Station Name','Weather','Soil','SimID','Treatment','Start\nYear','End\nYear',
                                               'Water\nStress','Nitrogen\nStress','Temp\nVariance (oC)','Rain\nVariance (%)','CO2\nVariance (ppm)'])
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
        self.table2.horizontalHeader().setSectionResizeMode(13,QHeaderView.ResizeToContents)
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
        rotation_object.rotationUpSig.connect(self.populate)

    def populate(self):
        rlist = extract_pastrunsidDB(-99)
 
        # When setRowCount is set to 0, the table gets refreshed.
        self.table2.setRowCount(0)
        self.table2.setRowCount(len(rlist))
        self.table2.setColumnCount(14)
        self.table2.simGrp = QButtonGroup()
        for row1 in range(len(rlist)): 
            for col in range(len(rlist[row1])):
                if(row1 == 0 or rlist[row1][0] != rlist[row1-1][0]):
                    if col == 0:
                        radioitem = QRadioButton(str(rlist[row1][col]))
                        self.table2.simGrp.addButton(radioitem,col)
                        self.table2.setCellWidget(row1,col,radioitem)
                    else:
                        self.table2.setItem(row1,col,QTableWidgetItem(str(rlist[row1][col])))
                else:
                    if col < 5:
                        self.table2.setItem(row1,col,QTableWidgetItem())
                    else:
                        self.table2.setItem(row1,col,QTableWidgetItem(str(rlist[row1][col])))


    def on_click_plotPlantTab(self):
        LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
        checkedVar = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                for key, value in self.finalVarDescDict.items():
                    if checkbox.text() == value:
                         checkedVar.append(key)

        data_df = pd.DataFrame([])
        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            t1 = pd.DataFrame([])
            if self.cropArr[runNum] != "fallow":
                self.g01Tablename = "g01_" + self.cropArr[runNum]
                exid = read_experimentDB_id(self.cropArr[runNum],self.expArr[runNum])
                tid = read_treatmentDB_id(exid,self.treatArr[runNum])
                plantDensity = getPlantDensity(tid)
                t1 = extract_cropOutputData(self.g01Tablename,self.simIDArr[runNum])
                tableID = self.g01Tablename + "_id"
                if self.cropArr[runNum] == "maize":
                    t1.drop(columns=[tableID,'jday','Note'], inplace=True)
                    t1 = t1.add_suffix('__mai')
                    t1.rename(columns={'Date_Time__mai':'Date_Time'}, inplace=True)
                    t1.loc[t1.SolRad__mai <= 0,'SolRad__mai'] = np.nan
                    t1['PFD__mai'] = (t1['PFD__mai']*3600)/1000000
                elif self.cropArr[runNum] == "potato":
                    t1.drop(columns=[tableID,'jday'], inplace=True)
                    t1 = t1.add_suffix('__pot')
                    t1.rename(columns={'Date_Time__pot':'Date_Time'}, inplace=True)
                    t1.loc[t1.SolRad__pot <= 0,'SolRad__pot'] = np.nan
                    t1['PFD__pot'] = (t1['PFD__pot']*3600)/1000000
                elif self.cropArr[runNum] == "soybean":
                    t1.drop(columns=[tableID,'jday'], inplace=True)
                    t1 = t1.add_suffix('__soy')
                    t1.rename(columns={'Date_Time__soy':'Date_Time'}, inplace=True)
                    t1.loc[t1.SolRad__soy <= 0,'SolRad__soy'] = np.nan
                    t1['PFD__soy'] = (t1['PFD__soy']*3600)/1000000
                elif self.cropArr[runNum] == "cotton":
                    t1.drop(columns=[tableID], inplace=True)
                    t1 = t1.add_suffix('__cot')
                    t1.rename(columns={'Date_Time__cot':'Date_Time'}, inplace=True)
                    t1.loc[t1.SRad__cot <= 0,'SRad__cot'] = np.nan
            data_df = data_df.append(t1,ignore_index=True) 

        new_df = data_df['Date_Time'].str.split(' ', n=1, expand=True)
        data_df['Date'] = new_df[0]
        data_df['Date'] = pd.to_datetime(data_df['Date'])
        for key in self.finalVarFuncDict:
            data_df[key] = pd.to_numeric(data_df[key],errors='coerce')
        data_df_grouped = data_df.groupby(['Date'], as_index=False).agg(self.finalVarFuncDict)
        data_df_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        data_df_grp = data_df_grouped.set_index('Date_Time').resample('1D').asfreq().fillna(0)                     
        data_df_grp.reset_index(inplace=True)
        tmstampArray = np.array([row['Date_Time'].timestamp() for index, row in data_df_grp.iterrows()])

        self.plantGraphWidget.clear()
        self.plantGraphWidget.setLabel("bottom", "Date")
        self.plantGraphWidget.showGrid(x=True, y=True)
        self.legend = self.plantGraphWidget.addLegend()
        
        i = 0
        maxY = 0
        for var in checkedVar:
            color = LINECOLORS[i]
            pen = pg.mkPen(color,width=3)
            if max(data_df_grp[var]) > maxY:
                maxY = max(data_df_grp[var])
            self.plantGraphWidget.plot(x=tmstampArray,y=np.array(data_df_grp[var]), name=self.finalVarDescUnitDict[var], pen=pen)
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
                for key, value in self.finalSoilCNVarDescDict.items():
                    if checkbox.text() == value:
                         checkedVar.append(key)

        # Create dictionary to hold dataframes
        data_df = pd.DataFrame([])
        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            t7 = pd.DataFrame([])
            self.g07Tablename = "g07_" + self.cropArr[runNum]
            t7 = extract_cropOutputData(self.g07Tablename,self.simIDArr[runNum])
            # drop the id column 
            t7 = t7.drop(columns=[self.g07Tablename + "_id"])
            # Read area from geometry table
            geo_df = readGeometrySimID(self.simIDArr[runNum])
            # Merge geo_df dataframe to t7 dataframe
            t7 = pd.merge(geo_df,t7, how='inner', left_on=['X','Y'], right_on=['X','Y'])
            # each simulation has its own rowSP and eomult, so here we are storing these values
            t7['eomult'] = self.eomultArr[runNum]
            t7['rowSP'] = self.rowSPArr[runNum]
            data_df = data_df.append(t7,ignore_index=True) 

        # Rename data_df to t7
        t7 = data_df
        new_df = t7['Date_Time'].str.split(' ', n=1, expand=True)
        # Get only date
        t7['Date'] = new_df[0]
        t7['Date'] = pd.to_datetime(t7['Date'])
        t7 = t7.drop(columns=["Date_Time"])
        for key in t7:
            if key != "Date":
                t7[key] = pd.to_numeric(t7[key],errors='coerce')
        t7 = t7.fillna(0)

        # Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth and the bottom
        # of the profile is 0, we have to reverse this for the layer file. Thus we subtract the max depth from all the Y's'
        maxY = max(t7['Y'])
        t7['Y'] = maxY-t7['Y']

        #values are now total ugrams in the domain area (1/2 row spacing *1 cm), scale to kg/ha
        t7['fact']=1.0/(0.01*t7['rowSP']/100.0*t7['eomult']) # m2 area if the slab
        t7['fact']=t7['fact']*10000./1000./1000./1000.  #scale area

        # First group every node by Date, X and Y
        # average the 24 hourly periods over each day
        t7 = t7.groupby(['Date','X','Y'], as_index=False).agg({'Area':['mean'],'Humus_N':['mean'],'Humus_C':['mean'],'Litter_N':['mean'],
                                                       'Litter_C':['mean'],'Manure_N':['mean'],'Manure_C':['mean'],
                                                       'Root_N':['mean'],'Root_C':['mean'],'fact':['mean']})

        t7 = t7.drop(columns=["X","Y"])
        t7.columns = ["_".join(x) for x in t7.columns.ravel()]
        t7.rename(columns={'Date_':'Date'}, inplace=True)

        # Multiply by area to get total g in each node
        for key in t7:
            if (key != "Date" and key != "Area_mean" and key != "fact"):
                t7[key] = t7[key]*t7['Area_mean']
        t7 = t7.drop(columns=["Area_mean"])

        # Group by Date adding all nodal values
        t7 = t7.groupby(['Date'], as_index=False).agg({'Humus_N_mean':['sum'],'Humus_C_mean':['sum'],'Litter_N_mean':['sum'],
                                                       'Litter_C_mean':['sum'],'Manure_N_mean':['sum'],'Manure_C_mean':['sum'],
                                                       'Root_N_mean':['sum'],'Root_C_mean':['sum'],'fact_mean':['mean']})
        t7.columns = ["_".join(x) for x in t7.columns.ravel()]
        t7.rename(columns={'Date_':'Date_Time'}, inplace=True)

        tmstampArray = np.array([row['Date_Time'].timestamp() for index, row in t7.iterrows()])
        #values are now total ugrams in the domain area (1/2 row spacing *1 cm), scale to kg/ha
        for column in t7.columns:
          if column in ['Humus_N_mean_sum','Humus_C_mean_sum','Litter_N_mean_sum','Litter_C_mean_sum','Manure_N_mean_sum','Manure_C_mean_sum','Root_N_mean_sum','Root_C_mean_sum']:
              t7[column]=t7[column]*t7['fact_mean_mean']                                         
              
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
            self.soilCNWidget.plot(x=tmstampArray,y=np.array(t7[var+'_mean_sum']), name=self.finalSoilCNVarDescUnitDict[var], pen=pen)
            if i < 6:
                i = i + 1
            else:
                i = 0
        # set Y  and X range
        self.soilCNWidget.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,maxY*1.05),padding=0)
        self.soilCNWidget.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=maxY*1.05)


    def on_click_plotSoil2DTab(self):
        date = self.comboDate.currentText()
        data_df = pd.DataFrame([])
        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            t3 = pd.DataFrame([])
            self.g03Tablename = "g03_" + self.cropArr[runNum]
            t3 = extract_cropOutputData(self.g03Tablename,self.simIDArr[runNum])
            tableID = self.g03Tablename + "_id"
            t3.drop(columns={tableID}, inplace=True)
            data_df = data_df.append(t3,ignore_index=True) 
        new_df = data_df['Date_Time'].str.split(' ', n=1, expand=True)
        data_df['Date'] = new_df[0]

        for key in self.varSoilwhn2DDescUnitDict:
            data_df[key] = pd.to_numeric(data_df[key],errors='coerce')
        data_df = data_df.fillna(0)
        data_df_grouped = data_df.groupby(['Date','X','Y'], as_index=False).agg(self.varSoilwhn2DFuncDict)
        data_df_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        df_collection = data_df_grouped.loc[data_df_grouped['Date_Time'] == date].filter(['hNew','thNew','NO3N','Temp','X','Y'],axis=1)

        rows = 1
        columns = 4
        i = 1

        ## Create image
        self.soilwhnTab.fig.clear()
        self.soilwhnTab.canvas.flush_events()
        for var, desc in self.varSoilwhn2DDescUnitDict.items():
            title = desc
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
            levels = np.linspace(z.min(), z.max(),10)
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
            i = i + 1


    def on_click_rootTab(self):
        date = self.comboDateRoot.currentText()

        data_df = pd.DataFrame([])
        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            t4 = pd.DataFrame([])
            if self.cropArr[runNum] != "fallow":
                self.g04Tablename = "g04_" + self.cropArr[runNum]
                t4 = extract_cropOutputData(self.g04Tablename,self.simIDArr[runNum])
                tableID = self.g04Tablename + "_id"
                t4.drop(columns=[tableID], inplace=True)
            data_df = data_df.append(t4,ignore_index=True) 

        new_df = data_df['Date_Time'].str.split(' ', n=1, expand=True)
        data_df['Date'] = new_df[0]
        data_df['RDenM'] = pd.to_numeric(data_df['RDenM'],errors='coerce')
        data_df['RDenY'] = pd.to_numeric(data_df['RDenY'],errors='coerce')
        data_df['RMassM'] = pd.to_numeric(data_df['RMassM'],errors='coerce')
        data_df['RMassY'] = pd.to_numeric(data_df['RMassY'],errors='coerce')
        # Creating RDenT and RMassT variables
        data_df['RDenT'] = data_df['RDenM'] + data_df['RDenY']
        data_df['RMassT'] = data_df['RMassM'] + data_df['RMassY']
        data_df_grouped = data_df.groupby(['Date','X','Y'], as_index=False).agg(self.varRootFuncDict)
        data_df_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        df_collection = data_df_grouped.loc[data_df_grouped['Date_Time'] == date].filter(['RDenT','RMassT','X','Y'],axis=1)

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
            x = new_arr[:,0].reshape(nx,ny)
            y = new_arr[:,1].reshape(nx,ny)
            z = new_arr[:,2].reshape(nx,ny)
            maxY = max(map(max, y))
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
        SeasPSoEvMax = 0
        SeasASoEvMax = 0
        SeasPTranMax = 0
        SeasATranMax = 0
        SeasRainMax = 0
        SeasInfilMax = 0
        checkedVar = []
        LINECOLORS = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
        for i, checkbox in enumerate(self.surfChaCheckboxes):
            if checkbox.isChecked():
                for key, value in self.varSurfChaDescDict.items():
                    if checkbox.text() == value:
                         checkedVar.append(key)

        data_df = pd.DataFrame([])
        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            t5 = pd.DataFrame([])
            self.g05Tablename = "g05_" + self.cropArr[runNum]
            exid = read_experimentDB_id(self.cropArr[runNum],self.expArr[runNum])
            tid = read_treatmentDB_id(exid,self.treatArr[runNum])
            plantDensity = getPlantDensity(tid)
            t5 = extract_cropOutputData(self.g05Tablename,self.simIDArr[runNum])
            tableID = self.g05Tablename + "_id"
            t5.drop(columns={tableID}, inplace=True)
            for var in checkedVar:
                t5[var] = (t5[var] * plantDensity)/1000
            t5['SeasPSoEv'] = t5['SeasPSoEv'] + SeasPSoEvMax
            t5['SeasASoEv'] = t5['SeasASoEv'] + SeasASoEvMax
            t5['SeasPTran'] = t5['SeasPTran'] + SeasPTranMax
            t5['SeasATran'] = t5['SeasATran'] + SeasATranMax
            t5['SeasRain'] = t5['SeasRain'] + SeasRainMax
            t5['SeasInfil'] = t5['SeasInfil'] + SeasInfilMax
            SeasPSoEvMax = t5['SeasPSoEv'].max()
            SeasASoEvMax = t5['SeasASoEv'].max()
            SeasPTranMax = t5['SeasPTran'].max()
            SeasATranMax = t5['SeasATran'].max()
            SeasRainMax = t5['SeasRain'].max()
            SeasInfilMax = t5['SeasInfil'].max()
            
            data_df = data_df.append(t5,ignore_index=True) 
        new_df = data_df['Date_Time'].str.split(' ', n=1, expand=True)
        data_df['Date'] = new_df[0]

        for key in self.varSurfChaFuncDict:
            data_df[key] = pd.to_numeric(data_df[key],errors='coerce')
        data_df = data_df.fillna(0)
        data_df_grouped = data_df.groupby(['Date'], as_index=False).agg(self.varSurfChaFuncDict)
        data_df_grouped.rename(columns={'Date':'Date_Time'}, inplace=True)
        data_df_grouped['Date_Time'] = pd.to_datetime(data_df_grouped['Date_Time'])
        tmstampArray = np.array([row['Date_Time'].timestamp() for index, row in data_df_grouped.iterrows()])

        self.surfChaGraphWidget.clear()
        self.surfChaGraphWidget.setLabel("bottom", "Date")
        self.surfChaGraphWidget.showGrid(x=True, y=True)
        self.legend = self.surfChaGraphWidget.addLegend()
        
        i = 0
        maxY = 0
        for var in checkedVar:
            color = LINECOLORS[i]
            pen = pg.mkPen(color,width=3)
            if max(data_df_grouped[var]) > maxY:
                maxY = max(data_df_grouped[var])
            self.surfChaGraphWidget.plot(x=tmstampArray,y=np.array(data_df_grouped[var]), name=self.varSurfChaDescUnitDict[var], pen=pen)
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
            self.rotationID = self.table2.simGrp.buttons()[self.rowNumChecked].text()
            self.cropname = self.table2.item(self.rowNumChecked,6).text().split('/')[0]   

            delete_pastrunsDB_rotationID(self.rotationID,run_dir,self.cropname)
            self.populate()


    def on_click_table_widget(self):
        '''
        This gets called when USER clicks one of the old simulation row/column. 
        It will plot the graph(s) for the selected simulation
        '''
        global img, data, i, updateTime, fps
        regexp_num = QtCore.QRegExp('\d+(\.\d+)?')
        validator_num = QtGui.QRegExpValidator(regexp_num)
        tab = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        self.simIDArr = []
        self.cropArr = []   
        self.expArr = []   
        self.treatArr = [] 
        self.eomultArr = []
        self.rowSPArr = []

        self.rowNumChecked = [self.table2.simGrp.buttons()[x].isChecked() for x in range(len(self.table2.simGrp.buttons()))].index(True)
        self.rotationID = self.table2.simGrp.buttons()[self.rowNumChecked].text()

        # self.rowNumChecked is the index of the radio box that was checked which doesn't match the 
        # table row index, that the radio box is located.
        placeOnTable = self.rowNumChecked + 1
        count = 0
        for x in range(self.table2.rowCount()):
            #print(self.table2.item(x,0))
            if self.table2.item(x,0) is None:
                count = count + 1
                if count == placeOnTable:
                    ind = x

        self.sitename = self.table2.item(ind,1).text()    
        self.stationtypename = self.table2.item(ind,2).text()    
        self.weathername = self.table2.item(ind,3).text()    
        self.soilname = self.table2.item(ind,4).text()
        self.simIDArr.append(self.table2.item(ind,5).text())
        self.cropArr.append(self.table2.item(ind,6).text().split('/')[0])   
        self.expArr.append(self.table2.item(ind,6).text().split('/')[1])   
        self.treatArr.append(self.table2.item(ind,6).text().split('/')[2]) 

        # Find crop, experiment and treatments associated with this rotation
        nextRow = ind + 1
        while nextRow < self.table2.rowCount():
            if self.table2.item(nextRow,1).text() == "":
                self.simIDArr.append(self.table2.item(nextRow,5).text())
                self.cropArr.append(self.table2.item(nextRow,6).text().split('/')[0])   
                self.expArr.append(self.table2.item(nextRow,6).text().split('/')[1])   
                self.treatArr.append(self.table2.item(nextRow,6).text().split('/')[2])
            else:
                break
            nextRow = nextRow + 1

        self.display1.clear()
        scrollbar = QScrollArea(widgetResizable=True)
        self.simTab = QWidget()
        scrollbar.setWidget(self.simTab)
        self.plantTab = QWidget()
        self.soilCNTab = QWidget()
        self.soilTSTab = QWidget()
        self.soilwhnTab = QWidget()
        self.rootTab = QWidget()
        self.surfChaTab = QWidget()

        ########## simTab ##########
        self.simTabWidget = QtWidgets.QWidget(self.simTab)
        self.simTab.mainlayout = QFormLayout(self.simTabWidget)
        self.simTabWidget.setLayout(self.simTab.mainlayout)
        self.simTab.setLayout(self.simTab.mainlayout)

        genInfoBox = QVBoxLayout()
 
        # Box with general info like sitename, soil, station and weather
        genInfoBoxSum = QHBoxLayout()
        genInfoBoxSumLabel = QLabel()
        genInfoBoxSum.addWidget(genInfoBoxSumLabel)
        genInfoBoxSum.setAlignment(Qt.AlignTop)

        self.simSummaryGen = "<i>General Information </i>"
        self.simSummaryGen += "<br><br><i>Site: </i>" + self.sitename
        self.simSummaryGen += tab + "<i>Soil: </i>" + self.soilname
        self.simSummaryGen += tab + "Station Name: </i>" + self.stationtypename
        self.simSummaryGen += tab + "<i>Weather: </i>" + self.weathername
        genInfoBoxSumLabel.setText(self.simSummaryGen)

        # Adding sections to genInfoBox
        genInfoBox.addLayout(genInfoBoxSum)

        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            # Box with information about crop, cultivar, treatment and experiment
            runInfoBoxSum = QHBoxLayout()
            runInfoBoxSumLabel = QLabel()
            runInfoBoxSum.addWidget(runInfoBoxSumLabel)
            runInfoBoxSum.setAlignment(Qt.AlignTop)

            self.simSummaryRun = tab + "<br><br><i>Crop: </i>" + self.cropArr[runNum]
            self.simSummaryRun += tab + "<i>Experiment: </i>" + self.expArr[runNum]
            self.simSummaryRun += tab + "<i>Treatment: </i>" + self.treatArr[runNum]
            runInfoBoxSumLabel.setText(self.simSummaryRun)

            # Adding sections to genInfoBox
            genInfoBox.addLayout(runInfoBoxSum)

            # Separator
            separatorBox = QHBoxLayout()
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setLineWidth(2)
            separatorBox.addWidget(separator)

            # Adding sections to genInfoBox
            genInfoBox.addLayout(separatorBox)

            # Create horizontal box to store the verticql boxes with dates, agronomic and environmental data
            datesAgroEnvBoxSum = QHBoxLayout()
         
            # Agronomic dates
            genInfoBoxAgroDates = QVBoxLayout()
            genInfoBoxAgroDatesLabel = QLabel()
            genInfoBoxAgroDates.addWidget(genInfoBoxAgroDatesLabel)
            genInfoBoxAgroDates.setAlignment(Qt.AlignTop)

            exid = read_experimentDB_id(self.cropArr[runNum],self.expArr[runNum])
            tid = read_treatmentDB_id(exid,self.treatArr[runNum])
            plantDensity = getPlantDensity(tid)
            operationList = read_operationsDB_id(tid) #gets all the operations
            FertilizerDateList = []
            BeginDate = ""
            SowingDate = ""
            TillageDate = ""
            EmergenceDate = ""
            HarvestDate = ""
            EndDate = ""            
                 
            for ii,jj in enumerate(operationList):
                if jj[1] == 'Simulation Start':
                    BeginDate = jj[2] #month/day/year
 
                    initCond = readOpDetails(jj[0],jj[1])
                    self.plantDensity = initCond[0][3]
                    self.eomultArr.append(initCond[0][8])
                    self.rowSPArr.append(initCond[0][9])
                    self.cultivar = initCond[0][10]

                if jj[1] == 'Sowing':                            
                    SowingDate=jj[2]

                if jj[1] == 'Tillage':                            
                    TillageDate=jj[2]

                if jj[1] in "Fertilizer":   
                    FertilizerDateList.append(jj[2])       

                if jj[1] == 'Emergence':                            
                    EmergenceDate=jj[2]

                if jj[1] == 'Harvest':                            
                    HarvestDate=jj[2] #month/day/year

                if jj[1] == 'Simulation End':                            
                    EndDate=jj[2] #month/day/year

            FertilizerDate = ""
            if len(FertilizerDateList) >= 1:
                FertilizerDate = ", "
                FertilizerDate = FertilizerDate.join(FertilizerDateList) 

            self.simSummaryDates = "<i>Simulation Dates </i>"
            self.simSummaryDates += "<br><i>Start Date: </i>" + BeginDate
            if TillageDate != "":
                self.simSummaryDates += "<br><i>Tillage Date: </i>" + TillageDate
            if self.cropArr[runNum] != "fallow":
                self.simSummaryDates += "<br><i>Planting Date: </i>" + SowingDate
            if FertilizerDate != "":
                self.simSummaryDates += "<br><i>Fertilization Date: </i>" + FertilizerDate
            if self.cropArr[runNum] == "potato":
                TuberInitDate = getTuberInitDate(self.simIDArr[runNum])
                MaturityDate = getMaturityDate(self.simIDArr[runNum])
                self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
                self.simSummaryDates += "<br><i>Tuber Initiation Date: </i>" + TuberInitDate
                self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
            elif self.cropArr[runNum] == "maize":
                EmergenceDate = getMaizeDateByDev(self.simIDArr[runNum],"Emerged")
                TasseledDate = getMaizeDateByDev(self.simIDArr[runNum],"Tasseled")
                SilkedDate = getMaizeDateByDev(self.simIDArr[runNum],"Silked")
                MaturityDate = getMaizeDateByDev(self.simIDArr[runNum],"Matured")
                self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
                self.simSummaryDates += "<br><i>Tasseled Date: </i>" + TasseledDate
                self.simSummaryDates += "<br><i>Silked Date: </i>" + SilkedDate
                self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
            elif self.cropArr[runNum] == "soybean":
                FirstFlowerDate = getSoybeanDevDate(self.simIDArr[runNum],1)
                PodInitDate = getSoybeanDevDate(self.simIDArr[runNum],3)
                SeedInitDate = getSoybeanDevDate(self.simIDArr[runNum],4)
                MaturityDate = getSoybeanDevDate(self.simIDArr[runNum],7)
                self.simSummaryDates += "<br><i>Emergence Date: </i>" + EmergenceDate
                self.simSummaryDates += "<br><i>First Flower Date: </i>" + FirstFlowerDate
                self.simSummaryDates += "<br><i>Pod Initiation Date: </i>" + PodInitDate
                self.simSummaryDates += "<br><i>Seed Initiation Date: </i>" + SeedInitDate
                self.simSummaryDates += "<br><i>Maturity Date: </i>" + MaturityDate
            if self.cropArr[runNum] != "fallow":
                self.simSummaryDates += "<br><i>Harvest Date: </i>" + HarvestDate
 
            genInfoBoxAgroDatesLabel.setText(self.simSummaryDates)
            datesAgroEnvBoxSum.addLayout(genInfoBoxAgroDates)

            # Agronomic data
            if self.cropArr[runNum] != "fallow":
                genInfoBoxAgroData = QVBoxLayout()
                genInfoBoxAgroDataLabel = QLabel()
                genInfoBoxAgroData.addWidget(genInfoBoxAgroDataLabel)
                genInfoBoxAgroData.setAlignment(Qt.AlignTop)

                self.simSummaryAgroData = ""
                if self.cropArr[runNum] == "potato" or self.cropArr[runNum] == "soybean":
                    if self.cropArr[runNum] == "potato":
                        agroDataTuple = getPotatoAgronomicData(self.simIDArr[runNum], HarvestDate)
                    else:
                        #print(self.simIDArr[runNum])
                        #print(HarvestDate)
                        agroDataTuple = getSoybeanAgronomicData(self.simIDArr[runNum], HarvestDate)
                    #print("agroDataTuple=",agroDataTuple)
                    NitrogenUptakeTuple = getNitrogenUptake(self.simIDArr[runNum], HarvestDate, self.cropArr[runNum])
                    self.simSummaryAgroData = "<i>Simulation Agronomic Data at <br>" + HarvestDate + " (harvest date)</i>"
                    self.simSummaryAgroData += "<br><i>Yield: </i>" + '{:3.2f}'.format(agroDataTuple[0]*plantDensity*10) + " kg/ha"
                    self.simSummaryAgroData += "<br><i>Total biomass: </i>" +  '{:3.2f}'.format(agroDataTuple[1]*plantDensity*10) + " kg/ha"
                    self.simSummaryAgroData += "<br><i>Nitrogen Uptake: </i>" +  '{:3.2f}'.format(NitrogenUptakeTuple[0]*plantDensity/10) + " kg/ha"
                    self.simSummaryAgroData += "<br><i>Transpiration: </i>" +  '{:3.2f}'.format(agroDataTuple[2]*plantDensity/1000) + " mm"
                elif self.cropArr[runNum] == "maize":
                    if(MaturityDate != "N/A"):
                        agroDataTuple = getMaizeAgronomicData(self.simIDArr[runNum], MaturityDate)
                        self.simSummaryAgroData = "<i>Simulation Agronomic Data at <br>" + MaturityDate + " (maturity date)</i>"
                    else:
                        agroDataTuple = getMaizeAgronomicData(self.simIDArr[runNum], HarvestDate)
                        self.simSummaryAgroData = "<i>Simulation Agronomic Data at <br>" + HarvestDate + " (harvest date)</i>"
                    self.simSummaryAgroData += "<br><i>Yield: </i>" + '{:3.2f}'.format(agroDataTuple[0]*plantDensity*10) + " kg/ha"
                    self.simSummaryAgroData += "<br><i>Total biomass: </i>" + '{:3.2f}'.format(agroDataTuple[1]*plantDensity*10) + " kg/ha"
                    self.simSummaryAgroData += "<br><i>Nitrogen Uptake: </i>" +  '{:3.2f}'.format(agroDataTuple[2]*plantDensity*10) + " kg/ha"
                elif self.cropArr[runNum] == "cotton":
                    yieldDataTuple = getCottonYieldData(self.simIDArr[runNum])
                    yieldDate = dt.strptime(yieldDataTuple[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
                    FirstSquareDate = getCottonDevDate(self.simIDArr[runNum],"1stSquare")
                    FirstBloomDate = getCottonDevDate(self.simIDArr[runNum],"1stBloom")
                    FirstOpenBollDate = getCottonDevDate(self.simIDArr[runNum],"1stOpenBoll")
                    envDataTuple = getEnvironmentalData(self.simIDArr[runNum],HarvestDate,self.cropArr[runNum])
                    self.envSummaryData = "<i>Simulation Environmental Data </i>"
                    self.simSummaryAgroDates = "<i>Simulation Agronomic Data at <br>" + yieldDate + "</i>"
                    self.simSummaryAgroDates += "<br><i>Date of first square: </i>" + FirstSquareDate
                    self.simSummaryAgroDates += "<br><i>Date of first bloom: </i>" + FirstBloomDate
                    self.simSummaryAgroDates += "<br><i>Date of first open boll: </i>" + FirstOpenBollDate
                    self.simSummaryAgroDates += "<br><i>Yield: </i>" + '{:3.2f}'.format(yieldDataTuple[1]*1.12) + " kg/ha"

                genInfoBoxAgroDataLabel.setText(self.simSummaryAgroData)
                datesAgroEnvBoxSum.addLayout(genInfoBoxAgroData)

            # Environment Data
            envInfoBoxData = QVBoxLayout()
            envInfoBoxDataLabel = QLabel()
            envInfoBoxData.addWidget(envInfoBoxDataLabel)
            envInfoBoxData.setAlignment(Qt.AlignTop)

            if self.cropArr[runNum] == "potato" or self.cropArr[runNum] == "soybean":
                envDataTuple = getEnvironmentalData(self.simIDArr[runNum], HarvestDate, self.cropArr[runNum])
                self.envSummaryData = "<i>Simulation Environmental Data at <br>" + HarvestDate + " (harvest date)</i>"
            elif self.cropArr[runNum] == "maize":
                if(MaturityDate != "N/A"):
                    envDataTuple = getEnvironmentalData(self.simIDArr[runNum], MaturityDate, self.cropArr[runNum])
                    self.envSummaryData = "<i>Simulation Environmental Data at <br>" + MaturityDate + " (maturity date)</i>"
                else:
                    envDataTuple = getEnvironmentalData(self.simIDArr[runNum], HarvestDate, self.cropArr[runNum])
                    self.envSummaryData = "<i>Simulation Environmental Data at <br>" + HarvestDate + " (harvest date)</i>"
            elif self.cropArr[runNum] == "fallow":
                plantDensity = 6.5
                envDataTuple = getEnvironmentalData(self.simIDArr[runNum], EndDate, self.cropArr[runNum])
                self.envSummaryData = "<i>Simulation Environmental Data at <br>" + EndDate + " (simulation end date)</i>"
 
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

            datesAgroEnvBoxSum.addLayout(envInfoBoxData)

            # Adding sections to genInfoBox
            genInfoBox.addLayout(datesAgroEnvBoxSum)

        self.simTab.mainlayout.addRow(genInfoBox)
        self.simTab.setLayout(self.simTab.mainlayout)
     
        ########## plantTab ##########
        # Creates dictionaries based on crop type
        self.finalVarDescDict, self.finalVarDescUnitDict, self.finalVarFuncDict = genDictOutput(self.cropArr,"plant",1)

        dateAxis = TimeAxisItem(orientation='bottom')
        self.plantGraphWidget = pg.PlotWidget(axisItems = {'bottom':dateAxis}) 
        self.plantTab.groupBox = QGroupBox("Select parameter to plot")
        self.leftBoxLayout = QGridLayout()

        self.checkboxes = []
        i = 0
        for var in self.finalVarDescDict:
            checkbox = QtWidgets.QCheckBox(self.finalVarDescDict[var])
            self.checkboxes.append(checkbox)
            j = i//3
            if i % 3 == 0:
                self.leftBoxLayout.addWidget(checkbox,j,0)
            elif i % 3 == 1:
                self.leftBoxLayout.addWidget(checkbox,j,1)
            else:
                self.leftBoxLayout.addWidget(checkbox,j,2)
            i+=1
        j+=1


        self.plotButtom = QPushButton("Plot")

        self.leftBoxLayout.addWidget(self.plotButtom,j,0,1,3)
        self.leftBoxLayout.addWidget(self.plantGraphWidget,0,3,j-1,3)
        self.plantTab.groupBox.setLayout(self.leftBoxLayout)
        self.plotButtom.clicked.connect(self.on_click_plotPlantTab)
 
        self.plantTab.mainlayout = QHBoxLayout()
        self.plantTab.mainlayout.addWidget(self.plantTab.groupBox)
        self.plantTab.setLayout(self.plantTab.mainlayout)
     
        ########## Soil Carbon Nitrogen tab ##########
        # Creates dictionaries based on crop type
        self.finalSoilCNVarDescDict, self.finalSoilCNVarDescUnitDict, self.finalSoilCNVarFuncDict = genDictOutput(self.cropArr,"soilCN",1)

        dateAxis = TimeAxisItem(orientation='bottom')
        self.soilCNWidget = pg.PlotWidget(axisItems = {'bottom':dateAxis}) 
        self.soilCNTab.groupBox = QGroupBox("Select parameter to plot")
        self.leftBoxLayout = QGridLayout()

        self.soilCheckboxes = []
        i = 0
        for var in self.finalSoilCNVarDescDict:
            checkbox = QtWidgets.QCheckBox(self.finalSoilCNVarDescDict[var])
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
     
        ########## Soil Water Heat Nitrogen components ##########
        # Creates dictionaries based on crop type
        self.varSoilwhn2DDescDict, self.varSoilwhn2DDescUnitDict, self.varSoilwhn2DFuncDict = genDictOutput(self.cropArr,"soilwhn2D",1)

        self.soilwhnTab.fig = plt.figure()
        self.soilwhnTab.canvas = FigureCanvas(self.soilwhnTab.fig)
        self.soilwhnTab.groupBox = QGroupBox()

        date_df = pd.DataFrame([])
        # Create and populate date combo
        # Loop through each run model to give detail information about each run
        for runNum in range(len(self.simIDArr)):
            self.g03Tablename = "g03_" + self.cropArr[runNum]
            t3 = extract_cropOutputData(self.g03Tablename,self.simIDArr[runNum])
            tableID = self.g03Tablename + "_id"
            t3.drop(columns={tableID}, inplace=True)
            date_df = date_df.append(t3,ignore_index=True) 
        new_df = date_df['Date_Time'].str.split(' ', n=1, expand=True)
        date_df['Date'] = new_df[0]
        dateList = date_df['Date'].unique()

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
        self.plotButtomSoil.clicked.connect(self.on_click_plotSoil2DTab)

        self.soilwhnTab.mainlayout = QVBoxLayout()
        self.soilwhnTab.mainlayout.addWidget(self.soilwhnTab.groupBox)
        self.soilwhnTab.mainlayout.addWidget(self.soilwhnTab.canvas)
        self.soilwhnTab.setLayout(self.soilwhnTab.mainlayout)
     
        ########## Soil Time Series Tab ##########
        # Creates dictionaries based on crop type
        self.varSoilTSDescDict, self.varSoilTSDescUnitDict, self.varSoilTSFuncDict = genDictOutput(self.cropArr,"soilTS",0)

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
     
        data_df = pd.DataFrame([])
        thNewLastDay = 0
        NO3NLastDay = 0
        # Loop through each run model to append to the dataframe
        for runNum in range(len(self.simIDArr)):
            self.g03Tablename = "g03_" + self.cropArr[runNum]
            #print("runNum=",self.simIDArr[runNum])
            t3 = pd.DataFrame([])
            t3 = extract_cropOutputData(self.g03Tablename,self.simIDArr[runNum])
            # Read geometry table for this simulation
            geo_df = readGeometrySimID(self.simIDArr[runNum])
            # Merge geo_df dataframe to t3 dataframe
            t3 = t3.merge(geo_df, how='inner', on=['X','Y'])
            tableID = self.g03Tablename + "_id"
            t3.drop(columns=[tableID,"Layer"], inplace=True)
            t3['thNew'] = t3['thNew'] + thNewLastDay
            t3['NO3N'] = t3['NO3N'] + NO3NLastDay
            t3['thNewArea'] = t3['thNew'] * t3['Area']
            t3['thNewNO3NArea'] = t3['thNew'] * t3['NO3N'] * t3['Area']
            t3['totWat'] = t3['thNewArea']/(self.eomultArr[runNum]*self.rowSPArr[runNum])*10
            t3['NConc'] = t3['thNewNO3NArea']*(14/64)/10/(self.eomultArr[runNum]*self.rowSPArr[runNum])
            # Get the values for the last day of simultion
            thNewMax = t3['thNew'].iloc[-1]
            NO3NMax = t3['NO3N'].iloc[-1]
            
            data_df = data_df.append(t3,ignore_index=True) 

        t3 = data_df
        new_df = t3['Date_Time'].str.split(' ', n=1, expand=True)
        # Get only date
        t3['Date'] = new_df[0]
        t3['Date'] = pd.to_datetime(t3['Date'])
        t3['Y'] = pd.to_numeric(t3['Y'],errors='coerce')
        for key in self.varSoilTSFuncDict:
            t3[key] = pd.to_numeric(t3[key],errors='coerce')
        t3 = t3.fillna(0)

        # Since 2dsoil assigns Y values from the max depth ->0 where the surface is the maximum Depth 
        # and the bottom of the profile is 0, we have to reverse this for the layer file. Thus we 
        # subtract the max depth from all the Y's'
        maxY = max(t3['Y'])
        t3['Y'] = maxY-t3['Y']

        # Need to get layers from soil_long table
        connCrop, cCrop = openDB(dbDir + '\\crop.db')
        querySL = "select Bottom_depth as Y from soil_long where o_sid = (select id from soil where soilname = '" + self.soilname + "')"
        tSL = pd.read_sql_query(querySL,connCrop)
        tSL = tSL.reset_index()
        tSL['Y'] = pd.to_numeric(tSL['Y'],errors='coerce')

        # Assign layer
        t3Grouped = pd.DataFrame()
        prevY = 0
        for index, rowSL in tSL.iterrows():
            t3Temp = pd.DataFrame()
            mask = (t3['Y']>=prevY) & (t3['Y']<=rowSL['Y'])
            t3Temp = t3.loc[mask]
            t3Temp['layer'] = rowSL['Y']
            prevY = rowSL['Y'] + 0.0001
            t3Grouped = t3Grouped.append(t3Temp)

        # First, we need to group the data by day
        t3GrpDay = t3Grouped.groupby(['Date','X','Y'],as_index=False).mean()
        t3 = t3Grouped.drop(columns=["Date_Time","X","Y","Q","NH4N","GasCon","hNew","Area"])

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
        totWatProf = t3.groupby('Date',as_index=False)['totWat'].sum()
        # Get values for x-axis, these values will be used in all graphics on this tab.
        totWatProf['Date'] = pd.to_datetime(totWatProf['Date'])
        tmstampArray = np.array([row['Date'].timestamp() for index, row in totWatProf.iterrows()])
        totWatProfMaxY = max(totWatProf['totWat'])
        self.totWaterProfilePlot.plot(x=tmstampArray,y=np.array(totWatProf['totWat']), pen=pen)
        # Set x-axis and y-axis
        self.totWaterProfilePlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,totWatProfMaxY*1.05),padding=0)
        self.totWaterProfilePlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=totWatProfMaxY*1.05)

        # NNO3 concentration profile
        NConcProf = t3.groupby('Date',as_index=False)['NConc'].sum()
        NNO3ConcProfMaxY = max(NConcProf['NConc'])
        self.NNO3ConcProfilePlot.plot(x=tmstampArray,y=np.array(NConcProf['NConc']), pen=pen)
        # Set NNO3 concentration profile x-axis and y-axis
        self.NNO3ConcProfilePlot.setRange(xRange=(min(tmstampArray),max(tmstampArray)),yRange=(0,NNO3ConcProfMaxY*1.05),padding=0)
        self.NNO3ConcProfilePlot.setLimits(xMin=min(tmstampArray),xMax=max(tmstampArray),yMin=0,yMax=NNO3ConcProfMaxY*1.05)

        # Group by layer
        layers = t3.layer.unique()
        i = 0
        totWatLayMaxY = 0
        watContLayMaxY = 0
        NNO3ConcLayMaxY = 0
        tempMaxY = 0

        for layer in layers:
            temp = t3.loc[t3['layer']==layer]
            color = LINECOLORS[i]
            if i == 6:
                i = -1
            pen = pg.mkPen(color, width=3)

            # total water by layer
            totWatLay = temp.groupby(['Date','layer'],as_index=False)['totWat'].sum()
            if max(totWatLay['totWat']) > totWatLayMaxY:
                totWatLayMaxY = max(totWatLay['totWat'])
            self.totWaterLayerPlot.plot(x=tmstampArray,y=np.array(totWatLay['totWat']), name="Layer "+str(layer)+" cm", pen=pen)

            # water content by layer
            watContLay = temp.groupby(['Date','layer'],as_index=False)['thNew'].mean()
            if max(watContLay['thNew']) > watContLayMaxY:
                watContLayMaxY = max(watContLay['thNew'])
            self.waterContentLayerPlot.plot(x=tmstampArray,y=np.array(watContLay['thNew']), name="Layer "+str(layer)+" cm", pen=pen)

            # NNO3 concentration by layer
            NConcLay = temp.groupby(['Date','layer'],as_index=False)['NConc'].sum()
            if max(NConcLay['NConc']) > NNO3ConcLayMaxY:
                NNO3ConcLayMaxY = max(NConcLay['NConc'])
            self.NNO3ConcLayerPlot.plot(x=tmstampArray,y=np.array(NConcLay['NConc']), name="Layer "+str(layer)+" cm", pen=pen)

            # temperature by layer
            tempLay = temp.groupby(['Date','layer'],as_index=False)['Temp'].mean()
            if max(tempLay['Temp']) > tempMaxY:
                tempMaxY = max(tempLay['Temp'])
            self.tempPlot.plot(x=tmstampArray,y=np.array(tempLay['Temp']), name="Layer "+str(layer)+" cm", pen=pen)

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
        # Creates dictionaries based on crop type
        self.varRootDescDict, self.varRootDescUnitDict, self.varRootFuncDict = genDictOutput(self.cropArr,"root",1)

        self.rootTab.fig = plt.figure()
        self.rootTab.canvas = FigureCanvas(self.rootTab.fig)
        self.rootTab.groupBox = QGroupBox()

        data_df = pd.DataFrame([])
        for runNum in range(len(self.simIDArr)):
            t4 = pd.DataFrame([])
            if self.cropArr[runNum] != "fallow":
                self.g04Tablename = "g04_" + self.cropArr[runNum]
                t4 = extract_cropOutputData(self.g04Tablename,self.simIDArr[runNum])
                tableID = self.g04Tablename + "_id"
                t4.drop(columns=[tableID], inplace=True)
                data_df = data_df.append(t4,ignore_index=True) 
        new_df = data_df['Date_Time'].str.split(' ', n=1, expand=True)
        data_df['Date'] = new_df[0]
        dateRootList = data_df['Date'].unique()
 
        self.comboDateRoot = QComboBox() 
        for date in dateRootList:         
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
        self.varSurfChaDescDict, self.varSurfChaDescUnitDict, self.varSurfChaFuncDict = genDictOutput(self.cropArr,"surfCha",1)

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

        if self.rotationID != None:            
            self.display1.addTab(scrollbar,"Simulation Summary")
            self.display1.addTab(self.plantTab,"Plant")
            self.display1.addTab(self.soilCNTab,"Soil Carbon Nitrogen")            
            self.display1.addTab(self.soilwhnTab,"2D Soil Water Heat Nitrogen")            
            self.display1.addTab(self.soilTSTab,"Soil Time Series")            
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