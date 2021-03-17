import os
import sys
from PyQt5.QtCore import (QModelIndex, QVariant, Qt, pyqtSlot, pyqtSignal)
from PyQt5 import QtGui
from CustomTool.custom1 import *  # TreeOfTableModel
from CustomTool.UI import *
from PyQt5.QtGui import QColor,QFont
from PyQt5.Qt import QTreeView
from PyQt5.QtWidgets import QAbstractItemView

#######################
######### Data tree structure
#root
##crop
###experiment
####treatment
#####operation

# this will store the list of cropbasedata objects
class cropbasedatalist():
    def __init__(self):
        super(cropbasedatalist,self).__init__()
        self.list1 = [] # this will hold list of cropbasedata objects


class ServerModel(TreeOfTableModel):
    def __init__(self,parent=None):
        super(ServerModel,self).__init__(parent)
        print("inside servermodel")


    def data(self,index,role):        
        #alternating background color for the columns
        if (index.isValid() and role == Qt.BackgroundColorRole):
            if index.column()%2 ==1:
                return QVariant(QColor(Qt.lightGray))
            return QVariant(QColor(Qt.white))
        if role == Qt.FontRole:
            ffont = QtGui.QFont()
            ffont.setBold(True)
            ffont.setWeight(75)            
            return QVariant(ffont)
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            if node is None:
                return QVariant()
            if isinstance(node, BranchNode):
                if index.column() !=0:
                    return QVariant()
            parent = node.parent
            if parent is not None:
                return QVariant()
        return TreeOfTableModel.data(self,index,role)
        

class TreeOfTableWidget(QTreeView):
    # Add a signal
    getExperiment = pyqtSignal(int,str,str)
    getTreatment = pyqtSignal(int,str,str,str)
    getNewOperation = pyqtSignal(int,str,str,str)
    getOperation = pyqtSignal(int,str,str,str,str,QModelIndex)
    informUser = pyqtSignal(int,str)

    # load2 will be default
    def __init__(self,databasename,tablename,nesting, separator,loader=2,parent=None): 
        self.databasename=databasename
        self.tablename=tablename
        self.nesting=nesting
        self.separator=separator
        self.loader=loader
        super(TreeOfTableWidget,self).__init__(parent)
        self.setSelectionBehavior(QTreeView.SelectItems)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.savecurrentindex=0
        self.savecurrentnode = 0
                        
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(self.DragOnly)
        self.setDragEnabled(True)
        
        self.font().setPointSize(24)        
        self.font().Bold
        self.update()
        model = ServerModel(self)        
        self.setModel(model)
        
        try:
            print("Inside TreeOfTableWidget __init__")
            model.load2(databasename, tablename, nesting, separator, loader)   
        except IOError as e:
            QMessageBox.warning(self,"Server Info-Error",unicode(e))
  
        self.doubleClicked.connect(self.tclicked)        
        self.clicked.connect(self.tclicked)


    def setModel(self, model):
        super(TreeOfTableWidget, self).setModel(model)


    def tclicked(self,index):   
        print("cropdata: tclicked:In Signal,Click here")   
        if not isinstance(index.model().nodeFromIndex(index), LeafNode):   
            treedepth = self.model().getDepth(index)  # important, gives how deep in the tree            
            if(treedepth==2): #if(index.model().nodeFromIndex(index).name == "Add New Experiment"):
                if(index.model().nodeFromIndex(index).name == "Add New Experiment"):                    
                    str_experimentname = index.model().nodeFromIndex(index).name                    
                    str_cropname = index.model().nodeFromIndex(index).parent.name                    
                    self.getExperiment.emit(1,str_experimentname,str_cropname)                    
                else:                    
                    str_experimentname = index.model().nodeFromIndex(index).name
                    str_cropname = index.model().nodeFromIndex(index).parent.name
                    self.getExperiment.emit(5,str_experimentname,str_cropname)
            elif(treedepth==3): #elif(index.model().nodeFromIndex(index).name == "Add New Treatment"):
                currentnode = index.model().nodeFromIndex(index)
                currentnodeparent = currentnode.parent.name #do we need this
                currentnodeparentindex = self.model().createIndex(1,0,currentnodeparent)                              
                str_experimentname = index.model().nodeFromIndex(index).parent.name
                str_cropname = currentnode.parent.parent.name
                str_treatmentname = index.model().nodeFromIndex(index).name
                if(index.model().nodeFromIndex(index).name == "Add New Treatment"):                    
                    self.getTreatment.emit(2,str_experimentname,str_cropname,str_treatmentname)
                else: # deletes the treatment
                    self.getTreatment.emit(6,str_experimentname,str_cropname,str_treatmentname)
            elif(index.model().nodeFromIndex(index).name == "Add New Operation"):                
                currentnode = index.model().nodeFromIndex(index)  
                str_treatmentname = currentnode.parent.name                           
                str_experimentname = currentnode.parent.parent.name 
                str_cropname = currentnode.parent.parent.parent.name                
                self.getNewOperation.emit(3,str_treatmentname,str_experimentname,str_cropname)
            elif(treedepth >= 4):  #len(index.model().nodeFromIndex(index)) > 4):
                print("debug: It is an operation, name=", index.model().nodeFromIndex(index).name)                 
                print("debug: nesting=",self.nesting, "depth=", treedepth)
                currentnode = index.model().nodeFromIndex(index)  
                currentnodeparent = currentnode.parent.name #do we need this
                currentnodeparentindex = self.model().createIndex(1,0,currentnodeparent) 

                self.savecurrentnode = index.model().nodeFromIndex(index)
                self.savecurrentindex = currentnodeparentindex
                # Need to get operation id to update the right record.  To accomplish this I concatenated operation_id to operation_name
                op_id = currentnode.children[0][0].split('op_id=')[1]
                str_operationname = op_id+'_'+currentnode.name                           
                str_treatmentname = currentnode.parent.name
                str_experimentname = currentnode.parent.parent.name 
                str_cropname = currentnode.parent.parent.parent.name
                self.getOperation.emit(4,str_treatmentname,str_experimentname,str_cropname,str_operationname,index)
            else:
                print("debug:cropdata: getExperiment. emit 0")
                self.getExperiment.emit(0,'Blank','Blank')
              

    def currentFields(self):
        return self.model().asRecord(self.currentIndex())


    def make_connection_2_table(self,table_object):
         print("In make_connection_2_table")
         cstatus = table_object.sig2.connect(self.update_tree)
         cstatus2 = table_object.sig2t.connect(self.update_tree3)
         print("Out make_connection_2_table")
         return cstatus


    @pyqtSlot(int)
    def update_tree(self,intval):
        print("debug:cropdata.py: update_tree:intval=",intval)
        if intval ==2:
            print("debug: new entry either in experiment/treatment/operation")
            self.model().emitDataChanged()
            
        if intval ==3: # for delete experiment
            s_current = self.currentIndex()
            # preserve the parent link before the remove operation, type QModelIndex
            s_parent = self.currentIndex().parent() 
            print("CropData, row count before remove=",self.model().rowCount(self.currentIndex().parent()))
            print("CropData, row # to be removed=",self.currentIndex().row())     
            # what if the node to be removed has children and grandchildren? Do we need to remove them?? 
            if s_parent.isValid(): #agmip or crop
                row2del = self.currentIndex().row()                
                nnode_2delindex = self.model().index(row2del,0,s_parent)                             
                nnode_2del = self.model().nodeFromIndex(nnode_2delindex) #E, agmip
                for treatmentloop in range(len(nnode_2del.children)): # T iowa6
                    nnode_child= nnode_2del.children[0] #treatmentloop]
                    # row=0 because we are deleting from begining, therefore after delete operation next 
                    # row becomes the top row.
                    nnode_childindex = self.model().index(0,0,nnode_2delindex) 
                    for operationloop in range(len(nnode_child)): #O, Simulation Start etc
                        leaf_child= nnode_child[0] #operationloop]
                        print("Debug: leaf_child=",leaf_child)
                        # deleting the operation
                        delstatus_operation = self.model().removeRow(0,nnode_childindex) 
                    # deleting the treatment
                    delstatus_treatment = self.model().removeRow(0,nnode_childindex.parent()) 

            # this section works on empty experiment 
            # deleting the experiment     
            test1 = self.model().removeRow(self.currentIndex().row(),self.currentIndex().parent()) 
            self.model().layoutChanged.emit()
            self.model().emitDataChanged()    
 
            s_current = self.currentIndex()
            test_list = []

            while s_current.isValid():
                test_list.append(s_current.row())
                s_current = self.model().parent(s_current)
            
            self.model().beginResetModel()
            print("Inside update_tree, intval=1")
            self.model().load2(self.databasename, self.tablename,self.nesting,self.separator)
            self.model().endResetModel()
            self.model().layoutChanged.emit()
            self.model().emitDataChanged()
            
            tlen = len(test_list)
            n_parent = None
            nnode = self.model().nodeFromIndex(QModelIndex())
            for i in range(tlen): #len(test_list)):       
                nnode = nnode.child(test_list.pop()) #   nodeFromIndex(n_parent)
                print("i1=",i," child=",nnode.name)
            
            n_parent = self.model().createIndex(0,0,nnode)
            self.setCurrentIndex(n_parent)
            self.setExpanded(n_parent,True)

     
        ## works but have to reload the data        
        if intval ==1: # for add operation
            #need to work with parent name instead of parent index, because parent index will change 
            #after call to load()
            #after load, search for parent (by name). Get its index and call setExpanded(theindex, expand)
            s_current = self.currentIndex()
            test_list = []

            while s_current.isValid():
                test_list.append(s_current.row())
                s_current = self.model().parent(s_current)
            
            print("debug: new entry either in experiment/treatment/operation: intval=",intval)
            self.model().beginResetModel()
            print("Inside update_tree, intval=1")
            self.model().load2(self.databasename, self.tablename,self.nesting,self.separator)
            self.model().endResetModel()
            self.model().layoutChanged.emit()
            self.model().emitDataChanged()
            
            tlen = len(test_list)
            n_parent = None
            nnode = self.model().nodeFromIndex(QModelIndex())
            for i in range(tlen): #len(test_list)):       
                nnode = nnode.child(test_list.pop()) #   nodeFromIndex(n_parent)
                print("i1=",i," child=",nnode.name)
            
            n_parent = self.model().createIndex(0,0,nnode)
            self.setCurrentIndex(n_parent)
            self.setExpanded(n_parent,True)

        if intval ==6: 
            # because logic here destroy the data tree and rebuild from database, it will address the 
            # cases of add treatment, delete treatment. This should for all add or insert operations, as 
            # we first empty the tree and then filling it up from database capture the row for current 
            # item, current_item_forefathers, delete the entire tree and then reload it from the database
            # need to work with parent name instead of parent index, because parent index will change 
            # after call to load() after load, search for parent (by name). Get its index and 
            # call setExpanded(theindex, expand)
            s_current = self.currentIndex()
            test_list = []

            while s_current.isValid():
                test_list.append(s_current.row())            
                s_current = self.model().parent(s_current)

            s_rootindex = QModelIndex()
            s_root = self.model().root

            if len(s_root.children) >0: #root
                for croploop in range(len(s_root.children)):
                    crop_2delindex= self.model().index(0,0,s_rootindex)                             
                    crop_2del = self.model().nodeFromIndex(crop_2delindex) #corn

                    for experimentloop in range(len(crop_2del.children)):
                        exp_2delindex = self.model().index(0,0,crop_2delindex)                             
                        exp_2del = self.model().nodeFromIndex(exp_2delindex) #agmip 

                        for treatmentloop in range(len(exp_2del.children)): #  iowa6
                            treat_2del= exp_2del.children[0] #treatmentloop]
                            # row=0 because we are deleting from begining, therefore after delete 
                            # operation next row becomes the top row.                    
                            treat_2delindex = self.model().index(0,0,exp_2delindex) 
                            
                            for operationloop in range(len(treat_2del)):
                                leaf_child= treat_2del[0]
                                # deleting the operation                        
                                delstatus_operation = self.model().removeRow(0,treat_2delindex) 
                            # deleting the treatment
                            delstatus_treat = self.model().removeRow(0,exp_2delindex) 
                        # deleting the experiment
                        delstatus_exp = self.model().removeRow(0,crop_2delindex) 

                # why are we doing separetly.[it is crashing or not adding t1 in e2. For some reason 
                # treatment names have to be unique??
                for rootloop in range(len(s_root.children)):
                    delstatus_crop=s_root.children.pop(-1) #0)
                    print("debug: popped=",delstatus_crop)

            # check root, root children, roo_children.type
            self.model().beginResetModel()
            print("Inside update_tree, intval=6")
            self.model().load2(self.databasename, self.tablename,self.nesting,self.separator)
            self.model().endResetModel()
            self.model().layoutChanged.emit()
            self.model().emitDataChanged()
            
            tlen = len(test_list)
            n_parent = None
            nnode = self.model().nodeFromIndex(QModelIndex())
            tmp_str0=''
            for i in range(tlen): #len(test_list)):       
                nnode = nnode.child(test_list.pop()) #   nodeFromIndex(n_parent)                
                print("i2=",i," child=",nnode.name)
                tmp_str0 = tmp_str0 + nnode.name
                if i < tlen-1:
                    tmp_str0 = tmp_str0 + "->"
            
            n_parent = self.model().createIndex(0,0,nnode)
            
            self.setCurrentIndex(n_parent)
            self.setExpanded(n_parent,True)

        # because logic here destroy the data tree and rebuild from database, it will address the cases 
        # of add treatment, delete treatment. This should for all add or insert operations, as we first 
        # empty the tree and then filling it up from database capture the row# for current item, 
        # current_item_forefathers, delete the entire tree and then reload it from the database need to 
        # work with parent name instead of parent index, because parent index will change after call to load()
        # after load, search for parent (by name). Get its index and call setExpanded(theindex, expand)
        if intval ==66: 
            s_current = self.currentIndex()
            test_list = []

            while s_current.isValid():
                test_list.append(s_current.row())            
                s_current = self.model().parent(s_current)

            # begin delete
            s_rootindex = QModelIndex()
            s_root = self.model().root

            if len(s_root.children) >0: #root
                for croploop in range(len(s_root.children)):
                    crop_2delindex= self.model().index(0,0,s_rootindex)                             
                    crop_2del = self.model().nodeFromIndex(crop_2delindex) #corn

                    for experimentloop in range(len(crop_2del.children)):
                        exp_2delindex = self.model().index(0,0,crop_2delindex)                             
                        exp_2del = self.model().nodeFromIndex(exp_2delindex) #agmip 

                        for treatmentloop in range(len(exp_2del.children)): #  iowa6
                            treat_2del= exp_2del.children[0] #treatmentloop] 
                            # row=0 because we are deleting from begining, therefore after delete 
                            # operation next row becomes the top row.                           
                            treat_2delindex = self.model().index(0,0,exp_2delindex) 
                            
                            for operationloop in range(len(treat_2del)):
                                leaf_child= treat_2del[0]  
                                # deleting the operation                     
                                delstatus_operation = self.model().removeRow(0,treat_2delindex) 
                            # deleting the treatment
                            delstatus_treat = self.model().removeRow(0,exp_2delindex) 
                        delstatus_exp = self.model().removeRow(0,crop_2delindex) # deleting the experiment

                # why are we doing separetly.[it is crashing or not adding t1 in e2. For some reason 
                # treatment names have to be unique??
                for rootloop in range(len(s_root.children)):
                    delstatus_crop=s_root.children.pop(-1) #0)
                    print("debug: popped=",delstatus_crop)

            # check root, root children, roo_children.type
            self.model().beginResetModel()
            print("Inside update_tree, intval=66")
            self.model().load2(self.databasename, self.tablename,self.nesting,self.separator)
            self.model().endResetModel()
            self.model().layoutChanged.emit()
            self.model().emitDataChanged()
            
            tlen = len(test_list)
            n_parent = None
            nnode = self.model().nodeFromIndex(QModelIndex())
            tmp_str0=''
            for i in range(tlen): #len(test_list)):       
                nnode = nnode.child(test_list.pop()) #   nodeFromIndex(n_parent)                
                print("i3=",i," child=",nnode.name)
                tmp_str0 = tmp_str0 + nnode.name
                if i < tlen-1:
                    tmp_str0 = tmp_str0 + "->"
            
            n_parent = self.model().createIndex(0,0,nnode)
            
            self.setCurrentIndex(n_parent)
            self.setExpanded(n_parent,True)
            self.informUser.emit(0,tmp_str0)
  

    @pyqtSlot(int,str,str,str,str)
    def update_tree3(self,intval,experimentname,cropname,treatmentname,operationname):
        print("inside update_tree3: intval, experiment, crop names=",intval,experimentname,cropname)
        if(intval ==2):
            # find which row to expand
            t6 = None #QModelIndex() # initialize to root
            tmp2 = self.model().nodeFromIndex(QModelIndex())
            tmp3 = self.model().createIndex(1,0,tmp2)
            tmp4 = tmp2.childWithKey(cropname)
            if tmp4 is not None:
                for lloop1 in range(len(tmp4)):
                    if tmp4.children[lloop1][1].name == experimentname:
                        t6 = self.model().createIndex(1,0,tmp4.childAtRow(lloop1))
                
                if t6 is not None:
                    tmp5 = self.model().nodeFromIndex(self.model().createIndex(1,0,t6))
                    self.expand(t6)
                else:
                    self.expand(self.model().createIndex(1,0,tmp4))
            else:
                self.expand(tmp3)
            
            print("debug: experient name=", experimentname)
            print("debug: new entry either in experiment/treatment/operation")

        if intval ==4: # for insert experiment
            s_current = self.currentIndex() # this would be index of "Add New Experiment"
            # preserve the parent link before the remove operation. This would be corn crop
            s_parent = self.currentIndex().parent() 
            print("CropData, row count before remove=",self.model().rowCount(self.currentIndex().parent()))
            s_root = self.currentIndex().parent()             
            print("CropData, row count before insert=",self.model().rowCount(self.currentIndex().parent()))
            self.model().beginInsertRows(s_root,s_current.row(),s_current.row())              
            pnode = self.model().nodeFromIndex(s_root)     # this will give parent node, corn 
            # creating a new node with experiment name and add a subnode of "Add New Treatment"
            newbranch =BranchNode(experimentname)
            newbranch.insertChild(BranchNode("Add New Treatment"))
            # this should insert the new experiment node just before the "Add New Experiment"
            pnode.insertChildAtIndex(newbranch,s_current.row()) 
            self.model().endInsertRows()
            print("CropData, row count after insert=",self.model().rowCount(self.currentIndex().parent()))

            test_list = []
            while s_current.isValid():
                test_list.append(s_current.row())                
                s_current = self.model().parent(s_current)
                            
            self.model().layoutChanged.emit()
            self.model().emitDataChanged()    
            tlen = len(test_list)
            n_parent = None
            nnode = self.model().nodeFromIndex(QModelIndex())
            for i in range(tlen): #len(test_list)):       
                nnode = nnode.child(test_list.pop()) #   nodeFromIndex(n_parent)            
                print("i=",i," child=",nnode.name)
            
            n_parent = self.model().createIndex(0,0,nnode)
            self.setCurrentIndex(n_parent)
            self.setExpanded(n_parent,True)
    
        
    def dragEnterEvent(self, QDragEnterEvent):
        print("Inside dragenter, treewidget")
        return super().dragEnterEvent(QDragEnterEvent)


    def dropEvent(self, QDropEvent):
        print("Inside drop, treewidget")
        return super().dropEvent(QDropEvent)        