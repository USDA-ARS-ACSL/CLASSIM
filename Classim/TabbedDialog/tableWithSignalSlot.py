from doctest import set_unittest_reportflags
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
        tree_object.getExperiment.connect(self.get_tree)
        tree_object.getTreatment.connect(self.get_treatment)
        tree_object.getNewOperation.connect(self.get_operation)
        tree_object.getOperation.connect(self.get_existingoperation)
        tree_object.informUser.connect(self.informuser)


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
        #print("get_treatment works. val=",intval)
        if intval==2:
            self.showNewTreatmentDialog('New',str_experimentname,str_cropname)
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
        #print("informuser val & tree_str=",intval,tree_str)
        if intval==0:
            self.showUserInformationDialog('New Treatment Node addded',tree_str)  #  experimentname,cropname
        elif intval==1:             
            self.sitetable1.setVisible(False) 
              

    @pyqtSlot(int,str,str,str)
    def get_operation(self,intval,strval1,strval2,strval3):
        #print("get_operation works. val=",intval)
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
        tmp_str2 = tree_str + " Treatment node added in the left panel. All operations are added. Please \
check their operations dates and correct them if needed."
        print(tmp_str2)
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
        self.cropname = str_cropname
        self.experimentname = QLineEdit()        
        regexp_alphanum = QtCore.QRegExp('\w+')
        validator_alphanum = QtGui.QRegExpValidator(regexp_alphanum)
        test1state = self.experimentname.setValidator(validator_alphanum)        
        self.savebutton1 = QPushButton("Save")
        
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
        self.sitetable1.setRowCount(5)
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
        self.sitetable1.setVisible(True) 
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
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
        self.yesbutton = QPushButton("Yes")
        self.nobutton = QPushButton("No")
        self.sitetable1.clear()
        self.sitetable1.reset()
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally   
        self.sitetable1.setRowCount(2)
        self.sitetable1.setColumnCount(2)
        self.show_table_rows()            
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setItem(0,0,QTableWidgetItem("Do you want to delete the experiment?"))
        self.sitetable1.setCellWidget(0,1,self.experimentname)
        self.sitetable1.setCellWidget(1,0,self.yesbutton)       
        self.sitetable1.setCellWidget(1,1,self.nobutton)       
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
        if len(self.experimentname.text()) == 0:
            messageUser("Empty string. Please, provide valid EXPERIMENT name. Hint: Alphanumeric ")
        else:
            #call database insert command
            status = check_and_update_experimentDB(self.experimentname.text(),self.cropname)
            if status:
                messageUser(self.experimentname.text()+ " added in left panel, please add new treatment to it.")
                if self.sitetable1.isHidden() == False:
                    self.sitetable1.hide()
                # goes to update3, insert data inot datatree instead of re-loading the datatree (causing crash, due 
                # to improper handling)
                self.sig2t.emit(4,self.experimentname.text(),self.cropname,"blank_treament","blank_operation")
            else:
                messageUser("Experiment name exist. Use different name !!")


    def on_yesbutton_experiment_clicked(self,value):         
        delete_flag = messageUserDelete("Are you sure you want to delete this experiment?")
        if delete_flag:
            status = check_and_delete_experimentDB(self.experimentname.text(),self.cropname)
            if status:
                self.sitetable1.clear()
                self.sitetable1.hide()
                # this way no need to re-load the data after deletion. Delete from database and delete from tree
                self.sig2.emit(3)
                return True
            else:
                return False


    def on_nobutton_experiment_clicked(self,value):         
        self.sig2t.emit(2,self.experimentname.text(),self.strval)
   
              
    def on_deletebutton_treatment_clicked(self,value):         
        delete_flag = messageUserDelete("Are you sure you want to delete this treatment?")
        if delete_flag:
            status = check_and_delete_treatmentDB(self.tname,self.ename,self.cname)
            if status:
                self.sitetable1.clear()
                self.sitetable1.reset()
                self.sitetable1.clearContents()
                self.sitetable1.setRowCount(0) 
                self.sitetable1.hide()         
                self.sig2.emit(6)
                return True
            else:
                return False


    def on_copytobutton_treatment_clicked(self,value):                  
        if len(self.newtreatmentname.text()) == 0:
            messageUser("Please, provide valid treatment name.")
            #call database insert command
            status = copy_treatmentDB(self.tname,self.ename,self.cname,self.newtreatmentname.text())
            if status:
                if self.sitetable1.isHidden() == False:
                    self.sitetable1.hide()             
                # faultline check self.informuser(0,'hello')
                # will send it update(), deletes the current tree and re-load the datatree from database
                self.sig2.emit(66)                
            else:
                messageUser("Treatment name exist. Please, use different name!")


    def on_savebutton_treatment_clicked(self,value):         
        if len(self.treatmentname.text()) == 0:
            messageUser("Empty string. Please, provide valid TREATMENT name. Hint: Alphanumeric ")
            #call database insert command
            status = check_and_update_treatmentDB(self.treatmentname.text(),self.strval1,self.strval2)
            if status:
                if self.sitetable1.isHidden() == False:
                    self.sitetable1.hide()             
                # faultline check self.informuser(0,'hello')
                # will send it update(), deletes the current tree and re-load the datatree from database
                self.sig2.emit(66)                
            else:
                messageUser("Treatment name exist. Please, use different name!")
                 
                 
    def showNewTreatmentDialog(self,value,strval1,strval2):
        """
         QTable object. Ask user to enter the name of new experiment.
         Need to verify the USEr input is SAFE for database. After verification, insert this entry to 
         table: Experiment
        """
        self.strval1 = strval1
        self.strval2 = strval2
        self.treatmentname = QLineEdit()
        regexp_alphanum = QtCore.QRegExp('\w+')
        validator_alphanum = QtGui.QRegExpValidator(regexp_alphanum)
        test1state = self.treatmentname.setValidator(validator_alphanum)
        self.savebutton1 = QPushButton("Save")
        self.sitetable1.clear()
        self.sitetable1.reset()
        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally     
        
        self.sitetable1.setRowCount(2)
        self.sitetable1.setColumnCount(2)        
        self.show_table_rows()             

        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setItem(0,0,QTableWidgetItem("Enter New Treatment"))
        self.sitetable1.setCellWidget(0,1,self.treatmentname)
        self.sitetable1.setCellWidget(1,1,self.savebutton1)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.savebutton1.clicked.connect(self.on_savebutton_treatment_clicked)


    def getTreatmentSummary(ename,cname,tname):
        conn, c = openDB(dbDir + '\\crop.db')
        if c:
            #Get treatment id
            search_tuple = (tname,ename,cname)
            c1=c.execute("SELECT tid FROM treatment where name = ? and t_exid = (select exid from experiment where name =? and crop = ?)",search_tuple)
            tid = c1.fetchone()
            operationSummary = "<b>Treatment Summary</b><br>"
            if tid != None:
                #print("tid=",tid)
                # Get all operations associated with this treatment
                op = c.execute("SELECT name, odate, opID, DATE(year||'-'||month||'-'||day) as dt_frmtd FROM (SELECT *, CASE WHEN LENGTH(substr(odate, 1, \
                                instr(odate,'/')-1)) = 2 THEN substr(odate, 1, instr(odate,'/')-1) ELSE '0'|| substr(odate, 1, instr(odate,'/')-1) \
                                END as month, CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),\
                                '/')-1)) = 2 THEN substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1) ELSE \
                                '0'|| substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1) END AS day, CASE \
                                WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, instr(odate,'/')+1),'/')+1)) = 4 THEN \
                                substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, instr(odate,'/')+1),'/')+1) END AS year FROM operations) \
                                where o_t_exid=? order by dt_frmtd",tid)
                op_rows = op.fetchall()
                #print(op_rows)
                for op_row in op_rows:
                    if(op_row[0] == "Simulation Start"):
                        if cname == "fallow":
                            operationSummary += str(op_row[0]) + " Date: " + str(op_row[1]) + "<br>"
                        else:
                            initCond = readOpDetails(op_row[2],op_row[0])
                            loc = "Middle"
                            if(initCond[0][8]  == 0.5):
                                loc = "Left"
                            if(initCond[0][4] == 1):
                                irrigFlag = "Yes"
                            else:
                                irrigFlag = "No"
                            operationSummary += str(op_row[0]) + " Date: " + str(op_row[1]) + "<br>"
                            operationSummary += "Cultivar: " + initCond[0][10] + "<br>Plant Density (number of plants/m2): " + \
                                                str(initCond[0][3]) + "<br>Seed Depth (cm): " + str(initCond[0][6]) + \
                                                "<br>Row Spacing (cm): " + str(initCond[0][9]) + "<br>Auto Irrigation : " + \
                                                irrigFlag + "<br>Location of Planting Grid: " + loc + "<br>"
                    elif(op_row[0] == "Tillage"):
                        tillage = readOpDetails(op_row[2],op_row[0])
                        operationSummary += "Tillage Type: " + str(tillage[0][3])
                        if op_row[1] != "" and tillage[0][3] != "No tillage":
                             operationSummary += " Date: " + str(op_row[1])
                        operationSummary += "<br>"
                    elif(op_row[0] == "Fertilizer"):
                        fert = readOpDetails(op_row[2],op_row[0])
                        operationSummary += str(fert[0][3]) + " Date: " + str(op_row[1]) + " Fertilizer Depth (cm): " + str(fert[0][4]) + "<br>"
                        for j in range(len(fert)):
                            operationSummary += str(fert[j][5]) + ": " + str(fert[j][6]) + " kg/ha<br>"
                    elif(op_row[0] == "Plant Growth Regulator"):
                        pgr = readOpDetails(op_row[2],op_row[0])
                        operationSummary += str(op_row[0]) + " Date: " + str(op_row[1]) + "<br>" + \
                                            "Chemical: " + str(pgr[0][3]) + ", Appication Type: " + str(pgr[0][4]) + "<br>" + \
                                            "Bandwidth: " + str(pgr[0][5]) + ", Rate: " + str(pgr[0][6]) + str(pgr[0][7]) + "<br>"
                    elif(op_row[0] == "Surface Residue"):
                        surfRes = readOpDetails(op_row[2],op_row[0])
                        operationSummary += str(op_row[0]) + " Date: " + str(op_row[1]) + "<br>" + \
                                            "Residue Type: " + str(surfRes[0][3]) + ", " + str(surfRes[0][4]) + ": " + str(surfRes[0][5]) + "<br>"
                    else:
                        operationSummary += op_row[0] + " Date: " + str(op_row[1]) + "<br>"

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
        self.newtreatmentname = QLineEdit("")
        self.udialog = QLabel()
        self.deletebutton = QPushButton("Delete")
        self.copytobutton = QPushButton("CopyTo")
        self.treatmentSummary = Tabless_Widget.getTreatmentSummary(self.ename,self.cname,self.tname)
        self.udialog.setText(self.treatmentSummary)      

        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0)
        self.sitetable1.clear()
        self.sitetable1.reset()        
        self.sitetable1.setRowCount(4)
        self.sitetable1.setColumnCount(2)           
        self.show_table_rows()             
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()
        self.sitetable1.setItem(0,0,QTableWidgetItem("What do you want to do with treatment?"))
        self.sitetable1.setCellWidget(1,0,self.deletebutton)
        self.sitetable1.setCellWidget(2,0,self.copytobutton)
        self.sitetable1.setCellWidget(2,1,self.newtreatmentname)
        self.sitetable1.setCellWidget(3,0,self.udialog)
        self.sitetable1.setVisible(True) 
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.deletebutton.clicked.connect(self.on_deletebutton_treatment_clicked)
        self.copytobutton.clicked.connect(self.on_copytobutton_treatment_clicked)


    def showNewOperationDialog(self,value,strval1,strval2,strval3):
        """
         QTable object. Asks user to SELECT operation from the given set of operation.
         Need to verify the USER input is SAFE for database. After verification, insert this 
         entry to table: Operation
        """
        self.treatmentname = strval1
        self.experimentname = strval2
        self.cropname = strval3
        #print("treatment=",self.treatmentname)
        #print("experiment=",self.experimentname)
        #print("crop=",self.cropname)        
        
        self.datelabel = QLabel("Date")
        self.calendar = QDateEdit()
        firstoperation_date = getme_date_of_first_operationDB(self.treatmentname, self.experimentname ,self.cropname)
        #print("firstoperation_date=",firstoperation_date)
        # first find out if this the new operation or there is a operation defined for this treatment. 
        # So we use the calendar date logic
        if len(firstoperation_date) > 0:
            firstoperation_date_parts = firstoperation_date[0].split("/") # 10/20/2006
            self.calendar.setMinimumDate(QDate(int(firstoperation_date_parts[2]),int(firstoperation_date_parts[0]),int(firstoperation_date_parts[1])))
            #print("debug:tabless_widget: first operation date=",firstoperation_date," ",firstoperation_date_parts[2]," ",firstoperation_date_parts[1])
        else:
            self.calendar.setMinimumDate(QDate(1900,1,1))
        self.calendar.setMaximumDate(QDate(2200,1,1))
        self.calendar.setDisplayFormat("MM/dd/yyyy")
        self.calendar.setCalendarPopup(True)

        self.fertClasslabel = QLabel("Fertilizer Class")
        self.comboFertClass = QComboBox()
        # This will be populated with optional operations, at the moment the optional
        #  operations are in the fertilizationClass and PGRChemical tables, PGRChemical operation
        # is only available for cotton.
        self.fertClass = read_fertilizationClass()        
        self.comboFertClass.clear()
        self.comboFertClass.addItem("Select Fertilization")
        for fertilization in self.fertClass:
            self.comboFertClass.addItem(fertilization)

        self.cropvarietylabel = QLabel("Cultivar")
        self.combocropvariety = QComboBox()

        self.eomultlabel = QLabel("Location of Planting Grid")
        self.comboeomult = QComboBox()

        self.yseedlabel = QLabel("Seed Depth (cm)")
        self.yseedlabeledit = QLineEdit("5")

        self.fDepthlabel = QLabel("Fertilizer Depth (cm)")
        self.fDepthlabeledit = QLineEdit("")

        self.seedMasslabel = QLabel("Seedpiece Mass (g)")
        self.seedMasslabeledit = QLineEdit("0")

        self.poplabel = QLabel("Plant Density (number of plants/m2)")
        self.poplabeledit = QLineEdit("6.5")

        self.rowspacinglabel = QLabel("Row Spacing (cm)")
        self.rowspacinglabeledit = QLineEdit("75")

        self.autoirrigationlabel = QLabel("Auto Irrigation")
        # Create and populate autoIrrigation combo
        self.comboAutoIrrig = QComboBox()          
        self.comboAutoIrrig.addItem("Yes") # val = 1
        self.comboAutoIrrig.addItem("No") # val = 0

        self.tillageTypelabel = QLabel("Tillage Type")
        # Create tillageType combo
        self.comboTillageType = QComboBox()
        self.tillageTypeList  = read_tillageTypeDB()            
        for record in sorted(self.tillageTypeList):
            self.comboTillageType.addItem(record)

        # At the moment fetilizer nutrients labels will be hard coded
        self.quantityClabel = QLabel("Carbon (C) (kg/ha)")
        self.quantityClabeledit = QLineEdit("")

        self.quantityNlabel = QLabel("Nitrogen (N) (kg/ha)")
        self.quantityNlabeledit = QLineEdit("")

        ##################### Plant Growth Regulator (PGR) is an optional operation available only for cotton
        self.PGRChemicallabel = QLabel("Plant Growth Regulator Chemical")
        # Create PGRChem combo
        self.comboPGRChemical = QComboBox()
        self.PGRChemicalList = read_PGRChemicalDB()
        self.comboPGRChemical.addItem("Select Plant Growth Regulator Chemical")
        for record in sorted(self.PGRChemicalList):
            self.comboPGRChemical.addItem(record)

        self.PGRAppTypelabel = QLabel("PGR Application Type")
        # Create PGR Application Method combo
        self.comboPGRAppType = QComboBox()
        self.PGRAppTypeList = read_PGRAppTypeDB()
        for record in sorted(self.PGRAppTypeList):
            self.comboPGRAppType.addItem(record)

        self.PGRBandwidthlabel = QLabel("PGR Application Bandwidth")
        self.PGRBandwidthedit = QLineEdit("")

        self.PGRAppRatelabel = QLabel("PGR Application Rate")
        self.PGRAppRateedit = QLineEdit("")

        self.PGRAppUnitlabel = QLabel("PGR Application Units")
        # Create PGR Application unit combo
        self.comboPGRAppUnit = QComboBox()
        self.PGRAppUnitList = read_PGRAppUnitDB()
        for record in sorted(self.PGRAppUnitList):
            self.comboPGRAppUnit.addItem(record)

        # Surface Residue is an optional operation
        self.surfReslabel = QLabel("Surface Residue")
        # Create surface residue type combo
        self.comboSurfResType = QComboBox()
        self.surfResTypeList = read_SurfResTypeDB()
        self.comboSurfResType.addItem("Select Surface Residue Type")
        for record in sorted(self.surfResTypeList):
            self.comboSurfResType.addItem(record)

        self.comboSurfResApplType = QComboBox()
        self.surfResApplTypeList = read_SurfResApplTypeDB()
        self.comboSurfResApplType.addItem("Select Surface Residue Application Type")
        for record in sorted(self.surfResApplTypeList):
            self.comboSurfResApplType.addItem(record)
        self.surfResApplTypeValedit = QLineEdit("")

        self.savebutton1 = QPushButton("Save")

        #checking USER input for NUMERIC values
        regexp_num = QtCore.QRegExp('^\d*[.]?\d*$')
        validator_num = QtGui.QRegExpValidator(regexp_num)
        test1state = self.quantityClabeledit.setValidator(validator_num)
        test1state = self.quantityNlabeledit.setValidator(validator_num)
        test1state = self.poplabeledit.setValidator(validator_num)
        test1state = self.yseedlabeledit.setValidator(validator_num)
        test1state = self.rowspacinglabeledit.setValidator(validator_num)
        test1state = self.fDepthlabeledit.setValidator(validator_num)
        test1state = self.seedMasslabeledit.setValidator(validator_num)
        test1state = self.PGRBandwidthedit.setValidator(validator_num)
        test1state = self.PGRAppRateedit.setValidator(validator_num)
        test1state = self.surfResApplTypeValedit.setValidator(validator_num)
       

        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0)
        self.sitetable1.clear()
        self.sitetable1.reset()

        self.sitetable1.setRowCount(21)
        self.sitetable1.setColumnCount(3)       
        self.show_table_rows()        
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()

        self.sitetable1.setCellWidget(0,0,self.fertClasslabel)        
        self.sitetable1.setCellWidget(1,0,self.datelabel)        
        self.sitetable1.setCellWidget(2,0,self.cropvarietylabel)
        # Plant density
        self.sitetable1.setCellWidget(3,0,self.poplabel)
        # Seed depth
        self.sitetable1.setCellWidget(4,0,self.yseedlabel)
        self.sitetable1.setCellWidget(5,0,self.rowspacinglabel)
        self.sitetable1.setCellWidget(6,0,self.eomultlabel)
        self.sitetable1.setCellWidget(7,0,self.seedMasslabel)
        self.sitetable1.setCellWidget(8,0,self.autoirrigationlabel)
        self.sitetable1.setCellWidget(9,0,self.tillageTypelabel)
        self.sitetable1.setCellWidget(10,0,self.fDepthlabel)
        self.sitetable1.setCellWidget(11,0,self.quantityClabel)
        self.sitetable1.setCellWidget(12,0,self.quantityNlabel)
        self.sitetable1.setCellWidget(13,0,self.PGRChemicallabel)
        self.sitetable1.setCellWidget(14,0,self.PGRAppTypelabel)
        self.sitetable1.setCellWidget(15,0,self.PGRBandwidthlabel)
        self.sitetable1.setCellWidget(16,0,self.PGRAppRatelabel)
        self.sitetable1.setCellWidget(17,0,self.PGRAppUnitlabel)
        self.sitetable1.setCellWidget(18,0,self.surfReslabel)
        self.sitetable1.setCellWidget(19,0,self.comboSurfResApplType)

        self.sitetable1.setCellWidget(0,1,self.comboFertClass)
        self.sitetable1.setCellWidget(1,1,self.calendar)
        self.sitetable1.setCellWidget(2,1,self.combocropvariety)
        self.sitetable1.setCellWidget(3,1,self.poplabeledit)
        self.sitetable1.setCellWidget(4,1,self.yseedlabeledit)
        self.sitetable1.setCellWidget(5,1,self.rowspacinglabeledit)
        self.sitetable1.setCellWidget(6,1,self.comboeomult)
        self.sitetable1.setCellWidget(7,1,self.seedMasslabeledit)
        self.sitetable1.setCellWidget(8,1,self.comboAutoIrrig)
        self.sitetable1.setCellWidget(9,1,self.comboTillageType)
        self.sitetable1.setCellWidget(10,1,self.fDepthlabeledit)
        self.sitetable1.setCellWidget(11,1,self.quantityClabeledit)
        self.sitetable1.setCellWidget(12,1,self.quantityNlabeledit)
        self.sitetable1.setCellWidget(13,1,self.comboPGRChemical)
        self.sitetable1.setCellWidget(14,1,self.comboPGRAppType)
        self.sitetable1.setCellWidget(15,1,self.PGRBandwidthedit)
        self.sitetable1.setCellWidget(16,1,self.PGRAppRateedit)
        self.sitetable1.setCellWidget(17,1,self.comboPGRAppUnit)
        self.sitetable1.setCellWidget(18,1,self.comboSurfResType)
        self.sitetable1.setCellWidget(19,1,self.surfResApplTypeValedit)
        self.sitetable1.setCellWidget(20,1,self.savebutton1)
        
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)

        self.sitetable1.showRow(0)
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
        if self.cropname == "cotton":
            self.sitetable1.showRow(13)
        else:
            self.sitetable1.hideRow(13)
        self.sitetable1.hideRow(14)
        self.sitetable1.hideRow(15)
        self.sitetable1.hideRow(16)
        self.sitetable1.hideRow(17)
        self.sitetable1.showRow(18)
        self.sitetable1.hideRow(19)
        self.sitetable1.hideRow(20)
        self.comboFertClass.currentIndexChanged.connect(self.oncomboactivated)
        self.comboPGRChemical.currentIndexChanged.connect(self.oncomboPGRactivated)
        self.comboSurfResType.currentIndexChanged.connect(self.oncomboSurfResactivated)


    def showExistingOperationDialog(self,value,strval1,strval2,strval3,strval4):
        """
         str_treatmentname,str_experimentname,str_cropname,str_operationname
         QTable object. 
         Will show the existing operation. Will allow  to modify its values.
         Create the field table. Query the OPERATION table and get the flag values
        """
        self.treatmentname = strval1
        self.experimentname = strval2
        self.cropname = strval3
        # strval4 contains operation_id and operation_name concatenated with '_' character
        self.operationname = strval4.split('_')[1]
        self.op_id = strval4.split('_')[0]
        #print("treat = ", self.treatmentname, " expir = ", self.experimentname, " crop nm = ", self.cropname, " op name = ", self.operationname, " op_id = ",self.op_id) 
        self.record = readOpDetails(self.op_id,self.operationname)
        #print("debug: record=",self.record)
        self.datelabel = QLabel("Date")
        self.calendar = QDateEdit()
        self.calendar.setMinimumDate(QDate(1900,1,1))
        self.calendar.setMaximumDate(QDate(2200,1,1))
        self.calendar.setDisplayFormat("MM/dd/yyyy")
        self.calendar.setCalendarPopup(True)
        fformat = QtGui.QTextCharFormat()
        fformat.setForeground(QtGui.QColor(151, 180, 152))
        
        self.savebutton1 = QPushButton("Update")
        self.deletebutton = QPushButton("Delete")
        
        self.fertClasslabel = QLabel("Fertilizer Class")
        self.comboFertClass = QComboBox()

        self.cropvarietylabel = QLabel("Cultivars")
        self.combocropvariety = QComboBox()

        self.eomultlabel = QLabel("Location of Planting Grid")
        self.comboeomult = QComboBox()

        self.autoirrigationlabel = QLabel("Auto Irrigation")
        self.comboAutoIrrig = QComboBox()   
        
        self.tillageTypelabel = QLabel("Tillage Type")
        self.comboTillageType = QComboBox()

        self.yseedlabel = QLabel("Seed Depth (cm)")
        self.yseedlabeledit = QLineEdit("")

        self.poplabel = QLabel("Plant Density (number of plants/m2)")
        self.poplabeledit = QLineEdit("")

        self.rowspacinglabel = QLabel("Row Spacing (cm)")
        self.rowspacinglabeledit = QLineEdit("")

        self.fDepthlabel = QLabel("Fertilizer Depth (cm)")
        self.fDepthlabeledit = QLineEdit("")

        self.seedMasslabel = QLabel("Seedpiece Mass (g)")
        self.seedMasslabeledit = QLineEdit("")

        # At the moment fetilizer nutrients labels will be hard coded
        self.quantityClabel = QLabel("Carbon (C) (kg/ha)")
        self.quantityClabeledit = QLineEdit("")

        self.quantityNlabel = QLabel("Nitrogen (N) (kg/ha)")
        self.quantityNlabeledit = QLineEdit("")

        self.PGRChemicallabel = QLabel("Plant Growth Regulator Chemical")
        self.comboPGRChemical = QComboBox()

        self.PGRAppTypelabel = QLabel("PGR Application Type")
        self.comboPGRAppType = QComboBox()

        self.PGRBandwidthlabel = QLabel("PGR Application Bandwidth")
        self.PGRBandwidthedit = QLineEdit("")

        self.PGRAppRatelabel = QLabel("PGR Application Rate")
        self.PGRAppRateedit = QLineEdit("")

        self.PGRAppUnitlabel = QLabel("PGR Application Units")
        self.comboPGRAppUnit = QComboBox()

        self.fertSurfReslabel = QLabel("Total Residue (kg/ha)")
        self.fertSurfResTypelabel = QLabel("Residue Type")

        self.fertSurfReslabeledit = QLineEdit("")
        self.comboSurfResType = QComboBox()

        self.surfReslabel = QLabel("Surface Residue")
        self.comboSurfResType = QComboBox()

        self.comboSurfResApplType = QComboBox()
        self.surfResApplTypeValedit = QLineEdit("")

        self.sitetable1.clearContents()
        self.sitetable1.setRowCount(0) # necessary. It will clean the table internally     
        self.sitetable1.clear()
        self.sitetable1.reset()
        
        self.sitetable1.setRowCount(21)
        self.sitetable1.setColumnCount(3)
        self.show_table_rows()           
        self.sitetable1.horizontalHeader().hide()
        self.sitetable1.verticalHeader().hide()

        self.sitetable1.setCellWidget(0,0,self.fertClasslabel)        
        self.sitetable1.setCellWidget(1,0,self.datelabel)
        self.sitetable1.setCellWidget(2,0,self.cropvarietylabel)
        self.sitetable1.setCellWidget(3,0,self.poplabel)
        self.sitetable1.setCellWidget(4,0,self.yseedlabel)
        self.sitetable1.setCellWidget(5,0,self.rowspacinglabel)
        self.sitetable1.setCellWidget(6,0,self.eomultlabel)
        self.sitetable1.setCellWidget(7,0,self.seedMasslabel)
        self.sitetable1.setCellWidget(8,0,self.autoirrigationlabel)
        self.sitetable1.setCellWidget(9,0,self.tillageTypelabel)
        self.sitetable1.setCellWidget(10,0,self.fDepthlabel)
        self.sitetable1.setCellWidget(11,0,self.quantityClabel)
        self.sitetable1.setCellWidget(12,0,self.quantityNlabel)
        self.sitetable1.setCellWidget(13,0,self.PGRChemicallabel)
        self.sitetable1.setCellWidget(14,0,self.PGRAppTypelabel)
        self.sitetable1.setCellWidget(15,0,self.PGRBandwidthlabel)
        self.sitetable1.setCellWidget(16,0,self.PGRAppRatelabel)
        self.sitetable1.setCellWidget(17,0,self.PGRAppUnitlabel)
        self.sitetable1.setCellWidget(18,0,self.surfReslabel)
        self.sitetable1.setCellWidget(19,0,self.comboSurfResApplType)
        if self.operationname == 'Fertilizer' or self.operationname == "Plant Growth Regulator" or self.operationname == "Surface Residue":
            self.sitetable1.setCellWidget(20,0,self.deletebutton)

        self.sitetable1.setCellWidget(0,1,self.comboFertClass)
        self.sitetable1.setCellWidget(1,1,self.calendar)        
        self.sitetable1.setCellWidget(2,1,self.combocropvariety)
        self.sitetable1.setCellWidget(3,1,self.poplabeledit)
        self.sitetable1.setCellWidget(4,1,self.yseedlabeledit)
        self.sitetable1.setCellWidget(5,1,self.rowspacinglabeledit)
        self.sitetable1.setCellWidget(6,1,self.comboeomult)
        self.sitetable1.setCellWidget(7,1,self.seedMasslabeledit)
        self.sitetable1.setCellWidget(8,1,self.comboAutoIrrig)
        self.sitetable1.setCellWidget(9,1,self.comboTillageType)
        self.sitetable1.setCellWidget(10,1,self.fDepthlabeledit)
        self.sitetable1.setCellWidget(11,1,self.quantityClabeledit)
        self.sitetable1.setCellWidget(12,1,self.quantityNlabeledit)
        self.sitetable1.setCellWidget(13,1,self.comboPGRChemical)
        self.sitetable1.setCellWidget(14,1,self.comboPGRAppType)
        self.sitetable1.setCellWidget(15,1,self.PGRBandwidthedit)
        self.sitetable1.setCellWidget(16,1,self.PGRAppRateedit)
        self.sitetable1.setCellWidget(17,1,self.comboPGRAppUnit)
        self.sitetable1.setCellWidget(18,1,self.comboSurfResType)
        self.sitetable1.setCellWidget(19,1,self.surfResApplTypeValedit)
        self.sitetable1.setCellWidget(20,1,self.savebutton1)
        
        header = self.sitetable1.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        self.sitetable1.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.sitetable1.verticalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)

        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        #print("record=",self.record)

        # Calendar
        if self.record[0][2] != '':
            self.sitetable1.showRow(1) 
            # recover the mm,dd,yyyy and set the calendar
            record_parts = self.record[0][2].split("/")
            currentYear = record_parts[2]
            self.calendar.setDate(QDate(int(currentYear),int(record_parts[0]),int(record_parts[1])))

        if self.operationname == "Simulation Start" and self.cropname != "fallow":        
            self.sitetable1.hideRow(0)
            self.readcropvarietylist  = read_cultivar_DB(self.cropname)            
            for record2 in sorted(self.readcropvarietylist):
                self.combocropvariety.addItem(record2)
            matchedindex = self.combocropvariety.findText(str(self.record[0][10])) 
            if matchedindex >= 0:
                self.combocropvariety.setCurrentIndex(matchedindex)

            # Build eomult picklist
            self.comboeomult.addItem("Left") # val = 0.5
            self.comboeomult.addItem("Middle") # val = 1.0
            if(self.record[0][8] == 0.5):
                 matchedindex = self.comboeomult.findText("Left")
            else:
                 matchedindex = self.comboeomult.findText("Middle")
            self.comboeomult.setCurrentIndex(matchedindex)

            # Create and populate autoIrrigation combo
            self.comboAutoIrrig.addItem("Yes") # val = 1
            self.comboAutoIrrig.addItem("No") # val = 0
            if(self.record[0][4] == 1):
                 matchedindex = self.comboAutoIrrig.findText("Yes")
            else:
                 matchedindex = self.comboAutoIrrig.findText("No")
            self.comboAutoIrrig.setCurrentIndex(matchedindex)

            self.poplabeledit.setText(str(self.record[0][3]))  
            self.yseedlabeledit.setText(str(self.record[0][6]))  
            self.rowspacinglabeledit.setText(str(self.record[0][9]))  
            self.seedMasslabeledit.setText(str(self.record[0][11]))
                        
            self.sitetable1.showRow(2)                    
            self.sitetable1.showRow(3)                    
            self.sitetable1.showRow(4)                    
            self.sitetable1.showRow(5)                    
            self.sitetable1.showRow(6)                    
            self.sitetable1.showRow(8) 
            # This is true for potato and soybean  
            if self.cropname == "potato":
                self.sitetable1.showRow(7)
            else:                    
                self.sitetable1.hideRow(7)
            self.sitetable1.hideRow(9)
            self.sitetable1.hideRow(10)
            self.sitetable1.hideRow(11)
            self.sitetable1.hideRow(12)
            self.sitetable1.hideRow(13)
            self.sitetable1.hideRow(14)
            self.sitetable1.hideRow(15)
            self.sitetable1.hideRow(16)
            self.sitetable1.hideRow(17)
            self.sitetable1.hideRow(18)
            self.sitetable1.hideRow(19)

        # Check if there is any fertilization operation on fertilizationOp table
        elif self.operationname == 'Fertilizer':
            #print(self.record)
            self.sitetable1.showRow(0) 
            self.fertClass = read_fertilizationClass()        
            self.comboFertClass.clear()
            self.comboFertClass.addItem("Select Fertilization")
            for fertilization in self.fertClass:
                self.comboFertClass.addItem(fertilization)
            self.comboFertClass.setCurrentIndex(self.comboFertClass.findText(self.record[0][3]))
            self.comboFertClass.setEnabled(False) 
           
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
            for j in range(len(self.record)):
                # Need depth only once
                if j == 0:
                    # Depth
                    self.sitetable1.showRow(10) 
                    self.fDepthlabeledit.setText(str(self.record[j][4]))

                if((self.record[j][3] == "Manure" or self.record[j][3] == "Litter") and self.record[j][5] == "Carbon (C)"):
                    self.sitetable1.showRow(11)
                    self.quantityClabeledit.setText(str(self.record[j][6]))

                if(self.record[j][5] == "Nitrogen (N)"):
                    self.sitetable1.showRow(12)        
                    self.quantityNlabeledit.setText(str(self.record[j][6]))
                self.sitetable1.hideRow(18)
                self.sitetable1.hideRow(19)
            self.sitetable1.hideRow(13)
            self.sitetable1.hideRow(14)
            self.sitetable1.hideRow(15)
            self.sitetable1.hideRow(16)
            self.sitetable1.hideRow(17)
           
        # Tillage
        elif(self.operationname == "Tillage"):
            self.sitetable1.hideRow(0)
            self.sitetable1.hideRow(2)
            self.sitetable1.hideRow(3)
            self.sitetable1.hideRow(4)
            self.sitetable1.hideRow(5)
            self.sitetable1.hideRow(6)
            self.sitetable1.hideRow(7)
            self.sitetable1.hideRow(8)
            self.sitetable1.showRow(9)
            self.sitetable1.hideRow(10)                    
            self.sitetable1.hideRow(11)                    
            self.sitetable1.hideRow(12)                    
            self.tillageTypeList  = read_tillageTypeDB()            
            for record in sorted(self.tillageTypeList):
                self.comboTillageType.addItem(record)
            matchedindex = self.comboTillageType.findText(str(self.record[0][3]))
            self.comboTillageType.setCurrentIndex(matchedindex)
            self.comboTillageType.currentIndexChanged.connect(self.oncomboTillageActivated)
            if(self.comboTillageType.currentText() == "No tillage"):
                self.sitetable1.hideRow(1)
            else:
                self.sitetable1.showRow(1)
            self.sitetable1.hideRow(13)
            self.sitetable1.hideRow(14)
            self.sitetable1.hideRow(15)
            self.sitetable1.hideRow(16)
            self.sitetable1.hideRow(17)
            self.sitetable1.hideRow(18)
            self.sitetable1.hideRow(19)

        # Plant Growth Regulator
        elif self.operationname == "Plant Growth Regulator":
            self.sitetable1.hideRow(0)
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
            # Create PGRChem combo
            self.PGRChemicalList = read_PGRChemicalDB()
            self.comboPGRChemical.addItem("Select Plant Growth Regulator Chemical")
            for record in sorted(self.PGRChemicalList):
                self.comboPGRChemical.addItem(record)
            matchedindex = self.comboPGRChemical.findText(str(self.record[0][3]))
            self.comboPGRChemical.setCurrentIndex(matchedindex)      
            self.sitetable1.showRow(13)
            # Create PGR Application Method combo
            self.PGRAppTypeList = read_PGRAppTypeDB()
            for record in sorted(self.PGRAppTypeList):
                self.comboPGRAppType.addItem(record)
            matchedindex = self.comboPGRAppType.findText(str(self.record[0][4]))
            self.comboPGRAppType.setCurrentIndex(matchedindex)      
            self.sitetable1.showRow(14)
            self.PGRBandwidthedit.setText(str(self.record[0][5]))
            self.sitetable1.showRow(15)
            self.PGRAppRateedit.setText(str(self.record[0][6]))
            self.sitetable1.showRow(16)
            # Create PGR Application unit combo
            self.PGRAppUnitList = read_PGRAppUnitDB()
            for record in sorted(self.PGRAppUnitList):
                self.comboPGRAppUnit.addItem(record)
            matchedindex = self.comboPGRAppUnit.findText(str(self.record[0][7]))
            self.comboPGRAppUnit.setCurrentIndex(matchedindex)      
            self.sitetable1.showRow(17)
            self.sitetable1.hideRow(18)
            self.sitetable1.hideRow(19) 
        elif self.operationname == "Surface Residue":
            self.sitetable1.hideRow(0)
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
            self.sitetable1.hideRow(13)
            self.sitetable1.hideRow(14)
            self.sitetable1.hideRow(15)
            self.sitetable1.hideRow(16)
            self.sitetable1.hideRow(17)

            self.surfResTypeList = read_SurfResTypeDB()
            self.comboSurfResType.addItem("Select Surface Residue Type")
            for record in sorted(self.surfResTypeList):
                self.comboSurfResType.addItem(record)
            matchedindex = self.comboSurfResType.findText(str(self.record[0][3]))
            self.comboSurfResType.setCurrentIndex(matchedindex)      
            self.sitetable1.showRow(18)

            self.surfResApplTypeList = read_SurfResApplTypeDB()
            self.comboSurfResApplType.addItem("Select Surface Residue Application Type")
            for record in sorted(self.surfResApplTypeList):
                self.comboSurfResApplType.addItem(record)
            matchedindex = self.comboSurfResApplType.findText(str(self.record[0][4]))
            self.comboSurfResApplType.setCurrentIndex(matchedindex)      
            self.surfResApplTypeValedit.setText(str(self.record[0][5]))
            self.sitetable1.showRow(19)
        else:
            self.sitetable1.hideRow(0)
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
            self.sitetable1.hideRow(13)
            self.sitetable1.hideRow(14)
            self.sitetable1.hideRow(15)
            self.sitetable1.hideRow(16)
            self.sitetable1.hideRow(17)
            self.sitetable1.hideRow(18)
            self.sitetable1.hideRow(19)

        self.sitetable1.showRow(20)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        self.savebutton1.clicked.connect(self.on_savebutton_operation_clicked)
        self.deletebutton.clicked.connect(self.on_deletebutton_operation_clicked)
        
        
    def oncomboactivated(self,listindex):
    # This function is only activated when an Fertilization is added, therefore only
    # fertilization items should be activated
        self.operationname = "Fertilizer"
        #print("text=",self.operationname)        

        self.sitetable1.showRow(0)
        self.sitetable1.showRow(1)
        self.sitetable1.hideRow(2)
        self.sitetable1.hideRow(3)
        self.sitetable1.hideRow(4)
        self.sitetable1.hideRow(5)
        self.sitetable1.hideRow(6)
        self.sitetable1.hideRow(7)
        self.sitetable1.hideRow(8)
        self.sitetable1.hideRow(9)
        self.sitetable1.showRow(10)
        if(self.comboFertClass.currentText() == "Manure" or self.comboFertClass.currentText() == "Litter"):
            self.sitetable1.showRow(11)
        else:
            self.sitetable1.hideRow(11)
        self.sitetable1.showRow(12) 
        self.sitetable1.hideRow(13)
        self.sitetable1.hideRow(14)
        self.sitetable1.hideRow(15)
        self.sitetable1.hideRow(16)
        self.sitetable1.hideRow(17)
        self.sitetable1.hideRow(18)
        self.sitetable1.hideRow(19)
        self.sitetable1.showRow(20)

        self.op_id = -10
        self.savebutton1.clicked.connect(self.on_savebutton_operation_clicked)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        
        
    def oncomboPGRactivated(self,listindex):
    # This function is only activated when a PGR operation is added, therefore only
    # PGR items should be activated
        self.operationname = "Plant Growth Regulator"
        #print("text=",self.operationname)        

        self.sitetable1.hideRow(0)
        self.sitetable1.showRow(1)
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
        self.sitetable1.showRow(13)
        self.sitetable1.showRow(14)
        self.sitetable1.showRow(15)
        self.sitetable1.showRow(16)
        self.sitetable1.showRow(17)
        self.sitetable1.hideRow(18)
        self.sitetable1.hideRow(19)
        self.sitetable1.showRow(20)

        self.op_id = -10
        self.savebutton1.clicked.connect(self.on_savebutton_operation_clicked)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        
        
    def oncomboSurfResactivated(self,listindex):
    # This function is only activated when a Surface Residue operation is added, therefore only
    # Surface Residue items should be activated
        self.operationname = "Surface Residue"
        #print("text=",self.operationname)        

        self.sitetable1.hideRow(0)
        self.sitetable1.showRow(1)
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
        self.sitetable1.hideRow(13)
        self.sitetable1.hideRow(14)
        self.sitetable1.hideRow(15)
        self.sitetable1.hideRow(16)
        self.sitetable1.hideRow(17)
        self.sitetable1.showRow(18)
        self.sitetable1.showRow(19)
        self.sitetable1.showRow(20)

        self.op_id = -10
        self.savebutton1.clicked.connect(self.on_savebutton_operation_clicked)
        self.sitetable1.resizeColumnsToContents();
        self.sitetable1.resizeRowsToContents();
        self.sitetable1.setShowGrid(False)
        
        
    def oncomboTillageActivated(self,listindex):
        # Tillage
        if(self.comboTillageType.currentText() == "No tillage"):
            self.sitetable1.hideRow(1)
        else:
            self.sitetable1.showRow(1)
        
        
    def on_savebutton_operation_clicked(self,value):
        #print("Inside save operation")
        #print("value=",value)
        #print("treatment=", self.treatmentname)
        #print("experiment=", self.experimentname)
        #print("crop=", self.cropname)
        #print("operation_id=",self.op_id)
        #print("operation=",self.operationname)

        # All operations have a record on operations table
        new_record = []
        initCond_record = [6.5,0,0,5,0.65,0.5,75,"fallow",0]
        tillage_record = []
        fert_record = []
        fertNut_record = []
        PGR_record = []
        SR_record = []
        set_unittest_reportflags

        new_record.append(self.operationname)
        if self.operationname == "Tillage" and self.comboTillageType.currentText() == "No tillage":
            new_record.append("")
        else:
            new_record.append(self.calendar.date().toString("MM/dd/yyyy"))


        if self.operationname == "Simulation Start" and self.cropname != "fallow":
            initCond_record = []
            print("cultivar= ",self.combocropvariety.currentText())
            initCond_record.append(float(self.poplabeledit.text()))
            if self.comboAutoIrrig.currentText() == "Yes":
                initCond_record.append(1)
            else:
                initCond_record.append(0)
            # xseed is dependent on the eomult value
            if self.comboeomult.currentText() == "Left":
                initCond_record.append(0.0)
            else:
                initCond_record.append(float(self.rowspacinglabeledit.text())/2)
            initCond_record.append(float(self.yseedlabeledit.text()))  
            # cec = 0.65
            initCond_record.append(0.65)
            if self.comboeomult.currentText() == "Left":
                initCond_record.append(0.5)
            else:
                initCond_record.append(1.0)
            initCond_record.append(float(self.rowspacinglabeledit.text()))  
            initCond_record.append(self.combocropvariety.currentText())
            initCond_record.append(float(self.seedMasslabeledit.text()))

            # Validate row spacing
            if(initCond_record[6] < 1 or initCond_record[6] > 200):
                return messageUserInfo("Row spacing should be a value between 1 and 200 cm.")

            if self.cropname == "maize":
                # Validate plant density
                if(initCond_record[0] < 1 or initCond_record[0] > 20):
                    return messageUserInfo("Plant density for maize should be a value between 1 and 20 number of plants/m2.")
                # Validate seed depth
                if(initCond_record[3] < 2 or initCond_record[3] > 7):
                    return messageUserInfo("Seed depth for maize should be a value between 2 and 7 cm.")

            elif self.cropname == "potato":
                # Validate plant density
                if(initCond_record[0] < 1 or initCond_record[0] > 300):
                    return messageUserInfo("Plant density for potato should be a value between 1 and 25 number of plants/m2.")
                # Validate seed depth
                if(initCond_record[3] < 1 or initCond_record[3] > 20):
                    return messageUserInfo("Seed depth for potato should be a value between 1 and 20 cm.")
                # Validate seedpiece mass
                if(initCond_record[8] < 0 or initCond_record[8] > 50):
                    return messageUserInfo("Seedpiece mass for potato should be a value between 0 and 50 g.")

            elif self.cropname == "soybean":
                # Validate plant density
                if(initCond_record[0] < 20):
                    return messageUserInfo("Plant density for soybean should be a value equal or greater than 20 number of plants/m2, a smaller amount may lead to model errors..")

        elif self.operationname == "Tillage":
            tillage_record.append(self.comboTillageType.currentText()) 

        elif self.operationname == "Fertilizer":
            fert_record.append(self.comboFertClass.currentText())
            # depth
            if float(self.fDepthlabeledit.text()) >= 0:
                fert_record.append(float(self.fDepthlabeledit.text()))
            else:
                return messageUserInfo("Please enter Fertilizer Depth.")

            # Nitrogen
            if float(self.quantityNlabeledit.text()) <= 0:
                return messageUserInfo("Nitrogen amount should be greater than 0.")
            if float(self.quantityNlabeledit.text()) > 6000:                  
                return messageUserInfo("Check nitrogen amount, it is too high.")
            fertNut_record.append(float(self.quantityNlabeledit.text()))
            fertNut_record.append("Nitrogen (N)")

            # Carbon
            if (self.comboFertClass.currentText() == "Manure" or self.comboFertClass.currentText() == "Litter"):
                if float(self.quantityClabeledit.text()) <= 0:
                    return messageUserInfo("Carbon amount should be greater than 0.")                  
                if float(self.quantityClabeledit.text()) > 10000:                  
                    return messageUserInfo("Check carbon amount, it is too high.")
                fertNut_record.append(float(self.quantityClabeledit.text()))
                fertNut_record.append("Carbon (C)")
        elif self.operationname == "Plant Growth Regulator":
            PGR_record.append(self.comboPGRChemical.currentText())
            PGR_record.append(self.comboPGRAppType.currentText())
            if float(self.PGRBandwidthedit.text()) <= 0:
                return messageUserInfo("PGR application bandwidth should be greater than 0.")
            PGR_record.append(float(self.PGRBandwidthedit.text()))
            if float(self.PGRAppRateedit.text()) <= 0:
                return messageUserInfo("PGR application rate should be greater than 0.")
            PGR_record.append(float(self.PGRAppRateedit.text()))
            PGR_record.append(self.comboPGRAppUnit.currentText())
        elif self.operationname == "Surface Residue":
            SR_record.append(self.comboSurfResType.currentText())
            self.surfResApplType = self.comboSurfResApplType.currentText()
            SR_record.append(self.surfResApplType)
            self.surfResApplTypeVal = float(self.surfResApplTypeValedit.text())
            SR_record.append(self.surfResApplTypeVal)
            # Validate mass/thickness
            if self.surfResApplType == "Mass (kg/ha)":
                if self.surfResApplTypeVal < 1000 or self.surfResApplTypeVal > 10000:
                    return messageUserInfo("Surface residue mass should be greater than 1,000kg/ha and less than 10,000kg/ha.")
            else:
                if self.surfResApplTypeVal < 2 or self.surfResApplTypeVal > 10:
                    return messageUserInfo("Surface residue thickness should be greater than 2cm and less than 10cm.")

        status = check_and_update_operationDB(self.op_id, self.treatmentname, self.experimentname, self.cropname, new_record, \
                                              initCond_record, tillage_record, fert_record, fertNut_record, PGR_record, SR_record)

        if status:
            self.sitetable1.setVisible(False)
            self.sig2.emit(1)


    def on_deletebutton_operation_clicked(self,value):
        delete_flag = messageUserDelete("Are you sure you want to delete this operation?")
        if delete_flag:
            status = check_and_delete_operationDB(self.op_id,self.operationname)
            if status:
                self.sitetable1.setVisible(False)
                self.sig2.emit(3)
                return True
            else:
                return False