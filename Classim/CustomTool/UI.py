import re
import os

from PyQt5 import QtSql, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

def messageUser(errMessage):
    '''
  Function that sends an error message to the user.
  Input:
    errMessage = message that explains error message to user
  Output:
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(errMessage)
    msg.setWindowTitle("Error")
    msg.exec_()
    return True


def messageUserInfo(errMessage):
    '''
  Function that sends an informative message to the user, like number of records ingested in the database.
  Input:
    errMessage = message that explains error message to user
  Output:
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(errMessage)
    msg.setWindowTitle("Important")
    msg.exec_()
    return False


def messageUserDelete(errMessage):
    '''
  Function that asks confirmation if user wants to delete a particular record.
  Input:
    errMessage = message that asks if user wants to delete a particular recor.
  Output:
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText(errMessage)
    msg.setWindowTitle("Delete")
    msg.setStandardButtons(QMessageBox.Yes)
    msg.addButton(QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    if(msg.exec_() == QMessageBox.Yes):
        return True
    else:
        return False


def messageUserIngest(errMessage):
    '''
  Function that asks confirmation if user wants to proceed with data ingestion into the database.
  Input:
    errMessage = message that asks if user wants to proceed with data ingestion into the database.
  Output:
    '''
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText(errMessage)
    msg.setWindowTitle("Continue")
    msg.setStandardButtons(QMessageBox.Yes)
    msg.addButton(QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    if(msg.exec_() == QMessageBox.Yes):
        return True
    else:
        return False
