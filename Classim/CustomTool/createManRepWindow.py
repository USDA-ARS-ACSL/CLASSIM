import os
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QVBoxLayout, QHeaderView, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import Qt
from DatabaseSys.Databasesupport import *
from pprint import pprint

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
dbDir = os.path.join(gparent_dir,'classim')

class createManRepWindow(QWidget):
    """
    This window is a QWidget.
    """
    def __init__(self):
        conn, c = openDB(dbDir + '\\crop.db')
        if c:
            super().__init__()
            self.setGeometry(0,0,520,400)
            layout = QVBoxLayout()
            self.title = QLabel("Management Report")
            # Defining search box
            self.query = QLineEdit()
            self.query.setPlaceholderText("Search...")
            self.query.textChanged.connect(self.search)
            # Defining table
            self.table = QTableWidget(self)
            self.header = QHeaderView(QtCore.Qt.Horizontal)
            self.header.setSectionsClickable(True)
            self.table.setHorizontalHeader(self.header)
            self.table.setSortingEnabled(True)
            self.table.setColumnCount(5)
            horHeaders = ["Crop","Experiment","Treatment","Operation","Date"]
            self.table.setHorizontalHeaderLabels(horHeaders)
            self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
            self.table.verticalHeader().hide()

            # Query the database
            query = "select crop, e.name as experiment, t.name as treatment, \
                     (case when f.nutrient != '' then o.name || ' - ' || f.nutrient || ': ' || f.nutrientQuantity || ' kg/ha' else o.name end) as operation, \
                     o.odate as opDate from treatment as t, operations as o, experiment as e \
                     left join fertNutOp as f on o.opID=f.opID where t.Tid=o.o_t_exid and \
                     t.t_exid=e.exid order by crop, experiment, treatment, opDate"
            df = pd.read_sql_query(query,conn)

            for index, row in df.iterrows():
                if row['opDate'] == "":
                    row['opDate'] = "None"
                self.table.insertRow(index)
                self.table.setItem(index,0,QTableWidgetItem(row['crop']))
                self.table.setItem(index,1,QTableWidgetItem(row['experiment']))
                self.table.setItem(index,2,QTableWidgetItem(row['treatment']))
                self.table.setItem(index,3,QTableWidgetItem(row['operation']))
                self.table.setItem(index,4,QTableWidgetItem(row['opDate']))

            layout.addWidget(self.title)
            layout.addWidget(self.query)
            layout.addWidget(self.table)
            self.setLayout(layout)


    def search(self, s):
        # Clear current selection.
        self.table.setCurrentItem(None)

        if not s:
            # Empty string, don't search.
            return

        matching_items = self.table.findItems(s, Qt.MatchContains)
        if matching_items:
            # We have found something.
            for item in matching_items:
                item.setSelected(True)
