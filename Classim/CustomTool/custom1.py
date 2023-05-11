import bisect
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from contextlib import contextmanager
from TabbedDialog import *
from DatabaseSys.Databasesupport import *
from PyQt5.QtCore import Qt, QModelIndex, QVariant, QAbstractItemModel

KEY,NODE = range(2)

@contextmanager
def noSignals(obj):
    """ Context for blocking signals on a QObject"""
    obj.blockSignals(True)
    yield
    obj.blockSignals(False)


class BranchNode(object):
    def __init__(self,name,parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        

    def __lt__(self, other):
        if isinstance(other, BranchNode):
            return self.orderKey() < other.orderKey()
        return False


    def getname(self):
        return self.name


    def orderKey(self):
        return self.name


    def toString(self):
        return self.name


    def __len__(self):
        return len(self.children)


    def child(self,row):
        #return self.children[row]
        return self.children[row][NODE]


    def parent(self):
        return self.parent


    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)


    def childAtRow(self,row):
        if row < 0 or row >= len(self.children):
            print("stop here")           
        return self.children[row][NODE]


    def rowOfChild(self,child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1


    def childWithKey(self,key):
        if not self.children:
            return None
        i=bisect.bisect_left(self.children,(key,None))
        if i < 0 or i >=len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None


    def insertChild(self,child):
        child.parent = self
        ## do we need sorting
        #print("child len=",len(self.children)," child key = ",child.orderKey())
        self.children.insert(len(self.children),(child.orderKey(),child))


    def insertChildAtIndex(self,child,pos):
        child.parent = self
        ## do we need sorting
        #print("InsertChildAtIndex",pos)
        if 0<= pos <= len(self.children):
            self.children.insert(pos,(child.orderKey(),child))


    def hasLeaves(self):
        if not self.children:
            return False
        return isinstance(self.children[0], LeafNode)


    def remove_child_at_row(self,row):
        """
        Removes the child object from the children list 
        """
        #print("Remove node")
        if row <0 or row >= len(self.children):
            return False
        child = self.children.pop(row)        
        child[NODE].parent = None
        return True


    def removeChild(self,row):
        #print("Remove node new")
        if row <0 or row >= len(self.children):
            return False
        child = self.children.pop(row)
        child[NODE].parent = None        
        child = None
        return True


class LeafNode(object):
     def __init__(self,fields, parent=None):
         super(LeafNode,self).__init__()
         self.parent= parent
         self.fields = fields


     def orderKey(self):
         return u"\t".join(self.fields).lower()


     def toString(self, separator="\t"):
         return separator.join(self.fields)


     def __len__(self):
         return len(self.fields)


     def field(self,column):
         #print("debug: Indexerror, column=",column," len(self.fields)=",len(self.fields))
         assert 0 <= column <= len(self.fields)
         return self.fields[column]


     def asRecord(self):
         #print("asRecord:leaf")
         record = []
         branch = self.parent
         while branch is not None:
             record.insert(0,branch.toString())
             branch = branch.parent

         assert record and not record[0]
         #print("size of record=",len(record))
         record = record[1:]
         return record + self.fields


     def remove_child_at_row(self,row):
        """
        Removes the child object from the children list 
        """
        if row <0 or row >= len(self.fields):
            return False
        child = self.fields.pop(row)        
        return True


class TreeOfTableModel(QAbstractItemModel):
    #need data, database, tree branch and leaf
    def __init__(self,parent=None):
        super(TreeOfTableModel,self).__init__(parent)
        self.columns =0
        self.root = BranchNode("")
        self.headers = []
        
            
    # see at //doc.qt.io/qt-4.8/model-view-programming.html#using-drag-drop-with-item-views
    def supportedDropActions(self):
        """
         Allowing re-ordering of nodes
        """
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction


    #Models indicate to views which items can be dragged, and which will accept drops, by reimplementing the 
    #QAbstractItemModel::flags() function to provide suitable flags.
    def flags(self,index):
        """
         Returns whether or not the current item is selectable/editable/enabled.
         Probably here we can further fine tune to do just the nodes with leaves.
        """
        defaultFlags = QAbstractItemModel.flags(self,index)
        
        if not index.isValid():
            # works return QtCore.Qt.ItemIsEnabled | defaultFlags
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsDragEnabled | defaultFlags
        return QtCore.Qt.ItemIsEnabled |QtCore.Qt.ItemIsSelectable |QtCore.Qt.ItemIsDragEnabled| \
               QtCore.Qt.ItemIsDropEnabled | defaultFlags


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
          Sets the data
        """
        #print("Set Data Called")
        if value:
            item = index.internalPointer()
            item.set_value(value)            
            # set a emit signal

        return True


    #When items of data are exported from a model in a drag and drop operation, they are encoded into an appropriate
    #format corresponding to one or more MIME types. Models declare the MIME types that they can use to supply 
    #items by reimplementing the QAbstractItemModel::mimeTypes() function, returning a list of standard MIME types.
    def mimeTypes(self):
        """
         Accept only the internal drop type, plain text        
        """
        return ['text/plain']


    def dragMoveEvent(self, event):
        #print("Tree:dragMove event entered")
        if event.mimeData().hasFormat("application/x-ltreedata"):
            event.accept()
        else:
            event.ignore()


    def dragEnterEvent(self, event):
        #print("Tree:dragEnter event entered")
        if event.mimeData().hasFormat("application/x-ltreedata"):
            event.accept()
        else:
            event.ignore()


    def mimeData(self, index):
        """
         String wrap the index up as a list of rows and columns of each parent, grandparent and so on..
         Q1: are we starting from the lowest leaf (index[0]) and moving upwards toward root (theindex becomes invalid)?
         Q2: Or do we need to work only on the index which is dragged?

        """
        temp_str = ""
        temp_str1 = ""
        temp_str2 = ""
        theIndex = index[0]
        generation_count = 0
        while theIndex.isValid():
            generation_count= generation_count+1
            temp_str1 = theIndex.internalPointer().name
            if generation_count==1:
                temp_str2 = temp_str1
            else:
                temp_str2 = temp_str1 + "/" +temp_str2
                
            theIndex = self.parent(theIndex)
           
        if generation_count ==3:
            temp_str =temp_str2     
        mimeData = QtCore.QMimeData()
        mimeData.setText(temp_str)
        return mimeData


    def insertRow(self,row,parentIndex):
        parentNode = parentIndex
        if not parentIndex.isValid():
            #parent can be invalid when it is a root node (root parent returns an empty QModelIndex)
            parentNode = self.root  
            
        self.insertRows(row,1,parentNode)
        return True
        

    def insertRows(self,row,count, parentIndex):
        self.beginInsertRows(parentIndex,row,(row +(count-1)))
        parentItem = parentIndex.internalPointer().insertChildAtIndex(row)
        # should we add something like parentItem.insertChild()
        self.endInsertRows()
        return True
    
            
    def removeRow(self,row,parentIndex):
        parentNode = parentIndex
        if not parentIndex.isValid():
            #parent can be invalid when it is a root node (root parent returns an empty QModelIndex)
            parentNode = self.root
        self.removeRows(row,1,parentNode)
        return True


    def load2(self,databasename,tablename,nesting,separator,loader=2):
        assert nesting >0        
        self.nesting = nesting
        self.root = BranchNode("")
        exception=None
        ### reset but coalapse entire tree  #self.beginInsertRows(QModelIndex(),0,0)
        try:
            rlist = read_cropDB()
            if len(rlist) > 0:
                self.addCropExperiment(rlist,False,loader)
        except IOError:
            print("Exception happened here")


    def emitDataChanged(self):
        '''
        Test if it replot view without losing the current state of view
        '''
        self.dataChanged.emit(QtCore.QModelIndex(),QtCore.QModelIndex())

        
    def addCropExperiment(self,fields,callReset=True,loader=2):
        """
        This will call addExperiment, addtreatment, addoperation functions iteratively
        """
        #print("Inside addCropExperiment: laoder=",loader)        
        try:
            for i in range(len(fields)):
                root = self.root
                key = fields[i]
                branch = root.childWithKey(key)
                if branch is not None:
                    root = branch
                else:
                    branch = BranchNode(fields[i])                      
                    root.insertChild(branch)                    
                    root = branch
                    
                rlist = read_experiment(fields[i])                
                if len(rlist) >0:
                    self.addExperimentTreatment(rlist,fields[i],False,loader)
                    if loader==2:
                        branch = BranchNode("Add New Experiment")                        
                        root.insertChild(branch)                        
                else:
                    if loader==2:   # loader==2 case represents default build of management tree.
                        branch = BranchNode("Add New Experiment")                        
                        root.insertChild(branch)                        
                        self.columns = 1 # testing # works but crashes without any error                    
        except IOError:
            print("Exception happened, addCropExperiment")


    def addExperimentTreatment(self,therlist,thecropname,callReset=True,loader=2):
        """
        This method fills the Tree of TreeOfTableModel.
        1).First, it iterates the database table crop.experiment and add a NODE for each experiment in the database 
           table.
        2).Second, for each experiment id, it queries the TREATEMENT table and add that treatment entries as SUBNODE 
           under Experiment NODE
        3).Third, for each treament node/entry, it queries the operation table and add a sub-sub node under the 
           TREATMENT SUBNODE
        4).Fourth, is add sub-node "Add New Operation" underneath the operation subnodes. Clicking this, would open a 
           dialog/model to add the new operation to the current set of operation
        5).Fifth, it adds a new SUBNODE "Add New treatment" under the treatment branch. Clicking this would allow to
           draft new treatment via new diaog box.
        6).Sixth, it adds new NODE "Add New Experiment" under the experiment branch. Clicking this would allow to 
           draft a new entry for the experiment.

        Argument LOADER controls if "Add New Experiment or Add New Operation should be added to tree or not. If 
        loader=2, default, then they will be added to tree. "
        """      
        for i in range(len(therlist)):            
            key = thecropname
            root = self.root
            branch = None
            branch = root.childWithKey(key)
            if branch is not None:
                root = branch
                branch = BranchNode(therlist[i])
                root.insertChild(branch)
                root = branch
            else:
                branch = BranchNode(therlist[i])
                root.insertChild(branch)
                root = branch

            # now work on populating this new branch  
            new_branches = read_treatmentDB(key,root.name)    
            #print("new_branches = ", new_branches)
            theader5 = ["1","2","3","4","5","6","7","8","9"]
            ### adding here to see if it will enable the empty tree display
            self.columns = max(self.columns, len(theader5)) 
            assert branch is not None
            for k in range(len(new_branches)):
                branch = BranchNode(new_branches[k])
                new_leaves = read_operationsDB(thecropname,root.name,new_branches[k])

                if new_leaves is not None:
                    root.insertChild(branch)
                    for j in range(len(new_leaves)):                             
                        self.columns = max(self.columns, len(theader5))
                        branch.insertChild(BranchNode(new_leaves[j][0]))   
                        tmp_bra = branch.childAtRow(j)
                        tmp_header =[] 
                        op = str(new_leaves[j][0])
                        if op == "Tillage" and str(new_leaves[j][1]) == "":
                            tmp_header.append("No Tillage")
                        elif op == "Fertilizer":
                            fertInfo = readOpDetails(str(new_leaves[j][2]),op)
                            tmp_header.append(fertInfo[0][3])
                        else:
                            tmp_header.append("Date: "+str(new_leaves[j][1]))
                        tmp_header.append("op_id="+str(new_leaves[j][2]))

                        tmp_bra.insertChild(LeafNode(tmp_header,tmp_bra))                     
                    if loader==2:
                        branch.insertChild(BranchNode("Add New Operation"))
            if loader==2:
                branch = BranchNode("Add New Treatment")
                root.insertChild(branch)
            if callReset:
                self.reset()
             
  
    def asRecord(self,index):
        leaf = self.nodeFromIndex(index)
        #print("asRecord:Model")
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asRecord()
        return []


    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root


    def rowCount(self,parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)


    def columnCount(self,parent):
        return self.columns


    def childCount(self): #new
        return len(self.children)


    def child(self,row): #new
        return self.children[row]


    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop| Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        node = self.nodeFromIndex(index)        
        assert node is not None
        if isinstance(node, BranchNode):
            return (QVariant(node.toString())) if index.column() ==0 else QVariant(str(""))
        return QVariant(node.field(index.column()))
  
      
    def headerData(self,section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return (QVariant(self.headers[section])) if section < len(self.headers) else QVariant()
        return QVariant()

    def index(self,row,column, parent):
        if self.hasIndex(row,column,parent):
            #assert self.root
            branch = self.nodeFromIndex(parent)
            if branch:
                return self.createIndex(row,column, branch.childAtRow(row))
        else:
            return QModelIndex()

        
    def parent(self, child):
        # old 
        node = self.nodeFromIndex(child)  
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent == self.root:
            return QModelIndex()
        if parent is None:
            return QModelIndex()
        if type(parent) != BranchNode:
            return QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex() 
        row = grandparent.rowOfChild(parent)
        return self.createIndex(row, 0, parent)
        

    def getDepth(self, index):
        #root has rdepth value of 1
        rdepth = 1
        tnode = self.nodeFromIndex(index).parent
        ## works in some cases while tnode is not self.root: # None:
        while tnode.parent is not None:
            rdepth = rdepth+1
            tnode = tnode.parent             
        return rdepth