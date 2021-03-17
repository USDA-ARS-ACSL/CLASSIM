import sqlite3
import re
import os
import pandas as pd

from PyQt5 import QtSql, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime as dt
from datetime import datetime, timedelta
from CustomTool.UI import *

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
dbDir = os.path.join(gparent_dir,'crop_int')
if not os.path.exists(dbDir):
    os.makedirs(dbDir)


def insert_update_sitedetails(record_tuple,buttontext):
    '''
 Insert or update a record on sitedetails table
 Input:
    record_tuple=(sitename, latitude, longitude, altitude)
    buttontext is Save or Update
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    else:        
        record_tuple2= record_tuple[1:]
        record_tuple3= (record_tuple[0],)
        record_tuple4= record_tuple[1:] + (record_tuple[0],)
        qstatus=False
        if buttontext.find('Save')==0:
            c1 = c.execute("SELECT sitename FROM sitedetails where sitename = ?",record_tuple3 )  
            c1_row = c1.fetchone() #c1.fetchall()
            if c1_row == None:
                qstatus = c.execute("insert into sitedetails(sitename, rlat, rlon, altitude) values (?,?,?,?)",record_tuple)             
                conn.commit()        
                conn.close()
                return True
            else:                     
                conn.close()
                return False
        else: 
            qstatus = c.execute("update sitedetails set rlat=?, rlon=?, altitude=? where sitename=?",record_tuple4)       
            conn.commit() 
            conn.close()
            return True
                    
        return False


def delete_sitedetails(record_tuple):
    '''
  Delete a record from sitedetails table
  Input:
    record_tuple = (sitename)
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    else:        
        c.execute("delete from sitedetails where sitename = ?",record_tuple)  
        conn.commit()
        conn.close()
        return True


def extract_sitedetails(site_string):
    '''
  Retrieve site information from sitedetails table
  Input:
    site_string = sitename
  Output:
    tuple = (site id, latitude, longitude, altitude)
    '''

    result1 =0
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    else:
        #print("site_string=",site_string)
        c1 = c.execute("select id,rlat,rlon,altitude from sitedetails where sitename = '%s';"%(site_string)) 
        c1_row = c1.fetchall()
        if c1_row != None:
            for c1_row_record in c1_row:
                result1 = (c1_row_record[0],c1_row_record[1],c1_row_record[2],c1_row_record[3])
        conn.close()    
        
    return result1


def read_cropDB():
    '''
  List all crops in the database
  Output: 
    Tuple with crop name
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    else:
        #need auto increment ID, nonnull
        c1 = c.execute("SELECT id, cropname FROM crops")  
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                id = c1rowrecord[0]
                name = c1rowrecord[1]
                rlist.append(name)
              
        conn.close()
        return rlist


def read_cultivar_DB(cropname):
    '''
  Extracts hybridname list from cultivar_corn based on the cropname. First get the id from crops table based on 
  crop name then use this information  to link with cultivar_corn table.
  Input:
    cropname
  Output:
    tuple with hybridname list for specific crop
    '''
    rlist =[] # list   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    if len(cropname) > 0:     
        if(cropname=="corn"):   
            c1=c.execute("SELECT hybridname FROM cultivar_corn")   
        else:     
            c1=c.execute("SELECT hybridname FROM cultivar_potato")   

        c1_rows = c1.fetchall()
        for c1_row in c1_rows:        
            rlist.append(c1_row[0])
            
    conn.close()
    return rlist


def read_cultivar_DB_detailed(hybridname,cropname):
    '''
  Extracts the link id from cropname and  croptable. With linkid, we can query cultivar_corn table to get details of the crop variety.
  This one gives lot more parameters
  Input:
    hybridname
    cropname
  Output:
    tuple with complete information about a particular hybridname
    '''
    rlist =() # tuple   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    if len(cropname) > 0:   
        if(cropname == "corn"):
            c1=c.execute("SELECT juvenileleaves, DaylengthSensitive, Rmax_LTAR, Rmax_LTIR, PhyllFrmTassel,StayGreen,LM_min,RRRM,RRRY,RVRL,ALPM,\
                          ALPY,RTWL,RTMinWTperArea,EPSI,IUPW,CourMax,Diffx, Diffz,Velz,lsink,Rroot,Constl_M,ConstK_M,Cmin0_M,ConstI_Y,ConstK_Y,\
                          Cmin0_Y,hybridname FROM cultivar_corn where hybridname = ?",[hybridname])      
        if(cropname == "potato"):       
            c1=c.execute("SELECT A1, A6, A8, A9, A10, G1, G2, G3, G4, RRRM, RRRY, RVRL, ALPM, ALPY, RTWL, RTMinWTperArea, EPSI, IUPW, CourMax,\
                          Diffx, Diffz, Velz, lsink, Rroot, Constl_M, ConstK_M, Cmin0_M, ConstI_Y, ConstK_Y, Cmin0_Y FROM cultivar_potato where \
                          hybridname = ?",[hybridname])      
        c1_row = c1.fetchone()
        if c1_row != None:        
            rlist=c1_row
    conn.close()
    return rlist


def read_experimentDB():
    '''
  Extracts list of experiments.
  Output:
    tuple with experiment names
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    else:
        #need auto increment ID, nonnull
        c1 = c.execute("SELECT exid, name FROM experiment")  
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                id = c1rowrecord[0]
                name = c1rowrecord[1]
                rlist.append(name) 
        conn.close()
        return rlist


def getExpTreatByCrop(cropname):
    '''
  Extracts experiment based on crop name.
  Input:
    cropname
  Output:
    tuple with experiment names
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    else:
        #need auto increment ID, nonnull
        c1 = c.execute("select e.name || '/' || t.name as expTreat from experiment e, treatment t where t_exid=exid and e.crop = ? order by e.name, t.name",[cropname])  
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord[0])
    conn.close()
    return rlist


def read_experimentDB_id(cropname, experimentname):
    '''
  Extracts experiment id based on crop and treatment name.
  Input:
    cropname
    treatmentname
  Output:
    experiment id
    '''
    rlist =None # list   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    
    record_tuple =(cropname,experimentname)
    if len(cropname) > 0 and len(experimentname) > 0:
        c2 = c.execute("SELECT exid FROM experiment where crop = ? and name = ?",record_tuple)
        c2_row = c2.fetchone()
        if c2_row != None:
            rlist = c2_row[0]

    conn.close()    
    return rlist


def read_operationsDB_id(o_t_exid):
    '''
  Get all operations using treatment id.
  Input:
    o_t_exid = treatment id
  Output:
    tuple listing all operations with full detail.
    '''
    rlist =[] # list   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    
    if isinstance(o_t_exid,int):
        print("Debug: o_t_exid=",o_t_exid)
        c2 = c.execute("SELECT name,depth,quantity, odate,pop,autoirrigation,rowangle,xseed,yseed,cec,eomult,rowSpacing,cultivar,\
                        fDepth, seedpieceMass FROM operations where o_t_exid = ?", (o_t_exid,))
        c2_row = c2.fetchall()
        if c2_row != None:
            for c2_row_record in c2_row:
                rlist.append(c2_row_record)

    conn.close()    
    return rlist


def getPlantDensity(o_t_exid):
    '''
  Get all operations using treatment id.
  Input:
    o_t_exid = treatment id
  Output:
    plant density
    '''
    rlist = ""  
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    
    if isinstance(o_t_exid,int):
        print("Debug: o_t_exid=",o_t_exid)
        c2 = c.execute("SELECT pop FROM operations where name = 'Initial Field Values' and o_t_exid = ?", (o_t_exid,))
        c2_row = c2.fetchone()
        if c2_row != None:            
            rlist= c2_row[0]

    conn.close()    
    return rlist


def read_treatmentDB_id(exid,treatmentname):
    '''
  Returns treatment id based on treatment name and experiment id.
  Input:
    exid = experiment id
    treatmentname
  Output:
    tid = treatment id
    '''
    rlist =None # list   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    treatmentname2 = treatmentname+'%'
    record_tuple =(exid,treatmentname2)
    if isinstance(exid,int) and isinstance(treatmentname2,str):
        c2 = c.execute("SELECT tid FROM treatment where t_exid = ? and name like ?",record_tuple)
        c2_row = c2.fetchone()
        if c2_row != None:            
            rlist= c2_row[0]
    conn.close()    
    return rlist


def check_and_update_experimentDB(item,cropname):
    '''
  Check if there is an experiment with name "item" for a pasrticular crop name. Insert record if this combination is 
  new, otherwise returns false.
  Input:
    item = experiment name
    cropname
  Output:
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    if len(item) > 0:
        c1 = c.execute("SELECT exid, name FROM experiment where name = '%s' and crop = '%s';" %(''.join(item),''.join(cropname)))  
        c1_row = c1.fetchone() #c1.fetchall()
        if c1_row == None:
            c2 = c.execute("insert into experiment (name,crop) values ('%s','%s');" %(''.join(item),''.join(cropname)))
            conn.commit()
        else:  # means data already exist
            return False 
    conn.close()  
    return True


def check_and_delete_soilDB(soilname):
    '''
  Delete records on tables gridratio, soil_long and soil based on soil name.
  Input:
    soilname
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    id = 0
    c.execute("Select id, o_gridratio_id FROM soil where soilname =?",[soilname])
    for op in c:
        id = int(op["id"])
        gridratio_id = int(op["o_gridratio_id"])

    if id > 0:
        delete_flag = messageUserDelete("Are you sure you want to delete this record?")
        if delete_flag:
            print("delete soil",soilname)
            c.execute("DELETE FROM gridratio where gridratio_id = ?",(gridratio_id,))
            c.execute("DELETE FROM soil_long where o_sid = ?",(id,))
            c.execute("DELETE FROM soil where soilname =?",[soilname])
            conn.commit()

    conn.close()          


def check_and_delete_experimentDB(experimentname,cropname):
    '''
  Check if the item exist in experiment table, then do a iterative deletion of treatments & operations and then delete this experiment
  Input:
    experimentname
    cropname
  Output:
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    print("experiment=",experimentname)
    print("crop=",cropname)
    record_tuple = (experimentname,cropname)     
    if len(experimentname) > 0:
        c1 = c.execute("SELECT exid, name FROM experiment where name = '%s' and crop = '%s';" %(''.join(experimentname),''.join(cropname)))  
        c1_row = c1.fetchone() #c1.fetchall()
        if c1_row != None:
            # get treatments defined under this experiment
            rtuple = (c1_row[0],)
            g_tid = c.execute("SELECT tid, name FROM treatment where t_exid=?", rtuple)  # getting treatment ids
            g_tid_rows = g_tid.fetchall()
            for g_tid_row in g_tid_rows:
                rtuple3 = (g_tid_row[0],)
                g_oid = c.execute("DELETE FROM OPERATIONS where o_t_exid=?",rtuple3)
                g_oid = c.execute("DELETE FROM treatment where tid=?",rtuple3)
            
            c2 = c.execute("DELETE FROM experiment where name=? AND crop=?",record_tuple)
            conn.commit()

    conn.close()  
    return True


def check_and_delete_treatmentDB(treatmentname, experimentname ,cropname):
    '''
  Check if the item exist in experiment table, then do a iterative deletion of treatments & operations and then delete this experiment
  Input:
    treatmentname
    experimentname
    cropname
  Output:
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    c1 = c.execute("SELECT exid, name FROM experiment where name = '%s' and crop = '%s';" %(''.join(experimentname),''.join(cropname)))  
    c1_row = c1.fetchone() #c1.fetchall()
    if c1_row != None:
        # get treatments defined under this experiment
        rtuple = (c1_row[0],)
        rtuple_str = str(c1_row[0])
        g_tid = c.execute("SELECT tid, name FROM treatment where t_exid= '%s' and name ='%s';" %(''.join(rtuple_str),''.join(treatmentname)))  # getting treatment ids
        g_tid_rows = g_tid.fetchall()
        for g_tid_row in g_tid_rows:
            rtuple3 = (g_tid_row[0],)
            g_oid = c.execute("DELETE FROM OPERATIONS where o_t_exid=?",rtuple3)
            g_oid = c.execute("DELETE FROM treatment where tid=?",rtuple3)          
        conn.commit()

    conn.close() 
    return True


def update_pastrunsDB(site,managementname,weather,stationtype,soilname,startyear, endyear,waterstress,nitrostress,lcomment):     
    '''
  Insert a new record on pastrun table and returns the assigned id.
  Input:
    site
    managementname
    weather
    stationtype
    soilname
    startyear
    endyear
    waterstress
    nitrostress
    lcomment
  Output:
    pastrun id
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    if lcomment != None:
        ocomment = lcomment
    else:
        ocomment = "blank"

    odate =  datetime.now()
    record_tuple =(site,managementname,weather,soilname,stationtype,startyear,endyear,odate,waterstress,nitrostress,ocomment)

    qstatus = c.execute("insert into pastruns (site, treatment, weather, soil, stationtype, startyear, endyear, odate, waterstress, nitrostress, comment) \
                        values (?,?,?,?,?,?,?,?,?,?,?)", record_tuple)    
    conn.commit()
    # retrieve the ID
    c1row = c.execute("select id from pastruns where site =? AND treatment = ? AND weather = ? AND soil = ? AND stationtype = ? \
                      AND startyear = ? AND endyear = ? AND odate = ? AND waterstress = ? AND nitrostress = ? AND comment = ?",record_tuple)    
    c1_row = c1row.fetchone()
    if c1_row != None:
        rlist=list(c1_row)
    conn.close()
    return rlist


def delete_pastrunsDB(id):     
    '''
  Insert a new record on pastrun table and returns the assigned id.
  Input:
    id
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    query = "delete from pastruns where id=" + id
    qstatus = c.execute(query)    
    conn.commit()
    conn.close()
    return True


def extract_pastrunsidDB():    
    '''
  Returns a tuple with all pastruns in the database.
  Input:
  Output:
    Tuple with complete pastruns information.
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    c1 = c.execute('select p.id, p.site, p.treatment, p.stationtype, p.weather, p.soil, p.startyear from pastruns as p group by \
                   p.id order by p.id desc')      
    c1_rows = c1.fetchall()
    for c1_row in c1_rows:
        rlist.append(c1_row)
    conn.close()
    return rlist


def check_and_update_treatmentDB(treatmentname, experimentname, cropname):
    '''
  Check if treatment already exist in the database and if it is new insert the new treatment and create the default operations
  related with this treatment.  The default operations are Simulation Start, Sowing, Harvest ans Simulation End.
  Input:
    treatmentname
    experimentname
    cropname
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    record_tuple =(treatmentname,experimentname,cropname)
    if len(experimentname) > 0:        
        c1=c.execute("SELECT tid FROM treatment where name = ? and t_exid = (select exid from experiment where name =? and crop = ?)",record_tuple)
        c1_row = c1.fetchone()
        if c1_row == None:
            c2 = c.execute("SELECT exid, name FROM experiment where name = ? and crop = ?",record_tuple[1:])
            c2_row = c2.fetchone()
            if c2_row !=None:
                t_exid = c2_row[0] #str(query2.value(0))
                #insert
                record_tuple = (t_exid,treatmentname)
                qstatus = c.execute("insert into treatment (t_exid, name) values (?,?)",record_tuple) # auto increment of tid
                conn.commit()
                # here we insert default operations of (Simulation Start and sowing). Read these 3 operations from 
                # default_operation table and insert them.
                # Populate Simulation Start and Sowing with today date
                now = datetime.now()
                today_date = now.strftime("%m/%d/%Y")
                yesterday_date = (now - timedelta(1)).strftime('%m/%d/%Y')
                in5days_date = (now + timedelta(5)).strftime('%m/%d/%Y')
                in7days_date = (now + timedelta(7)).strftime('%m/%d/%Y')
                in60days_date = (now + timedelta(60)).strftime('%m/%d/%Y')
                in65days_date = (now + timedelta(65)).strftime('%m/%d/%Y')

                op_id = -10 # This indicates that the record is new
                # This flag indicates that record is new
                OperationName = 'Simulation Start'
                operation_record = read_defaultOperationNameDB(OperationName)
                operation_record[6] = yesterday_date
                print(operation_record)
                check_and_update_operationDB(op_id, treatmentname, experimentname, cropname, operation_record)

                OperationName = 'Initial Field Values'
                operation_record = read_defaultOperationNameDB(OperationName)
                operation_record[6] = ""
                print(operation_record)
                check_and_update_operationDB(op_id, treatmentname, experimentname, cropname, operation_record)
                
                OperationName = 'Sowing'
                operation_record = read_defaultOperationNameDB(OperationName)
                operation_record[6] = in7days_date
                print(operation_record)
                check_and_update_operationDB(op_id, treatmentname, experimentname, cropname, operation_record)

                OperationName = 'Harvest'
                operation_record = read_defaultOperationNameDB(OperationName)
                operation_record[6] = in60days_date
                print(operation_record)
                check_and_update_operationDB(op_id, treatmentname, experimentname, cropname, operation_record)

                OperationName = 'Simulation End'
                operation_record = read_defaultOperationNameDB(OperationName)
                operation_record[6] = in65days_date
                print(operation_record)
                check_and_update_operationDB(op_id, treatmentname, experimentname, cropname, operation_record)

                if(cropname == "potato"):
                    OperationName = 'Emergence'
                    operation_record = read_defaultOperationNameDB(OperationName)
                    operation_record[6] = in5days_date
                    print(operation_record)
                    check_and_update_operationDB(op_id, treatmentname, experimentname, cropname, operation_record)

                conn.commit()
                conn.close()
                return True
        else: # data exist, so not inserting
            return False
    db.close()
    return False


def check_and_delete_operationDB(op_id):
    '''
  Deletes the selected entry from the operation tables.
  Input:
    op_id = operation id
  Output:
    '''
    rlist =[] # list
   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    record_tuple = op_id,
    #chk_str = "Delete FROM operations where id=?",record_tuple
    #print("debug: operation deletion:",chk_str)
    qstatus = c.execute("Delete FROM operations where id=?",record_tuple)
   
    conn.commit()
    conn.close()
    return True


def check_and_update_operationDB(op_id,treatmentname, experimentname, cropname, operation_record):
    '''
  Check if operation exist, if it exist the record is updated otherwise a new record is inserted into 
  operations table.
  Input:
    op_id = operation id
    treatmentname 
    experimentname
    cropname
    operation_record
  Ouput:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    op_id = int(op_id)
    # If op_id=-10, it means it is a new operation record so we need to find treatment id and experiment id
    if len(treatmentname) > 0:        
        record_tuple =(treatmentname,experimentname,cropname)
        c1=c.execute("SELECT tid FROM treatment where name = ? and t_exid = (select exid from experiment where name =? and crop = ?)",record_tuple)
        c1_row = c1.fetchone()
        # tables experiment & treatment are expected to have some value for tid and t_exid.
        if c1_row !=None:
            o_t_exid = c1_row[0]
        #insert
        record_tuple0 = (o_t_exid,)
        temp_tuple = tuple(operation_record)
        record_tuple = record_tuple0 + temp_tuple
        print("rec_tuple=",temp_tuple)

        # Need to do date validation before inserting or updating a operation for "Fertilizer-N" and "Simulation End"
        if(temp_tuple[0] == "Simulation End" or temp_tuple[0] == "Fertilizer-N"):
            validate_date(o_t_exid,temp_tuple[0],temp_tuple[6])

        readlist = read_defaultOperationsDB()        
        for record in sorted(readlist):
            # Test only for the operation we are trying to insert
            if(record[1] == temp_tuple[0]):
                print("op_id = ", op_id)
                if(op_id != -10):
                    record_tuple2 = record_tuple + (op_id,)
                    #call update
                    print("update ",record[1])
                    print("record tuple=",record_tuple2)
                    qstatus = c.execute("update operations set o_t_exid =?, name=?, depth_flag=?, quantity_flag=?, date_flag=?, depth=?, quantity=?, \
                                         odate=?, comment=?, cultivarflag=?, pop=?, autoirrigation=?, rowangle=?, xseed=?, yseed=?, cec=?, eomult=?, \
                                         rowSpacing=?, cultivar=?, fDepth=?, seedpieceMass=? where id =? ",record_tuple2)
                else:
                    print("record tuple insert =",record_tuple)
                    qstatus = c.execute("insert into operations (o_t_exid, name, depth_flag,quantity_flag, date_flag, depth, quantity, odate, \
                                         comment, cultivarflag, pop, autoirrigation, rowangle, xseed, yseed, cec, eomult, rowSpacing, cultivar, \
                                         fDepth, seedpieceMass) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",record_tuple)
                conn.commit()
                conn.close()
                return True
    return False


def validate_date(o_t_exid,op_name,date):
    '''
  Validate date for a specific operation and send an error message to the user in case a problem is found. 
  Input:
    o_t_exid
    op_name
    date
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()   
    if not c:
        print("database not open")
        return False

    err_string = ""
    date = dt.strptime(date,"%m/%d/%Y")
    print("Date: ",date)
    
    # Check if there is any operation for date_flag=1 for a particular experiment/treatment
    search_operation = (o_t_exid,)
    c.execute("SELECT name, odate, DATE(year||'-'||month||'-'||day) as dt_frmtd FROM (SELECT *, CASE WHEN LENGTH(substr(odate, 1, \
               instr(odate,'/')-1)) = 2 THEN substr(odate, 1, instr(odate,'/')-1) ELSE '0'|| substr(odate, 1, instr(odate,'/')-1) END as month, \
               CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1)) = 2 THEN \
               substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1) ELSE '0'|| \
               substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, instr(odate,'/')+1),'/')-1) END AS day, CASE WHEN \
               LENGTH(substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, instr(odate,'/')+1),'/')+1)) = 4 THEN \
               substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, instr(odate,'/')+1),'/')+1) END AS year FROM operations) where \
               date_flag=1 and o_t_exid=? order by dt_frmtd", search_operation)

    for op in c:
        op_date = dt.strptime(op["odate"],"%m/%d/%Y")
        op_date_string = op_date.strftime("%b %d, %Y")
        print("Op Date: ",op_date)
        if(op["name"] == "Simulation Start"):
            if(date <= op_date):
                err_string = "Date should be greater then Simulation Start date (%s)." % str(op_date_string)
        elif(op["name"] == "Sowing"):
            if(op_name == "Harvest" or op_name == "Simulation End"):
                if(date <= op_date):
                    err_string += "Date should be greater then sowing date (%s)." % str(op_date_string)
        elif(op["name"] == "Harvest"):
            if(op_name == "Simulation End"):
                if(date <= op_date):
                    err_string += "Date should be greater then harvest date (%s)." % str(op_date_string)
        elif(op["name"] == "Simulation End"):
            if(op_name != "Simulation End"):
                if(date >= op_date):
                    err_string += "Date should be less then Simulation End date (%s)." % str(op_date_string)
    conn.close()
    if(err_string != ""):
        messageUser(err_string)
    return True


def getme_date_of_last_operationDB(treatmentname, experimentname ,cropname):
    '''
  It will extract operation dates for a particular treatment under given experiment and given crop
  Input:
    treatmentname
    experimentname
    cropname
  Output:
    '''
    rlist =[] # list
   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    search_str0 = treatmentname     
    search_str1 = experimentname 
    search_str2 = cropname     
    record_tuple =(search_str0,search_str1,search_str2)
    if len(search_str1) > 0:        
        c1=c.execute("SELECT tid, t_exid FROM treatment where name = ? and t_exid = ( select exid from experiment where name =? \
                      and crop = ?)",record_tuple)
        c1_row = c1.fetchone()
        # tables experiment & treatment are expected to have some value for tid and t_exid.
        if c1_row !=None:
            o_t_exid = c1_row[0]
            search_record_tuple = (o_t_exid,)                        
            c2=c.execute("SELECT odate, max(strftime('%s','now') -strftime(odate)) FROM operations where odate!='' and o_t_exid=?",search_record_tuple)
            c2_row = c2.fetchone()
            rlist.append(c2_row[0]) 
            conn.close()
            return rlist
 
    return False


def read_operation_timeDB2(operationname, treatmentname, experimentname ,cropname):
    '''
  Checks if the operations exist, then extract the time info based on operation, treatment, experiment and
  crop name.
  Input: 
    treatmentname
    experimentname
    cropname
    operationname.
  Output: 
    operationname date info
    '''
    rtuple =() 
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    record_tuple =(treatmentname,experimentname,cropname)
    check_str = re.sub(' ','',operationname)
    if len(experimentname) > 0 and len(check_str) > 0:        
        c1=c.execute("SELECT tid, t_exid FROM treatment where name = ? and t_exid = ( select exid from experiment where name =? \
                      and crop = ?)",record_tuple)
        c1_row = c1.fetchone()
        # tables experiment & treatment are expected to have some value for tid and t_exid.
        if c1_row !=None:
            o_t_exid = c1_row[0]
            #search and extract            
            record_tuple = (o_t_exid, operationname)            
            c2 = c.execute("SELECT odate, DATE(year||'-'||month||'-'||day) as dt_frmtd FROM (SELECT *, CASE WHEN LENGTH(substr(odate, 1, \
                            instr(odate,'/')-1)) = 2 THEN substr(odate, 1, instr(odate,'/')-1) ELSE '0'|| substr(odate, 1, instr(odate,'/')-1) \
                            END as month, CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, \
                            instr(odate,'/')+1),'/')-1)) = 2 THEN substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, \
                            instr(odate,'/')+1),'/')-1) ELSE '0'|| substr(substr(odate, instr(odate,'/')+1), 1, instr(substr(odate, \
                            instr(odate,'/')+1),'/')-1) END AS day, CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), \
                            instr(substr(odate, instr(odate,'/')+1),'/')+1)) = 4 THEN substr(substr(odate, instr(odate,'/')+1), \
                            instr(substr(odate, instr(odate,'/')+1),'/')+1) END AS year FROM operations) where o_t_exid = ? and name = ? \
                            order by dt_frmtd", record_tuple)
            c2_row = c2.fetchone()
            if c2_row != None:
                rtuple = c2_row[0]

    conn.close()
    return rtuple


def read_operation_valuesDB2(operationid):
    '''
  Extract operation info based on operation id
  Input: 
    treatmentname
    experimentname
    cropname
    operationname
  Output: 
    tuple with operation info
    '''
    rtuple =() 
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    #search and extract            
    record_tuple = operationid,            
    c1 = c.execute("SELECT id, name, depth_flag, quantity_flag, date_flag, depth, quantity, odate, comment, cultivarflag, pop, autoirrigation, rowangle, xseed, \
                    yseed, cec, eomult, rowSpacing, cultivar, fDepth, seedpieceMass from operations where id = ?",record_tuple)
    c1_row = c1.fetchone()
    if c1_row != None:
        rtuple = c1_row

    conn.close()
    return rtuple


def read_treatmentDB(item):
    '''
  Returns treatment name based on experiment name.
  Input:
    item = experiment name
  Output:
    return treatment name
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    search_str = item #str(item.text())    
    if len(item) > 0:    
        c1 = c.execute("SELECT name FROM treatment where t_exid = (select exid from experiment where name ='%s');"%(item))    
        c1_row = c1.fetchall()
        if c1_row != None:
            for c1_row_record in c1_row:
                rlist.append(c1_row_record[0])
        conn.close()
        
    return rlist


def read_operationsDB(eitem,titem):
    '''
  Returns all operations in ascending order by date based on experiment id and treatment id.
  Input:
    eitem = experiment id
    titem = treatment id
  Output:
    Tuple with complete operation information sorted by date in ascending order
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
   
    if len(eitem) > 0:
        c1 = c.execute("SELECT name, depth_flag, quantity_flag, date_flag, depth, quantity, odate, cultivarflag, pop, autoirrigation, \
                       rowangle, xseed, yseed, cec, eomult, rowSpacing, cultivar, id, fDepth, DATE(year||'-'||month||'-'||day) as dt_frmtd \
                       FROM (SELECT *, CASE WHEN LENGTH(substr(odate, 1, instr(odate,'/')-1)) = 2 THEN substr(odate, 1, instr(odate,'/')-1) \
                       ELSE '0'|| substr(odate, 1, instr(odate,'/')-1) END as month, CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), 1, \
                       instr(substr(odate, instr(odate,'/')+1),'/')-1)) = 2 THEN substr(substr(odate, instr(odate,'/')+1), 1, \
                       instr(substr(odate, instr(odate,'/')+1),'/')-1) ELSE '0'|| substr(substr(odate, instr(odate,'/')+1), 1, \
                       instr(substr(odate, instr(odate,'/')+1),'/')-1) END AS day, CASE WHEN LENGTH(substr(substr(odate, instr(odate,'/')+1), \
                       instr(substr(odate, instr(odate,'/')+1),'/')+1)) = 4 THEN substr(substr(odate, instr(odate,'/')+1), instr(substr(odate, \
                       instr(odate,'/')+1),'/')+1) END AS year FROM operations) where o_t_exid = (select tid from treatment where name ='%s' AND \
                       t_exid =(select exid from experiment where name ='%s')) order by dt_frmtd"%(titem,eitem))            
        c1_row = c1.fetchall()
        if c1_row != None:
            for c1_row_record in c1_row:
                tmp_list = [c1_row_record[0],c1_row_record[1],c1_row_record[2],c1_row_record[3],c1_row_record[4],c1_row_record[5],\
                            c1_row_record[6],c1_row_record[7],c1_row_record[8],c1_row_record[9],c1_row_record[10],c1_row_record[11],\
                            c1_row_record[12],c1_row_record[13],c1_row_record[14],c1_row_record[15],c1_row_record[16],c1_row_record[17],\
                            c1_row_record[18]]
                rlist.append(tmp_list)
    conn.close()
    return rlist


def read_FaqDB(tabname):
    '''
  Returns FAQ information based on tabname
  Input:
    tabname
  Output:
    Tuple with FAQ information for a particular tab.
    '''
    rlist =[]
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
   
    if tabname == None:
        c1= c.execute("SELECT id, tabname, question, answer FROM Faq")            
    else:
        if(tabname=="cultivar"):
            tabname = tabname + "%"
        record_tuple = (tabname,)
        c1= c.execute("SELECT id, tabname, question, answer FROM Faq where tabname='general' or tabname like ?",record_tuple)            

    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:                
            rlist.append(c1_row_record)
    
    conn.close()
    return rlist

    
def read_sitedetailsDB():
    '''
  Returns list with site names.
  Input:
  Output:
    Tuple with sitenames list.
    '''
    rlist =[]
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False   
       
    c1= c.execute("SELECT id, sitename FROM sitedetails order by sitename")            
    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:                
            rlist.append(c1_row_record[1])
    conn.close()
    return rlist


def read_defaultOperationsDB():
    '''
  Returns tuple with a list of default operations with default values
  Input:
  Output:
    Tuple with default operations with default values
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
     
    c1= c.execute("SELECT name, depth_flag, quantity_flag, date_flag, depth, quantity, odate, comment, cultivarflag, \
                   pop, autoirrigation, rowangle, xseed, yseed, cec, eomult, rowSpacing, cultivarname, fDepth, \
                   seedpieceMass FROM defaultoperations")            
    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:                
            rlist.append([-10,c1_row_record[0],c1_row_record[1],c1_row_record[2],c1_row_record[3],c1_row_record[4],\
                          c1_row_record[5],c1_row_record[6],c1_row_record[7],c1_row_record[8],c1_row_record[9],\
                          c1_row_record[10],c1_row_record[11],c1_row_record[12],c1_row_record[13],c1_row_record[14],\
                          c1_row_record[15],c1_row_record[16],c1_row_record[17],c1_row_record[18],c1_row_record[19]])
    conn.close()
    return rlist


def read_defaultOperationNameDB(OperationName):
    '''
  Returns tuple with a list of default operations with default values by operation name
  Input:
    OperationName
  Output:
    Tuple with default operation with default values
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
   
    c1= c.execute("SELECT name, depth_flag, quantity_flag, date_flag,depth, quantity, odate, comment, cultivarflag, pop, autoirrigation, \
                   rowangle, xseed, yseed, cec, eomult, rowSpacing, cultivarname, fDepth, seedpieceMass FROM defaultoperations where \
                   name = ?", [OperationName])            
    c1_row = c1.fetchone()
    if c1_row != None:
        rlist=list(c1_row)
    conn.close()
    return rlist


def read_soilOMDB(soilname): 
    '''
  Returns soil information from soil_long table based on soilname.
  Input:
    soilname
  Output:
    Tuple with soil information
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select rowid, Sand, Silt, Clay, BD, OM_pct, TH33, TH1500 FROM soil_long where o_sid = (SELECT id FROM soil \
                       where soilname = ? )",[soilname])
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
                #print("debug: c1rowrecord:", c1rowrecord)
    conn.close()
    return rlist


def read_soilhydroDB(soilname): 
    '''
  Returns soil hydro information from soil_long table based on soilname.
  Input:
    soilname
  Output:
    Tuple with soil information
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select thr, ths, tha, th, Alfa, n, Ks, Kk, thk, BD, OM_pct, Sand, Silt FROM soil_long where o_sid = \
                       (SELECT id FROM soil where soilname = ? )",[soilname])
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
                #print("debug: c1rowrecord:", c1rowrecord)
    conn.close()
    return rlist


def insert_into_soillong(soilname,soilrow):   
    '''
  Insert the soil record on soil_long table based on soilname.
  Input:
    soilname
    soilrow = tuple with soil information to be ingested on soil_long table
  Output:
    '''  
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    c1 = c.execute("SELECT id FROM soil where soilname=?",(soilname,))
    c1_row = c1.fetchall()
    if c1_row != []: #if c1_row != None:
        new_tuple = tuple(c1_row[0]) + soilrow    
        qstatus = c.execute("insert into soil_long (o_sid,Bottom_depth,OM_pct,NO3,NH4,HnNew,InitType,Tmpr,Sand,Silt,Clay,BD,\
                             TH33,TH1500,thr,ths,tha,th,Alfa,n,Ks,Kk,thk,kh,kL,km,kn,kd,fe,fh,r0,rL,rm,fa,nq,cs) \
                             values (?,?,?/100,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0.00007,0.035,0.07,0.2,0.00001,0.6,\
                             0.2,10.0,50.0,10.0,0.1,8,0.00001)",new_tuple)         
        conn.commit()
    conn.close()
    return True


def read_soillongDB(soilname): 
    '''
  Insert the soil record on soil_long table based on soilname.
  Input:
    soilname
    soilrow = tuple with soil information to be ingested on soil_long table
  Output:
    '''  
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    #print("Debug: soilname='",soilname,"'")
    if len(soilname) > 0:
        c1= c.execute("Select Bottom_depth,OM_pct,NO3,NH4,HnNew,initType,Tmpr,Sand,Silt,Clay,BD,TH33,TH1500,thr,ths,tha,th,Alfa,n,Ks,\
                       Kk,thk,kh,kL,km,kn,kd,fe,fh,r0,rL,rm,fa,nq,cs FROM soil_long where o_sid = (SELECT id FROM \
                       soil where soilname = ?)",[soilname])
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
                #print("debug: c1rowrecord:", c1rowrecord)
    conn.close()
    return rlist


def getSiteFromSoilname(soilname): 
    '''
  Insert the soil record on soil_long table based on soilname.
  Input:
    soilname
  Output:
    '''  
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    #print("Debug getSiteFromSoilname: soilname='",soilname,"'")
    if len(soilname) > 0:
        c1= c.execute("select sitename from soil so, sitedetails si where so.site_id = si.id and soilname=?",[soilname])
        c1_row = c1.fetchone()
        if c1_row != None:
            rlist = list(c1_row)
    conn.close()
    return rlist


def read_soilshortDB(soilname): 
    '''
  Returns more restricted soil information from soil_long table based on soilname
  are not asked from users.
  Input:
    soilname
  Output:
    Tuple with soil information
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select Bottom_depth,initType,OM_pct,NO3,NH4,HnNew,Tmpr,Sand,Silt,Clay,BD,TH33,TH1500,thr,ths,tha,th,Alfa,n,Ks,Kk,thk FROM soil_long \
                       where o_sid = (SELECT id FROM soil where soilname = ? )",[soilname])      
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
                #print("debug: c1rowrecord:", c1rowrecord)
    conn.close()
    return rlist


def read_soiltextureDB(soilname): 
    '''
  Returns soil texture information from soil_long table based on soilname
  are not asked from users.
  Input:
    soilname
  Output:
    Tuple with soil information
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select Sand,Silt,Clay FROM soil_long where o_sid = (SELECT id FROM soil where soilname = ? )",[soilname])
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
                #print("debug: c1rowrecord:", c1rowrecord)
    conn.close()
    return rlist


def read_soilnitrogenDB(soilname):
    '''
  Returns soil nitrogen information from soil_long table based on soilname
  are not asked from users.
  Input:
    soilname
  Output:
    Tuple with soil information
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select kh,kL,km,kn,kd,fe,fh,r0,rL,rm,fa,nq,cs FROM soil_long where o_sid = (SELECT id FROM soil where \
                       soilname = ? )",[soilname])
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
    conn.close()
    return rlist


def read_soluteDB(id=1): #
    '''
  Returns default solute information to be used in the soil2d solute input file
  Input:
    id
  Output:
    Tuple with solute information
    '''
    rtuple = ()
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if isinstance(id, int):
        c1= c.execute("Select name,EPSI,IUPW,CourMax,Diffusion_Coeff FROM solute where id = ? ",[id])
        c1row = c1.fetchone()
        if c1row != None:
            rtuple = (c1row[0],c1row[1],c1row[2],c1row[3],c1row[4])
    conn.close()
    return rtuple


def read_dispersivityDB(texture): #
    '''
  Return the selected record from the dispersivity table based on texture
  Input:
    texture
  Output:
    Tuple with dispersivity information
    '''
    rtuple = ()
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if texture != "":
        query = "Select alpha FROM dispersivity where texturecl like '%" + texture + "%'"
        c1= c.execute(query)
        c1row = c1.fetchone()
        if c1row != None:
            rtuple = (c1row[0])
    conn.close()
    return rtuple


def read_soillongDB_maxdepth(soilname):
    '''
  Return max Bottom_depth from soil_long based on soilname
  Input:
    soilname
  Output:
    Tuple with max Bottom_depth
    '''
    rlist = 0 #[]
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select max(Bottom_depth) FROM soil_long where o_sid = (SELECT id FROM soil where soilname = ? )",[soilname])
        c1row = c1.fetchone() #all()
        if c1row != None:
            rlist = c1row[0]
            #for c1rowrecord in c1row:
            #    rlist.append(c1rowrecord)
    conn.close()
    return rlist 


def delete_soillong(soilname):   
    '''
  Delete the soillong parameters
  Input:
    soilname
  Output:
    '''  
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    c1= c.execute("Select o_sid, id from soil_long where o_sid = (Select id FROM soil where soilname =? ORDER by id ASC)",[soilname])
    c1row = c1.fetchall()  
    for c1rowitem in c1row: 
        temp_tuple = (c1rowitem[0],c1rowitem[1])       
        c2 = c.execute("delete from soil_long where o_sid=? and id=? ",temp_tuple)
    conn.commit()            
    conn.close()
    return True 


def insert_soilgridratioDB(soilgrid_tuple):   
    '''
  Insert the soilgrid-ratio parameters. Returns the gridratio_id which might be needed for in soil table.
  Input:
    soilgrid_tuple = information to be inserted into gridratio table
  Output:
    next_gridratio_id
    '''  
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    #find what would be the id for next entry inside the gridratio table    
    c1= c.execute("Select max(gridratio_id) FROM gridratio")
    c1row = c1.fetchone()
    next_gridratio_id = 1
    if c1row != None:
        next_gridratio_id = c1row[0] +1
    
    new_tuple = (next_gridratio_id,)+ soilgrid_tuple    
    qstatus = c.execute("insert into gridratio (gridratio_id,SR1,SR2,IR1,IR2,PlantingDepth,XLimitRoot,BottomBC) values (?,?,?,?,?,?,?,?)",new_tuple)    
    conn.commit()     
    conn.close()
    return next_gridratio_id 
    

def check_soilDB(soilname,site_id): 
    '''
  Check if soil exist based on soilname.
  Input:
    soilname
  Output:
    id = soil id
    '''  
    rlist = []   
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    soiltuple = (soilname,site_id)
    c1= c.execute("SELECT id FROM soil where soilname=? and site_id=?",soiltuple)
    c1row = c1.fetchone()
    if c1row != None:
        rlist.append(c1row[0])
    
    conn.close()
    print("soilname check", rlist)
    return rlist 			 


def check_and_insert_soilDB(soilname,site_id,gridratio_id):
    '''
  Check if soil already exist based on soilname and if it doesn't exist insert record into soil.
  Input:
    soilname
    gridratio_id
  Output:
    '''  
    rlist = []   
    rlist = check_soilDB(soilname,site_id)
    soiltuple = (soilname,site_id,gridratio_id)
    ###if rlist !=0:
    print("rlist=",rlist)
    if rlist ==[]:
        conn = sqlite3.connect(dbDir + '\\crop.db')
        c = conn.cursor()   
        if not c:
            print("database not open")
            return False
        c1= c.execute("insert into soil (soilname, site_id, o_gridratio_id) values (?,?,?)",soiltuple)
        conn.commit()        
        conn.close()
        return True
    else:
        messageUser("This soilname exist, please use a different name.")
        return False


def read_soilDB():    
    '''
  Returns soil list
  Input:
  Output:
    Tuple with soil id and name
    '''  
    rlist = [] #list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False    

    c1 = c.execute("SELECT id, soilname FROM soil order by soilname")      
    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:
            rlist.append(c1_row_record[1])
        
    conn.close()       
    return rlist


def read_soilgridratioDB(soilname):
    '''
  Returns gridration information based on soilname
  Input:
    soilname
  Output:
    Tuple with gridratio information 
    '''  
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if len(soilname) > 0:
        c1= c.execute("Select SR1,SR2,IR1,IR2,PlantingDepth,XLimitRoot,BottomBC FROM gridratio where gridratio_id = (SELECT \
                       o_gridratio_id FROM soil where soilname = ? )",[soilname])
        c1row = c1.fetchall()
        if c1row != None:
            for c1rowrecord in c1row:
                rlist.append(c1rowrecord)
                #print("debug: c1rowrecord:", c1rowrecord)
            
    conn.close()
    return rlist


def read_biologydefault():
    '''
  Returns default biologydefault information to be used in the soil2d biology input file
  Input:
  Output:
    Tuple with biologydefault information
    '''
    rlist =[] # list    
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    
    c1 = c.execute("SELECT dthH, dthL, es, Th_m, tb, QT, dThD, Th_d FROM biologydefault")          
    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:
            rlist.append(c1_row_record)
    conn.close()           
    return rlist


def read_experiment(item):
    '''
  Returns all experiments based on crop name.
  Input:
    item = crop name
  Output:
    Tuple with experiment name and id list
    '''
    rlist =[] # list
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    
    search_str = item     
    if len(search_str) > 0:
        c1 = c.execute("SELECT exid, name FROM experiment where crop= '%s';"%(search_str))          
        c1_row = c1.fetchall()
        if c1_row != None:
            for c1_row_record in c1_row:
                rlist.append(c1_row_record[1])     
        conn.close()    
        
    return rlist


def read_weather_id_forsite(site):  
    '''
  Returns weather id list for a specific site name.
  Input:
    site
  Output:
    Tuple with weather id list
    '''
    rlist = []
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    c1 = c.execute("SELECT distinct weather_id FROM weather_data where site = ?",(site,))
    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:
            #rlist[str(c1_row_record[0])] =c1_row_record[1]
            rlist.append(c1_row_record[0])
        
    conn.close()            
    return rlist


def read_weatheryears_fromtreatment(treatment):  
    '''
  Returns operation date list for a specific treatment name
  Input:
    treatment info
  Output:
    Tuple with operation date list
    '''
    rlist = [] # list {} # dictionary
    conn = sqlite3.connect(dbDir + '\\crop.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    experiment_name = treatment.split('/')[1]
    treatment_name = treatment.split('/')[2]

    clause = (experiment_name,treatment_name)
    c1 = c.execute("SELECT distinct odate from operations o, treatment t, experiment e where t.tid = o.o_t_exid \
                    and e.exid=t.t_exid and e.name=? and t.name = ?",clause) 
    for op in c1:
        print("op=",op["odate"]) 
        if(op["odate"] != ""):
            dd,mon,yy = op["odate"].split("/")
            rlist.append(int(yy))

    return sorted(set(rlist))


def read_weather_metaDBforsite(site):  
    '''
  Returns tuple with id and stationtype list for a specific site name
  Input:
    site
  Output:
    Tuple with id and stationtype list
    '''
    rlist ={} # dictionary
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False

    if len(site) > 0: 
        c1 = c.execute("SELECT id, stationtype FROM weather_meta where site=?",[site])  
        c1_row = c1.fetchall()
        print("crow=",c1_row)
        if c1_row != None:
            for c1_row_record in c1_row:
                rlist[str(c1_row_record[0])] =c1_row_record[1]
        
    conn.close()            
    return rlist


def read_weather_metaDB():  
    '''
  Returns tuple with id and stationtype list.
  Input:
  Output:
    Tuple with id and stationtype list
    '''
    rlist ={} # dictionary
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()   
    if not c:
       print("database not open")
       return False
    
    c1 = c.execute("SELECT id, stationtype FROM weather_meta order by stationtype")  
    c1_row = c1.fetchall()
    if c1_row != None:
        for c1_row_record in c1_row:
            rlist[str(c1_row_record[0])] =c1_row_record[1]
        
    conn.close()            
    return rlist


def read_weatherlongDB(stationtype):  
    '''
  Returns tuple with complete weather_meta information based on stationtype
  Input:
    stationtype
  Output:
    Tuple with complete weather_meta information
    '''
    rlist =() 
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    #print("Debug: stationtype=",stationtype)
    c1 = c.execute("Select rlat,rlon,Bsolar,Btemp,Atemp,BWInd,BIR,AvgWind,AvgRainRate,ChemCOnc,AvgCO2,stationtype,site FROM weather_meta wm, sitedetails s \
                    where wm.site=s.sitename and stationtype = ? ",[stationtype])
    c1row = c1.fetchone()
    if c1row != None:
        rlist = c1row

    conn.close()
    return rlist


def insert_update_weather(record_tuple,buttontext):
    '''
  Insert or update information on weather_meta table based on buttontext
  Input:
    record_tuple = tuple with weather meta information
    buttontext =  save or update
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if buttontext.find('SaveAs')==0:
        qstatus = c.execute("insert into weather_meta (Bsolar,Btemp,Atemp,BWInd,BIR,AvgWind,AvgRainRate,ChemCOnc,AvgCO2,site,stationtype) values \
                             (?,?,?,?,?,?,?,?,?,?,?)",record_tuple) 
    else:
        #do update
        qstatus = c.execute("update weather_meta SET Bsolar=?, Btemp=?, Atemp=?, BWInd=?, BIR=?, AvgWind=?, AvgRainRate=?, ChemCOnc=?, AvgCO2=?, site=? \
                             where stationtype= ? ",record_tuple) 
    
    conn.commit()
    conn.close()
    return True


def delete_weather(site,stationtype):
    '''
  Delete all information on weather_meta and weather_data tables based on site and stationtype
  Input:
    site
    stationtype
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    weathertuple = (stationtype,site)
    c.execute("delete from weather_meta where stationtype=? and site=?",weathertuple) 
    c.execute("delete from weather_data where weather_id=? and site=?",weathertuple) 
    conn.commit()
    conn.close()
    return True


def delete_cultivarCorn(cultivarname):
    '''
  Delete record on cultivar_corn table based on cultivarname
  Input:
    cultivarname
  Output:
    '''
    cultivartuple = read_cultivar_DB_detailed(cultivarname,"corn")  
    if not cultivartuple:
        return False

    delete_flag = messageUserDelete("Are you sure you want to delete this record?")
    if delete_flag:
        conn = sqlite3.connect(dbDir + '\\crop.db')
        c = conn.cursor()
        if not c:
            print("database not open")
            return False

        c.execute("delete from cultivar_corn where hybridname=?",[cultivarname]) 
        conn.commit()
        conn.close()
    return True


def delete_cultivarPotato(cultivarname):
    '''
  Delete record on cultivar_corn table based on cultivarname
  Input:
    cultivarname
  Output:
    '''
    delete_flag = messageUserDelete("Are you sure you want to delete this record?")
    if delete_flag:
        conn = sqlite3.connect(dbDir + '\\crop.db')
        c = conn.cursor()
        if not c:
            print("database not open")
            return False

        c.execute("delete from cultivar_potato where hybridname=?",[cultivarname]) 
        conn.commit()
        conn.close()
    return True


def insertUpdateCultivarCorn(record_tuple,buttontext):
    '''
  Update/insert cultivar table based on buttontext
  Input:
    record_tuple = information that will be ingested on cultivar_corn
    buttontext = Save/update
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if buttontext == "SaveAs":
        qstatus = c.execute("insert into cultivar_corn (hybridname,juvenileleaves,DaylengthSensitive,Rmax_LTAR,Rmax_LTIR,PhyllFrmTassel,StayGreen,\
                             LM_min,RRRM,RRRY,RVRL,ALPM,ALPY,RTWL,RTMinWTperArea,EPSI,IUPW,CourMax,Diffx,Diffz,VelZ,lsink,Rroot,Constl_M,ConstK_M,Cmin0_M,\
                             ConstI_Y,ConstK_Y,Cmin0_Y) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",record_tuple) 
    else:
        #do update        
        record_tuple1 = record_tuple[1:] + (record_tuple[0],)
        qstatus = c.execute("update cultivar_corn SET juvenileleaves=?, DaylengthSensitive=?, Rmax_LTAR=?, Rmax_LTIR=?, PhyllFrmTassel=?, StayGreen=?,\
                             LM_min=?, RRRM=?, RRRY=?, RVRL=?, ALPM=?, ALPY=?, RTWL=?, RTMinWTperArea=?, EPSI=?, IUPW=?, CourMax=?, Diffx=?, Diffz=?, VelZ=?, \
                             lsink=?, Rroot=?, Constl_M=?, ConstK_M=?, Cmin0_M=?, ConstI_Y=?, ConstK_Y=?, Cmin0_Y=? where hybridname=? ",record_tuple1) 
    conn.commit()
    conn.close()
    return True


def insertUpdateCultivarPotato(record_tuple,buttontext):
    '''
  Update/insert cultivar table based on buttontext
  Input:
    record_tuple = information that will be ingested on cultivar_corn
    buttontext = Save/update
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\crop.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False
    if buttontext == "SaveAs":
        qstatus = c.execute("insert into cultivar_potato (hybridname,A1,A6,A8,A9,A10,G1,G2,G3,G4,RRRM,RRRY,RVRL,ALPM,ALPY,RTWL,\
                             RTMinWTperArea,EPSI,IUPW,CourMax,Diffx,Diffz,VelZ,lsink,Rroot,Constl_M,ConstK_M,Cmin0_M,ConstI_Y,ConstK_Y,\
                             Cmin0_Y) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",record_tuple) 
    else:
        #do update        
        record_tuple1 = record_tuple[1:] + (record_tuple[0],)
        qstatus = c.execute("update cultivar_potato SET A1=?, A6=?, A8=?, A9=?, A10=?, G1=?, G2=?, G3=?, G4=?, RRRM=?, RRRY=?, \
                             RVRL=?, ALPM=?, ALPY=?, RTWL=?, RTMinWTperArea=?, EPSI=?, IUPW=?, CourMax=?, Diffx=?, Diffz=?, VelZ=?, lsink=?, \
                             Rroot=?, Constl_M=?, ConstK_M=?, Cmin0_M=?, ConstI_Y=?, ConstK_Y=?, Cmin0_Y=? where hybridname=?",record_tuple1) 
    conn.commit()
    conn.close()
    return True


def extract_cropOutputData(tablename,simulationname):
    '''
  Returns output table for a specific tablename and simulationname
  Input:
    tablename
    simulationname
  Output:
    dataframe with output information
    '''
    conn = sqlite3.connect(dbDir + '\\cropOutput.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    query = "select * from " + tablename + " where " + tablename + "_id=" + simulationname
    df = pd.read_sql_query(query,conn)
    conn.close()
    return df
 

def delete_cropOutputSim(id,crop):
    '''
  Returns output table for a specific tablename and simulationname
  Input:
    id
    crop
  Output:
    '''
    conn = sqlite3.connect(dbDir + '\\cropOutput.db')
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    if(crop == "corn"):
        file_ext = ["g01","g02","g03","g04","g05","g06"]
    else:
        file_ext = ["g01","g03","g04","g05","g06","nitrogen","plantStress"]

    for ext in file_ext:
        table_name = ext+"_"+crop
        id_name = table_name+"_id"
        query = "delete from " + table_name + " where " + id_name + "=" + id
        #c.execute(query) 
        conn.commit()

    conn.close()
    return True
 

def extract_date_time(row):
    '''
  Split date and returns as a timestamp.
  Input:
    row
  Output:
    date as a timestamp
    '''
    (m,d,y) = str(row['date']).split('/')
    h = row['time']
    return pd.Timestamp(int(y),int(m),int(d),h)


def ingestOutputFile(table_name,g_name,simulationname):
    '''
  Ingest file with output data in cropOutput database.
  Input:
    table_name
    g_name = input filename with full path
    simulationname
  Output:
    '''
    #print(g_name)
    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    id = table_name + "_id"
    g_df = pd.read_csv(g_name,skipinitialspace=True,index_col=False)
    # strip leading and trailing spaces from column names
    for col in g_df.columns: 
        g_df.rename(columns={col:col.strip()},inplace=True)
    g_df[id] = int(simulationname)

    if(table_name == "g01_corn" or table_name == "g02_corn" or table_name == "g01_potato" or table_name == "nitrogen_potato" \
       or table_name == "plantStress_potato" or table_name == "plantStress_corn"):
        # Change date format
        g_df['Date_Time'] = g_df.apply(lambda row: extract_date_time(row), axis=1)
        g_df = g_df.drop(columns=['date','time'])
        if(table_name == "g01_corn"):
            g_df.rename(columns={'LA/pl':'LA_pl','TotleafDM':'TotLeafDM'},inplace=True)
        if(table_name == "g01_potato"):
            g_df.rename(columns={'LA/pl':'LA_pl'},inplace=True)
        if(table_name == "nitrogen_potato" or table_name == "plantStress_potato" or table_name == "plantStress_corn"):
            g_df = g_df.drop(columns=['jday'])
            if(table_name == "nitrogen_potato"):
                g_df.rename(columns={'Seed N':'seed_N'},inplace=True)

    if(table_name == "g03_corn" or table_name == "g04_corn" or table_name == "g05_corn" or table_name == "g06_corn" or \
       table_name == "g03_potato" or table_name == "g04_potato" or table_name == "g05_potato" or table_name == "g06_potato"):
        # Change date format
        # 2dsoil start counting the days stsrting on 12/30/1899.
        g_df['DateInit'] = pd.Timestamp('1899-12-30')
        #print(g_df['Date_time'])
        g_df['Date_time'] = g_df['DateInit'] + pd.to_timedelta(g_df['Date_time'], unit='D').dt.round('h')
        g_df = g_df.drop(columns=['DateInit','Date'])
        #print(g_df)

    g_df.to_sql(table_name,conn,if_exists="append",index=False)
    conn.close()
    return True


def getCornDateByDev(sim_id,cornPhase):
    '''
  Returns date for tuber initiation date.
  Input:
    sim_id = simulation id
    cornPhase = corm development phase keyword
  Output:
    tuber initiation date
    '''
    rlist = "" 

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    corntuple = (sim_id,cornPhase)
    c2 = c.execute("select min(Date_Time) from g01_corn where g01_corn_id=? and Note=?",corntuple)
    c2_row = c2.fetchone()
    if c2_row[0] != None:  
        date_time_obj = dt.strptime(c2_row[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
        rlist = date_time_obj
    else:
        rlist = "N/A"
    conn.close()   

    return rlist


def getMaxDateG01BySimID(crop, sim_id):
    '''
  Returns max date for G01 file when plat doesn't reach maturity date
  Input:
    crop
    sim_id = simulation id
  Output:
    last date
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    query = "select max(Date_Time) from g01_" + crop + " where g01_" + crop + "_id=" + sim_id
    print("query=",query)
    c2 = c.execute(query)
    c2_row = c2.fetchone()
    print(c2_row[0])
    date_time_obj = dt.strptime(c2_row[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
    rlist = date_time_obj
    conn.close()   

    return rlist


def getTuberInitDate(sim_id):
    '''
  Returns date for tuber initiation date.
  Input:
    sim_id = simulation id
  Output:
    tuber initiation date
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    c2 = c.execute("select min(Date_Time) from g01_potato where (tuberDM > 0 or Stage > 2.01) and g01_potato_id=?",[sim_id])
    c2_row = c2.fetchone()
    if c2_row[0] != None:  
        print(c2_row[0])
        date_time_obj = dt.strptime(c2_row[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
        rlist = date_time_obj
    else:
        rlist = "N/A"
    conn.close()   

    return rlist


def getMaturityDate(sim_id):
    '''
  Returns date for maturity date.
  Input:
    sim_id = simulation id
  Output:
    maturity date
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    c2 = c.execute("select min(Date_Time) from g01_potato where Stage > 10 and g01_potato_id=?",[sim_id])
    c2_row = c2.fetchone()
    if c2_row[0] != None:  
        date_time_obj = dt.strptime(c2_row[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
        rlist = date_time_obj
    else:
        rlist = "N/A"
    conn.close()   

    return rlist


def getPotatoAgronomicData(sim_id, date):
    '''
  Returns agronomical date.
  Input:
    sim_id = simulation id
    date = maturity date
  Output:
    tuberDM = yield
    totalDM = total biomass
    Tr-Act = transpiration
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    harvestDate = dt.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    querytuple = (sim_id,harvestDate+'%')

    c1 = c.execute("select max(tuberDM), max(totalDM), sum(\"Tr-Act\") from g01_potato where g01_potato_id=? and Date_Time <= ?",querytuple)
    c1row = c1.fetchone()
    if c1row != None:
        rlist = c1row

    conn.close()
    return rlist


def getCornAgronomicData(sim_id, date):
    '''
  Returns agronomical date.
  Input:
    sim_id = simulation id
    date = maturity date
  Output:
    tuberDM = yield
    totalDM = total biomass
    Tr-Act = transpiration
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    harvestDate = dt.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    querytuple = (sim_id,harvestDate+'%')

    c1 = c.execute("select (max(earDM)*.86), max(shootDM), sum(NUpt) from g01_corn where g01_corn_id=? and Date_Time <= ?",querytuple)
    c1row = c1.fetchone()
    if c1row != None:
        rlist = c1row

    conn.close()
    return rlist


def getEnvironmentalData(sim_id, date, crop):
    '''
  Returns agronomical data.
  Input:
    sim_id = simulation id
    date = maturity date
    crop
  Output:
    tuberDM = yield
    totalDM = total biomass
    Tr-Act = transpiration
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    maturityDate = dt.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    query = "select max(SeasPTran), max(SeasATran), max(SeasASoEv), max(SeasPSoEv), max(abs(Drainage)), max(SeasInfil), \
             sum(Runoff_02), max(SeasRain) from g05_" + crop + " where g05_" + crop + "_id=" + sim_id + " and \
             Date_Time <= '" + maturityDate + "%'"
    c1 = c.execute(query)
    c1row = c1.fetchone()
    if c1row != None:
        rlist = c1row

    conn.close()
    return rlist


def getPotatoNitrogenUptake(sim_id, date):
    '''
  Returns agronomical date.
  Input:
    sim_id = simulation id
    date = maturity date
  Output:
    N_uptake = nitrogen uptake
    '''
    rlist = None # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    harvestDate = dt.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    querytuple = (sim_id,harvestDate+'%')

    c1 = c.execute("select max(N_uptake) from nitrogen_potato where nitrogen_potato_id=? and Date_Time <= ?",querytuple)
    c1row = c1.fetchone()
    if c1row != None:
        rlist = c1row

    conn.close()
    return rlist


def getNitroWaterStressDates(sim_id):
    '''
  Returns dates where nitrogen and water (<=0.75) stress were present.
  Input:
    sim_id = simulation id
  Output:
    Tuple containing
    Date_Time = date
    PSIEffect_leaf = Water stress on leaf expansion
    NEffect_leaf = Nitrogen stress on leaf expansion
    PSIEffect_Pn = Water stress on leaf photosynthesis
    NEffect_Pn = Nitrogen stress on photosynthesis
    '''

    rlist = [] # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    c1 = c.execute("select Date_Time, PSIEffect_leaf, NEffect_leaf, PSIEffect_Pn, NEffect_Pn from plantStress_potato where \
                    PSIEffect_leaf <= 0.75 or NEffect_leaf <= 0.75 or PSIEffect_Pn <= 0.75 or NEffect_Pn <= 0.75 and plantStress_potato_id=?",[sim_id])
    c1row = c1.fetchall()
    if c1row != None:
        for c1rowrecord in c1row:
            rlist.append(c1rowrecord)

    conn.close()
    return rlist


def getCornPlantStressDates(sim_id):
    '''
  Returns dates where nitrogen and water (<=0.75) stress were present.
  Input:
    sim_id = simulation id
  Output:
    Tuple containing
    Date_Time = date
	waterstress = Water Stress
	N_stress = N Stress
	Shade_Stress = C Stress
	PotentialArea = Potential Area
    '''

    rlist = [] # list   

    conn = sqlite3.connect(dbDir + '\\cropOutput.db') 
    c = conn.cursor()
    if not c:
        print("database not open")
        return False

    c1 = c.execute("select Date_Time, waterstress, N_stress, Shade_Stress, PotentialArea from plantStress_corn where \
                    waterstress >= 0.25 or N_stress >= 0.25 or Shade_Stress >= 0.25 or PotentialArea >= 0.25 and \
                    plantStress_corn_id=?",[sim_id])
    c1row = c1.fetchall()
    if c1row != None:
        for c1rowrecord in c1row:
            rlist.append(c1rowrecord)

    conn.close()
    return rlist
