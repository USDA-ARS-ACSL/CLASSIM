import subprocess
#import threading
import time
import os
import csv
import numpy as np
import pandas as pd
import sys
import math
import re
import ctypes as ct
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *
from helper.Texture import *
from subprocess import Popen
from os import path
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream, pyqtSignal, QCoreApplication, QBasicTimer

global runpath1
global app_dir
global repository_dir

gusername = os.environ['username'] #windows. What about linux
gparent_dir = 'C:\\Users\\'+gusername +'\\Documents'
app_dir = os.path.join(gparent_dir,'classim_v3')
if not os.path.exists(app_dir):
    os.makedirs(app_dir)

global db
db = app_dir+'\\crop.db'

run_dir = os.path.join(app_dir,'run')
if not os.path.exists(run_dir):
    os.makedirs(run_dir)

runpath1= run_dir
repository_dir = os.path.join(runpath1,'store')


## This should always be there
if not os.path.exists(repository_dir):
    print('RotationTab Error: Missing repository_dir')


def copyFile(src,dest):
# Copy this way will make it wait for this command to finish first
    try:
        copyresult = subprocess.run(['copy',src,dest],stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
    except len(copyresult.stderr) > 0:
        print('Error1 in Copy function: %s', copyresult.stderr)
        

def WriteBiologydefault(field_name,field_path):
#  writes to file: BiologyDefault.bio
    CODEC="UTF-8"        
    filename = field_path+"\\BiologyDefault.bio"              
    fh = QFile(filename)
    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:
        biolist = read_biologydefault()
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)
        fout<<"*** Example 12.3: Parameters of abiotic responce: file 'SetAbio.dat'"<<"\n"
        fout<<"Dehumification, mineralization, nitrification dependencies on moisture:"<<"\n"
        fout<<"dThH    dThL    es    Th_m"<<"\n"
        fout<<'%-14.6f%-14.6f%-14.6f%-14.6f' %(biolist[0][0],biolist[0][1],biolist[0][2],biolist[0][3])<<"\n"
        fout<<"Dependencies of temperature"<<"\n"
        fout<<"tb     QT"<<"\n"
        fout<<'%-14.6f%-14.6f' %(biolist[0][4],biolist[0][5])<<"\n"
        fout<<"Denitrification dependencies on water content"<<"\n"
        fout<<"dThD   Th_d"<<"\n"
        fout<<'%-14.6f%-14.6f' %(biolist[0][6],biolist[0][7])<<"\n"
    fh.close()


def WriteIrrigationFile(field_name,field_path):
############### Write DRP file
     CODEC="UTF-8"        
     filename = field_path+"\\"+field_name+".drp"
     fh = QFile(filename)

     if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
         print("Could not open file")
     else:
         fout = QTextStream(fh)            
         fout.setCodec(CODEC)
         fout<<"*****Script for Drip application module ***** mAppl is cm water per hour to a 45 x 30 cm area"<<"\n"                    
         fout<<"Number of Drip irrigations(max=25)"<<"\n"                    
         fout<<0<<"\n"
         fout<<"No drip irrigation"<<"\n"                
         fh.close()
 

def WriteCropVariety(crop,cultivar,field_name,field_path):
    hybridname = cultivar
    #print("Debug: hybridname=",hybridname)
    hybridparameters = read_cultivar_DB_detailed(hybridname,crop)
    CODEC="UTF-8"

    filename = field_path+"\\"+hybridname+".var"
    #print("filename=",filename)
    #print("hybridparameters=",hybridparameters)
    fh = QFile(filename)

    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:            
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)

        if crop  == "maize":
        #     0                  1              2          3              4            5       6     7    8    9    10   11   12
        #juvenileleaves, DaylengthSensitive, Rmax_LTAR, Rmax_LTIR, PhyllFrmTassel,StayGreen,LM_min,RRRM,RRRY,RVRL,ALPM,ALPY,RTWL,
        #      13        14   15    16      17     18    19   20   21     22         23     24       25        26      27       28    
        #RTMinWTperArea,EPSI,IUPW,CourMax,Diffx, Diffz,Velz,lsink,Rroot,Constl_M,ConstK_M,Cmin0_M,ConstI_Y,ConstK_Y,Cmin0_Y,hybridname
            fout<<"maize growth simulation for variety "<<hybridname<<"\n"
            fout<<"Juvenile   Daylength   StayGreen  LM_Min Rmax_LTAR              Rmax_LTIR                Phyllochrons from "<<"\n"
            fout<<"leaves     Sensitive                     Leaf tip appearance   Leaf tip initiation       TassellInit"<<"\n"            
            fout<<'%-14.0f%-14.0f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f' %(hybridparameters[0],hybridparameters[1],hybridparameters[5],hybridparameters[6],\
            hybridparameters[2],hybridparameters[3],hybridparameters[4])<<"\n"
        elif crop == "potato":
        # 0    1  2    3   4    5   6  7    8    9    10    11    12     13   14     15              16    17     18     19
        # A1, A6, A8, A9, A10, G1, G2, G3, G4, RRRM, RRRY, RVRL, ALPM, ALPY, RTWL, RTMinWTperArea, EPSI, IUPW, CourMax, Diffx,
        #  20     21     22     23       24        25        26       27        28     29
        # Diffz, Velz, lsink, Rroot, Constl_M, ConstK_M, Cmin0_M, ConstI_Y, ConstK_Y, Cmin0_Y
            a2 = (hybridparameters[0]-1)/10
            a3 = 100
            a4 = 1
            a5 = hybridparameters[1]-1
            a7 = hybridparameters[2]-1
            fout<<"*** EX4 Coefficient Calibration for Agmip 2017"<<"\n"
            fout<<hybridname<<"\n"
            fout<<"Genetic Coefficients"<<"\n"
            fout<<"A1(T1) A2(T2) A3(LAI) A4(Srad) A5(Tamp) A6(Tamp) A7(Pd) A8(Pd) A9(N) A10(N) G1(Det) G2(Exp) G3(TGR) G4(SLW)"<<"\n"
            fout<<'%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f%-14.3f' %(hybridparameters[0],a2,a3,a4,a5,\
            hybridparameters[1],a7,hybridparameters[2],hybridparameters[3],hybridparameters[4],hybridparameters[5],hybridparameters[6],hybridparameters[7],\
            hybridparameters[8])<<"\n"
        # soybean
        elif crop == "soybean":
        # 0          1       2   3   4   5   6   7  8   9   10  11  12  13  14  15   16    17  18  19  20  21  22  23  24
        # matGrp, seedLb, fill, v1, v2, v3, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, g1, g2, g3, g4, g5, g6, g7,
        # 25  26    27   28    29    30    31    32         33          34    35    36       37     38    39     40    41 
        # g8, g9, RRRM, RRRY, RVRL, ALPM, ALPY, RTWL, RTMinWTperArea, EPSI, IUPW, CourMax, Diffx, Diffz, Velz, lsink, Rroot,
        # 42         43          44       45      46         47 
        # Constl_M, ConstK_M, Cmin0_M, ConstI_Y, ConstK_Y, Cmin0_Y
            fout<<"soybean growth simulation for variety "<<hybridname<<"\n"
            fout<<"[Phenology]"<<"\n"
            fout<<"MG SEEDLB FILL PARM(2) PARM(3) PARM(4) PARM(5) PARM(6) PARM(7) PARM(8) PARM(9) PARM(10) PARM(11) \
PARM(12) PARM(13) PARM(14) PARM(15) PARM(16) PARM(17) PARM(18) PARM(19) PARM(20) PARM(21) PARM(22) PARM(23) PARM(24) PARM(25)"<<"\n"
            fout<<'%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f\
                   %-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f%-14.5f' \
                   %(hybridparameters[0],hybridparameters[1],hybridparameters[2],hybridparameters[3],hybridparameters[4],\
                   hybridparameters[5],hybridparameters[6],hybridparameters[7],hybridparameters[8],hybridparameters[9],\
                   hybridparameters[10],hybridparameters[11],hybridparameters[12],hybridparameters[13],hybridparameters[14],\
                   hybridparameters[15],hybridparameters[16],hybridparameters[17],hybridparameters[18],hybridparameters[19],\
                   hybridparameters[20],hybridparameters[21],hybridparameters[22],hybridparameters[23],hybridparameters[24],\
                   hybridparameters[25],hybridparameters[26])<<"\n"
        # cotton
        elif crop == "cotton":
        #     0         1         2         3         4         5         6         7         8        9
        # calbrt11, calbrt12, calbrt13, calbrt15, calbrt16, calbrt17, calbrt18, calbrt19, calbrt22, calbrt26,
        #     10       11        12        13        14        15        16        17        18       19
        # calbrt27, calbrt28, calbrt29, calbrt30, calbrt31, calbrt32, calbrt33, calbrt34, calbrt35, calbrt36, 
        #     20       21        22        23        24        25        26        27        28       29
        # calbrt37, calbrt38, calbrt39, calbrt40, calbrt41, calbrt42, calbrt43, calbrt44, calbrt45, calbrt47, 
        #     30       31        32        33        34
        # calbrt48, calbrt49, calbrt50, calbrt52, calbrt57
            calbrt1 = 0.9
            calbrt2 = -0.22
            calbrt3 = -2.2
            calbrt4 = 0.1
            calbrt5 = -5.5
            calbrt6 = 0.5
            calbrt7 = 0.5
            calbrt8 = 0.1
            calbrt9 = 1.65
            calbrt10 = 2.15
            calbrt14 = 0.1
            calbrt20 = 1
            calbrt21 = 1
            calbrt23 = 1
            calbrt24 = 1
            calbrt25 = 1
            calbrt46 = 1
            calbrt51 = 1
            calbrt53 = 1
            calbrt54 = 0
            calbrt55 = 0.9
            calbrt56 = 1
            calbrt58 = 1
            calbrt59 = 1
            calbrt60 = 1
            rrrm = 166.7
            rrry = 31.3
            rvrl = 0.73
            alpm = 0.6
            alpy = 0.3
            rtwl = 0.00001
            mrwpua = 0.0002
            epsi = 1
            iupw = 1
            courmax = 1           
            diffx = 2.4
            diffz = 2.9
            velz = 0
            isink = 1
            rroot = 0.03
            constlm = 35
            constkm = 0.5
            cminom = 0.01
            constly = 17.2
            constky = 0.75
            cminoy = 0.03
            fout<<"Cotton growth simulation for variety "<<hybridname<<"\n"
            fout<<"[Phenology]"<<"\n"
            fout<<hybridname<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f\
                   %-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f\
                   %-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f\
                   %-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f\
                   %-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f%-14.6f\
                   %-14.6f%-14.6f%-14.6f%-14.6f%-14.6f' %(calbrt1,calbrt2,calbrt3,calbrt4,calbrt5,
                   calbrt6,calbrt7,calbrt8,calbrt9,calbrt10,hybridparameters[0],hybridparameters[1],
                   hybridparameters[2],calbrt14,hybridparameters[3],hybridparameters[4],hybridparameters[5],
                   hybridparameters[6],hybridparameters[7],calbrt20,calbrt21,hybridparameters[8],
                   calbrt23,calbrt24,calbrt25,hybridparameters[9],hybridparameters[10],
                   hybridparameters[11],hybridparameters[12],hybridparameters[13],hybridparameters[14],
                   hybridparameters[15],hybridparameters[16],hybridparameters[17],hybridparameters[18],
                   hybridparameters[19],hybridparameters[20],hybridparameters[21],hybridparameters[22],
                   hybridparameters[23],hybridparameters[24],hybridparameters[25],hybridparameters[26],
                   hybridparameters[27],hybridparameters[28],calbrt46,hybridparameters[29],hybridparameters[30],
                   hybridparameters[31],hybridparameters[32],calbrt51,hybridparameters[33],calbrt53,calbrt54,
                   calbrt55,calbrt56,hybridparameters[34],calbrt58,calbrt59,calbrt60)<<"\n"
        fout<<"[SoilRoot]"<<"\n"
        fout<<"*** WATER UPTAKE PARAMETER INFORMATION **************************"<<"\n"
        fout<<"RRRM       RRRY    RVRL"<<"\n"
        if crop  == "maize":
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[7],hybridparameters[8],hybridparameters[9])<<"\n"
            fout<<" ALPM    ALPY     RTWL    RtMinWtPerUnitArea"<<"\n"
            fout<<'%-14.8f%-14.8f%-14.8f%-14.8f' %(hybridparameters[10],hybridparameters[11],hybridparameters[12],hybridparameters[13])<<"\n"
            fout<<"[RootDiff]"<<"\n"
            fout<<"*** ROOT MOVER PARAMETER INFORMATION **************************"<<"\n"
            fout<<"EPSI        lUpW             CourMax"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[14],hybridparameters[15],hybridparameters[16])<<"\n"
            fout<<"Diffusivity and geotropic velocity"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[17],hybridparameters[18],hybridparameters[19])<<"\n"
            fout<<"[SoilNitrogen]"<<"\n"
            fout<<"*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************"<<"\n"
            fout<<"ISINK    Rroot         "<<"\n"
            fout<<'%-14.6f%-14.6f' %(hybridparameters[20],hybridparameters[21])<<"\n"
            fout<<"ConstI   Constk     Cmin0 "<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[22],hybridparameters[23],hybridparameters[24])<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[25],hybridparameters[26],hybridparameters[27])<<"\n"
        elif crop == "potato":
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[9],hybridparameters[10],hybridparameters[11])<<"\n"
            fout<<" ALPM    ALPY     RTWL    RtMinWtPerUnitArea"<<"\n"
            fout<<'%-14.8f%-14.8f%-14.8f%-14.8f' %(hybridparameters[12],hybridparameters[13],hybridparameters[14],hybridparameters[15])<<"\n"
            fout<<"[RootDiff]"<<"\n"
            fout<<"*** ROOT MOVER PARAMETER INFORMATION **************************"<<"\n"
            fout<<"EPSI        lUpW             CourMax"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[16],hybridparameters[17],hybridparameters[18])<<"\n"
            fout<<"Diffusivity and geotropic velocity"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[19],hybridparameters[20],hybridparameters[21])<<"\n"
            fout<<"[SoilNitrogen]"<<"\n"
            fout<<"*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************"<<"\n"
            fout<<"ISINK    Rroot         "<<"\n"
            fout<<'%-14.6f%-14.6f' %(hybridparameters[22],hybridparameters[23])<<"\n"
            fout<<"ConstI   Constk     Cmin0 "<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[24],hybridparameters[25],hybridparameters[26])<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[27],hybridparameters[28],hybridparameters[29])<<"\n"
        elif crop == "soybean":
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[27],hybridparameters[28],hybridparameters[29])<<"\n"
            fout<<" ALPM    ALPY     RTWL    RtMinWtPerUnitArea"<<"\n"
            fout<<'%-14.8f%-14.8f%-14.8f%-14.8f' %(hybridparameters[30],hybridparameters[31],hybridparameters[32],hybridparameters[33])<<"\n"
            fout<<"[RootDiff]"<<"\n"
            fout<<"*** ROOT MOVER PARAMETER INFORMATION **************************"<<"\n"
            fout<<"EPSI        lUpW             CourMax"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[34],hybridparameters[35],hybridparameters[36])<<"\n"
            fout<<"Diffusivity and geotropic velocity"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[37],hybridparameters[38],hybridparameters[39])<<"\n"
            fout<<"[SoilNitrogen]"<<"\n"
            fout<<"*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************"<<"\n"
            fout<<"ISINK    Rroot         "<<"\n"
            fout<<'%-14.6f%-14.6f' %(hybridparameters[40],hybridparameters[41])<<"\n"
            fout<<"ConstI   Constk     Cmin0 "<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[42],hybridparameters[43],hybridparameters[44])<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(hybridparameters[45],hybridparameters[46],hybridparameters[47])<<"\n"
        elif crop == "cotton":
            fout<<'%-14.6f%-14.6f%-14.6f' %(rrrm,rrry,rvrl)<<"\n"
            fout<<" ALPM    ALPY     RTWL    RtMinWtPerUnitArea"<<"\n"
            fout<<'%-14.8f%-14.8f%-14.8f%-14.8f' %(alpm,alpy,rtwl,mrwpua)<<"\n"
            fout<<"[RootDiff]"<<"\n"
            fout<<"*** ROOT MOVER PARAMETER INFORMATION **************************"<<"\n"
            fout<<"EPSI        lUpW             CourMax"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(epsi,iupw,courmax)<<"\n"
            fout<<"Diffusivity and geotropic velocity"<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(diffx,diffz,velz)<<"\n"
            fout<<"[SoilNitrogen]"<<"\n"
            fout<<"*** NITROGEN ROOT UPTAKE PARAMETER INFORMATION **************************"<<"\n"
            fout<<"ISINK    Rroot         "<<"\n"
            fout<<'%-14.6f%-14.6f' %(isink,rroot)<<"\n"
            fout<<"ConstI   Constk     Cmin0 "<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(constlm,constkm,cminom)<<"\n"
            fout<<'%-14.6f%-14.6f%-14.6f' %(constly,constky,cminoy)<<"\n"

        fout<<"[Gas_Exchange Species Parameters] "<<"\n"
        fout<<"**** for photosynthesis calculations ***"<<"\n"
        fout<<"EaVp    EaVc    Eaj     Hj      Sj     Vpm25   Vcm25    Jm25    Rd25    Ear       g0    g1"<<"\n"
        fout<<"75100   55900   32800   220000  702.6   70      50       300    2       39800   0.017   4.53"<<"\n"
        fout<<"*** Second set of parameters for Photosynthesis ****"<<"\n"
        fout<<"f (spec_correct)     scatt  Kc25    Ko25    Kp25    gbs         gi      gamma1"<<"\n"
        fout<<"0.15                 0.15   650      450    80      0.003       1       0.193"<<"\n"
        fout<<"**** Third set of photosynthesis parameters ****"<<"\n"
        fout<<"Gamma_gsw  sensitivity (sf) Reference_Potential_(phyla, bars) stomaRatio widthFact lfWidth (m)"<<"\n"
        fout<<"  10.0        2.3               -1.2                             1.0        0.72   0.050"<<"\n"
        fout<<"**** Secondary parameters for miscelanious equations ****"<<"\n"
        fout<<"internal_CO2_Ratio   SC_param      BLC_param"<<"\n"
        fout<<"0.7                   1.57           1.36"<<"\n"
        if(crop  == "maize" or crop == "soybean" or crop == "cotton"):
            fout<<"***** Q10 parameters for respiration and leaf senescence"<<"\n"
            fout<<"Q10MR            Q10LeafSenescense"<<"\n"
            fout<<"2.0                     2.0"<<"\n"
            fout<<"**** parameters for calculating the rank of the largest leaf and potential length of the leaf based on rank"<<"\n"
            fout<<"leafNumberFactor_a1 leafNumberFactor_b1 leafNumberFactor_a2 leafNumberFactor_b2"<<"\n"
            fout<<"-10.61                   0.25                   -5.99           0.27"<<"\n"
            fout<<"**************Leaf Morphology Factors *************"<<"\n"
            fout<<"LAF        WLRATIO         A_LW"<<"\n"
            fout<<" 1.37          0.106           0.75"<<"\n"
            fout<<"*******************Temperature factors for growth *****************************"<<"\n"
            fout<<"T_base                 T_opt            t_ceil  t_opt_GDD"<<"\n"
            fout<<"8.0                   32.1              43.7       34.0"<<"\n"
        fout<<"\n"
    fh.close()
            

def WriteWeather(experiment,treatmentname,stationtype,weather,field_name,field_path,tempVar,rainVar,CO2Var):
    # First create .wea file that stores the daily/hourly weather information for the simulation period
    filename = field_path+'\\'+stationtype + '.wea'   
    # getting weather data from sqlite
    conn, c = openDB(db)

    # get date range for treatment
    op_date_query = "select distinct odate from operations o, treatment t, experiment e where t.tid = o.o_t_exid and e.exid=t.t_exid and e.name=? and t.name = ?"
    df_op_date = pd.read_sql(op_date_query,conn,params=[experiment,treatmentname])
    df_op_date['odate'] = pd.to_datetime(df_op_date['odate'])
    sdate = df_op_date['odate'].min() - timedelta(days=1)
    edate = df_op_date['odate'].max() + timedelta(days=1)
    diffInDays = (edate - sdate)/np.timedelta64(1,'D')
        
    weather_query = "select jday, date, hour, srad, tmax, tmin, temperature, rain, wind, rh, co2 from weather_data where stationtype=? and weather_id=? order by date" 
    df_weatherdata_orig = pd.read_sql(weather_query,conn,params=[stationtype,weather])   
    # Convert date column to Date type
    df_weatherdata_orig['date'] = pd.to_datetime(df_weatherdata_orig['date'])
    firstDate = df_weatherdata_orig['date'].min()
    lastDate = df_weatherdata_orig['date'].max()
    df_weatherdata = df_weatherdata_orig.copy()
    mask = (df_weatherdata['date'] >= sdate) & (df_weatherdata['date'] <= edate)
    df_weatherdata = df_weatherdata.loc[mask]
    #Check if dataframe is empty
    if df_weatherdata.empty == True or (df_weatherdata.shape[0] + 1) < diffInDays:
        messageUser("Weather data is available for the data range of " + firstDate.strftime("%m/%d/%Y") + " and " + lastDate.strftime("%m/%d/%Y"))
        return False

    # Check if data is daily or hourly
    hourly_flag = 0
    weather_length = df_weatherdata['date'].max() - df_weatherdata['date'].min()
    num_records = len(df_weatherdata)
    df_weatherdata['date'] = pd.to_datetime(df_weatherdata['date'],format='%Y-%m-%d')
    #print(ltreatmentname)
    #print("weather_length=",weather_length.days," num_records=",num_records)
    if(num_records > (weather_length.days+1)):
        # header for hourly file
        df_weatherdata = df_weatherdata.drop(columns=['tmax','tmin'])
        weather_col_names = ["JDay", "Date", "hour", "Radiation", "temperature", "rain", "Wind", "rh", "CO2"] 
        hourly_flag = 1
        df_weatherdata = df_weatherdata.sort_values(by=['date','hour'])
        # Sensitivity analyses temperature variance
        if tempVar != 0:
            df_weatherdata['temperature'] = df_weatherdata['temperature'] + float(tempVar)
        #print("Hourly")
    else:
        #print("bd",df_weatherdata)
        # header for daily file
        df_weatherdata = df_weatherdata.drop(columns=['hour','temperature'])
        weather_col_names = ["JDay", "Date", "Radiation", "Tmax","Tmin", "rain", "Wind", "rh", "CO2"] 
        df_weatherdata = df_weatherdata.sort_values(by=['date'])
        # Sensitivity analyses temperature variance
        if tempVar != 0:
            df_weatherdata['tmax'] = df_weatherdata['tmax'] + float(tempVar)
            df_weatherdata['tmin'] = df_weatherdata['tmin'] + float(tempVar)
        #print("Daily")
        #print("ad",df_weatherdata)

    df_weatherdata['date'] = df_weatherdata['date'].dt.strftime('%m/%d/%Y')
    df_weatherdata.columns = weather_col_names         

    rh_flag = 1
    if (df_weatherdata['rh'].isna().sum() > 0 or (df_weatherdata['rh'] == '').sum() > 0):
        df_weatherdata = df_weatherdata.drop(columns=['rh'])
        rh_flag = 0

    co2_flag = 1  
    if CO2Var != "None":
        df_weatherdata['CO2'] = float(CO2Var)
    else:
        if (df_weatherdata['CO2'].isna().sum() > 0 or (df_weatherdata['CO2'] == '').sum() > 0):
            df_weatherdata = df_weatherdata.drop(columns=['CO2'])
            co2_flag = 0

    rain_flag = 1
    # Sensitivity analyses rain number is in %
    if rainVar != 0:
        df_weatherdata['rain'] = df_weatherdata['rain'] + (df_weatherdata['rain']*(float(rainVar)/100.0))         
    else:
        if (df_weatherdata['rain'].isna().sum() > 0 or (df_weatherdata['rain'] == '').sum() > 0):
            df_weatherdata = df_weatherdata.drop(columns=['rain'])
            rain_flag = 0

    wind_flag = 1
    if (df_weatherdata['Wind'].isna().sum() > 0 or (df_weatherdata['Wind'] == '').sum() > 0):
        df_weatherdata = df_weatherdata.drop(columns=['Wind'])
        wind_flag = 0

    # the inputs for weather file comes from the weather flags. So we have to build that data stream 
    # and then write
    comment_value = ",".join(df_weatherdata.columns)
    #write the comment first
    with open(filename,'a') as ff:
        ff.write(comment_value)
        ff.write('\n')

    df_weatherdata.to_csv(filename,sep=' ',index=False,quotechar='"',quoting=csv.QUOTE_NONNUMERIC,mode='a')

    # Create .cli file
    # Extracts weather information from the weather_meta table and write the text file.       
    weatherparameters = read_weatherlongDB(stationtype) #returns a tuple
    CODEC="UTF-8"
    extension=".cli"
    filename = field_path+"\\"+stationtype+".cli"
    hourlyWeather = 0

#        print("Debug: weatherparameters=",weatherparameters)
#        print("Debug: filename=",filename)
    fh = QFile(filename) 
    header = ""
    val = ""
    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:            
        if(wind_flag == 0):
            header = "wind"
            val = str(weatherparameters[7])
        # IRAV is only used with daily data and if there is no column of rain intensity values
        if(hourly_flag == 0):
            header = header + "    irav"
            val = val + "    " + str(weatherparameters[8])
        header = header + "    ChemConc"
        val =  val + "    " + str(weatherparameters[9])
        if(co2_flag == 0):
            header = header + "    Co2"
            if CO2Var == "None":
                val =  val + "    " + str(weatherparameters[10])
            # Seinsitivity analyses CO2 variance
            else:
                val =  val + "    " + str(CO2Var)
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)
        #    0        1         2       3      4      5     6      7          8          9       10        11         12
        # Latitude, Longitude, Bsolar, Btemp, Atemp, BWInd, BIR, AvgWind, AvgRainRate, ChemCOnc, AvgCO2, stationtype, site
        fout<<"***STANDARD METEOROLOGICAL DATA  Header file for "<<stationtype<<"\n"
        fout<<"Latitude Longitude"<<"\n"
        fout<<'%-14.6f%-14.6f' %(weatherparameters[0],weatherparameters[1])<<"\n"
        fout<<"^Daily Bulb T(1) ^Daily Wind(2) ^RainIntensity(3) ^Daily Conc^(4) ^Furrow(5) ^Rel_humid(6) ^CO2(7)"<<"\n"
        fout<<'%-14d%-14d%-14d%-14d%-14d%-14d%-14d' %(0,wind_flag,hourly_flag,0,0,rh_flag,co2_flag)<<"\n"
        fout<<"Parameters for changing of units: BSOLAR BTEMP ATEMP ERAIN BWIND BIR "<<"\n"
        fout<<"BSOLAR is 1e6/3600 to go from j m-2 h-1 to wm-2"<<"\n"
        fout<<'%-14.1f%-14.1f%-14.4f%-14.1f%-14.1f%-14.1f' %(weatherparameters[2],weatherparameters[3],weatherparameters[4],0.1,weatherparameters[5],weatherparameters[6])<<"\n"
        fout<<"Average values for the site"<<"\n"
        fout<<header<<"\n"
        fout<<val<<"\n"            
    fh.close()
    return hourly_flag, edate


def WriteSoluteFile(soilname,field_name,field_path):
# Writes the SOLUTE FILE
    CODEC="UTF-8"
    filename = field_path+"\\NitrogenDefault.sol"        
    fh = QFile(filename)
        
    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:            
        soiltexture_list = read_soiltextureDB(soilname) #read soil file content 
        # 1 is the default solute record. Output type= tuple.
        # read solute file content
        solute_tuple = read_soluteDB(1)
        TextureCl=[] #empty list

        for irow in soiltexture_list:
            texture = Texture(irow[0],irow[2]).whatTexture()
            textures = list(filter(str.strip,texture.split("/")))
            if len(textures) >= 1:
                # Assumption: we won't have more than 2 textures, but choose the second one in that 
                # case. -1 will give last entry
                TextureCl.append(textures[-1])          

        #get dispersivity texture pairs
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)
            
        fout<<"*** SOLUTE MOVER PARAMETER INFORMATION ***"<<"\n"
        fout<<"Number of solutes"<<"\n"
        fout<<"1"<<"\n"
        fout<<"Computational parameters "<<"\n"
        fout<<"EPSI        lUpW             CourMax"<<"\n"
        fout<<'%-14.6f%-14.6f%-14.6f' %(solute_tuple[1],solute_tuple[2],solute_tuple[3])<<"\n"
        fout<<"Material Information"<<"\n"
        fout<<"Solute#, Ionic/molecular diffusion coefficients of solutes "<<"\n"
        fout<<'%-14.6f%-14.6f' %(1,solute_tuple[4])<<"\n"
        fout<<"Solute#, Layer#, Lingitudinal Dispersivity, Transversal Dispersivity (units are cm)"<<"\n"
            
        for counter in range(0,len(TextureCl)):
            dispersivity = read_dispersivityDB(TextureCl[counter])
            fout<<'%-14.6f%-14.6f%-14.6f%-14.6f' %(1,counter,dispersivity,dispersivity/2)<<"\n"
        fout<<"\n"                
    fh.close()


def WriteTimeFileData(treatmentname,experimentname,cropname,stationtype,hourlyFlag,field_name,field_path,hourly_flag,soilModel_flag):
#  Writes the Time information into *.tim FILE

    startdate ='Blank'
    enddate ='Blank'
    dt=0.0001
    dtMin=0.0000001
    DMul1 = 1.3
    DMul2 = 0.3
    CODEC="UTF-8"
    filename = field_path+'\\'+field_name + '.tim'
    fh = QFile(filename)
    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:      
        startdate = read_operation_timeDB2('Simulation Start',treatmentname, experimentname ,cropname)                 
        enddate = read_operation_timeDB2('Simulation End', treatmentname, experimentname ,cropname)   
            
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)            
        fout<<"*** SYNCHRONIZER INFORMATION *****************************"<<"\n"
        fout<<"Initial time       dt       dtMin     DMul1    DMul2    tFin"<<"\n"
        #fout<<"'%-16s'%-14.4f%-14.4f%-14.4f%-14.4f%-16s" %(startdate,dt,dtMin,DMul1,DMul2,enddate)<<"\n"
        fout<<"'%-10s'  %-14.4f%-14.10f%-14.4f%-14.4f'%-10s'" %(startdate,dt,dtMin,DMul1,DMul2,enddate)<<"\n"
        fout<<"Output variables, 1 if true  Daily    Hourly"<<"\n"
        fout<<'%-16d%-14d' %(1-hourlyFlag,hourlyFlag)<<"\n"
        fout<<"Daily Hourly Weather data frequency. if daily enter 1   0; if hourly enter 0  1"<<"\n"
        fout<<'%-16d%-14d' %(1-hourly_flag, hourly_flag)<<"\n"
        fout<<"run to end of soil model if 1, when crop matures the model ends, otherwise continues to stop date in time file"<<"\n"
        fout<<'%-14d' %(soilModel_flag)<<"\n\n"
    fh.close()


def WriteNitData(soilname,field_name,field_path,rowSpacing):
#  Writes Soil Nitrogen parameters into *.nit FILE

    # Nitrogen data from the soil
    soilnitrogen_list = read_soilnitrogenDB(soilname)
    NCount = len(soilnitrogen_list)        
    #maximum width of grid
    #get horizontal coordinates where fertilizer will be applied
    MaxX = rowSpacing/2

    CODEC="UTF-8"
    filename = field_path+"\\"+field_name+".nit"      
    fh = QFile(filename)

    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:                  
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)            
        fout<<" *** SoilNit parameters for location"<<"***\n"  #prefix details comes here.
        fout<<"ROW SPACING (m)"<<"\n"
        fout<<MaxX<<"\n"
        fout<<"                             Potential rate constants:       Ratios and fractions:"<<"\n"
        fout<<"m      kh     kL       km       kn        kd             fe   fh    r0   rL    rm   fa    nq   cs"<<"\n"
        for rrow in range(0,NCount):
            record_tuple=soilnitrogen_list[rrow]
            fout<<'%-14d%-14.5f%-14.3f%-14.6f%-14.1f%-14.5f%-14.1f%-14.1f%-14d%-14d%-14d%-14.1f%-14d%-14.5f' %(rrow+1,record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7],record_tuple[8],record_tuple[9],record_tuple[10],record_tuple[11],record_tuple[12])<<"\n"
    fh.close()


def WriteSoiData(soilname,field_name,field_path):
#  Writes Soil data into *.soi FILE

    # hydrology data from the soil
    soil_hydrology_list = read_soilhydroDB(soilname)   

    NCount = len(soil_hydrology_list)               
    CODEC="UTF-8"        
    #field_path = os.path.join(runpath1,field_name)
    filename = field_path+'\\'+soilname + '.soi'        
    fh = QFile(filename)

    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:                  
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)            
        fout<<"           *** Material information ****                                                                   g/g  \n"  #prefix details comes here.
        fout<<"   thr       ths         tha       th      Alfa      n        Ks         Kk       thk       BulkD     OM    Sand    Silt\n"
        for rrow in range(0,NCount):
            record_tuple=soil_hydrology_list[rrow]
            record_tuple = [float(i) for i in record_tuple]
            fout<<'%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f%-9.6f' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7],record_tuple[8],record_tuple[9],record_tuple[10],record_tuple[11],record_tuple[12])<<"\n"

    fh.close()
    filename = field_path+'\\'+field_name + '.dat'        
    fh = QFile(filename)

    soil_OM_list = read_soilOMDB(soilname)     
    NCount = len(soil_OM_list)
    #print("debug:soil texture",soil_OM_list,"\n")
    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:                  
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)            
        fout<<" Matnum      sand     silt    clay     bd     om   TH33       TH1500 \n"      
        for rrow in range(0,NCount):
            record_tuple=soil_OM_list[rrow]
            #print("debug:soil texture",record_tuple,"\n")
            fout<<'%-5d%-8.3f%-8.3f%-8.3f%-8.3f%-8.3f%-8.3f%-8.3f' %(record_tuple[0],record_tuple[1],record_tuple[2],record_tuple[3],record_tuple[4],record_tuple[5],record_tuple[6],record_tuple[7])<<"\n"

    fh.close()


def WriteRunFile(cropname,soilname,field_name,cultivar,field_path,stationtype):
#  Writes Run file with input data file names

    CODEC="UTF-8"        
    filename = field_path+"\\Run"+field_name+".dat"             
    fh = QFile(filename)
    hybridname = cultivar
    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:                  
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)            
        fout<<field_path<<"\\"<<stationtype<<".wea\n"
        fout<<field_path<<"\\"<<field_name<<".tim\n"
        fout<<field_path<<"\\"<<"BiologyDefault.bio\n"            
        fout<<field_path<<"\\"<<stationtype<<".cli\n"
        fout<<field_path<<"\\"<<field_name<<".nit\n"
        fout<<field_path<<"\\"<<"NitrogenDefault.sol\n"
        fout<<field_path<<"\\"<<soilname<<".soi\n"
        fout<<field_path<<"\\"<<field_name<<".man\n"
        fout<<field_path<<"\\"<<field_name<<".drp\n"
        fout<<field_path<<"\\"<<"Water.DAT\n"
        fout<<field_path<<"\\"<<"WatMovParam.dat\n"
        fout<<field_path<<"\\"<<field_name<<".ini\n"
        fout<<field_path<<"\\"<<hybridname<<".var\n"
        fout<<field_path<<"\\"<<field_name<<".grd\n"
        fout<<field_path<<"\\"<<field_name<<".nod\n"
        fout<<field_path<<"\\"<<"MassBI.dat\n"
        fout<<field_path<<"\\"<<field_name<<".g01\n"
        if cropname == "maize":
            fout<<field_path<<"\\"<<field_name<<".g02\n"
        else:
            fout<<field_path<<"\\"<<"plantstress.crp\n"
        fout<<field_path<<"\\"<<field_name<<".G03\n"
        fout<<field_path<<"\\"<<field_name<<".G04\n"
        fout<<field_path<<"\\"<<field_name<<".G05\n"
        fout<<field_path<<"\\"<<field_name<<".G06\n"
        fout<<field_path<<"\\"<<field_name<<".G07\n"
        fout<<field_path<<"\\"<<"MassBI.out\n"
        fout<<field_path<<"\\"<<"runoffmassbl.txt\n"
        if cropname == "cotton":
            fout<<field_path<<"\\"<<"Cotton.out\n"
            fout<<field_path<<"\\"<<"Cotton.sum\n"
        fh.close()


def WriteManagement(cropname,experiment,treatmentname,field_name,field_path,rowSpacing):
# Get data from operation, fertilizerOp and fertNutOp
 
    fertCount = 0
    PGRCount = 0

    #use crop to find exid in experiment table
    #use exid and treatmentname to find tid from treatment table
    # use tid(o_t_exid) to find all the operations
    operationList = []
    fDepth = []
    date = []
    ammtT = []
    ammtC = []
    ammtN = []
    PGRDate = []
    PGRChem =  []
    PGRAppMeth = []
    PGRBandwidth = []
    PGRAppRate = []
    PGRAppUnit = []

    exid = read_experimentDB_id(cropname,experiment)
    tid = read_treatmentDB_id(exid,treatmentname)
    operationList = read_operationsDB_id(tid)
    #print("op list=",operationList)
    factor= (rowSpacing/2)/10000

    for ii,jj in enumerate(operationList):
        if jj[1] == "Fertilizer":   
            fertInfo = readOpDetails(jj[0],jj[1])
            #print(fertInfo)
            for j in range(len(fertInfo)):
                # Need to get date and depth only once
                if j == 0:
                    # Depth
                    fDepth.append(fertInfo[j][4])
                    # Date
                    date.append(fertInfo[j][2])

                # FertilizationClass = Fertilizer-N, the ammtT is the ammount of Nitrogen 
                if fertInfo[j][3] == "Fertilizer-N":
                    ammtT.append(fertInfo[j][6]*factor*100)
                    ammtC.append(0)
                    ammtN.append(0)
                else:
                    if j == 0:
                        ammtT.append(0)
                    if fertInfo[j][5] == "Carbon (C)":
                        ammtC.append(fertInfo[j][6]*factor*100)
                    if fertInfo[j][5] == "Nitrogen (N)":
                        ammtN.append(fertInfo[j][6]*factor*100)
            fertCount=fertCount+1
        if jj[1] == "Plant Growth Regulator":
            PGRInfo = readOpDetails(jj[0],jj[1])
            PGRDate.append(PGRInfo[0][2])
            PGRChem.append(PGRInfo[0][3])
            PGRAppMeth.append(PGRInfo[0][8])
            PGRBandwidth.append(PGRInfo[0][5])
            PGRAppRate.append(PGRInfo[0][6])
            PGRAppUnit.append(PGRInfo[0][9])
            PGRCount=PGRCount+1

    # Write *.MAN file
    CODEC="UTF-8"
    filename = field_path+"\\"+field_name+".man"                
    fh = QFile(filename)
    placeholder = 0

    if not fh.open(QIODevice.WriteOnly|QIODevice.Text):
        print("Could not open file")
    else:
        fout = QTextStream(fh)            
        fout.setCodec(CODEC)
        fout<<"****Script for chemical application module  *******mg/cm2= kg/ha* 0.01*rwsp*eomult*100"<<"\n"
        fout<<"Number of Fertilizer applications (max=25) mappl is in total mg N applied to grid (1 kg/ha = 1 mg/m2/width of application) application divided by width of grid in cm is kg ha-1"<<"\n"                    
        fout<<'%-14d' %(fertCount)<<"\n"
        fout<<"tAppl(i)  AmtAppl(i)  depth(i)  mAppl_C(i)  mAppl_N(i)  (repeat these 3 lines for the number of fertilizer applications)"<<"\n"
        for j in range(len(date)):
            fout<<"'"<<date[j]<<"' "'%-14.6f%-14.6f%-14.6f%-14.6f' %(ammtT[j],fDepth[j],ammtC[j],ammtN[j])<<"\n"
        if cropname == "cotton":
            fout<<"[PGR]"<<"\n"
            fout<<"Number of PGR applications; 0: No PGR"<<"\n"
            fout<<'%-14d' %(PGRCount)<<"\n"
            fout<<"pgrDate		Brand	Appl_Method	Band_Width Appl_Rate	Appl_Unit"<<"\n"
            for j in range(len(PGRDate)):
                fout<<"'"<<PGRDate[j]<<"' '"<<PGRChem[j]<<"' "'%-14d%-14.6f%-14.6f%-14d' %(PGRAppMeth[j],PGRBandwidth[j],PGRAppRate[j],PGRAppUnit[j])<<"\n"
        fh.close()