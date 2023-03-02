import sys
import numpy as np
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import shutil
import time
from datetime import date, timedelta, datetime
from time import mktime
from shutil import copyfile

global app_dir
global index


'''
Generates dictionaries that will be used on outputTab.py and RotOutputTab.py.  The dictionaries correpond to 
tables on cropOutput database.
'''

def genDictOutput(cropArr,tabName,rotFlag):

    ########## plantTab ##########
    # g01_cropname table 
    # Maize
    varDescMaiDict = {'Leaves':'Number of leaves (appeared) (crop)','MaturLvs':'Number of mature leaves (crop)',
                      'Dropped':'Number of dropped leaves (crop)','LA_pl':'Green leaf area per plant (crop)',
                      'LA_dead':'Dead leaf area (crop)','LAI':'Leaf area index (crop)','RH':'Relative humidity (crop)',
                      'LeafWP':'Leaf water potential (crop)','PFD':'Photosynthetic flux density (crop)',
                      'SolRad':'Solar radiation (crop)','SoilT':'Soil temperature at soil surface (crop)',
                      'Tair':'Air temperture at 2m (crop)','Tcan':'Canopy temperature (crop)','ETdmd':'Potential Transpiration (crop)',
                      'ETsply':'Actual Transpiration (crop)','Pn':'Net Photosynthesis (crop)','Pg':'Gross photosynthesis (crop)',
                      'Respir':'Respiration (crop)','av_gs':'Average stomatal conductance (crop)','VPD':'Vapor pressure density (crop)',
                      'Nitr':'Total nitrogen in the plant (crop)','N_Dem':'Nitrogen demand (crop)','NUpt':'Nitrogen uptake (crop)',
                      'LeafN':'Leaf nitrogen content (crop)','PCRL':'Carbon allocated to roots (crop)','totalDM':'Total dry matter (crop)',
                      'shootDM':'Shoot dry matter (crop)','earDM':'Ear dry matter (crop)','TotLeafDM':'Leaf dry matter (crop)',
                      'DrpLfDM':'Dropped leaf dry matter (crop)','stemDM':'Stem dry matter (crop)','rootDM':'Root dry matter (crop)',
                      'SoilRt':'Soil root dry matter (crop)','MxRtDep':'Maximum root depth (crop)','AvailW':'Available water in root zone (crop)',
                      'solubleC':'Soluble sugars as carbon (crop)'}
    varDescUnitMaiDict = {'Leaves':'Number of leaves (appeared) (crop)','MaturLvs':'Number of mature leaves (crop)',
                          'Dropped':'Number of dropped leaves (crop)','LA_pl':'Green leaf area per plant (crop) (cm2)',
                          'LA_dead':'Dead leaf area (crop) (cm2)','LAI':'Leaf area index (crop)',
                          'RH':'Relative humidity (crop) (%)','LeafWP':'Leaf water potential (crop) (bars)',
                          'PFD':'Photosynthetic flux density (crop) (mol photons/day/m2)','SolRad':'Solar radiation (crop) (W/m2)',
                          'SoilT':'Soil temperature at soil surface (crop) (oC)','Tair':'Air temperture at 2m (crop) (oC)',
                          'Tcan':'Canopy temperature (crop) (oC)','ETdmd':'Potential Transpiration (crop) (g/plant)',
                          'ETsply':'Actual Transpiration (crop) (g/plant)','Pn':'Net Photosynthesis (crop) (g carbon/plant/day)',
                          'Pg':'Gross photosynthesis (crop) (g carbo/plant/day)','Respir':'Respiration (crop) (g carbon/plant/day)',
                          'av_gs':'Average stomatal conductance (crop)','VPD':'Vapor pressure density (crop) (kPa)',
                          'Nitr':'Total nitrogen in the plant (crop) (mg/plant)','N_Dem':'Nitrogen demand (crop) (g/plant)',
                          'NUpt':'Nitrogen uptake (crop) (g/plant)','LeafN':'Leaf nitrogen content (crop) (%)',
                          'PCRL':'Carbon allocated to roots (crop) (g/plant)','totalDM':'Total dry matter (crop) (g/plant)',
                          'shootDM':'Shoot dry matter (crop) (g/plant)','earDM':'Ear dry matter (crop) (g/plant)',
                          'TotLeafDM':'Leaf dry matter (crop) (g/plant)','DrpLfDM':'Dropped leaf dry matter (crop) (g/plant)',
                          'stemDM':'Stem dry matter (crop) (g/plant)','rootDM':'Root dry matter (crop) (g/plant)',
                          'SoilRt':'Soil root dry matter (crop) (g/plant)','MxRtDep':'Maximum root depth (crop) (cm)',
                          'AvailW':'Available water in root zone (crop) (g)','solubleC':'Soluble sugars as carbon (crop) (g/plant)'}
    varFuncMaiDict = {'Leaves':'max','MaturLvs':'max','Dropped':'max','LA_pl':'max','LA_dead':'max','LAI':'max',
                      'RH':'mean','LeafWP':'mean','PFD':'sum','SolRad':'mean','SoilT':'mean','Tair':'mean',
                      'Tcan':'mean','ETdmd':'sum','ETsply':'sum','Pn':'sum','Pg':'sum','Respir':'sum',
                      'av_gs':'mean','VPD':'mean','Nitr':'mean','N_Dem':'sum','NUpt':'sum','LeafN':'max',
                      'PCRL':'max','totalDM':'max','shootDM':'max','earDM':'max','TotLeafDM':'max','DrpLfDM':'max',
                      'stemDM':'max','rootDM':'max','SoilRt':'max','MxRtDep':'max','AvailW':'max','solubleC':'max'}

    # Potato
    varDescPotDict = {'LAI':'Leaf area index (crop)','PFD':'Photosynthetic flux density (crop)','SolRad':'Solar radiation (crop)',
                      'Tair':'Air temperture at 2m (crop)','Tcan':'Canopy temperature (crop)','Pgross':'Gross photosynthesis (crop)',
                      'Rg+Rm':'Respiration (crop)','Tr-Pot':'Potential Transpiration (crop)','Tr-Act':'Actual Transpiration (crop)',
                      'Stage':'Stage (crop)','totalDM':'Total dry matter (crop)','leafDM':'Leaf dry matter (crop)',
                      'stemDM':'Stem dry matter (crop)','rootDM':'Root dry matter (crop)','tuberDM':'Tuber dry matter (crop)',
                      'deadDM':'Dead dry matter (crop)','LWPave':'Leaf water potential (crop)','gs_ave':'Average stomatal conductance (crop)',
                      'N_uptake':'Nitrogen Uptake (crop)','tot_N':'Total Nitrogen in the Plant (crop)','leaf_N':'Leaf nitrogen (crop)',
                      'stem_N':'Stem nitrogen (crop)','root_N':'Root nitrogen (crop)','tuber_N':'Tuber nitrogen (crop)'}
    varDescUnitPotDict = {'LAI':'Leaf area index (crop)','PFD':'Photosynthetic flux density (crop) (mol photons/day/m2)',
                          'SolRad':'Solar radiation (crop) (W/m2)','Tair':'Air temperture at 2m (crop) (oC)',
                          'Tcan':'Canopy temperature (crop) (oC)','Pgross':'Gross photosynthesis (crop) (g carbon/plant/day)',
                          'Rg+Rm':'Respiration (crop) (g carbon/plant/day)','Tr-Pot':'Potential Transpiration (crop) (mg/plant)',
                          'Tr-Act':'Actual Transpiration (crop) (mg/plant)','Stage':'Stage (crop)',
                          'totalDM':'Total dry matter (crop) (g/plant)','leafDM':'Leaf dry matter (crop) (g/plant)',
                          'stemDM':'Stem dry matter (crop) (g/plant)','rootDM':'Root dry matter (crop) (g/plant)',
                          'tuberDM':'Tuber dry matter (crop) (g/plant)','deadDM':'Dead dry matter (crop) (g/plant)',
                          'LWPave':'Leaf water potential (crop) (bars)','gs_ave':'Average stomatal conductance (crop)',
                          'N_uptake':'Nitrogen Uptake (crop) (mg/plant)','tot_N':'Total Nitrogen in the Plant (crop) (mg/plant)',
                          'leaf_N':'Leaf nitrogen (crop) (mg/plant)','stem_N':'Stem nitrogen (crop) (mg/plant)',
                          'root_N':'Root nitrogen (crop) (mg/plant)','tuber_N':'Tuber nitrogen (crop) (mg/plant)'}
    varFuncPotDict = {'LAI':'max','PFD':'sum','SolRad':'mean','Tair':'mean','Tcan':'mean','Pgross':'sum',
                      'Rg+Rm':'sum','Tr-Pot':'sum','Tr-Act':'sum','Stage':'max','totalDM':'max','leafDM':'max',
                      'stemDM':'max','rootDM':'max','tuberDM':'max','deadDM':'max','LWPave':'mean','gs_ave':'mean',
                      'N_uptake':'mean','tot_N':'mean','leaf_N':'mean','stem_N':'mean','root_N':'mean','tuber_N':'mean'}

    # Soybean
    varDescSoyDict = {'PFD':'Photosynthetic flux density (crop)','SolRad':'Solar radiation (crop)','Tair':'Air temperture at 2m (crop)',
	                  'Tcan':'Canopy temperature (crop)','Pgross':'Gross photosynthesis (crop)','Pnet':'Net photosynthesis (crop)',
	                  'gs':'Maximum stomatal conductance (crop)','PSIL':'Leaf Water Potential (crop)','LAI':'Leaf area index (crop)',
	                  'LAREAT':'Leaf area (crop)','totalDM':'Total dry matter (crop)','rootDM':'Root dry matter (crop)',
                      'stemDM':'Stem dry matter (crop)','leafDM':'Leaf dry matter (crop)','seedDM':'Seed dry matter (crop)',
	                  'podDM':'Pod dry matter (crop)','DeadDM':'Dead dry matter (crop)','Tr_pot':'Potential Transpiration (crop)',
	                  'Tr_act':'Actual Transpiration (crop)'}
    varDescUnitSoyDict = {'PFD':'Photosynthetic flux density (crop) (mol photons/day/m2)','SolRad':'Solar radiation (crop) (W/m2)',
                          'Tair':'Air temperture at 2m (crop) (oC)','Tcan':'Canopy temperature (crop) (oC)',
                          'Pgross':'Gross photosynthesis (crop) (g carbon/plant/day)','Pnet':'Net photosynthesis (crop) (g carbon/plant/day)',
                          'gs':'Maximum stomatal conductance (crop)','PSIL':'Leaf Water Potential (crop) (bars)',
                          'LAI':'Leaf area index (crop)','LAREAT':'Leaf area (crop) (cm2)',
                          'totalDM':'Total dry matter (crop) (g/plant)','rootDM':'Root dry matter (crop) (g/plant)',
                          'stemDM':'Stem dry matter (crop) (g/plant)','leafDM':'Leaf dry matter (crop) (g/plant)',
                          'seedDM':'Seed dry matter (crop) (g/plant)','podDM':'Pod dry matter (crop) (g/plant)',
                          'DeadDM':'Dead dry matter (crop) (g/plant)','Tr_pot':'Potential Transpiration (crop) (mg/plant)',
                          'Tr_act':'Actual Transpiration (crop) (mg/plant)'}
    varFuncSoyDict = {'PFD':'sum','SolRad':'mean','Tair':'mean','Tcan':'mean','Pgross':'sum','Pnet':'sum',
                      'gs':'mean','PSIL':'mean','LAI':'max','LAREAT':'max','totalDM':'max','rootDM':'max',
                      'stemDM':'max','leafDM':'max','seedDM':'max','podDM':'max','DeadDM':'max','Tr_pot':'sum',
                      'Tr_act':'sum'}

    # Cotton
    varDescCotDict = {'PlantH':'Plant height (crop)','LAI':'Leaf area index (crop)','Nodes':'Number of main stem nodes (crop)',
                      'Sites':'Number of fruiting sites (crop)','N_Squares':'Number of squares (crop)','N_GB':'Number of green bolls (crop)',
                      'SquareDM':'Squares dry matter (crop)','GB_DM':'Green boll dry matter (crop)','OB_DM':'Open boll dry matter (crop)',
                      'LeafDM':'Leaf dry matter (crop)','StemDM':'Stem dry matter (crop)','RootDM':'Root dry matter (crop)','Yield':'Total yield (crop)',
                      'Temp':'Average temperature (crop)','L_Temp':'Average leaf temperature (crop)','Rain':'Rain+irrigation (crop)',
                      'SRad':'Solar radiation (crop)','RH':'Relative humidity (crop)','PlantN':'Total plant nitrogen (crop)',
                      'S_Psi':'Average soil water potential in the root zone (crop)','L_Psi':'Leaf water potential (crop)',
                      'LArea':'Leaf area (crop)','Pnet':'Net photosynthesis (crop)','SPnet':'Cumulative net photosynthesis (crop)'}
    varDescUnitCotDict = {'PlantH':'Plant height (crop) (in)','LAI':'Leaf area index (crop)','Nodes':'Number of main stem nodes (crop)',
                          'Sites':'Number of fruiting sites (crop)','N_Squares':'Number of squares (crop)','N_GB':'Number of green bolls (crop)',
                          'SquareDM':'Squares dry matter (crop) (g/plant)','GB_DM':'Green boll dry matter (crop) (g/plant)',
                          'OB_DM':'Open boll dry matter (crop) (g/plant)','LeafDM':'Leaf dry matter (crop) (g/plant)',
                          'StemDM':'Stem dry matter (crop) (g/plant)','RootDM':'Root dry matter (crop) (g/plant)','Yield':'Total yield (crop) (lb/acre)',
                          'Temp':'Average temperature (crop) (oC)','L_Temp':'Average leaf temperature (crop) (oC)','Rain':'Rain+irrigation (crop) (in/day)',
                          'SRad':'Solar radiation (crop) langley/day)','RH':'Relative humidity (crop) (%)','PlantN':'Total plant nitrogen (crop) (g/plant)',
                          'S_Psi':'Average soil water potential in the root zone (crop) (bar)','L_Psi':'Leaf water potential (crop) (bar)',
                          'LArea':'Leaf area (crop) (m2)','Pnet':'Net photosynthesis (crop) (g carbon/plant/day)',
                          'SPnet':'Cumulative net photosynthesis (crop) (g carbon/plant/day)'}
    varFuncCotDict = {'PlantH':'max','LAI':'max','Nodes':'max','Sites':'max','N_Squares':'max','N_GB':'max','SquareDM':'max',
                      'GB_DM':'max','OB_DM':'max','LeafDM':'max','StemDM':'max','RootDM':'max','Yield':'max','Temp':'max',
                      'L_Temp':'max','Rain':'max','SRad':'max','RH':'max','PlantN':'max','S_Psi':'max','L_Psi':'max',
                      'LArea':'max','Pnet':'max','SPnet':'max'}

    ########## Soil Carbon Nitrogen tab ##########
    # g07_cropname table 
    varSoilCNDescDict = {'Humus_N':'Amount of Nitrogen in Humus','Humus_C':'Amount of Carbon in Humus',
                         'Litter_N':'Amount of Nitrogen in Litter','Litter_C':'Amount of Carbon in Litter',
                         'Manure_N':'Amount of Nitrogen in Manure','Manure_C':'Amount of Carbon in Manure',
                         'Root_N':'Amount of Nitrogen in Root','Root_C':'Amount of Carbon in Root'}
    varSoilCNDescUnitDict = {'Humus_N':'Amount of Nitrogen in Humus (kg/ha)','Humus_C':'Amount of Carbon in Humus (kg/ha)',
                             'Litter_N':'Amount of Nitrogen in Litter (kg/ha)','Litter_C':'Amount of Carbon in Litter (kg/ha)',
                             'Manure_N':'Amount of Nitrogen in Manure (kg/ha)','Manure_C':'Amount of Carbon in Manure (kg/ha)',
                             'Root_N':'Amount of Nitrogen in Root (kg/ha)','Root_C':'Amount of Carbon in Root (kg/ha)'}
    varSoilCNFuncDict = {'Humus_N':'sum','Humus_C':'sum','Litter_N':'sum','Litter_C':'sum','Manure_N':'sum','Manure_C':'sum',
                         'Root_N':'sum','Root_C':'sum'}

    ########## Soil Water Heat Nitrogen components 2D ##########
    # g03_cropname table 
    # Same variables for all crops
    varSoilwhn2DDescDict = {"hNew":"Soil Matric Potential","thNew":"Soil Water Content",
                            "NO3N":"Nitrogen Concentration","Temp":"Temperature"}
    varSoilwhn2DDescUnitDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)",
                                "NO3N":"Nitrogen Concentration\n(mg/L)","Temp":"Temperature\n(oC)"}
    varSoilwhn2DFuncDict = {'hNew':'mean','thNew':'mean','NO3N':'mean','Temp':'mean'}

    ########## Soil Time Series ##########
    # g03_cropname table 
    # Same variables for all crops
    varSoilTSDescDict = {"hNew":"Soil Matric Potential","thNew":"Soil Water Content",
                         "NO3N":"Nitrogen Concentration","Temp":"Temperature"}
    varSoilTSDescUnitDict = {"hNew":"Soil Matric Potential\n(cm suction)","thNew":"Soil Water Content\n(cm3/cm3)",
                             "NO3N":"Nitrogen Concentration\n(mg/L)","Temp":"Temperature\n(oC)"}
    varSoilTSFuncDict = {'hNew':'mean','thNew':'mean','NO3N':'sum','Temp':'mean'}

    ########## Root tab ##########
    # g04_cropname table 
    # Same variables for all crops

    varRootDescDict = {"RDenT":"Root Density Total","RMassT":"Root Mass Total"}
    varRootDescUnitDict = {"RDenT":"Root Density Total (g/cm2)","RMassT":"Root Mass Total (g/cm2)"}
    varRootFuncDict = {'RDenT':'max','RMassT':'max'}
    
    ### Surface Characteristics tab ###
    # g05_cropname table 
    # Same variables for all crops
    varSurfChaDescDict = {'PSoilEvap':'Potential soil evaporation','ASoilEVap':'Actual Soil evaporation',
                          'PE_T_int':'Potential transpiration by leaf energy balance','transp':'Transpiration',
                          'SeasPSoEv':'Seasonal potential soil evaporation','SeasASoEv':'Seasonal actual soil evaporation',
                          'SeasPTran':'Seasonal potential transpiration','SeasATran':'Seasonal actual transpiration',
                          'SeasRain':'Seasonal rainfall','SeasInfil':'Seasonal infiltration','Runoff':'Runoff'}
    varSurfChaDescUnitDict = {'PSoilEvap':'Potential soil evaporation (mm/cm2)','ASoilEVap':'Actual Soil evaporation (mm/cm2)',
                              'PE_T_int':'Potential transpiration by leaf energy balance (mm/cm2)','transp':'Transpiration (mm/cm2)',
                              'SeasPSoEv':'Seasonal potential soil evaporation (mm/cm2)','SeasASoEv':'Seasonal actual soil evaporation (mm/cm2)',
                              'SeasPTran':'Seasonal potential transpiration (mm/cm2)','SeasATran':'Seasonal actual transpiration (mm/cm2)',
                              'SeasRain':'Seasonal rainfall (mm/cm2)','SeasInfil':'Seasonal infiltration (mm/cm2)','Runoff':'Runoff (mm/cm2)'}
    varSurfChaFuncDict = {'PSoilEvap':'sum','ASoilEVap':'sum','PE_T_int':'sum','transp':'sum','SeasPSoEv':'sum',
                          'SeasASoEv':'max','SeasPTran':'max','SeasATran':'max','SeasRain':'max','SeasInfil':'max',
                          'Runoff':'sum'}

    # The dictionary for plant will not be the same for simulation and rotation
    if tabName  == "plant":  
        # Single simulation
        if rotFlag == 0:
            finalVarDescDict = dict()
            finalVarDescUnitDict = dict()
            finalVarFuncDict = dict()
            if cropArr[0] == "maize":
                finalVarDescDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescMaiDict.items()}
                finalVarDescUnitDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescUnitMaiDict.items()}
                finalVarFuncDict = {f"{key}": str(val).replace("(crop)","") for key, val in varFuncMaiDict.items()}
            elif cropArr[0] == "potato":
                finalVarDescDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescPotDict.items()}
                finalVarDescUnitDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescUnitPotDict.items()}
                finalVarFuncDict = {f"{key}": str(val).replace("(crop)","") for key, val in varFuncPotDict.items()}
            elif cropArr[0] == "soybean":
                finalVarDescDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescSoyDict.items()}
                finalVarDescUnitDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescUnitSoyDict.items()}
                finalVarFuncDict = {f"{key}": str(val).replace("(crop)","") for key, val in varFuncSoyDict.items()}
            elif cropArr[0] == "cotton":
                finalVarDescDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescCotDict.items()}
                finalVarDescUnitDict = {f"{key}": str(val).replace("(crop)","") for key, val in varDescUnitCotDict.items()}
                finalVarFuncDict = {f"{key}": str(val).replace("(crop)","") for key, val in varFuncCotDict.items()}

            return finalVarDescDict, finalVarDescUnitDict, finalVarFuncDict
        else:
            finalVarDescDict = dict()
            finalVarDescUnitDict = dict()
            finalVarFuncDict = dict()
            for runNum in range(len(cropArr)):
                tempVarDescDict = dict()
                tempVarDescUnitDict = dict()
                tempVarFuncDict = dict()

                if cropArr[runNum] == "maize":
                    tempVarDescDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescMaiDict.items()}
                    tempVarDescUnitDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescUnitMaiDict.items()}
                    tempVarFuncDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varFuncMaiDict.items()}
                elif cropArr[runNum] == "potato":
                    tempVarDescDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescPotDict.items()}
                    tempVarDescUnitDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescUnitPotDict.items()}
                    tempVarFuncDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varFuncPotDict.items()}
                elif cropArr[runNum] == "soybean":
                    tempVarDescDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescSoyDict.items()}
                    tempVarDescUnitDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescUnitSoyDict.items()}
                    tempVarFuncDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varFuncSoyDict.items()}
                elif cropArr[runNum] == "cotton":
                    tempVarDescDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescCotDict.items()}
                    tempVarDescUnitDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varDescUnitCotDict.items()}
                    tempVarFuncDict = {f"{key}__{cropArr[runNum][0:3]}": str(val).replace("crop",cropArr[runNum]) for key, val in varFuncCotDict.items()}

                finalVarDescDict.update(tempVarDescDict) 
                finalVarDescUnitDict.update(tempVarDescUnitDict) 
                finalVarFuncDict.update(tempVarFuncDict) 

            return finalVarDescDict, finalVarDescUnitDict, finalVarFuncDict
    elif tabName  == "soilCN":
        return varSoilCNDescDict, varSoilCNDescUnitDict, varSoilCNFuncDict
    elif tabName  == "soilwhn2D":
        return varSoilwhn2DDescDict, varSoilwhn2DDescUnitDict, varSoilwhn2DFuncDict
    elif tabName  == "soilTS":
        return varSoilTSDescDict, varSoilTSDescUnitDict, varSoilTSFuncDict
    elif tabName  == "root":
        return varRootDescDict, varRootDescUnitDict, varRootFuncDict
    elif tabName  == "surfCha":
        return varSurfChaDescDict, varSurfChaDescUnitDict, varSurfChaFuncDict