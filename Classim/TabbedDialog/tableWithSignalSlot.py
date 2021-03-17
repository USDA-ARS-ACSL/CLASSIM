import sqlite3
import re
from PyQt5 import QtSql,QtCore
from PyQt5.QtWidgets import QWidget, QTableWidget, QComboBox, QFormLayout, QPushButton, QTableWidgetItem, QLineEdit, QCalendarWidget, QLabel, QMessageBox, QDateEdit
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDate
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from TabbedDialog.ManagementTab import *
import time

class Tabless_Widget(QTableWidget):
    """
     subclass of QTableWidget. 
     Purpose to have signal-slot connection with Tree custom class
    """
    sig2 = pyqtSignal(int)
    sig2t = pyqtSignal(int,str,str,str,str)
    def __init__(self):
        super(Tabless_Widget,self).__init__()
        self.init_ui()


    def init_ui(self):
        self.sitetable1 = QTableWidget()
        self.status = QLabel()
        self.sitetable1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.summary = QTextEdit()
        self.summary.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.summary.setReadOnly(True)   
        self.summary.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.summary.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)         
        self.summary.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # horizontal, vertical        
        self.summary.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.sitetable1.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.sitetable1.setShowGrid(False)
        self.sitetable1.setStyleSheet('QTableView::item {background-color: white;}')


    def show_table_rows(self):
        for jj in range(self.sitetable1.rowCount()):
            self.sitetable1.showRow(jj)
        

    def make_connection_2_tree(self,tree_object):
        print("Make connection")
        tree_object.getExperiment.connect(self.get_tree)
        tree_object.getTreatment.connect(self.get_treatment)
        tree_object.getNewOperation.connect(self.get_operation)
        tree_object.getOperation.connect(self.get_existingoperation)
        tree_object.informUser.connect(self.informuser)
        #return cstatus


    @pyqtSlot(int,str,str)
    def get_tree(self,intval,str_experimentname,str_cropname):
        #print("debug: tablewithsignalslot:get_tree: val,cropname=",intval, str_cropname)
        if intval==1:   
            ### works only for avoiding silent crash on multiple clicks on ADD NEW Experiment          
            if self.sitetable1.isVisible()==False:
                self.showNewExperimentDialog('New',str_cropname)
            self.sitetable1.setVisible(True)
        elif intval==0:                
            self.sitetable1.clear()
            self.sitetable1.reset()
            self.sitetable1.clearContents()
            self.sitetable1.setRowCount(0)       
            self.sitetable1.setVisible(False)             
        elif intval==5:    
            self.showDeleteExperimentDialog('Delete',str_experimentname,str_cropname)
            self.sitetable1.setVisible(True)     
             

    @pyqtSlot(int,str,str,str)
    def get_treatment(self,intval,str_experimentname,str_cropname,str_treatmentname):
        print("get_treatment works. val=",intval)
        if intval==2:
            self.showNewTreatmentDialog('New',str_experimentname,str_cropname)  #  experimentname,cropname
            self.sitetable1.setVisible(True)                          
        elif intval==0:             
            self.sitetable1.setVisible(False) 
        elif intval==6:   
            if self.sitetable1.isHidden() == False:
                self.sitetable1.clear()
                self.sitetable1.reset()
                self.sitetable1.hide()  
            #  experimentname,cropname        
            self.showDeleteTreatmentDialog('Delete',str_experimentname,str_cropname,str_treatmentname)  
            self.sitetable1.setVisible(True)                          


    @pyqtSlot(int,str)
    def informuser(self,intval,tree_str):
        print("informuser val & tree_str=",intval,tree_str)
        if intval==0:
            self.showUserInformationDialog('New Treatment Node addded',tree_str)  #  experimentname,cropname
        elif intval==1:             
            self.sitetable1.setVisible(False) 
              

    @pyqtSlot(int,str,str,str)
    def get_operation(self,intval,strval1,strval2,strval3):
        print("get_operation works. val=",intval)
        if intval==3:
            self.showNewOperationDialog('New',strval1,strval2,strval3) # treatmentname, experimentname,cropname
            self.sitetable1.setVisible(True)                          
        elif intval==0:             
            self.sitetable1.setVisible(False)  
             

    @pyqtSlot(int,str,str,str,str,QModelIndex)
    def get_existingoperation(self,intval,strval1,strval2,strval3,strval4,index):
        #print("Debug: tableWithSignalSlot.get_existingoperation() val=",intval)
        if intval==4:
            # treatmentname, experimentname,cropname,operationname
            self.showExistingOperationDialog('New',strval1,strval2,strval3,strval4) 
            self.sitetable1.setVisible(True)                          
        elif intval==0:             
            self.sitetable1.setVisible(False)                        


    def showUserInformationDialog(self,value,tree_str):
        """
        QTable object. This will inform the USER what to do after adding "Add new Experiment/Treatment/Operation"
        """       
        self.savebutton1 = QPushButton("Ok")
        tmp_str2 = tree_str + "Treatment node added in the left panel. All operations are added. Please \
check their operations dates and correct them if needed."              
        self.summary.setText(tmp_str2)  
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally     
        self.sitetable1.clear()
        self.sitetable1.reset()        
        self.sitetable1.setRowCount(6)
        self.sitetable1.setColumnCount(2)        
        self.show_table_rows()       

        header = self.sitetable1.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)

        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setSpan(0,0,3,2)
        self.sitetable1.setCellWidget(0,0,self.summary)    
        self.sitetable1.setCellWidget(4,1,self.savebutton1)     
        self.sitetable1.setVisible(True) 
        self.sitetable1.resizeColumnsToContents()
        self.sitetable1.resizeRowsToContents()
        self.savebutton1.clicked.connect(self.on_okbutton_informuser_clicked)      
        
             
    def showNewExperimentDialog(self,value,str_cropname):
        """
         QTable object. Ask user to enter the name of new experiment.
         Need to verify the USEr input is SAFE for database. After verification, insert this entry to 
         table: Experiment
        """
        self.strval = str_cropname
        self.cropname =str_cropname
        self.experimentname = QLineEdit()        
        self.udialog = QLabel()
        regexp_alphanum = QtCore.QRegExp('\w+')
        validator_alphanum = QtGui.QRegExpValidator(regexp_alphanum)
        test1state = self.experimentname.setValidator(validator_alphanum)        
        self.savebutton1 = QPushButton("Save")
        
        # creating local summary1 object as C++ class and python wrapper for it were not synching well 
        # with operation of (delete/ create) 
        # important; to have preserve a reference this way and proper cleaning of cell widget inside a 
        # qtablewidget
        self.summary1 = QTextEdit("EXPERIMENT Name represents broader hierarchical dataset name, for \
example `Summer 2018`. Underneath it, one can define specific TREATMENT. Provide a unique experiment \
name, click SAVE. Once it is registered in left panel, you add new treatment(s)")        
        self.summary1.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.summary1.setReadOnly(True)   
        self.summary1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.summary1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)         
        self.summary1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # horizontal, vertical        
        self.summary1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.sitetable1.clear()
        self.sitetable1.reset()
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally             
        self.sitetable1.setRowCount(6)
        self.sitetable1.setColumnCount(2)        
        self.show_table_rows()       

        header = self.sitetable1.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)

        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setSpan(0,0,3,2)
        self.sitetable1.setCellWidget(0,0,self.summary1)
        self.sitetable1.setItem(3,0,QTableWidgetItem("Enter New Experiment Name"))
        self.sitetable1.setCellWidget(3,1,self.experimentname)
        self.sitetable1.setCellWidget(4,1,self.savebutton1)       
        self.sitetable1.setCellWidget(5,0,self.udialog)
        self.sitetable1.setVisible(True) 
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        ##self.savebutton1.disconnect()        
        self.savebutton1.clicked.connect(self.on_savebutton_experiment_clicked)

############## delete experiment
    def showDeleteExperimentDialog(self,value,str_experimentname,str_cropname):
        """
         Delete the experiment
         QTable object. 
        """
        self.cropname = str_cropname
        self.experimentname = QLineEdit(str_experimentname)
        self.experimentname.setReadOnly(True)
        self.udialog = QLabel() 
        self.yesbutton = QPushButton("Yes")
        self.nobutton = QPushButton("No")
        self.sitetable1.clear()
        self.sitetable1.reset()
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally   
        self.sitetable1.setRowCount(3)
        self.sitetable1.setColumnCount(2)
        self.show_table_rows()            
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setItem(0,0,QTableWidgetItem("Do you want to delete the experiment:"))
        self.sitetable1.setCellWidget(0,1,self.experimentname)
        self.sitetable1.setCellWidget(1,0,self.yesbutton)       
        self.sitetable1.setCellWidget(1,1,self.nobutton)       
        self.sitetable1.setCellWidget(2,0,self.udialog)
        self.sitetable1.setVisible(True) 
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();        
        self.yesbutton.clicked.connect(self.on_yesbutton_experiment_clicked)
        self.nobutton.clicked.connect(self.on_nobutton_experiment_clicked)


    def on_okbutton_informuser_clicked(self):         
        if self.sitetable1.isHidden() == False:
            self.sitetable1.clear()
            self.sitetable1.reset()
        #return true

    def on_savebutton_experiment_clicked(self,value):         
        if len(self.experimentname.text()) ==0:
            self.udialog.setText("Empty string. Please, provide valid EXPERIMENT name. Hint: Alphanumeric ")
        else:
            self.udialog.setText("")
            #call database insert command
            status = check_and_update_experimentDB(self.experimentname.text(),self.cropname)
            if status:
                self.udialog.setText(self.experimentname.text()+ " added in left panel and Add New Treatment to it.")
                if self.sitetable1.isHidden() == False:
                    self.sitetable1.hide()
                # goes to update3, insert data inot datatree instead of re-loading the datatree (causing crash, due 
                # to improper handling)
                self.sig2t.emit(4,self.experimentname.text(),self.cropname,"blank_treament","blank_operation")
            else:
                self.udialog.setText("Experiment name exist. Use different name !!")

    def on_yesbutton_experiment_clicked(self,value):         
        self.udialog.setText("")
        #call database delete command
        status = check_and_delete_experimentDB(self.experimentname.text(),self.cropname)
        print("status=",status)
        if status:
            print("status=",status)
            self.udialog.setText("Success "+self.experimentname.text())            
            self.sitetable1.clear()
            self.sitetable1.hide()
            # this way no need to re-load the data after deletion. Delete from database and delete from tree
            self.sig2.emit(3)


    def on_nobutton_experiment_clicked(self,value):         
        self.udialog.setText("ok, no action taken")
        self.sig2t.emit(2,self.experimentname.text(),self.strval )
                 
    def on_yesbutton_treatment_clicked(self,value):         
        self.udialog.setText("")
        #call database delete command
        status = 1
        status = check_and_delete_treatmentDB(self.treatmentname.text(),self.ename,self.cname)
        if status:
           self.udialog.setText("Success "+self.treatmentname.text())   
           self.sitetable1.clear()
           self.sitetable1.reset()
           self.sitetable1.clearContents()
           self.sitetable1.setRowCount(0) # necessary. It will clean the table internally   
           self.sitetable1.hide()         
           self.sig2.emit(6)


    def on_nobutton_treatment_clicked(self,value):                  
        self.sitetable1.clear()
        self.sitetable1.reset()
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally   
        self.sitetable1.hide()


    def on_savebutton_treatment_clicked(self,value):         
        if len(self.treatmentname.text()) ==0:
            self.udialog.setText("Empty string. Please, provide valid TREATMENT name. Hint: Alphanumeric ")
        else:
            self.udialog.setText("")
            #call database insert command
            status = check_and_update_treatmentDB(self.treatmentname.text(),self.strval1,self.strval2)
            if status:
                #self.udialog.setText("Success")                 
                if self.sitetable1.isHidden() == False:
                    self.sitetable1.hide()             
                # faultline check self.informuser(0,'hello')
                # will send it update(), deletes the current tree and re-load the datatree from database
                self.sig2.emit(66)                
            else:
                self.udialog.setText("Treatment name exist. Use different name !!")
                 
                 
    def showNewTreatmentDialog(self,value,strval1,strval2):
        """
         QTable object. Ask user to enter the name of new experiment.
         Need to verify the USEr input is SAFE for database. After verification, insert this entry to 
         table: Experiment
        """
        self.strval1 = strval1
        self.strval2 = strval2
        self.treatmentname = QLineEdit()
        self.udialog = QLabel()
        regexp_alphanum = QtCore.QRegExp('\w+')
        validator_alphanum = QtGui.QRegExpValidator(regexp_alphanum)
        test1state = self.treatmentname.setValidator(validator_alphanum)
        self.savebutton1 = QPushButton("Save")
        self.sitetable1.clear()
        self.sitetable1.reset()
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally     
        
        self.sitetable1.setRowCount(3)
        self.sitetable1.setColumnCount(2)        
        self.show_table_rows()             

        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setItem(0,0,QTableWidgetItem("Enter New Treatment"))
        self.sitetable1.setCellWidget(0,1,self.treatmentname)
        self.sitetable1.setCellWidget(1,1,self.savebutton1)
        self.sitetable1.setCellWidget(2,0,self.udialog)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.savebutton1.clicked.connect(self.on_savebutton_treatment_clicked)


    def getTreatmentSummary(ename,cname,tname):
        conn = sqlite3.connect(dbDir + '\\crop.db')
        c = conn.cursor()   
        if not c:
            print("database not open")
            return False

        #Get treatment id
        search_tuple = (tname,ename,cname)
        c1=c.execute("SELECT tid FROM treatment where name = ? and t_exid = (select exid from experiment where name =? and crop = ?)",search_tuple)
        tid = c1.fetchone()
        operationSummary = "<b>Treatment Summary</b><br>"
        if tid != None:
            # Get all operations associated with this treatment
            op = c.execute("SELECT name, odate, quantity, pop, yseed, eomult, rowSpacing, cultivar, fDepth, autoirrigation, \
                            DATE(year||'-'||month||'-'||day) as dt_frmtd FROM (SELECT *, CASE WHEN LENGTH(substr(odate, 1, \
                            instr(odate,'/')-1)) = 2 THEN substr(odate, 1, instr(odate,'/')-1) ELSE '0'|| substr(odate, 1, instr(odate,'/')-1) \
                            END as month, CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),\
                            '/')-1)) = 2 THEN substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1) ELSE \
                            '0'|| substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1) END AS day, CASE \
                            WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, instr(odate,'/')+1),'/')+1)) = 4 THEN \
                            substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, instr(odate,'/')+1),'/')+1) END AS year FROM operations) \
                            where o_t_exid=? order by dt_frmtd",tid)
            op_rows = op.fetchall()
            for op_row in op_rows:
                if(op_row[0] == "Initial Field Values"):
                    loc = "Middle"
                    if(op_row[5]  == 0.5):
                        loc = "Left"
                    if(op_row[9] == 1):
                        irrigFlag = "Yes"
                    else:
                        irrigFlag = "No"
                    operationSummary += "Cultivar: " + op_row[7] + "<br>Plant Density (number of plants/m2): " + str(op_row[3]) + "<br>" + \
                                        "Seed Depth (cm): " + str(op_row[4]) + "<br>Row Spacing (cm): " + str(op_row[6]) + "<br>" + \
                                        "Auto Irrigation : " + irrigFlag + "<br>Location of Planting Grid: " + loc + "<br>"
                else:
                    operationSummary += op_row[0] + " Date: " + op_row[1] + "<br>"

                if(op_row[0] == "Fertilizer-N"):
                    operationSummary += "Quantity (kg/ha): " + str(op_row[2]) + "<br>Fertilizer Depth (cm): " + str(op_row[8]) + "<br>"

        conn.close()
        return operationSummary
   
##### delete treatment #str_experimentname,str_cropname,str_treatmentname
    def showDeleteTreatmentDialog(self,value,strval1,strval2,strval3):
        """
         Deletes the treatment. Recursive to operation
        """
        self.ename = strval1
        self.cname = strval2
        self.tname = strval3
        self.treatmentname = QLineEdit(self.tname)
        self.treatmentname.setReadOnly(True)
        self.udialog = QLabel()
        self.yesbutton = QPushButton("Yes")
        self.nobutton = QPushButton("No")
        self.treatmentSummary = Tabless_Widget.getTreatmentSummary(self.ename,self.cname,self.tname)
        self.udialog.setText(self.treatmentSummary)      

        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0)
        self.sitetable1.clear()
        self.sitetable1.reset()        
        self.sitetable1.setRowCount(3)
        self.sitetable1.setColumnCount(2)           
        self.show_table_rows()             
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setItem(0,0,QTableWidgetItem("Do you want to delete the treatment"))
        self.sitetable1.setCellWidget(0,1,self.treatmentname)
        self.sitetable1.setCellWidget(1,0,self.yesbutton)
        self.sitetable1.setCellWidget(1,1,self.nobutton)
        self.sitetable1.setCellWidget(2,0,self.udialog)
        self.sitetable1.setVisible(True) 
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.yesbutton.clicked.connect(self.on_yesbutton_treatment_clicked)
        self.nobutton.clicked.connect(self.on_nobutton_treatment_clicked)


    def showNewOperationDialog(self,value,strval1,strval2,strval3):
        """
         QTable object. Asks user to SELECT operation from the given set of operation.
         Need to verify the USEr input is SAFE for database. After verification, insert this 
         entry to table: Operation
        """
        self.udialog = QLabel()
        self.treatmentname = strval1
        self.experimentname = strval2
        self.cropname = strval3
        self.calendar = QDateEdit()
        
        lastoperation_date = getme_date_of_last_operationDB(self.treatmentname, self.experimentname ,self.cropname)
        # first find out if this the new operation or there is a operation defined for this treatment. 
        # So we use the calendar date logic
        if len(lastoperation_date) > 0:
            lastoperation_date_parts = lastoperation_date[0].split("/") # 10/20/2006
            self.calendar.setMinimumDate(QDate(int(lastoperation_date_parts[2]),int(lastoperation_date_parts[0]),int(lastoperation_date_parts[1])))
            print("debug:tabless_widget: last operation date=",lastoperation_date," ",lastoperation_date_parts[2]," ",lastoperation_date_parts[1])
        else:
            self.calendar.setMinimumDate(QDate(1900,1,1))

        self.calendar.setMaximumDate(QDate(2200,1,1))
        self.calendar.setDisplayFormat("MM/dd/yyyy")
        self.calendar.setCalendarPopup(True)
        self.savebutton1 = QPushButton("Save")
        self.combo1 = QComboBox()
        self.combocropvariety = QComboBox()
        self.comboeomult = QComboBox()
        self.yseedlabel = QLabel("Seed Depth (cm)")
        self.quantitylabel = QLabel("Quantity (kg/ha)")
        self.fDepthlabel = QLabel("Fertilizer Depth (cm)")
        self.seedMasslabel = QLabel("Seedpiece Mass (g)")
        self.datelabel = QLabel("Date")
        self.cropvarietylabel = QLabel("Cultivars")
        self.poplabel = QLabel("Plant Density (number of plants/m2)")
        self.rowspacinglabel = QLabel("Row Spacing (cm)")
        self.autoirrigationlabel = QLabel("Auto Irrigation")
        self.eomultlabel = QLabel("Location of Planting Grid")

        self.blanklabeledit = QLineEdit("")
        self.quantitylabeledit = QLineEdit("")
        self.poplabeledit = QLineEdit("6.5")
        self.yseedlabeledit = QLineEdit("5")
        self.rowspacinglabeledit = QLineEdit("75")
        self.autoirrigationlabeledit = QLineEdit("0")
        self.fDepthlabeledit = QLineEdit("")
        self.seedMasslabeledit = QLineEdit("0")
        # Create and populate autoIrrigation combo
        self.comboAutoIrrig = QComboBox()          
        self.comboAutoIrrig.addItem("Yes") # val = 1
        self.comboAutoIrrig.addItem("No") # val = 0


        #checking USER input for NUMERIC values
        regexp_num = QtCore.QRegExp('^\d*[.]?\d*$')
        validator_num = QtGui.QRegExpValidator(regexp_num)
        test1state = self.quantitylabeledit.setValidator(validator_num)
        test1state = self.poplabeledit.setValidator(validator_num)
        test1state = self.yseedlabeledit.setValidator(validator_num)
        test1state = self.rowspacinglabeledit.setValidator(validator_num)
        test1state = self.fDepthlabeledit.setValidator(validator_num)
        test1state = self.seedMasslabeledit.setValidator(validator_num)
        
        #The operation will only show if quantity_flag=1 on defaultoperations table.
        self.readlist = read_defaultOperationsDB()        
        self.combo1.clear()
        self.combo1.addItem("Select Operation")
        for record in sorted(self.readlist):
            if record[3] == 1:
                self.combo1.addItem(record[1])                    
            
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally     
        self.sitetable1.clear()
        self.sitetable1.reset()

        self.sitetable1.setRowCount(16)
        self.sitetable1.setColumnCount(3)       
        self.show_table_rows()        
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setCellWidget(0,1,self.combo1)

        self.sitetable1.setCellWidget(1,0,self.datelabel)        
        self.sitetable1.setCellWidget(2,0,self.quantitylabel)
        self.sitetable1.setCellWidget(3,0,self.cropvarietylabel)
        # Plant density
        self.sitetable1.setCellWidget(4,0,self.poplabel)
        # Seed depth
        self.sitetable1.setCellWidget(5,0,self.yseedlabel)
        self.sitetable1.setCellWidget(6,0,self.rowspacinglabel)
        self.sitetable1.setCellWidget(7,0,self.eomultlabel)
        self.sitetable1.setCellWidget(8,0,self.fDepthlabel)
        self.sitetable1.setCellWidget(9,0,self.seedMasslabel)
        self.sitetable1.setCellWidget(10,0,self.autoirrigationlabel)

        self.sitetable1.setCellWidget(1,1,self.calendar)
        self.sitetable1.setCellWidget(2,1,self.quantitylabeledit)
        self.sitetable1.setCellWidget(3,1,self.combocropvariety)
        self.sitetable1.setCellWidget(4,1,self.poplabeledit)
        self.sitetable1.setCellWidget(5,1,self.yseedlabeledit)
        self.sitetable1.setCellWidget(6,1,self.rowspacinglabeledit)
        self.sitetable1.setCellWidget(7,1,self.comboeomult)
        self.sitetable1.setCellWidget(8,1,self.fDepthlabeledit)
        self.sitetable1.setCellWidget(9,1,self.seedMasslabeledit)
        self.sitetable1.setCellWidget(10,1,self.comboAutoIrrig)
        self.sitetable1.setCellWidget(11,1,self.savebutton1)
        
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)

        self.sitetable1.hideRow(1)
        self.sitetable1.hideRow(2)
        self.sitetable1.hideRow(3)
        self.sitetable1.hideRow(4)
        self.sitetable1.hideRow(5)
        self.sitetable1.hideRow(6)
        self.sitetable1.hideRow(7)
        self.sitetable1.hideRow(8)
        self.sitetable1.hideRow(9)
        self.sitetable1.hideRow(10)
        self.sitetable1.hideRow(11)
        self.sitetable1.hideRow(12)
        self.combo1.currentIndexChanged.connect(self.oncomboactivated)


    def showExistingOperationDialog(self,value,strval1,strval2,strval3,strval4):
        """
         str_treatmentname,str_experimentname,str_cropname,str_operationname
         QTable object. 
         Will show the existing operation. Will allow  to modify its values.
         Create the field table. Query the OPERATION table and get the flag values
        """
        self.udialog = QLabel()
        self.treatmentname = strval1
        self.experimentname = strval2
        self.cropname = strval3
        # strval4 contains operation_id and operation_name concatenated with '_' character
        self.operationname = strval4.split('_')[1]
        self.op_id = strval4.split('_')[0]
        #print("treat = ", self.treatmentname, " expir = ", self.experimentname, " crop nm = ", self.cropname, " op name = ", self.operationname, " op_id = ",self.op_id) 
        self.record = list(read_operation_valuesDB2(self.op_id))
        #print("debug: record=",self.record)
        self.calendar = QDateEdit()
        self.calendar.setMinimumDate(QDate(1900,1,1))
        self.calendar.setMaximumDate(QDate(2200,1,1))
        self.calendar.setDisplayFormat("MM/dd/yyyy")
        self.calendar.setCalendarPopup(True)
        fformat = QtGui.QTextCharFormat()
        fformat.setForeground(QtGui.QColor(151, 180, 152))
        
        self.savebutton1 = QPushButton("Update")
        self.deletebutton = QPushButton("Delete")
        
        self.combo1 = QComboBox()
        self.combocropvariety = QComboBox()
        self.comboeomult = QComboBox()
        self.comboAutoIrrig = QComboBox()          
        self.yseedlabel = QLabel("Seed Depth (cm)")
        self.quantitylabel = QLabel("Quantity (kg/ha)")
        self.datelabel = QLabel("Date")
        self.cropvarietylabel = QLabel("Cultivars")
        self.poplabel = QLabel("Plant Density (number of plants/m2)")
        self.rowspacinglabel = QLabel("Row Spacing (cm)")
        self.fDepthlabel = QLabel("Fertilizer Depth (cm)")
        self.seedMasslabel = QLabel("Seedpiece Mass (g)")
        self.autoirrigationlabel = QLabel("Auto Irrigation")
        self.eomultlabel = QLabel("Location of Planting Grid")

        self.blanklabeledit = QLineEdit("")
        self.quantitylabeledit = QLineEdit("")
        self.poplabeledit = QLineEdit("")
        self.yseedlabeledit = QLineEdit("")
        self.rowspacinglabeledit = QLineEdit("")
        self.fDepthlabeledit = QLineEdit("")
        self.seedMasslabeledit = QLineEdit("")

        #checking USER input for NUMERIC values
        regexp_num = QtCore.QRegExp('\.d+')
        validator_num = QtGui.QRegExpValidator(regexp_num)
        test1state = self.quantitylabeledit.setValidator(validator_num)
        test1state = self.poplabeledit.setValidator(validator_num)
        test1state = self.yseedlabeledit.setValidator(validator_num)
        test1state = self.rowspacinglabeledit.setValidator(validator_num)
        test1state = self.fDepthlabeledit.setValidator(validator_num)
        test1state = self.seedMasslabeledit.setValidator(validator_num)
        
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally     
        self.sitetable1.clear()
        self.sitetable1.reset()
        
        self.sitetable1.setRowCount(16)
        self.sitetable1.setColumnCount(3)
        self.show_table_rows()           
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()

        self.sitetable1.setCellWidget(1,0,self.datelabel)
        self.sitetable1.setCellWidget(2,0,self.quantitylabel)
        self.sitetable1.setCellWidget(3,0,self.cropvarietylabel)
        self.sitetable1.setCellWidget(4,0,self.poplabel)
        self.sitetable1.setCellWidget(5,0,self.yseedlabel)
        self.sitetable1.setCellWidget(6,0,self.rowspacinglabel)
        self.sitetable1.setCellWidget(7,0,self.eomultlabel)
        self.sitetable1.setCellWidget(8,0,self.fDepthlabel)
        self.sitetable1.setCellWidget(9,0,self.seedMasslabel)
        self.sitetable1.setCellWidget(10,0,self.autoirrigationlabel)
        if(self.operationname == "Fertilizer-N"):
            self.sitetable1.setCellWidget(11,0,self.deletebutton)

        self.sitetable1.setCellWidget(1,1,self.calendar)        
        self.sitetable1.setCellWidget(2,1,self.quantitylabeledit)
        self.sitetable1.setCellWidget(3,1,self.combocropvariety)
        self.sitetable1.setCellWidget(4,1,self.poplabeledit)
        self.sitetable1.setCellWidget(5,1,self.yseedlabeledit)
        self.sitetable1.setCellWidget(6,1,self.rowspacinglabeledit)
        self.sitetable1.setCellWidget(7,1,self.comboeomult)
        self.sitetable1.setCellWidget(8,1,self.fDepthlabeledit)
        self.sitetable1.setCellWidget(9,1,self.seedMasslabeledit)
        self.sitetable1.setCellWidget(10,1,self.comboAutoIrrig)
        self.sitetable1.setCellWidget(11,1,self.savebutton1)
        
        header = self.sitetable1.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        self.sitetable1.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.sitetable1.verticalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)

        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)

        if(self.operationname == "Initial Field Values"):        
            self.readcropvarietylist  = read_cultivar_DB(self.cropname)            
            for record2 in sorted(self.readcropvarietylist):
                self.combocropvariety.addItem(record2)
            matchedindex = self.combocropvariety.findText(str(self.record[18])) 
            if matchedindex >= 0:
                self.combocropvariety.setCurrentIndex(matchedindex)

            # Build eomult picklist
            self.comboeomult.addItem("Left") # val = 0.5
            self.comboeomult.addItem("Middle") # val = 1.0
            if(self.record[16] == 0.5):
                 matchedindex = self.comboeomult.findText("Left")
            else:
                 matchedindex = self.comboeomult.findText("Middle")
            self.comboeomult.setCurrentIndex(matchedindex)

            # Create and populate autoIrrigation combo
            self.comboAutoIrrig.addItem("Yes") # val = 1
            self.comboAutoIrrig.addItem("No") # val = 0
            if(self.record[11] == 1):
                 matchedindex = self.comboAutoIrrig.findText("Yes")
            else:
                 matchedindex = self.comboAutoIrrig.findText("No")
            self.comboAutoIrrig.setCurrentIndex(matchedindex)

            self.poplabeledit.setText(str(self.record[10]))  
            self.yseedlabeledit.setText(str(self.record[14]))  
            self.rowspacinglabeledit.setText(str(self.record[17]))  
            self.seedMasslabeledit.setText(str(self.record[20]))
                        
            self.sitetable1.hideRow(1) 
            self.sitetable1.showRow(3)                    
            self.sitetable1.showRow(4)                    
            self.sitetable1.showRow(5)                    
            self.sitetable1.showRow(6)                    
            self.sitetable1.showRow(7)   
            self.sitetable1.showRow(10)   
            if(re.search("potato",self.cropname)):
                self.sitetable1.showRow(9)
            else:                    
                self.sitetable1.hideRow(9)
        else:
            # Calendar
            self.sitetable1.showRow(1) 
            # recover the mm,dd,yyyy and set the calendar
            record_parts = self.record[7].split("/")
            
            currentYear = record_parts[2]
            self.calendar.setDate(QDate(int(currentYear),int(record_parts[0]),int(record_parts[1])))

            self.sitetable1.hideRow(3)
            self.sitetable1.hideRow(4)
            self.sitetable1.hideRow(5)
            self.sitetable1.hideRow(6)
            self.sitetable1.hideRow(7)
            self.sitetable1.hideRow(9)
            self.sitetable1.hideRow(10)

        # Quantity
        if(self.operationname == "Fertilizer-N"):
            self.sitetable1.showRow(2)  
            self.sitetable1.showRow(8)  
            self.quantitylabeledit.setText(str(self.record[6]))
            self.fDepthlabeledit.setText(str(self.record[19]))  
        else:
            self.sitetable1.hideRow(2)                    
            self.sitetable1.hideRow(8)                    
           
        self.sitetable1.showRow(11)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        self.savebutton1.clicked.connect(self.on_savebutton_operation_clicked)
        self.deletebutton.clicked.connect(self.on_deletebutton_operation_clicked)
        
        
    def oncomboactivated(self,listindex):
        print("text=",listindex)        
        self.record = [element for element in self.readlist if element[1] == self.combo1.currentText()][0]
        op = self.record[1]

        if(op == "Initial Field Values"):        
            self.readcropvarietylist  = read_cultivar_DB(self.cropname)            
            for record2 in sorted(self.readcropvarietylist):
                self.combocropvariety.addItem(record2)
            matchedindex = self.combocropvariety.findText(str(self.record[17])) 

            # Build eomult picklist
            self.comboeomult.addItem("Left") # value 0.5
            self.comboeomult.addItem("Middle") # value 1.0

            self.sitetable1.hideRow(1)
            self.sitetable1.showRow(3)                    
            self.sitetable1.showRow(4)                    
            self.sitetable1.showRow(5)                    
            self.sitetable1.showRow(6)                    
            self.sitetable1.showRow(7)
            if(re.search("potato",self.cropname)):
                self.sitetable1.showRow(9)                    
        else:
            self.sitetable1.showRow(1)
            self.sitetable1.hideRow(3)
            self.sitetable1.hideRow(4)
            self.sitetable1.hideRow(5)
            self.sitetable1.hideRow(6)
            self.sitetable1.hideRow(7)
            self.sitetable1.hideRow(9)

        # Quantity
        if(op == "Fertilizer-N"):
            print("Debug inside fertilizer-N")
            self.sitetable1.showRow(2)  
            self.sitetable1.showRow(8)  
        else:
            self.sitetable1.hideRow(2)                    
            self.sitetable1.hideRow(8)                    
        
        self.sitetable1.showRow(11)
        self.savebutton1.clicked.connect(self.on_savebutton_operation_clicked)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        
        
    def on_savebutton_operation_clicked(self,value):
        #print("Inside save operation")
        #print("value=",value)
        #print("treatment=", self.treatmentname)
        #print("experiment=", self.experimentname)
        #print("cropment=", self.cropname)
        op_id = self.record[0]
        #print("operation_id=",op_id)

        op = self.record[1]
        #print("operation=",op)
 
        print("record save=",self.record) 
        # Quantity
        if(op == "Fertilizer-N"):
            if(self.quantitylabeledit.text() != ""):
                self.record[6] = float(self.quantitylabeledit.text())
            else:
                messageUser("Quantity should be a number.")

            if(self.fDepthlabeledit.text() != ""):
                self.record[19] = float(self.fDepthlabeledit.text())
            else:
                messageUser("Fertilizer Depth should be a number.")

        if(op == "Initial Field Values"):
            print("cultivar= ",self.combocropvariety.currentText())
            self.record[10]= float(self.poplabeledit.text())
            self.record[14]= float(self.yseedlabeledit.text())  
            self.record[17]= float(self.rowspacinglabeledit.text())  
            self.record[18]= self.combocropvariety.currentText()
            self.record[20]= float(self.seedMasslabeledit.text())
            # Validate row spacing
            if(self.record[17] < 1 or self.record[17] > 200):
                messageUser("Row spacing should be a value between 1 and 200 cm.")
                return False
            if self.cropname == "corn":
                # Validate plant density
                if(self.record[10] < 1 or self.record[10] > 20):
                    messageUser("Plant density for corn should be a value between 1 and 20 number of plants/m2.")
                    return False
                # Validate seed depth
                if(self.record[14] < 2 or self.record[14] > 7):
                    messageUser("Seed depth for corn should be a value between 2 and 7 cm.")
                    return False
            elif self.cropname == "potato":
                # Validate plant density
                if(self.record[10] < 1 or self.record[10] > 300):
                    messageUser("Plant density for potato should be a value between 1 and 25 number of plants/m2.")
                    return False
                # Validate seed depth
                if(self.record[14] < 1 or self.record[14] > 20):
                    messageUser("Seed depth for potato should be a value between 1 and 20 cm.")
                    return False
                # Validate seedpiece mass
                if(self.record[20] < 0 or self.record[20] > 50):
                    messageUser("Seedpiece mass for potato should be a value between 0 and 50 g.")
                    return False
            if(self.comboeomult.currentText() == "Left"):
                  self.record[16] = 0.5
            if(self.comboeomult.currentText() == "Middle"):
                  self.record[16] = 1.0
            if(self.comboAutoIrrig.currentText() == "Yes"):
                  self.record[11] = 1
            if(self.comboAutoIrrig.currentText() == "No"):
                  self.record[11] = 0
            new_record = self.record[1:]
        else:
            new_record = self.record[1:]         
            new_date = self.calendar.date().toString("MM/dd/yyyy")
            print("new date= ",new_date)
            new_record[6] = new_date

        print("record before save=",self.record) 
        status = check_and_update_operationDB(op_id, self.treatmentname, self.experimentname, self.cropname, new_record)

        if status:
            self.udialog.setText("Success")
            self.sitetable1.setVisible(False)
            self.sig2.emit(1)


    def on_deletebutton_operation_clicked(self,value):
        print("Inside delete operation")
        print("value=",value)
        print("treatment=", self.treatmentname)
        print("experiment=", self.experimentname)
        print("cropment=", self.cropname)
        print("operation =",self.operationname) 
        print("record=",self.record) 
        op_id = self.record[0]
        print("operation_id=",op_id)
         
        status = check_and_delete_operationDB(op_id)
        if status:
            self.udialog.setText("Success")
            self.sitetable1.setVisible(False)
            self.sig2.emit(3)