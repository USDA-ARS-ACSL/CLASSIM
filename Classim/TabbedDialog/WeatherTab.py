import sqlite3
import re
import os
import pandas as pd
import dateparser as dp
import ssl
import time
from dateutil import parser
from PyQt5 import QtSql, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QVBoxLayout, QPushButton, QSizePolicy, QRadioButton, QButtonGroup, \
                            QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSlot
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
from functools import partial
from datetime import datetime, timedelta

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
dbDir = os.path.join(gparent_dir,'crop_int')
if not os.path.exists(dbDir):
    os.makedirs(dbDir)

global db
db = dbDir+'\\crop.db'

ssl._create_default_https_context = ssl._create_unverified_context

'''
Contains 3 classes.
1). Class GrowingTextEdit. Trying to make textbox height adjust with the content. Can be modified/replaced down the road. Lower 
    priority.
2). Class ItemWordWrap is to assist the text wrap features. You will find this class at the top of all the tab classes. In 
    future,we can centralize it. Lower priority.
3). Class Weather_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget. 
    It handles all the features of Weather Tab on the interface. It has signal slot mechanism. It does interact with the 
    DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets

    Tab screen is divided into 2 main panels. Left panel does the heavy lifting and interacts with user. Right panel is mainly 
    for frequently asked questions (FAQ) stored in sqlite table "Faq".
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
        text = index.model().data(index)
        document = QtGui.QTextDocument()
        document.setHtml(text) 
        width = index.model().data(index, QtCore.Qt.UserRole+1)
        if not width:
            width = 20
        document.setTextWidth(width) 
        return QtCore.QSize(document.idealWidth() + 10,  document.size().height())


class Weather_Widget(QWidget):
    def __init__(self):
        super(Weather_Widget,self).__init__()
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
        self.importfaq("weather")              
        self.faqtree.header().resizeSection(1,200)       
        self.faqtree.setItemDelegate(ItemWordWrap(self.faqtree))
        self.faqtree.setVisible(False)

        self.tab_summary = QTextEdit()        
        self.tab_summary.setPlainText("Here we control conversion factors, average values, on/off switches, statistical generation of weather inputs depending upon data availabilty from measurements.") 
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
        stationtypelists = read_weather_metaDB()
        self.stationtypelistlabel = QLabel("Station Type:")
        self.stationtypecombo = QComboBox()        
        self.stationtypelistlabel.setBuddy(self.stationtypecombo)
        self.stationtypecombo.addItem("Select from list")
        self.stationtypecombo.addItem("Add New Station Type")
        for id in sorted(stationtypelists, key = lambda i: (stationtypelists[i])):            
            self.stationtypecombo.addItem(stationtypelists[id])
        self.stationtypecombo.currentIndexChanged.connect(self.showweatherdetailscombo)
        self.stationtypecombo.update()

        self.sitelabel = QLabel("Site")
        self.sitecombo = QComboBox()        
        self.sitecombo.addItem("Select from list")

        self.weathersummarylabel = QLabel("")
        self.avgwindlabel = QLabel("Average Wind (Km/h)")
        self.avgwindedit = QLineEdit("")
        self.avgrainratelabel = QLabel("Average Rain Rate (cm)")
        self.avgrainrateedit = QLineEdit("")
        self.avgco2label = QLabel("Average CO2 (ppm)")
        self.avgco2edit = QLineEdit("")
        self.chemclabel = QLabel("N content in Rainfall (Kg/ha)")
        self.chemcedit = QLineEdit("")
        #Upload weather file button
        self.uploadwflabel = QLabel("Upload Weather File (.csv format)")
        self.buttonUpload = QPushButton("Upload File")
        self.buttonUpload.clicked.connect(self.upload_csv)
        self.downloadwflabel = QLabel("Download Weather Data (last 5 years)")
        self.buttonDownload = QPushButton("Download Data")
        self.buttonDownload.clicked.connect(self.downloadWeatherData)
        self.stationtypelabel = QLabel("Station Type")
        self.stationtypeedit = QLineEdit("")
        self.weatherbutton = QPushButton("Save")
        self.weatherdeletebutton = QPushButton("Delete")

        self.mainlayout.addLayout(self.vHeader,0,0,1,4)
        self.mainlayout.addWidget(self.faqtree,0,4,2,1)       
        self.mainlayout.addWidget(self.stationtypelistlabel,1,0)
        self.mainlayout.addWidget(self.stationtypecombo,1,1)
        self.mainlayout.addWidget(self.sitelabel,2,0)
        self.mainlayout.addWidget(self.sitecombo,2,1)
        self.mainlayout.addWidget(self.avgwindlabel,3,0)
        self.mainlayout.addWidget(self.avgwindedit,3,1)
        self.mainlayout.addWidget(self.avgrainratelabel,4,0)
        self.mainlayout.addWidget(self.avgrainrateedit,4,1)
        self.mainlayout.addWidget(self.avgco2label,5,0)
        self.mainlayout.addWidget(self.avgco2edit,5,1)
        self.mainlayout.addWidget(self.chemclabel,6,0)
        self.mainlayout.addWidget(self.chemcedit,6,1)
        self.mainlayout.addWidget(self.uploadwflabel,7,0)
        self.mainlayout.addWidget(self.buttonUpload,7,1)
        self.mainlayout.addWidget(self.downloadwflabel,8,0)
        self.mainlayout.addWidget(self.buttonDownload,8,1)
        self.mainlayout.addWidget(self.weathersummarylabel,9,0,1,4)
        self.mainlayout.addWidget(self.stationtypelabel,10,0)
        self.mainlayout.addWidget(self.stationtypeedit,10,1)
        self.mainlayout.addWidget(self.weatherbutton,10,2)
        self.mainlayout.addWidget(self.weatherdeletebutton,10,3)
        self.sitelabel.setVisible(False)
        self.sitecombo.setVisible(False)
        self.avgwindlabel.setVisible(False)
        self.avgwindedit.setVisible(False)
        self.avgrainratelabel.setVisible(False)
        self.avgrainrateedit.setVisible(False)
        self.avgco2label.setVisible(False)
        self.avgco2edit.setVisible(False)
        self.chemclabel.setVisible(False)
        self.chemcedit.setVisible(False)
        self.uploadwflabel.setVisible(False)
        self.buttonUpload.setVisible(False)
        self.downloadwflabel.setVisible(False)
        self.buttonDownload.setVisible(False)
        self.weathersummarylabel.setVisible(False)
        self.stationtypelabel.setVisible(False)
        self.stationtypeedit.setVisible(False)
        self.weatherbutton.setVisible(False)
        self.weatherdeletebutton.setVisible(False)
        self.setLayout(self.mainlayout) 


    def checkWeatherBySite(self,siteIndex):
        siteName = str(self.sitecombo.currentText())
        if siteName == "":
            return False
        # Get site lat lon
        weathertuple = extract_sitedetails(siteName)
        lat = weathertuple[1]
        lon = weathertuple[2]
        if(Weather_Widget.checkUS(lat,lon)):
            self.downloadwflabel.setVisible(True)
            self.buttonDownload.setVisible(True)
        else:
            self.downloadwflabel.setVisible(False)
            self.buttonDownload.setVisible(False)


    def showweatherdetailscombo(self,value):
        self.sitelabel.setVisible(False)
        self.sitecombo.setVisible(False)
        self.avgwindlabel.setVisible(False)
        self.avgwindedit.setVisible(False)
        self.avgrainratelabel.setVisible(False)
        self.avgrainrateedit.setVisible(False)
        self.avgco2label.setVisible(False)
        self.avgco2edit.setVisible(False)
        self.chemclabel.setVisible(False)
        self.chemcedit.setVisible(False)
        self.uploadwflabel.setVisible(False)
        self.buttonUpload.setVisible(False)
        self.downloadwflabel.setVisible(False)
        self.buttonDownload.setVisible(False)
        self.weathersummarylabel.setVisible(False)
        self.stationtypelabel.setVisible(False)
        self.stationtypeedit.setVisible(False)
        self.weatherbutton.setVisible(False)
        self.weatherdeletebutton.setVisible(False)
        value=self.stationtypecombo.currentIndex()        

        if self.stationtypecombo.itemText(value) == "Select from list":
            return True

        self.sitelists = read_sitedetailsDB()
        self.sitecombo.clear()
        self.sitecombo.addItem("")
        for item in sorted(self.sitelists):            
            self.sitecombo.addItem(item)

        self.sitelabel.setVisible(True)
        self.sitecombo.setVisible(True)
        self.avgwindlabel.setVisible(True)
        self.avgwindedit.setVisible(True)
        self.avgrainratelabel.setVisible(True)
        self.avgrainrateedit.setVisible(True)
        self.avgco2label.setVisible(True)
        self.avgco2edit.setVisible(True)
        self.chemclabel.setVisible(True)
        self.chemcedit.setVisible(True)
        self.uploadwflabel.setVisible(True)
        self.buttonUpload.setVisible(True)
        self.weatherbutton.setVisible(True)

        stationtype = str(self.stationtypecombo.currentText())
        if stationtype ==  "Add New Station Type":
            self.sitecombo.currentIndexChanged.connect(self.checkWeatherBySite,self.sitecombo.currentIndex())
            self.weathersummarylabel.setText("")
            self.avgwindedit.setText("")
            self.avgrainrateedit.setText("")
            self.avgco2edit.setText("")
            self.chemcedit.setText("")
            self.stationtypeedit.setText("")
            self.stationtypelabel.setVisible(True)
            self.stationtypeedit.setVisible(True)
            self.weatherbutton.setText("SaveAs")
            self.sitecombo.setEnabled(True)
        else:
            weathertuple = read_weatherlongDB(stationtype)  
            self.stationtypelabel.setVisible(False)
            self.stationtypeedit.setVisible(False)
            self.sitecombo.setEnabled(False)
            self.weatherbutton.setText("Update")
            if Weather_Widget.checkWeather(stationtype):
                self.downloadwflabel.setVisible(True)
                self.buttonDownload.setVisible(True)

            self.avgwindedit.setText(str(weathertuple[7]))
            self.avgrainrateedit.setText(str(weathertuple[8]))
            self.chemcedit.setText(str(weathertuple[9]))
            self.avgco2edit.setText(str(weathertuple[10]))
            self.sitecombo.setCurrentIndex(self.sitecombo.findText(str(weathertuple[12])))
        
            self.weatherSummary = Weather_Widget.getWeatherSummary(stationtype)
            self.weathersummarylabel.setText(self.weatherSummary)
            self.weathersummarylabel.setVisible(True)
            site = str(self.sitecombo.currentText())
            self.weatherdeletebutton.setVisible(True)
            self.weatherdeletebutton.clicked.connect(self.on_weatherdeletebuttonclick)
        self.weatherbutton.clicked.connect(lambda:self.on_weatherbuttonclick(stationtype))


    def getWeatherSummary(stationtype):
        # getting weather data from sqlite
        conn = sqlite3.connect(db)  

        date = []
        sdate = []
        edate = []
        weather_query = "select weather_id, date, hour, srad, tmax, tmin, temperature, rain, wind, rh, co2 from weather_data where weather_id = ?" 
        df_weatherdata = pd.read_sql(weather_query,conn,params=[stationtype]) 
        weatherSummary = stationtype + " Data Availability Report"
        if len(df_weatherdata.index) == 0:
            weatherSummary += "<br>No data available.<br>"
        else:
            # Convert date column to Date type
            df_weatherdata['date'] = pd.to_datetime(df_weatherdata.date)
            df_weatherdata = df_weatherdata.sort_values(by='date')
            date = df_weatherdata.date.tolist()
            sdate.append(date[0])
            for i in range(1, len(date)):
                if((date[i] != date[i-1]) and (date[i] != date[i-1] + timedelta(days=1))):
                    edate.append(date[i-1])
                    sdate.append(date[i])
            edate.append(date[len(date)-1])

            for sdt, edt in zip(sdate, edate):
                df_weatherSeg = df_weatherdata.loc[(df_weatherdata.date >= sdt) & (df_weatherdata.date <= edt)]
                startDate = sdt.strftime("%m/%d/%Y")
                endDate = edt.strftime("%m/%d/%Y")
                weatherSummary += "<br><i>Start Date:</i> " + startDate + "        <i>End Date:</i>" + endDate + "<br>"

                if df_weatherSeg['hour'].isna().sum() > 0:
                    weatherSummary += "Daily data. " + str(df_weatherSeg['date'].count()) + " records read.<br>"
                    if df_weatherSeg['tmax'].isna().sum() > 0:
                        weatherSummary += str(df_weatherSeg['tmax'].isna().sum()) + " records missing for maximum temperature.<br>"

                    if df_weatherSeg['tmin'].isna().sum() > 0:
                        weatherSummary += str(df_weatherSeg['tmin'].isna().sum()) + " records missing for minimum temperature.<br>"
                else:
                    weatherSummary += "Hourly data. " + str(df_weatherSeg['date'].count()) + " records read.<br>"
                    if df_weatherSeg['temperature'].isnull().sum() > 0:
                        weatherSummary += str(df_weatherSeg['temperature'].isnull().sum()) + " records missing for temperature.<br>"

                if df_weatherSeg['srad'].isna().sum() > 0:
                    weatherSummary += str(df_weatherSeg['srad'].isna().sum()) + " records missing for solar radiation.<br>"

                if df_weatherSeg['rain'].isna().sum() > 0:
                    weatherSummary += str(df_weatherSeg['rain'].isna().sum()) + " records missing for rain.<br>"

                if df_weatherSeg['wind'].isna().sum() > 0:
                    weatherSummary += str(df_weatherSeg['wind'].isna().sum()) + " records missing for wind speed..<br>"

                if df_weatherSeg['rh'].isna().sum() > 0:
                    weatherSummary += str(df_weatherSeg['rh'].isna().sum()) + " records missing for relative humidity.<br>"

                if df_weatherSeg['co2'].isna().sum() > 0:
                    weatherSummary += str(df_weatherSeg['co2'].isna().sum()) + " records missing for CO2.<br>"

        return weatherSummary


    def upload_csv(self):
        sttype = str(self.stationtypecombo.currentText())
        if self.weatherbutton.text() == "SaveAs":
            stationType = self.stationtypeedit.text()
            if (self.stationtypeedit.text() == ""):
                messageUser("Station type is empty. Please, type a station type name.")
                return False
        else:
            stationType = str(self.stationtypecombo.itemText(self.stationtypecombo.currentIndex()))
        dialog = QFileDialog()
        fname = dialog.getOpenFileName(None, "Import CSV", "", "CSV data files (*.csv)")
        data = pd.read_csv(fname[0])
        # lowercase all column names
        data.columns = map(str.lower, data.columns)
        # get column names
        colNames = list(data.columns.values)
        # check for minimum data requirement
        colNames = set(colNames)
        message = ""
        # test first for date, solar radiation and rain
        reqCol = ['date', 'srad', 'rain']
        for col in reqCol:
            if not col in colNames:
                 message = message + "\nColumn " + col + " is missing."

        if 'hour' not in colNames:
            if 'tmax' not in colNames:
                message = message + "Maximum temperature (tmax) is missing. "
            if 'tmin' not in colNames:
                message = message + "Minimum temperature (tmin) is missing. "
        else:
            if 'temperature' not in colNames:
                message = message + "Column temperature is missing. "

        if message != '':
            messageUser(message)
            return False
        else:
            out = "Would you like to proceed with the ingestion of the following data?\n\n"
            for i, j in data.iterrows():
                if(i <= 9):
                    if i == 0:
                        for col in colNames:
                            out = out + str(col) + ","
                        out = out[:-1] + "\n"
                    for col in colNames:
                        out = out + str(j[col]) + ","
                    out = out[:-1] + "\n"
            ingest_flag = messageUserIngest(out)
            if ingest_flag:
                site = str(self.sitecombo.currentText())

                data['date'] = data['date'].map(lambda date: dp.parse(str(date)))
                if not 'hour' in data:
                    data['hour'] = pd.to_datetime(data['date']).dt.strftime('%H')
                data['jday'] = pd.to_datetime(data['jday']).dt.strftime('%j')
                data['date'] = pd.to_datetime(data['date']).dt.strftime('%d%b%Y').str.upper()

                conn = sqlite3.connect(dbDir + '\\crop.db') 
                c = conn.cursor()
                if not c:
                    print("database not open")
                    return False

                # Check if data already exists in the database for stationType for this date range
                dateList = data['date']
                minDate = min(dateList)
                maxDate = max(dateList)

                query = "select * from weather_data where site='" + site + "' and weather_id='" + stationType + \
                        "' and date>='" + minDate + "' and date<='" + maxDate + "'"
                c1 = c.execute(query) 
                c1_row = c1.fetchone()
                if not c1_row == None:  # means data already exist
                    message = "There is already data for this site and weather type for this date range.  Would you like to replace this data?"
                    ingest_flag2 = messageUserIngest(message)
                    if not ingest_flag2:
                        return False
                    else:
                        queryDel = "DELETE FROM weather_data where site='" + site + "' and weather_id='" + stationType + \
                        "' and date>='" + minDate + "' and date<='" + maxDate + "'"
                        c.execute(queryDel)
                        conn.commit()

                # list of database fields on weather_data table
                dbColumns = ['weather_id','jday', 'date', 'hour', 'srad', 'wind', 'rh', 'rain', 'tmax', 'tmin', 'temperature', 'co2']

                for col in data.columns: 
                    if col not in dbColumns:
                        data.drop(col, axis=1, inplace=True)

                data['site'] = site
                data['weather_id'] = stationType
 
                # Time to create the columns that are missing
                for col in dbColumns:
                    if col not in data.columns:
                        data[col] = ''

                data = data[['site', 'weather_id','jday', 'date', 'hour', 'srad', 'wind', 'rh', 'rain', 'tmax', 'tmin', 'temperature', 'co2']]
                numRec = data.shape[0]
                recMessage = "Number of rows ingested into database: "+ str(numRec)

                data.to_sql('weather_data',conn,if_exists="append",index=False)
                conn.close() 
                self.weathersummarylabel.setVisible(True)
                self.weatherSummary = Weather_Widget.getWeatherSummary(stationType)
                self.weathersummarylabel.setText(self.weatherSummary)
                messageUserInfo(recMessage)


    def downloadWeatherData(self):
        sttype = str(self.stationtypecombo.currentText())
        if self.weatherbutton.text().find("SaveAs") > -1:
            sttype = self.stationtypeedit.text()
            if (sttype == ""):
                messageUser("Station type is empty. Please, type a station type name.")
                return False
        msgBox = QMessageBox()
        msgBox.setText("Downloading data, please wait.  New message will show how many records were recorded in the database.")
        msgBox.setWindowTitle("Downloading ....")
        msgBox.setWindowModality(QtCore.Qt.NonModal)
        msgBox.setStandardButtons(QMessageBox.Close)
        msgBox.exec()
        site = str(self.sitecombo.currentText())
        # Get site lat lon
        weathertuple = extract_sitedetails(site)     
        lat = str(weathertuple[1])
        lon = str(weathertuple[2])  
        url = "https://weather.aesl.ces.uga.edu/hourly?lat="+lat+"&lon="+lon+"&attributes=air_temperature,relative_humidity,wind_speed,shortwave_radiation,precipitation&output=csv"
        data = pd.read_csv(url)
        data['jday'] = data['date']
        data['hour'] = data['date']
        data['date'] = pd.to_datetime(data['date']).dt.strftime('%d%b%Y').str.upper()
        data['jday'] = pd.to_datetime(data['jday']).dt.strftime('%j')
        data['hour'] = pd.to_datetime(data['hour']).dt.strftime('%H')
        data.rename(columns={"air_temperature":"temperature","relative_humidity":"rh","wind_speed":"wind","shortwave_radiation":"srad","precipitation":"rain"}, inplace=True)
        # Convert solar radiation
        data['srad'] = data['srad'] * 3600 / 1000000
        msgBox.close()
        conn = sqlite3.connect(dbDir + '\\crop.db') 
        c = conn.cursor()
        if not c:
            print("database not open")
            return False

        # Check if data already exists in the database for stationType for this date range
        dateList = data['date']
        minDate = min(dateList)
        maxDate = max(dateList)
        query = "select * from weather_data where site='" + site + "' and weather_id='" + sttype + "' and date>='" + minDate + "' and date<='" + maxDate + "'"
        c1 = c.execute(query) 
        c1_row = c1.fetchone()
        if not c1_row == None:  # means data already exist
            message = "There is already data for this site and weather type for this date range.  Would you like to replace this data?"
            ingest_flag2 = messageUserIngest(message)
            if not ingest_flag2:
                return False
            else:
                queryDel = "DELETE FROM weather_data where site='" + site + "' and weather_id='" + sttype + "' and date>='" + minDate + "' and date<='" + maxDate + "'"
                c.execute(queryDel)
                conn.commit()

        # list of database fields on weather_data table
        dbColumns = ['weather_id','jday', 'date', 'hour', 'srad', 'wind', 'rh', 'rain', 'tmax', 'tmin', 'temperature', 'co2']
        data['site'] = site
        data['weather_id'] = sttype
 
        # Time to create the columns that are missing
        for col in dbColumns:
            if col not in data.columns:
                data[col] = ''

        data = data[['site', 'weather_id','jday', 'date', 'hour', 'srad', 'wind', 'rh', 'rain', 'tmax', 'tmin', 'temperature', 'co2']]
        numRec = data.shape[0]
        recMessage = "Number of rows ingested into database: "+ str(numRec)
        data.to_sql('weather_data',conn,if_exists="append",index=False, chunksize=200)
        conn.close() 
        self.weathersummarylabel.setVisible(True)
        self.weatherSummary = Weather_Widget.getWeatherSummary(sttype)
        self.weathersummarylabel.setText(self.weatherSummary)
        messageUserInfo(recMessage)


    @pyqtSlot()
    def on_weatherbuttonclick(self,item1):
        '''
         save the changes to weather table
        '''
        sttype = str(self.stationtypecombo.currentText())
        if self.weatherbutton.text() == "SaveAs":
            sttype = self.stationtypeedit.text()
            if (sttype == ""):
                messageUser("Station type is empty. Please, type a station type name.=",sttype)
                return False
            matchedindex = self.stationtypecombo.findText(sttype) 
            if (matchedindex > 0):
                messageUser("Station type exist. Please use a different name")
                return False

        bsolar = 1000000
        btemp = 1
        atemp = 0
        bwind = 1
        bir = 1
        avgrain = Weather_Widget.FloatOrZero(self.avgrainrateedit.text())
        if(avgrain < 0.5 or avgrain > 4):
            messageUserInfo("Average rain rates ranges from 0.5 to 4 cm/day.")
        
        record_tuple = (bsolar,btemp,atemp,bwind,bir,Weather_Widget.FloatOrZero(self.avgwindedit.text()),avgrain,Weather_Widget.FloatOrZero(self.chemcedit.text()),\
                        Weather_Widget.FloatOrZero(self.avgco2edit.text()),str(self.sitecombo.currentText()),sttype)
        c1 = insert_update_weather(record_tuple,self.weatherbutton.text())
        if c1:
            self.stationtypecombo.clear()        
            stationtypelists = read_weather_metaDB() 
            self.stationtypecombo.addItem("Select from list")
            self.stationtypecombo.addItem("Add New Station Type")
            for id in sorted(stationtypelists, key = lambda i: (stationtypelists[i])):            
                self.stationtypecombo.addItem(stationtypelists[id])
            self.sitelabel.setVisible(False)
            self.sitecombo.setVisible(False)
            self.avgwindlabel.setVisible(False)
            self.avgwindedit.setVisible(False)
            self.avgrainratelabel.setVisible(False)
            self.avgrainrateedit.setVisible(False)
            self.avgco2label.setVisible(False)
            self.avgco2edit.setVisible(False)
            self.chemclabel.setVisible(False)
            self.chemcedit.setVisible(False)
            self.uploadwflabel.setVisible(False)
            self.buttonUpload.setVisible(False)
            self.downloadwflabel.setVisible(False)
            self.buttonDownload.setVisible(False)
            self.weathersummarylabel.setVisible(False)
            self.stationtypelabel.setVisible(False)
            self.stationtypeedit.setVisible(False)
            self.weatherbutton.setVisible(False)
            self.weatherdeletebutton.setVisible(False)
            self.weatherbutton.setText("")


    @pyqtSlot()
    def on_weatherdeletebuttonclick(self):
        '''
        Delete record on weather table
        '''       
        site = str(self.sitecombo.currentText())
        stationtype = str(self.stationtypecombo.currentText())
        if site == "":
            return False
        delete_flag = messageUserDelete("Are you sure you want to delete this record?")
        if delete_flag:
            c1 = delete_weather(site,stationtype)
            if c1:
                self.stationtypecombo.clear()        
                stationtypelists = read_weather_metaDB() 
                self.stationtypecombo.addItem("Select from list")
                self.stationtypecombo.addItem("Add New Station Type")
                for id in sorted(stationtypelists, key = lambda i: (stationtypelists[i])):            
                    self.stationtypecombo.addItem(stationtypelists[id])
                self.sitelabel.setVisible(False)
                self.sitecombo.setVisible(False)
                self.avgwindlabel.setVisible(False)
                self.avgwindedit.setVisible(False)
                self.avgrainratelabel.setVisible(False)
                self.avgrainrateedit.setVisible(False)
                self.avgco2label.setVisible(False)
                self.avgco2edit.setVisible(False)
                self.chemclabel.setVisible(False)
                self.chemcedit.setVisible(False)
                self.uploadwflabel.setVisible(False)
                self.buttonUpload.setVisible(False)
                self.downloadwflabel.setVisible(False)
                self.buttonDownload.setVisible(False)
                self.weathersummarylabel.setVisible(False)
                self.stationtypelabel.setVisible(False)
                self.stationtypeedit.setVisible(False)
                self.weatherbutton.setVisible(False)
                self.weatherdeletebutton.setVisible(False)
            return True
        else:
            return False


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
     

    def FloatOrZero(value):
        try:
            return float(value)
        except:
            return 0.0


    def checkUS(lat,lon):
        # US continental bounding box
        top = 49.3457868 # north lat
        left = -124.7844079 # west long
        right = -66.9513812 # east long
        bottom =  24.7433195 # south lat
        if bottom <= lat <= top and left <= lon <= right:
            return True

        # Alaska bounding box
        left = -179.148909
        bottom = 51.214183	
        right = 179.77847	
        top = 71.365162
        if bottom <= lat <= top and (-180 <= lon <= left or right <= lon <= 180):
            return True

        # Hawaii bounding box
        left = -178.334698	
        bottom = 18.910361
        right = -154.806773
        top = 28.402123
        if bottom <= lat <= top and left <= lon <= right:
            return True
        else:
            return False


    def checkWeather(stationName):
        if stationName == "":
            return False
        # Get site lat lon
        weathertuple = read_weatherlongDB(stationName)             
        lat = weathertuple[0]
        lon = weathertuple[1]
        return Weather_Widget.checkUS(lat,lon)
