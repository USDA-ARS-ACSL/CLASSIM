BEGIN TRANSACTION;
DROP TABLE IF EXISTS "plantStress_maize";
CREATE TABLE IF NOT EXISTS "plantStress_maize" (
	"plantStress_maize_id"	INTEGER NOT NULL,
	"Date_Time"	TEXT NOT NULL,
	"waterstress"	REAL,
	"N_stress"	REAL,
	"Shade_Stress"	REAL,
	"PotentialArea"	REAL
);
DROP TABLE IF EXISTS "g07_maize";
CREATE TABLE IF NOT EXISTS "g07_maize" (
	"g07_maize_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	REAL,
	"Y"	REAL,
	"Humus_N"	REAL,
	"Humus_C"	REAL,
	"Litter_N"	REAL,
	"Litter_C"	REAL,
	"Manure_N"	REAL,
	"Manure_C"	REAL,
	"Root_N"	REAL,
	"Root_C"	REAL
);
DROP TABLE IF EXISTS "g07_potato";
CREATE TABLE IF NOT EXISTS "g07_potato" (
	"g07_potato_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	REAL,
	"Y"	REAL,
	"Humus_N"	REAL,
	"Humus_C"	REAL,
	"Litter_N"	REAL,
	"Litter_C"	REAL,
	"Manure_N"	REAL,
	"Manure_C"	REAL,
	"Root_N"	REAL,
	"Root_C"	REAL
);
DROP TABLE IF EXISTS "g04_maize";
CREATE TABLE IF NOT EXISTS "g04_maize" (
	"g04_maize_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	REAL,
	"Y"	REAL,
	"Node"	REAL,
	"RMassM"	REAL,
	"RMassY"	REAL,
	"RDenM"	REAL,
	"RDenY"	REAL,
	"WaterSink"	REAL,
	"NitSink"	REAL,
	"GasSink"	REAL
);
DROP TABLE IF EXISTS "g04_cotton";
CREATE TABLE IF NOT EXISTS "g04_cotton" (
	"g04_cotton_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"X"	REAL,
	"Y"	REAL,
	"Node"	INTEGER,
	"RMassM"	REAL,
	"RMassY"	REAL,
	"RDenM"	REAL,
	"RDenY"	REAL,
	"WaterSink"	REAL,
	"NitSink"	REAL,
	"GasSink"	REAL
);
DROP TABLE IF EXISTS "g01_potato";
CREATE TABLE IF NOT EXISTS "g01_potato" (
	"g01_potato_id"	INTEGER NOT NULL,
	"Date_Time"	TEXT NOT NULL,
	"jday"	INTEGER NOT NULL,
	"LA_pl"	REAL,
	"LAI"	REAL,
	"PFD"	REAL,
	"SolRad"	REAL,
	"Tair"	REAL,
	"Tcan"	REAL,
	"Pgross"	REAL,
	"Rg+Rm"	REAL,
	"Tr-Pot"	REAL,
	"Tr-Act"	REAL,
	"Stage"	REAL,
	"totalDM"	REAL,
	"leafDM"	REAL,
	"stemDM"	REAL,
	"rootDM"	REAL,
	"tuberDM"	REAL,
	"deadDM"	REAL,
	"Cdead"	REAL,
	"Cpool"	REAL,
	"LWPpd"	REAL,
	"LWPave"	REAL,
	"gs_ave"	REAL,
	"Nstress1"	REAL,
	"Nstress2"	REAL,
	"Wstress1"	REAL,
	"Wstress2"	REAL,
	"Wstress3"	REAL
);
DROP TABLE IF EXISTS "nitrogen_potato";
CREATE TABLE IF NOT EXISTS "nitrogen_potato" (
	"nitrogen_potato_id"	INTEGER NOT NULL,
	"Date_Time"	INTEGER,
	"tot_N"	REAL,
	"leaf_N"	REAL,
	"stem_N"	REAL,
	"root_N"	REAL,
	"tuber_N"	REAL,
	"dead_N"	REAL,
	"tot_N_C"	REAL,
	"leaf_N_C"	REAL,
	"stem_N_C"	REAL,
	"root_N_C"	REAL,
	"tubr_N_C"	REAL,
	"N_uptake"	REAL,
	"N_demand"	REAL,
	"seed_N"	REAL,
	"Nstress"	REAL
);
DROP TABLE IF EXISTS "plantStress_potato";
CREATE TABLE IF NOT EXISTS "plantStress_potato" (
	"plantStress_potato_id"	INTEGER NOT NULL,
	"Date_Time"	TEXT,
	"waterstressfactor"	REAL,
	"PSIEffect_leaf"	INTEGER,
	"NEffect_leaf"	REAL,
	"PSIEffect_Pn"	REAL,
	"NEffect_Pn"	REAL,
	"Dev_stage"	REAL,
	"Heat_veg"	REAL,
	"Heat_repre"	REAL
);
DROP TABLE IF EXISTS "g07_fallow";
CREATE TABLE IF NOT EXISTS "g07_fallow" (
	"g07_fallow_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	REAL,
	"Y"	REAL,
	"Humus_N"	REAL,
	"Humus_C"	REAL,
	"Litter_N"	REAL,
	"Litter_C"	REAL,
	"Manure_N"	REAL,
	"Manure_C"	REAL,
	"Root_N"	REAL,
	"Root_C"	REAL
);
DROP TABLE IF EXISTS "g07_soybean";
CREATE TABLE IF NOT EXISTS "g07_soybean" (
	"g07_soybean_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	REAL,
	"Y"	REAL,
	"Humus_N"	REAL,
	"Humus_C"	REAL,
	"Litter_N"	REAL,
	"Litter_C"	REAL,
	"Manure_N"	REAL,
	"Manure_C"	REAL,
	"Root_N"	REAL,
	"Root_C"	REAL
);
DROP TABLE IF EXISTS "g07_cotton";
CREATE TABLE IF NOT EXISTS "g07_cotton" (
	"g07_cotton_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	REAL,
	"Y"	REAL,
	"Humus_N"	REAL,
	"Humus_C"	REAL,
	"Litter_N"	REAL,
	"Litter_C"	REAL,
	"Manure_N"	REAL,
	"Manure_C"	REAL,
	"Root_N"	REAL,
	"Root_C"	REAL
);
DROP TABLE IF EXISTS "g01_maize";
CREATE TABLE IF NOT EXISTS "g01_maize" (
	"g01_maize_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"jday"	INTEGER,
	"Leaves"	REAL,
	"MaturLvs"	INTEGER,
	"Dropped"	INTEGER,
	"LA_pl"	REAL,
	"LA_dead"	REAL,
	"LAI"	REAL,
	"RH"	REAL,
	"LeafWP"	REAL,
	"PFD"	REAL,
	"SolRad"	REAL,
	"SoilT"	REAL,
	"Tair"	REAL,
	"Tcan"	REAL,
	"ETdmd"	REAL,
	"ETsply"	REAL,
	"Pn"	REAL,
	"Pg"	REAL,
	"Respir"	REAL,
	"av_gs"	REAL,
	"VPD"	REAL,
	"Nitr"	REAL,
	"N_Dem"	REAL,
	"NUpt"	REAL,
	"LeafN"	REAL,
	"PCRL"	REAL,
	"totalDM"	REAL,
	"shootDM"	REAL,
	"earDM"	REAL,
	"TotLeafDM"	REAL,
	"DrpLfDM"	REAL,
	"stemDM"	REAL,
	"rootDM"	REAL,
	"SoilRt"	REAL,
	"MxRtDep"	REAL,
	"AvailW"	REAL,
	"solubleC"	REAL,
	"Note"	TEXT
);
DROP TABLE IF EXISTS "g01_soybean";
CREATE TABLE IF NOT EXISTS "g01_soybean" (
	"g01_soybean_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"jday"	INTEGER,
	"RSTAGE"	REAL,
	"VSTAGE"	REAL,
	"PFD"	REAL,
	"SolRad"	REAL,
	"Tair"	REAL,
	"Tcan"	REAL,
	"Pgross"	REAL,
	"Pnet"	REAL,
	"gs"	REAL,
	"PSIL"	REAL,
	"LAI"	REAL,
	"LAREAT"	REAL,
	"totalDM"	REAL,
	"rootDM"	REAL,
	"stemDM"	REAL,
	"leafDM"	REAL,
	"seedDM"	REAL,
	"podDM"	REAL,
	"DeadDM"	REAL,
	"Tr_pot"	REAL,
	"Tr_act"	REAL,
	"wstress"	REAL,
	"Nstress"	REAL,
	"Limit"	TEXT
);
DROP TABLE IF EXISTS "nitrogen_soybean";
CREATE TABLE IF NOT EXISTS "nitrogen_soybean" (
	"nitrogen_soybean_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"total_N"	REAL,
	"leaf_N"	REAL,
	"stem_N"	REAL,
	"pod_N"	REAL,
	"seed_N"	REAL,
	"root_N"	REAL,
	"dead_N"	REAL,
	"plant_N_C"	REAL,
	"N_uptake"	REAL,
	"N_demand"	REAL,
	"Nstress"	REAL
);
DROP TABLE IF EXISTS "plantStress_cotton";
CREATE TABLE IF NOT EXISTS "plantStress_cotton" (
	"plantStress_cotton_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"W_stress"	REAL,
	"N_Veg_Str"	REAL,
	"N_Fru_Str"	REAL,
	"N_Rt_Str"	REAL,
	"C_Stress"	REAL
);
DROP TABLE IF EXISTS "plantStress_soybean";
CREATE TABLE IF NOT EXISTS "plantStress_soybean" (
	"plantStress_soybean_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"wstress"	REAL,
	"Nstress"	REAL,
	"Cstress"	REAL,
	"NEffect_ve"	REAL,
	"wstress2"	REAL
);
DROP TABLE IF EXISTS "geometry";
CREATE TABLE IF NOT EXISTS "geometry" (
	"simID"	INTEGER,
	"nodeNum"	INTEGER,
	"X"	NUMERIC,
	"Y"	NUMERIC,
	"Layer"	INTEGER,
	"Area"	NUMERIC
);
DROP TABLE IF EXISTS "g04_potato";
CREATE TABLE IF NOT EXISTS "g04_potato" (
	"g04_potato_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"X"	REAL,
	"Y"	REAL,
	"Node"	INTEGER,
	"RMassM"	REAL,
	"RMassY"	REAL,
	"RDenM"	REAL,
	"RDenY"	REAL,
	"WaterSink"	REAL,
	"NitSink"	REAL,
	"GasSink"	REAL
);
DROP TABLE IF EXISTS "g04_soybean";
CREATE TABLE IF NOT EXISTS "g04_soybean" (
	"g04_soybean_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"X"	REAL,
	"Y"	REAL,
	"Node"	INTEGER,
	"RMassM"	REAL,
	"RMassY"	REAL,
	"RDenM"	REAL,
	"RDenY"	REAL,
	"WaterSink"	REAL,
	"NitSink"	REAL,
	"GasSink"	REAL
);
DROP TABLE IF EXISTS "plantStress_fallow";
CREATE TABLE IF NOT EXISTS "plantStress_fallow" (
	"date"	TEXT,
	"time"	TEXT,
	"waterstress"	TEXT,
	"N_stress"	TEXT,
	"Shade_Stress"	TEXT,
	"PotentialArea"	TEXT,
	"plantStress_fallow_id"	INTEGER
);
DROP TABLE IF EXISTS "g05_soybean";
CREATE TABLE IF NOT EXISTS "g05_soybean" (
	"g05_soybean_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"PSoilEvap"	REAL,
	"ASoilEVap"	REAL,
	"PET_PEN"	REAL,
	"PE_T_int"	REAL,
	"transp"	REAL,
	"CumRain"	REAL,
	"infil"	REAL,
	"FLuxAct"	REAL,
	"Drainage"	REAL,
	"N_Leach"	REAL DEFAULT 0,
	"Runoff"	REAL,
	"cover"	REAL,
	"PSIM"	REAL,
	"SeasPSoEv"	REAL,
	"SeasASoEv"	REAL,
	"SeasPTran"	REAL,
	"SeasATran"	REAL,
	"SeasRain"	REAL,
	"SeasInfil"	REAL,
	"CO2Flux"	REAL,
	"O2Flux"	REAL
);
DROP TABLE IF EXISTS "g03_potato";
CREATE TABLE IF NOT EXISTS "g03_potato" (
	"g03_potato_id"	INTEGER NOT NULL,
	"Date_Time"	TEXT NOT NULL,
	"X"	REAL,
	"Y"	REAL,
	"hNew"	REAL,
	"thNew"	REAL,
	"Q"	REAL,
	"NO3N"	REAL,
	"NH4N"	REAL,
	"Temp"	REAL,
	"CO2Conc"	REAL,
	"O2Conc"	REAL
);
DROP TABLE IF EXISTS "g03_cotton";
CREATE TABLE IF NOT EXISTS "g03_cotton" (
	"g03_cotton_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"X"	REAL,
	"Y"	REAL,
	"hNew"	NUMERIC,
	"thNew"	REAL,
	"Q"	REAL,
	"NO3N"	REAL,
	"NH4N"	REAL,
	"Temp"	REAL,
	"CO2Conc"	REAL,
	"O2Conc"	REAL
);
DROP TABLE IF EXISTS "g03_maize";
CREATE TABLE IF NOT EXISTS "g03_maize" (
	"g03_maize_id"	INTEGER,
	"Date_Time"	TEXT,
	"X"	NUMERIC,
	"Y"	NUMERIC,
	"hNew"	REAL,
	"thNew"	REAL,
	"Q"	REAL,
	"NO3N"	REAL,
	"NH4N"	REAL,
	"Temp"	REAL,
	"CO2Conc"	REAL,
	"O2Conc"	REAL
);
DROP TABLE IF EXISTS "g03_soybean";
CREATE TABLE IF NOT EXISTS "g03_soybean" (
	"g03_soybean_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"X"	NUMERIC,
	"Y"	NUMERIC,
	"hNew"	NUMERIC,
	"thNew"	REAL,
	"Q"	REAL,
	"NO3N"	REAL,
	"NH4N"	REAL,
	"Temp"	REAL,
	"CO2Conc"	REAL,
	"O2Conc"	REAL
);
DROP TABLE IF EXISTS "g05_cotton";
CREATE TABLE IF NOT EXISTS "g05_cotton" (
	"g05_cotton_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"PSoilEvap"	REAL,
	"ASoilEVap"	REAL,
	"PET_PEN"	REAL,
	"PE_T_int"	REAL,
	"transp"	REAL,
	"CumRain"	REAL,
	"infil"	REAL,
	"FLuxAct"	REAL,
	"Drainage"	REAL,
	"N_Leach"	REAL,
	"Runoff"	REAL,
	"cover"	REAL,
	"PSIM"	REAL,
	"SeasPSoEv"	REAL,
	"SeasASoEv"	REAL,
	"SeasPTran"	REAL,
	"SeasATran"	REAL,
	"SeasRain"	REAL,
	"SeasInfil"	REAL,
	"CO2Flux"	REAL,
	"O2Flux"	REAL
);
DROP TABLE IF EXISTS "g05_fallow";
CREATE TABLE IF NOT EXISTS "g05_fallow" (
	"g05_fallow_id"	INTEGER,
	"Date_Time"	REAL,
	"PSoilEvap"	REAL,
	"ASoilEVap"	REAL,
	"PET_PEN"	REAL,
	"PE_T_int"	REAL,
	"transp"	REAL,
	"CumRain"	REAL,
	"infil"	REAL,
	"FLuxAct"	REAL,
	"Drainage"	REAL,
	"N_Leach"	REAL,
	"Runoff"	REAL,
	"cover"	REAL,
	"PSIM"	REAL,
	"SeasPSoEv"	REAL,
	"SeasASoEv"	REAL,
	"SeasPTran"	REAL,
	"SeasATran"	REAL,
	"SeasRain"	REAL,
	"SeasInfil"	REAL,
	"CO2Flux"	REAL,
	"O2Flux"	REAL
);
DROP TABLE IF EXISTS "g05_maize";
CREATE TABLE IF NOT EXISTS "g05_maize" (
	"g05_maize_id"	INTEGER,
	"Date_Time"	TEXT,
	"PSoilEvap"	NUMERIC,
	"ASoilEVap"	REAL,
	"PET_PEN"	REAL,
	"PE_T_int"	REAL,
	"transp"	REAL,
	"CumRain"	REAL,
	"infil"	REAL,
	"FLuxAct"	REAL,
	"Drainage"	REAL,
	"N_Leach"	REAL,
	"Runoff"	REAL,
	"cover"	REAL,
	"PSIM"	REAL,
	"SeasPSoEv"	REAL,
	"SeasASoEv"	REAL,
	"SeasPTran"	REAL,
	"SeasATran"	REAL,
	"SeasRain"	REAL,
	"SeasInfil"	REAL,
	"CO2Flux"	REAL,
	"O2Flux"	REAL
);
DROP TABLE IF EXISTS "g05_potato";
CREATE TABLE IF NOT EXISTS "g05_potato" (
	"g05_potato_id"	INTEGER NOT NULL,
	"Date_Time"	TEXT NOT NULL,
	"PSoilEvap"	REAL,
	"ASoilEVap"	REAL,
	"PET_PEN"	REAL,
	"PE_T_int"	REAL,
	"transp"	REAL,
	"CumRain"	REAL,
	"infil"	REAL,
	"FLuxAct"	REAL,
	"Drainage"	REAL,
	"N_Leach"	REAL,
	"Runoff"	REAL,
	"cover"	REAL,
	"PSIM"	REAL,
	"SeasPSoEv"	REAL,
	"SeasASoEv"	REAL,
	"SeasPTran"	REAL,
	"SeasATran"	REAL,
	"SeasRain"	REAL,
	"SeasInfil"	REAL,
	"CO2Flux"	REAL,
	"O2Flux"	REAL
);
DROP TABLE IF EXISTS "g03_fallow";
CREATE TABLE IF NOT EXISTS "g03_fallow" (
	"g03_fallow_id"	INTEGER,
	"Date_Time"	REAL,
	"X"	REAL,
	"Y"	REAL,
	"hNew"	REAL,
	"thNew"	REAL,
	"Q"	REAL,
	"NO3N"	REAL,
	"NH4N"	REAL,
	"Temp"	REAL,
	"CO2Conc"	REAL,
	"O2Conc"	INTEGER
);
DROP TABLE IF EXISTS "g01_cotton";
CREATE TABLE IF NOT EXISTS "g01_cotton" (
	"g01_cotton_id"	INTEGER,
	"Date_Time"	TIMESTAMP,
	"PlantH"	REAL,
	"LAI"	REAL,
	"LInt"	REAL,
	"Nodes"	INTEGER,
	"Sites"	INTEGER,
	"N_Squares"	INTEGER,
	"N_GB"	INTEGER,
	"N_OB"	INTEGER,
	"NLvsLoss"	INTEGER,
	"NSqLoss"	INTEGER,
	"NBollsLoss"	INTEGER,
	"NFruitShed"	INTEGER,
	"PetShd_DM"	REAL,
	"GB_lossDM"	REAL,
	"Lf_lossDM"	REAL,
	"Rt_lossDM"	REAL,
	"Dd_WtDM"	REAL,
	"SquareDM"	REAL,
	"GB_DM"	REAL,
	"OB_DM"	REAL,
	"LeafDM"	REAL,
	"StemDM"	REAL,
	"RootDM"	NUMERIC,
	"ResC"	REAL,
	"PlantDM"	REAL,
	"R_S"	REAL,
	"Yield"	NUMERIC,
	"Temp"	REAL,
	"L_Temp"	REAL,
	"Rain"	REAL,
	"SRad"	INTEGER,
	"PFD"	REAL,
	"RH"	REAL,
	"LeafN"	REAL,
	"StemN"	REAL,
	"SeedN"	REAL,
	"BurrN"	REAL,
	"RootN"	REAL,
	"Nloss"	REAL,
	"PlantN"	REAL,
	"N_uptake"	REAL,
	"S_Psi"	REAL,
	"L_Psi"	REAL,
	"LArea"	REAL,
	"VPD"	REAL,
	"StCond"	REAL,
	"Pnet"	REAL,
	"PGross"	REAL,
	"L_Res"	REAL,
	"Main_Res"	REAL,
	"Resp"	REAL,
	"SPnet"	REAL,
	"C_Bal"	REAL,
	"Nstress_Pn"	REAL,
	"Note"	TEXT
);
COMMIT;
