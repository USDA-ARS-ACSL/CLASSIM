import sys
import os
from TabbedDialog.Tabs import Tabs_Widget
from DatabaseSys.Databasesupport import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication

'''
Starting point for the application. It calls tabs.py (to calls all the other tabs of Welcome, Site, Soil, Cultivar, Weather, 
Management, Run, Output).
DPI scaling is handled here. Important.
Note the comment for remote debugging. Important.
'''

# for DPI scaling
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
 
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

os.environ["QT_SCALE_FACTOR"] ="1.25"

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

style = '''
QWidget {
    background-color: #e8f5e9;
} 

QLabel, QTextEdit {
    color: black;
}  

QPushButton {
    background-color: #97b498;
}

QPushButton:hover {
    color: gray;
}

QPushButton:pressed {
    background-color: #97b498;
}    

QTableWidget {
    Background: #c8e6c9;
    Border:none;
}

QHeaderView::section {
    background-color: #97b498;
}

QTreeView::branch:has-siblings:!adjoins-item {
    border-image: url(./images/vline.png) 0;
}

QTreeView::branch:has-siblings:adjoins-item {
    border-image: url(./images/branch-more.png) 0;
}

QTreeView::branch:!has-children:!has-siblings:adjoins-item {
    border-image: url(./images/branch-end.png) 0;
}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
    border-image: none;
    image: url(./images/branch-closed.png);
}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings  {
    border-image: none;
    image: url(./images/branch-open.png);
}

QDateEdit QAbstractItemView:enabled {
    selection-background-color: #97b498; 
 }

QCalendarWidget QTableView QLabel {
    color: #97b498;
}

QCalendarWidget navigationBar {
    background-color: #97b498; 
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    color: #97b498; 
}

QCalendarWidget QMenu,
QCalendarWidget QSpinBox {
    background-color: white;
    color: black;
}
'''

if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi, True)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(style)
    mQFont = app.font()

    if mQFont.pixelSize() >0 :
        mQFont.setPixelSize(11)
    else:
        mQFont.setPointSize(11)

    mQFont.setPointSizeF(7)
    mQFont.setPixelSize(7)
    app.setFont(mQFont)
    
    import sys
    sys.excepthook = except_hook

    conn, c = openDB(dbDir + '\\crop.db')
    if c:
        ManagementTab = Tabs_Widget()
        sys.exit(app.exec_())