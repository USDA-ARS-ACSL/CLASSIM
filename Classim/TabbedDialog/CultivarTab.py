from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QTreeWidgetItem, QWidget, QLabel, QHBoxLayout, QComboBox, QVBoxLayout, QPushButton, QSpacerItem, \
                            QSizePolicy, QRadioButton, QButtonGroup, QScrollArea, QGridLayout, QCheckBox, QHeaderView
from PyQt5.QtCore import pyqtSlot
from CustomTool.custom1 import *
from CustomTool.UI import *
from DatabaseSys.Databasesupport import *
from Models.cropdata import *
from TabbedDialog.tableWithSignalSlot import *

import re

'''
Contains 1 Class.
1). Class Cultivar_Widget is derived from Qwidget. It is initialed and called by Tabs.py -> class Tabs_Widget.
    It handles all the features of Cultivar Tab on the interface.  It has signal slot mechanism. It 
    interact with the DatabaseSys\Databasesupport.py for all the databases related task.
    Pretty generic and self explanotory methods. 
    Refer baseline classes at http://pyqt.sourceforge.net/Docs/PyQt5/QtWidgets.html#PyQt5-QtWidgets

    Tab screen is divided into 2 main panels.
    Left panel does the heavy lifting and interacts with user. 
    Right panel is mainly for frequently asked questions (FAQ) stored in sqlite table "Faq".
'''

#this is widget of type 1. It would be added to as a tab
class Cultivar_Widget(QWidget):
    def __init__(self):
        super(Cultivar_Widget,self).__init__()
        self.init_ui()


    def init_ui(self):
        self.setGeometry(QtCore.QRect(10,20,700,700))
    #   self.setFont(QtGui.QFont("Calibri",10))
        self.faqtree = QtWidgets.QTreeWidget(self)   
        self.faqtree.setHeaderLabel('FAQ')     
        self.faqtree.setGeometry(500,200, 400, 400)
        self.faqtree.setUniformRowHeights(False)
        self.faqtree.setWordWrap(True)
    #   self.faqtree.setFont(QtGui.QFont("Calibri",10))        
        self.faqtree.header().setStretchLastSection(False)  
        self.faqtree.header().setSectionResizeMode(QHeaderView.ResizeToContents)  
        self.faqtree.setVisible(False)

        self.tab_summary = QTextEdit("")        
        self.tab_summary.setPlainText("CULITVAR means different varieties of a CROP. For example, maize crop could be 90 or 120 maturity day crop. There are other specific parameters related to a crop variety. This tab allows to build a new crop variety from the default one and customize it further needs.") 
        self.tab_summary.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tab_summary.setReadOnly(True)  
        self.tab_summary.setMinimumHeight(40)    
        self.tab_summary.setAlignment(QtCore.Qt.AlignTop)
        self.helpcheckbox = QCheckBox("Turn FAQ on?")
        self.helpcheckbox.setChecked(False)
        self.helpcheckbox.stateChanged.connect(self.controlfaq)

        urlLink="<a href=\"https://www.ars.usda.gov/northeast-area/beltsville-md-barc/beltsville-agricultural-research-center/adaptive-cropping-systems-laboratory/\">Click here \
                to watch the Cultivar Tab Video Tutorial</a><br>"
        self.cultivarVidlabel=QLabel()
        self.cultivarVidlabel.setOpenExternalLinks(True)
        self.cultivarVidlabel.setText(urlLink)
  
        self.hbox = QHBoxLayout()    
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.mainlayout = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.hbox.addWidget(self.scrollArea)
        self.spacer = QSpacerItem(10,10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vHeader = QVBoxLayout()
        self.vHeader.setContentsMargins(0,0,0,0)
        self.vHeader.addWidget(self.tab_summary)
        self.vHeader.addWidget(self.cultivarVidlabel)
        self.vHeader.addWidget(self.helpcheckbox)
        self.vHeader.setAlignment(QtCore.Qt.AlignTop)

        ## Setting up the form elements    
        self.croplistlabel = QLabel("Select Crop")        
        self.cropcombo = QComboBox()       
        self.croplistlabel.setBuddy(self.cropcombo)
        self.croplists = read_cropDB()        
        self.cropcombo.addItem("Select a crop") 
        for key in self.croplists:    
            if key != "fallow":        
                self.cropcombo.addItem(key)
        self.cropcombo.currentIndexChanged.connect(self.showcultivarcombo)

        self.cultivarlistlabel = QLabel("Cultivar List")
        self.cultivarcombo = QComboBox()
        self.cultivarlistlabel.setBuddy(self.cultivarcombo)

        ###### Creating maize fields #####
        self.daylengthabel = QLabel("Daylength Sensitive")
        self.daylength_b1 = QRadioButton("Yes")
        self.daylength_b2 = QRadioButton("No")
        self.daylength_g = QButtonGroup()
        self.daylength_b1.setChecked(True)
        self.daylength_g.addButton(self.daylength_b1,1)
        self.daylength_g.addButton(self.daylength_b2,2)
        self.leaveslabel = QLabel("JuvenileLeaves")
        self.leavesedit = QLineEdit("")
        self.ltarlabel = QLabel("Rmax_LTAR")
        self.ltaredit = QLineEdit("0.46")
        self.ltirlabel = QLabel("Rmax_LTIR")
        self.ltiredit = QLineEdit("0.8")
        self.tassellabel = QLabel("PhyllFrmTassel")
        self.tasseledit = QLineEdit("4.0")
        self.staygreenlavel = QLabel("StayGreen")
        self.staygreenedit = QLineEdit("2.0")

        ###### Creating potato fields #####
        self.dailyAirTempEffectLabel = QLabel("Daily Air Temperature Effect")
        self.dailyAirTempEffectEdit = QLineEdit("")
        self.dailyAirTempAmpEffectLabel = QLabel("Daily Air Temperature Amplitude Effect")
        self.dailyAirTempAmpEffectEdit = QLineEdit("")
        self.photoEffectLabel = QLabel("Photoperiod Effect")
        self.photoEffectEdit = QLineEdit("")
        self.highNiEffectLabel = QLabel("High Nitrogen Effect")
        self.highNiEffectEdit = QLineEdit("")
        self.lowNiEffectLabel = QLabel("Low Nitrogen Effect")
        self.lowNiEffectEdit = QLineEdit("")
        self.determLabel = QLabel("Determinacy")
        self.determEdit = QLineEdit("")
        self.maxCanLeafExpRateLabel = QLabel("Maximum Canopy Leaf Expansion Rate")
        self.maxCanLeafExpRateEdit = QLineEdit("")
        self.maxTuberGrowthRateLabel = QLabel("Maximum Tuber Growth Rate")
        self.maxTuberGrowthRateEdit = QLineEdit("")
        self.specificLeafWeightLabel = QLabel("Specific Leaf Weight")
        self.specificLeafWeightEdit = QLineEdit("")

        ###### Creating soybean fields #####
        self.matGrpLabel = QLabel("Maturity Group")
        self.matGrpEdit = QLineEdit("2.7")
        self.seedLbLabel = QLabel("Number of Seeds per Pound Weight Typical for Cultivar")
        self.seedLbEdit = QLineEdit("3800")
        self.fillLabel = QLabel("Seed Fill Rate at 24oC")
        self.fillEdit = QLineEdit("7.5")
        self.v1Label = QLabel("Slope of the Dependence of Vegetative Stage on Temperature Integral")
        self.v1Edit = QLineEdit("0.00894")
        self.v2Label = QLabel("Maximum Vegetative Stage")
        self.v2Edit = QLineEdit("14.6")
        self.v3Label = QLabel("Correction Factor for the Early Vegetative Rate to Account for Clay Content")
        self.v3Edit = QLineEdit("0.5")
        self.r1Label = QLabel("Progress Rate towards Floral Initiation Before Solstice")
        self.r1Edit = QLineEdit("0.0198")
        self.r2Label = QLabel("Daily Rate of the Progress to Floral Initiation at Solstice")
        self.r2Edit = QLineEdit("0.0119")
        self.r3Label = QLabel("Daily Rate of the Progress to Floral Initiation After Solstice")
        self.r3Edit = QLineEdit("-0.0907")
        self.r4Label = QLabel("Progress Rate from Floral Initiation towards Full Bloom")
        self.r4Edit = QLineEdit("0.194")
        self.r5Label = QLabel("Slope of the Dependence of Full Bloom End on the Julian Day First")
        self.r5Edit = QLineEdit("0.522")
        self.r6Label = QLabel("Intercept of the Dependence of Full Bloom End on the Julian Day First")
        self.r6Edit = QLineEdit("132.1")
        self.r7Label = QLabel("Progress Rate from Full Bloom towards Full Seed")
        self.r7Edit = QLineEdit("0.00402")
        self.r8Label = QLabel("Length of the Plateau First Seed")
        self.r8Edit = QLineEdit("42")
        self.r9Label = QLabel("Length of the Plateau Full Seed with no Stress")
        self.r9Edit = QLineEdit("250")
        self.r10Label = QLabel("Rate of the Decay of the Full Seed Plateau as the Stress Increases")
        self.r10Edit = QLineEdit("0.5")
        self.r11Label = QLabel("Rate of the Progress towards Physiological Maturity")
        self.r11Edit = QLineEdit("0.008")
        self.r12Label = QLabel("Reproductive Stage to Stop Vegetative Growth")
        self.r12Edit = QLineEdit("5")
        self.g1Label = QLabel("Relates Potential Elongation and Dry Weight Increase Petioles")
        self.g1Edit = QLineEdit("0.0024")
        self.g2Label = QLabel("Potential Rate of the Root Weight Increase")
        self.g2Edit = QLineEdit("0.5")
        self.g3Label = QLabel("Relates to Increase in Pod Weight and Progress in Reproductive Stages")
        self.g3Edit = QLineEdit("2.2")
        self.g4Label = QLabel("Relates to Increase in Seed Weight and Fill")
        self.g4Edit = QLineEdit("2.8")
        self.g5Label = QLabel("Coefficient 'a' in Relationship between Height and Vegetative Stages")
        self.g5Edit = QLineEdit("1")
        self.g6Label = QLabel("Coefficient 'b' in Relationship between Height and Vegetative Stages")
        self.g6Edit = QLineEdit("1.684")
        self.g7Label = QLabel("Relates Number of Branches with the Plant Density")
        self.g7Edit = QLineEdit("0.5")
        self.g8Label = QLabel("Relates Stem Weight to Stem Elongation")
        self.g8Edit = QLineEdit("1.3")
        self.g9Label = QLabel("Relates Increment in Leaf Area to Increment in Vegetative Stages")
        self.g9Edit = QLineEdit("1")

        # Creating cotton fields
        self.calbrt11Label = QLabel("Relates boll safe age from abscission with age fo the boll, C and N-stress")
        self.calbrt11Edit = QLineEdit("4")
        self.calbrt12Label = QLabel("Maximum boll size")
        self.calbrt12Edit = QLineEdit("6.75")
        self.calbrt13Label = QLabel("Number of days after emergence that controls C-allocation in to stem")
        self.calbrt13Edit = QLineEdit("35")
        self.calbrt15Label = QLabel("Factor for C-allocation to stem for days after emergence > variety parameter 13")
        self.calbrt15Edit = QLineEdit("0.85")
        self.calbrt16Label = QLabel("Minimum leaf water potential for the day in well-watered soil in the estimation of stem growth water stress")
        self.calbrt16Edit = QLineEdit("-0.9")
        self.calbrt17Label = QLabel("Parameter in the estimation of potential square growth")
        self.calbrt17Edit = QLineEdit("0.9")
        self.calbrt18Label = QLabel("Parameter in the estimation of potential boll growth")
        self.calbrt18Edit = QLineEdit("0")
        self.calbrt19Label = QLabel("Parameter in the estimation of morphogenetic delays due to N-stress")
        self.calbrt19Edit = QLineEdit("1.5")
        self.calbrt22Label = QLabel("Correction factor for root/shoot ratio")
        self.calbrt22Edit = QLineEdit("1")
        self.calbrt26Label = QLabel("Parameter in the estimation time interval between pre-fruiting node")
        self.calbrt26Edit = QLineEdit("1.35")
        self.calbrt27Label = QLabel("Parameter in the estimation of time interval between nodes in the main stem and fruiting branch ")
        self.calbrt27Edit = QLineEdit("1")
        self.calbrt28Label = QLabel("Parameter in the estimation of time interval between nodes in the vegetative branches")
        self.calbrt28Edit = QLineEdit("1")
        self.calbrt29Label = QLabel("Parameter in the estimation of time from emergence to first square")
        self.calbrt29Edit = QLineEdit("0.9")
        self.calbrt30Label = QLabel("Parameter in the estimation of time from first square to bloom")
        self.calbrt30Edit = QLineEdit("1.15")
        self.calbrt31Label = QLabel("Parameter in the estimation of time from emergence to open boll")
        self.calbrt31Edit = QLineEdit("1.1")
        self.calbrt32Label = QLabel("Parameter in the estimation of leaf growth water stress ")
        self.calbrt32Edit = QLineEdit("1")
        self.calbrt33Label = QLabel("Minimum leaf water potential in well-watered soil in the estimation of leaf growth water stress")
        self.calbrt33Edit = QLineEdit("-0.85")
        self.calbrt34Label = QLabel("Parameter in the estimation of potential daily change in pre-fruiting leaf area")
        self.calbrt34Edit = QLineEdit("1")
        self.calbrt35Label = QLabel("Parameter in the estimation of potential daily change in mainstem leaf area")
        self.calbrt35Edit = QLineEdit("1")
        self.calbrt36Label = QLabel("Parameter in the estimation of potential daily change in mainstem and pre fruiting leaf weight")
        self.calbrt36Edit = QLineEdit("1.1")
        self.calbrt37Label = QLabel("Minimum LAI that affects boll temperature")
        self.calbrt37Edit = QLineEdit("3")
        self.calbrt38Label = QLabel("Parameter in the estimation of leaf age")
        self.calbrt38Edit = QLineEdit("0.75")
        self.calbrt39Label = QLabel("Parameter in the estimation of the physiological days for leaf abscission")
        self.calbrt39Edit = QLineEdit("1")
        self.calbrt40Label = QLabel("Parameter in the estimation of duration of leaf area expansion")
        self.calbrt40Edit = QLineEdit("2.5")
        self.calbrt41Label = QLabel("Parameter in the estimation of pre-fruiting leaf area at unfolding")
        self.calbrt41Edit = QLineEdit("1")
        self.calbrt42Label = QLabel("Parameter in the estimation of  mainstem leaf area at unfolding")
        self.calbrt42Edit = QLineEdit("1")
        self.calbrt43Label = QLabel("Parameter in the estimation of fruiting branch leaf area at unfolding")
        self.calbrt43Edit = QLineEdit("0.9")
        self.calbrt44Label = QLabel("Parameter in the estimation of internode elongation duration in plant height calculation")
        self.calbrt44Edit = QLineEdit("1")
        self.calbrt45Label = QLabel("Parameter in the estimation of initial internode length in plant height calculation")
        self.calbrt45Edit = QLineEdit("0.8")
        self.calbrt47Label = QLabel("Parameter in the estimation of reduction to initial internode length when the number of main stem nodes < 14")
        self.calbrt47Edit = QLineEdit("1.1")
        self.calbrt48Label = QLabel("Parameter in the estimation of reduction to initial internode length when the number of main stem nodes>=14")
        self.calbrt48Edit = QLineEdit("0.9")
        self.calbrt49Label = QLabel("Parameter in the estimation of current internode length")
        self.calbrt49Edit = QLineEdit("0.7")
        self.calbrt50Label = QLabel("Parameter in the estimation of bolls lost due to heat injury")
        self.calbrt50Edit = QLineEdit("1")
        self.calbrt52Label = QLabel("Relates potential fruit growth with temperature stress")
        self.calbrt52Edit = QLineEdit("1.35")
        self.calbrt57Label = QLabel("Relates potential fruit growth with water and temperature stress")
        self.calbrt57Edit = QLineEdit("1")

        self.cultivarnamelabel = QLabel("Cultivar Name")
        self.cultivarnameedit = QLineEdit("")
        self.cultivarbutton = QPushButton("Update")
        self.cultivardeletebutton = QPushButton("Delete")

        # Set main layout
        self.mainlayout.addLayout(self.vHeader,0,0,1,4)
        self.mainlayout.addWidget(self.faqtree,0,4,2,1)       
        self.mainlayout.addWidget(self.croplistlabel,1,0)
        self.mainlayout.addWidget(self.cropcombo,1,1,1,2)
        self.mainlayout.addWidget(self.cultivarlistlabel,2,0)
        self.mainlayout.addWidget(self.cultivarcombo,2,1,1,2)
 
        # maize
        self.mainlayout.addWidget(self.daylengthabel,3,0)
        self.mainlayout.addWidget(self.daylength_b1,3,1)
        self.mainlayout.addWidget(self.daylength_b2,3,2)
        self.mainlayout.addWidget(self.leaveslabel,4,0)
        self.mainlayout.addWidget(self.leavesedit,4,1,1,2)
        self.mainlayout.addWidget(self.ltarlabel,5,0)
        self.mainlayout.addWidget(self.ltaredit,5,1,1,2)
        self.mainlayout.addWidget(self.ltirlabel,6,0)
        self.mainlayout.addWidget(self.ltiredit,6,1,1,2)
        self.mainlayout.addWidget(self.tassellabel,7,0)
        self.mainlayout.addWidget(self.tasseledit,7,1,1,2)
        self.mainlayout.addWidget(self.staygreenlavel,8,0)
        self.mainlayout.addWidget(self.staygreenedit,8,1,1,2)

        # Potato
        self.mainlayout.addWidget(self.dailyAirTempEffectLabel,9,0)
        self.mainlayout.addWidget(self.dailyAirTempEffectEdit,9,1,1,2)
        self.mainlayout.addWidget(self.dailyAirTempAmpEffectLabel,10,0)
        self.mainlayout.addWidget(self.dailyAirTempAmpEffectEdit,10,1,1,2)
        self.mainlayout.addWidget(self.photoEffectLabel,11,0)
        self.mainlayout.addWidget(self.photoEffectEdit,11,1,1,2)
        self.mainlayout.addWidget(self.highNiEffectLabel,12,0)
        self.mainlayout.addWidget(self.highNiEffectEdit,12,1,1,2)
        self.mainlayout.addWidget(self.lowNiEffectLabel,13,0)
        self.mainlayout.addWidget(self.lowNiEffectEdit,13,1,1,2)
        self.mainlayout.addWidget(self.determLabel,14,0)
        self.mainlayout.addWidget(self.determEdit,14,1,1,2)
        self.mainlayout.addWidget(self.maxCanLeafExpRateLabel,15,0)
        self.mainlayout.addWidget(self.maxCanLeafExpRateEdit,15,1,1,2)
        self.mainlayout.addWidget(self.maxTuberGrowthRateLabel,16,0)
        self.mainlayout.addWidget(self.maxTuberGrowthRateEdit,16,1,1,2)
        self.mainlayout.addWidget(self.specificLeafWeightLabel,17,0)
        self.mainlayout.addWidget(self.specificLeafWeightEdit,17,1,1,2)

        # Soybean
        self.mainlayout.addWidget(self.matGrpLabel,18,0)
        self.mainlayout.addWidget(self.matGrpEdit,18,1,1,2)
        self.mainlayout.addWidget(self.seedLbLabel,19,0)
        self.mainlayout.addWidget(self.seedLbEdit,19,1,1,2)
        self.mainlayout.addWidget(self.fillLabel,20,0)
        self.mainlayout.addWidget(self.fillEdit,20,1,1,2)
        self.mainlayout.addWidget(self.v1Label,21,0)
        self.mainlayout.addWidget(self.v1Edit,21,1,1,2)
        self.mainlayout.addWidget(self.v2Label,22,0)
        self.mainlayout.addWidget(self.v2Edit,22,1,1,2)
        self.mainlayout.addWidget(self.v3Label,23,0)
        self.mainlayout.addWidget(self.v3Edit,23,1,1,2)
        self.mainlayout.addWidget(self.r1Label,24,0)
        self.mainlayout.addWidget(self.r1Edit,24,1,1,2)
        self.mainlayout.addWidget(self.r2Label,25,0)
        self.mainlayout.addWidget(self.r2Edit,25,1,1,2)
        self.mainlayout.addWidget(self.r3Label,26,0)
        self.mainlayout.addWidget(self.r3Edit,26,1,1,2)
        self.mainlayout.addWidget(self.r4Label,27,0)
        self.mainlayout.addWidget(self.r4Edit,27,1,1,2)
        self.mainlayout.addWidget(self.r5Label,28,0)
        self.mainlayout.addWidget(self.r5Edit,28,1,1,2)
        self.mainlayout.addWidget(self.r6Label,29,0)
        self.mainlayout.addWidget(self.r6Edit,29,1,1,2)
        self.mainlayout.addWidget(self.r7Label,30,0)
        self.mainlayout.addWidget(self.r7Edit,30,1,1,2)
        self.mainlayout.addWidget(self.r8Label,31,0)
        self.mainlayout.addWidget(self.r8Edit,31,1,1,2)
        self.mainlayout.addWidget(self.r9Label,32,0)
        self.mainlayout.addWidget(self.r9Edit,32,1,1,2)
        self.mainlayout.addWidget(self.r10Label,33,0)
        self.mainlayout.addWidget(self.r10Edit,33,1,1,2)
        self.mainlayout.addWidget(self.r11Label,34,0)
        self.mainlayout.addWidget(self.r11Edit,34,1,1,2)
        self.mainlayout.addWidget(self.r12Label,35,0)
        self.mainlayout.addWidget(self.r12Edit,35,1,1,2)
        self.mainlayout.addWidget(self.g1Label,36,0)
        self.mainlayout.addWidget(self.g1Edit,36,1,1,2)
        self.mainlayout.addWidget(self.g2Label,37,0)
        self.mainlayout.addWidget(self.g2Edit,37,1,1,2)
        self.mainlayout.addWidget(self.g3Label,38,0)
        self.mainlayout.addWidget(self.g3Edit,38,1,1,2)
        self.mainlayout.addWidget(self.g4Label,39,0)
        self.mainlayout.addWidget(self.g4Edit,39,1,1,2)
        self.mainlayout.addWidget(self.g5Label,40,0)
        self.mainlayout.addWidget(self.g5Edit,40,1,1,2)
        self.mainlayout.addWidget(self.g6Label,41,0)
        self.mainlayout.addWidget(self.g6Edit,41,1,1,2)
        self.mainlayout.addWidget(self.g7Label,42,0)
        self.mainlayout.addWidget(self.g7Edit,42,1,1,2)
        self.mainlayout.addWidget(self.g8Label,43,0)
        self.mainlayout.addWidget(self.g8Edit,43,1,1,2)
        self.mainlayout.addWidget(self.g9Label,44,0)
        self.mainlayout.addWidget(self.g9Edit,44,1,1,2)

        # Cotton
        self.mainlayout.addWidget(self.calbrt11Label,45,0)
        self.mainlayout.addWidget(self.calbrt11Edit,45,1,1,2)
        self.mainlayout.addWidget(self.calbrt12Label,46,0)
        self.mainlayout.addWidget(self.calbrt12Edit,47,1,1,2)
        self.mainlayout.addWidget(self.calbrt13Label,48,0)
        self.mainlayout.addWidget(self.calbrt13Edit,48,1,1,2)
        self.mainlayout.addWidget(self.calbrt15Label,49,0)
        self.mainlayout.addWidget(self.calbrt15Edit,49,1,1,2)
        self.mainlayout.addWidget(self.calbrt16Label,50,0)
        self.mainlayout.addWidget(self.calbrt16Edit,50,1,1,2)
        self.mainlayout.addWidget(self.calbrt17Label,51,0)
        self.mainlayout.addWidget(self.calbrt17Edit,51,1,1,2)
        self.mainlayout.addWidget(self.calbrt18Label,52,0)
        self.mainlayout.addWidget(self.calbrt18Edit,52,1,1,2)
        self.mainlayout.addWidget(self.calbrt19Label,53,0)
        self.mainlayout.addWidget(self.calbrt19Edit,53,1,1,2)
        self.mainlayout.addWidget(self.calbrt22Label,54,0)
        self.mainlayout.addWidget(self.calbrt22Edit,54,1,1,2)
        self.mainlayout.addWidget(self.calbrt26Label,55,0)
        self.mainlayout.addWidget(self.calbrt26Edit,55,1,1,2)
        self.mainlayout.addWidget(self.calbrt27Label,56,0)
        self.mainlayout.addWidget(self.calbrt27Edit,56,1,1,2)
        self.mainlayout.addWidget(self.calbrt28Label,57,0)
        self.mainlayout.addWidget(self.calbrt28Edit,57,1,1,2)
        self.mainlayout.addWidget(self.calbrt29Label,58,0)
        self.mainlayout.addWidget(self.calbrt29Edit,58,1,1,2)
        self.mainlayout.addWidget(self.calbrt30Label,59,0)
        self.mainlayout.addWidget(self.calbrt30Edit,59,1,1,2)
        self.mainlayout.addWidget(self.calbrt31Label,60,0)
        self.mainlayout.addWidget(self.calbrt31Edit,60,1,1,2)
        self.mainlayout.addWidget(self.calbrt32Label,61,0)
        self.mainlayout.addWidget(self.calbrt32Edit,61,1,1,2)
        self.mainlayout.addWidget(self.calbrt33Label,62,0)
        self.mainlayout.addWidget(self.calbrt33Edit,62,1,1,2)
        self.mainlayout.addWidget(self.calbrt34Label,63,0)
        self.mainlayout.addWidget(self.calbrt34Edit,63,1,1,2)
        self.mainlayout.addWidget(self.calbrt35Label,64,0)
        self.mainlayout.addWidget(self.calbrt35Edit,64,1,1,2)
        self.mainlayout.addWidget(self.calbrt36Label,65,0)
        self.mainlayout.addWidget(self.calbrt36Edit,65,1,1,2)
        self.mainlayout.addWidget(self.calbrt37Label,66,0)
        self.mainlayout.addWidget(self.calbrt37Edit,66,1,1,2)
        self.mainlayout.addWidget(self.calbrt38Label,67,0)
        self.mainlayout.addWidget(self.calbrt38Edit,67,1,1,2)
        self.mainlayout.addWidget(self.calbrt39Label,68,0)
        self.mainlayout.addWidget(self.calbrt39Edit,68,1,1,2)
        self.mainlayout.addWidget(self.calbrt40Label,69,0)
        self.mainlayout.addWidget(self.calbrt40Edit,69,1,1,2)
        self.mainlayout.addWidget(self.calbrt41Label,70,0)
        self.mainlayout.addWidget(self.calbrt41Edit,70,1,1,2)
        self.mainlayout.addWidget(self.calbrt42Label,71,0)
        self.mainlayout.addWidget(self.calbrt42Edit,71,1,1,2)
        self.mainlayout.addWidget(self.calbrt43Label,72,0)
        self.mainlayout.addWidget(self.calbrt43Edit,72,1,1,2)
        self.mainlayout.addWidget(self.calbrt44Label,73,0)
        self.mainlayout.addWidget(self.calbrt44Edit,73,1,1,2)
        self.mainlayout.addWidget(self.calbrt45Label,74,0)
        self.mainlayout.addWidget(self.calbrt45Edit,74,1,1,2)
        self.mainlayout.addWidget(self.calbrt47Label,75,0)
        self.mainlayout.addWidget(self.calbrt47Edit,75,1,1,2)
        self.mainlayout.addWidget(self.calbrt48Label,76,0)
        self.mainlayout.addWidget(self.calbrt48Edit,76,1,1,2)
        self.mainlayout.addWidget(self.calbrt49Label,77,0)
        self.mainlayout.addWidget(self.calbrt49Edit,77,1,1,2)
        self.mainlayout.addWidget(self.calbrt50Label,78,0)
        self.mainlayout.addWidget(self.calbrt50Edit,78,1,1,2)
        self.mainlayout.addWidget(self.calbrt52Label,79,0)
        self.mainlayout.addWidget(self.calbrt52Edit,79,1,1,2)
        self.mainlayout.addWidget(self.calbrt57Label,80,0)
        self.mainlayout.addWidget(self.calbrt57Edit,80,1,1,2)

        # Last line in the form
        self.mainlayout.addWidget(self.cultivarnamelabel,81,0)
        self.mainlayout.addWidget(self.cultivarnameedit,81,1,1,2)
        self.mainlayout.addWidget(self.cultivarbutton,81,3)
        self.mainlayout.addWidget(self.cultivardeletebutton,81,4)

        self.cultivarcombo.setVisible(False)
        self.cultivarlistlabel.setVisible(False)

        self.cornFieldSwitch(False)
        self.potatoFieldSwitch(False)
        self.soybeanFieldSwitch(False)
        self.cottonFieldSwitch(False)

        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        
        self.setLayout(self.hbox) 

 
    def cornFieldSwitch(self, state):
        self.daylengthabel.setVisible(state)
        self.daylength_b1.setVisible(state)
        self.daylength_b2.setVisible(state)
        self.leaveslabel.setVisible(state)
        self.leavesedit.setVisible(state)
        self.ltarlabel.setVisible(state)
        self.ltaredit.setVisible(state)
        self.ltirlabel.setVisible(state)
        self.ltiredit.setVisible(state)
        self.tassellabel.setVisible(state)
        self.tasseledit.setVisible(state)
        self.staygreenlavel.setVisible(state)
        self.staygreenedit.setVisible(state)
        return True


    def potatoFieldSwitch(self,state):
        self.dailyAirTempEffectLabel.setVisible(state)
        self.dailyAirTempEffectEdit.setVisible(state)
        self.dailyAirTempAmpEffectLabel.setVisible(state)
        self.dailyAirTempAmpEffectEdit.setVisible(state)
        self.photoEffectLabel.setVisible(state)
        self.photoEffectEdit.setVisible(state)
        self.highNiEffectLabel.setVisible(state)
        self.highNiEffectEdit.setVisible(state)
        self.lowNiEffectLabel.setVisible(state)
        self.lowNiEffectEdit.setVisible(state)
        self.determLabel.setVisible(state)
        self.determEdit.setVisible(state)
        self.maxCanLeafExpRateLabel.setVisible(state)
        self.maxCanLeafExpRateEdit.setVisible(state)
        self.maxTuberGrowthRateLabel.setVisible(state)
        self.maxTuberGrowthRateEdit.setVisible(state)
        self.specificLeafWeightLabel.setVisible(state)
        self.specificLeafWeightEdit.setVisible(state)
        return True


    def soybeanFieldSwitch(self,state):
        self.matGrpLabel.setVisible(state)
        self.matGrpEdit.setVisible(state)
        self.seedLbLabel.setVisible(state)
        self.seedLbEdit.setVisible(state)
        self.fillLabel.setVisible(state)
        self.fillEdit.setVisible(state)
        self.v1Label.setVisible(state)
        self.v1Edit.setVisible(state)
        self.v2Label.setVisible(state)
        self.v2Edit.setVisible(state)
        self.v3Label.setVisible(state)
        self.v3Edit.setVisible(state)
        self.r1Label.setVisible(state)
        self.r1Edit.setVisible(state)
        self.r2Label.setVisible(state)
        self.r2Edit.setVisible(state)
        self.r3Label.setVisible(state)
        self.r3Edit.setVisible(state)
        self.r4Label.setVisible(state)
        self.r4Edit.setVisible(state)
        self.r5Label.setVisible(state)
        self.r5Edit.setVisible(state)
        self.r6Label.setVisible(state)
        self.r6Edit.setVisible(state)
        self.r7Label.setVisible(state)
        self.r7Edit.setVisible(state)
        self.r8Label.setVisible(state)
        self.r8Edit.setVisible(state)
        self.r9Label.setVisible(state)
        self.r9Edit.setVisible(state)
        self.r10Label.setVisible(state)
        self.r10Edit.setVisible(state)
        self.r11Label.setVisible(state)
        self.r11Edit.setVisible(state)
        self.r12Label.setVisible(state)
        self.r12Edit.setVisible(state)
        self.g1Label.setVisible(state)
        self.g1Edit.setVisible(state)
        self.g2Label.setVisible(state)
        self.g2Edit.setVisible(state)
        self.g3Label.setVisible(state)
        self.g3Edit.setVisible(state)
        self.g4Label.setVisible(state)
        self.g4Edit.setVisible(state)
        self.g5Label.setVisible(state)
        self.g5Edit.setVisible(state)
        self.g6Label.setVisible(state)
        self.g6Edit.setVisible(state)
        self.g7Label.setVisible(state)
        self.g7Edit.setVisible(state)
        self.g8Label.setVisible(state)
        self.g8Edit.setVisible(state)
        self.g9Label.setVisible(state)
        self.g9Edit.setVisible(state)
        return True


    def cottonFieldSwitch(self,state):
        self.calbrt11Label.setVisible(state)
        self.calbrt11Edit.setVisible(state)
        self.calbrt12Label.setVisible(state)
        self.calbrt12Edit.setVisible(state)
        self.calbrt13Label.setVisible(state)
        self.calbrt13Edit.setVisible(state)
        self.calbrt15Label.setVisible(state)
        self.calbrt15Edit.setVisible(state)
        self.calbrt16Label.setVisible(state)
        self.calbrt16Edit.setVisible(state)
        self.calbrt17Label.setVisible(state)
        self.calbrt17Edit.setVisible(state)
        self.calbrt18Label.setVisible(state)
        self.calbrt18Edit.setVisible(state)
        self.calbrt19Label.setVisible(state)
        self.calbrt19Edit.setVisible(state)
        self.calbrt22Label.setVisible(state)
        self.calbrt22Edit.setVisible(state)
        self.calbrt26Label.setVisible(state)
        self.calbrt26Edit.setVisible(state)
        self.calbrt27Label.setVisible(state)
        self.calbrt27Edit.setVisible(state)
        self.calbrt28Label.setVisible(state)
        self.calbrt28Edit.setVisible(state)
        self.calbrt29Label.setVisible(state)
        self.calbrt29Edit.setVisible(state)
        self.calbrt30Label.setVisible(state)
        self.calbrt30Edit.setVisible(state)
        self.calbrt31Label.setVisible(state)
        self.calbrt31Edit.setVisible(state)
        self.calbrt32Label.setVisible(state)
        self.calbrt32Edit.setVisible(state)
        self.calbrt33Label.setVisible(state)
        self.calbrt33Edit.setVisible(state)
        self.calbrt34Label.setVisible(state)
        self.calbrt34Edit.setVisible(state)
        self.calbrt35Label.setVisible(state)
        self.calbrt35Edit.setVisible(state)
        self.calbrt36Label.setVisible(state)
        self.calbrt36Edit.setVisible(state)
        self.calbrt37Label.setVisible(state)
        self.calbrt37Edit.setVisible(state)
        self.calbrt38Label.setVisible(state)
        self.calbrt38Edit.setVisible(state)
        self.calbrt39Label.setVisible(state)
        self.calbrt39Edit.setVisible(state)
        self.calbrt40Label.setVisible(state)
        self.calbrt40Edit.setVisible(state)
        self.calbrt41Label.setVisible(state)
        self.calbrt41Edit.setVisible(state)
        self.calbrt42Label.setVisible(state)
        self.calbrt42Edit.setVisible(state)
        self.calbrt43Label.setVisible(state)
        self.calbrt43Edit.setVisible(state)
        self.calbrt44Label.setVisible(state)
        self.calbrt44Edit.setVisible(state)
        self.calbrt45Label.setVisible(state)
        self.calbrt45Edit.setVisible(state)
        self.calbrt47Label.setVisible(state)
        self.calbrt47Edit.setVisible(state)
        self.calbrt48Label.setVisible(state)
        self.calbrt48Edit.setVisible(state)
        self.calbrt49Label.setVisible(state)
        self.calbrt49Edit.setVisible(state)
        self.calbrt50Label.setVisible(state)
        self.calbrt50Edit.setVisible(state)
        self.calbrt52Label.setVisible(state)
        self.calbrt52Edit.setVisible(state)
        self.calbrt57Label.setVisible(state)
        self.calbrt57Edit.setVisible(state)
        return True


    def showcultivarcombo(self):
        cropname = self.cropcombo.currentText()
        self.cultivarcombo.setVisible(False)
        self.cultivarlistlabel.setVisible(False)
        self.cornFieldSwitch(False)
        self.potatoFieldSwitch(False)
        self.soybeanFieldSwitch(False)
        self.cottonFieldSwitch(False)
        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        

        if cropname != "Select a crop":
            self.cultivarcombo.setVisible(True)
            self.cultivarlistlabel.setVisible(True)

            cultivarlists = read_cultivar_DB(cropname) 
            self.cultivarcombo.clear()
            self.cultivarcombo.addItem("Select from list")    
            self.cultivarcombo.addItem("Add New Cultivar ("+cropname+")") 
            for key in cultivarlists:
                self.cultivarcombo.addItem(cropname + ":" + str(key))   
            self.cultivarcombo.currentIndexChanged.connect(self.showcultivardetailscombo)

            if self.helpcheckbox.isChecked():
                self.importfaq("cultivar")              
                self.faqtree.setVisible(True)

        return True


    def showcultivardetailscombo(self):
        cultivarname = self.cultivarcombo.currentText()

        self.cornFieldSwitch(False)
        self.potatoFieldSwitch(False)
        self.soybeanFieldSwitch(False)
        self.cottonFieldSwitch(False)

        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        

        if cultivarname == "Select from list":  
            action = ""
            return True
        else:      
            if cultivarname.find(":") != -1:
                (crop,cultivar) = cultivarname.split(":")
                action = "Update"
                self.cultivardeletebutton.setVisible(True)   
                self.cultivardeletebutton.clicked.connect(lambda:self.on_cultivardeletebuttonclick(crop,cultivar))
            else:
                crop = self.cropcombo.currentText()
                cultivar = ""
                action = "SaveAs"
                self.cultivarnamelabel.setVisible(True)
                self.cultivarnameedit.setVisible(True)

            self.cultivarbutton.setText(action)
            self.cultivarbutton.setVisible(True)
            self.cultivarbutton.clicked.connect(lambda:self.on_cultivarbuttonsclick(crop,cultivar))

        # Each cultivar has a different set of parameters, so this block of code will be specific for each crop maize
        if(crop == "maize"):
            self.cornFieldSwitch(True)
            ## putting 2 separate buttons for UPDATE and SAVEAS tasks
            if action == "SaveAs":
                self.leavesedit.setText("0")
                self.ltaredit.setText("0.46")
                self.ltiredit.setText("0.8")
                self.tasseledit.setText("4.0")
                self.staygreenedit.setText("2.0")
            elif action == "Update":
                cultivartuple = read_cultivar_DB_detailed(cultivar,crop)  

                if cultivartuple[0] is not None:
                    self.leavesedit.setText(str(cultivartuple[0]))

                if cultivartuple[1] > 0:
                    self.daylength_b1.setChecked(True)
                else:
                    self.daylength_b2.setChecked(True)

                if cultivartuple[2] is not None:
                    self.ltaredit.setText(str(cultivartuple[2]))
                if cultivartuple[3] is not None:
                    self.ltiredit.setText(str(cultivartuple[3]))
                if cultivartuple[4] is not None:
                    self.tasseledit.setText(str(cultivartuple[4]))
                if cultivartuple[5] is not None:
                    self.staygreenedit.setText(str(cultivartuple[5]))
          
        # Potato
        if(crop == "potato"):
            self.potatoFieldSwitch(True)
            if action == "SaveAs":
                self.dailyAirTempEffectEdit.setText("0")
                self.dailyAirTempAmpEffectEdit.setText("0")
                self.photoEffectEdit.setText("0")
                self.highNiEffectEdit.setText("0")
                self.lowNiEffectEdit.setText("0")
                self.determEdit.setText("0")
                self.maxCanLeafExpRateEdit.setText("0")
                self.maxTuberGrowthRateEdit.setText("0")
                self.specificLeafWeightEdit.setText("0")
            elif action == "Update":
                cultivartuple = read_cultivar_DB_detailed(cultivar,crop)  
                self.dailyAirTempEffectEdit.setText(str(cultivartuple[0]))
                self.dailyAirTempAmpEffectEdit.setText(str(cultivartuple[1]))
                self.photoEffectEdit.setText(str(cultivartuple[2]))
                self.highNiEffectEdit.setText(str(cultivartuple[3]))
                self.lowNiEffectEdit.setText(str(cultivartuple[4]))
                self.determEdit.setText(str(cultivartuple[5]))
                self.maxCanLeafExpRateEdit.setText(str(cultivartuple[6]))
                self.maxTuberGrowthRateEdit.setText(str(cultivartuple[7]))
                self.specificLeafWeightEdit.setText(str(cultivartuple[8]))

        # Soybean
        if(crop == "soybean"):
            self.soybeanFieldSwitch(True)
            if action == "SaveAs":
                self.matGrpEdit.setText("2.7")
                self.seedLbEdit.setText("3800")
                self.fillEdit.setText("7.5")
                self.v1Edit.setText("0.00894")
                self.v2Edit.setText("14.6")
                self.v3Edit.setText("0.5")
                self.r1Edit.setText("0.0198")
                self.r2Edit.setText("0.0119")
                self.r3Edit.setText("-0.0907")
                self.r4Edit.setText("0.194")
                self.r5Edit.setText("0.522")
                self.r6Edit.setText("132.1")
                self.r7Edit.setText("0.00402")
                self.r8Edit.setText("42")
                self.r9Edit.setText("250")
                self.r10Edit.setText("0.5")
                self.r11Edit.setText("0.008")
                self.r12Edit.setText("5")
                self.g1Edit.setText("0.0024")
                self.g2Edit.setText("0.5")
                self.g3Edit.setText("2.2")
                self.g4Edit.setText("2.8")
                self.g5Edit.setText("1")
                self.g6Edit.setText("1.684")
                self.g7Edit.setText("0.5")
                self.g8Edit.setText("1.3")
                self.g9Edit.setText("1")
            elif action == "Update":
                cultivartuple = read_cultivar_DB_detailed(cultivar,crop)  
                self.matGrpEdit.setText(str(cultivartuple[0]))
                self.seedLbEdit.setText(str(cultivartuple[1]))
                self.fillEdit.setText(str(cultivartuple[2]))
                self.v1Edit.setText(str(cultivartuple[3]))
                self.v2Edit.setText(str(cultivartuple[4]))
                self.v3Edit.setText(str(cultivartuple[5]))
                self.r1Edit.setText(str(cultivartuple[6]))
                self.r2Edit.setText(str(cultivartuple[7]))
                self.r3Edit.setText(str(cultivartuple[8]))
                self.r4Edit.setText(str(cultivartuple[9]))
                self.r5Edit.setText(str(cultivartuple[10]))
                self.r6Edit.setText(str(cultivartuple[11]))
                self.r7Edit.setText(str(cultivartuple[12]))
                self.r8Edit.setText(str(cultivartuple[13]))
                self.r9Edit.setText(str(cultivartuple[14]))
                self.r10Edit.setText(str(cultivartuple[15]))
                self.r11Edit.setText(str(cultivartuple[16]))
                self.r12Edit.setText(str(cultivartuple[17]))
                self.g1Edit.setText(str(cultivartuple[18]))
                self.g2Edit.setText(str(cultivartuple[19]))
                self.g3Edit.setText(str(cultivartuple[20]))
                self.g4Edit.setText(str(cultivartuple[21]))
                self.g5Edit.setText(str(cultivartuple[22]))
                self.g6Edit.setText(str(cultivartuple[23]))
                self.g7Edit.setText(str(cultivartuple[24]))
                self.g8Edit.setText(str(cultivartuple[25]))
                self.g9Edit.setText(str(cultivartuple[26]))
                   
        # Cotton
        if(crop == "cotton"):
            self.cottonFieldSwitch(True)
            if action == "SaveAs":
                self.calbrt11Edit.setText("4")
                self.calbrt12Edit.setText("6.75")
                self.calbrt13Edit.setText("35")
                self.calbrt15Edit.setText("0.85")
                self.calbrt16Edit.setText("-0.9")
                self.calbrt17Edit.setText("0.9")
                self.calbrt18Edit.setText("0")
                self.calbrt19Edit.setText("1.5")
                self.calbrt22Edit.setText("1")
                self.calbrt26Edit.setText("1.35")
                self.calbrt27Edit.setText("1")
                self.calbrt28Edit.setText("1")
                self.calbrt29Edit.setText("0.9")
                self.calbrt30Edit.setText("1.15")
                self.calbrt31Edit.setText("1.1")
                self.calbrt32Edit.setText("1")
                self.calbrt33Edit.setText("-0.85")
                self.calbrt34Edit.setText("1")
                self.calbrt35Edit.setText("1")
                self.calbrt36Edit.setText("1.1")
                self.calbrt37Edit.setText("3")
                self.calbrt38Edit.setText("0.75")
                self.calbrt39Edit.setText("1")
                self.calbrt40Edit.setText("2.5")
                self.calbrt41Edit.setText("1")
                self.calbrt42Edit.setText("1")
                self.calbrt43Edit.setText("0.9")
                self.calbrt44Edit.setText("1")
                self.calbrt45Edit.setText("0.8")
                self.calbrt47Edit.setText("1.1")
                self.calbrt48Edit.setText("0.9")
                self.calbrt49Edit.setText("0.7")
                self.calbrt50Edit.setText("1")
                self.calbrt52Edit.setText("1.35")
                self.calbrt57Edit.setText("1")
            elif action == "Update":
                cultivartuple = read_cultivar_DB_detailed(cultivar,crop)  
                self.calbrt11Edit.setText(str(cultivartuple[0]))
                self.calbrt12Edit.setText(str(cultivartuple[1]))
                self.calbrt13Edit.setText(str(cultivartuple[2]))
                self.calbrt15Edit.setText(str(cultivartuple[3]))
                self.calbrt16Edit.setText(str(cultivartuple[4]))
                self.calbrt17Edit.setText(str(cultivartuple[5]))
                self.calbrt18Edit.setText(str(cultivartuple[6]))
                self.calbrt19Edit.setText(str(cultivartuple[7]))
                self.calbrt22Edit.setText(str(cultivartuple[8]))
                self.calbrt26Edit.setText(str(cultivartuple[9]))
                self.calbrt27Edit.setText(str(cultivartuple[10]))
                self.calbrt28Edit.setText(str(cultivartuple[11]))
                self.calbrt29Edit.setText(str(cultivartuple[12]))
                self.calbrt30Edit.setText(str(cultivartuple[13]))
                self.calbrt31Edit.setText(str(cultivartuple[14]))
                self.calbrt32Edit.setText(str(cultivartuple[15]))
                self.calbrt33Edit.setText(str(cultivartuple[16]))
                self.calbrt34Edit.setText(str(cultivartuple[17]))
                self.calbrt35Edit.setText(str(cultivartuple[18]))
                self.calbrt36Edit.setText(str(cultivartuple[19]))
                self.calbrt37Edit.setText(str(cultivartuple[20]))
                self.calbrt38Edit.setText(str(cultivartuple[21]))
                self.calbrt39Edit.setText(str(cultivartuple[22]))
                self.calbrt40Edit.setText(str(cultivartuple[23]))
                self.calbrt41Edit.setText(str(cultivartuple[24]))
                self.calbrt42Edit.setText(str(cultivartuple[25]))
                self.calbrt43Edit.setText(str(cultivartuple[26]))
                self.calbrt44Edit.setText(str(cultivartuple[27]))
                self.calbrt45Edit.setText(str(cultivartuple[28]))
                self.calbrt47Edit.setText(str(cultivartuple[29]))
                self.calbrt48Edit.setText(str(cultivartuple[30]))
                self.calbrt49Edit.setText(str(cultivartuple[31]))
                self.calbrt50Edit.setText(str(cultivartuple[32]))
                self.calbrt52Edit.setText(str(cultivartuple[33]))
                self.calbrt57Edit.setText(str(cultivartuple[34]))


    @pyqtSlot()    
    def on_cultivarbuttonsclick(self, crop, cultivar):
        if crop == "maize" or crop == "soybean":
            alpm = 0.55
            diffx = 2.4
            diffz = 2.9
            velz = 0.0
            if crop == "maize":
                daylength_v = 1 if self.daylength_b1.isChecked() else 0       
                lm_min = 100.0 
        elif crop == "potato":
            alpm = 0.35
            diffx = 0.5
            diffz = 0.5
            velz = 0.5

        rrrm = 166.7
        rrry = 31.3
        rvrl = 0.73
        alpy = 0.04
        rtwl = 0.000106
        rtminwt = 0.0002
        epsi = 1.0
        iupw = 1.0
        courmax = 1.0
        lsink = 1.0
        rroot = 0.017
        constl_m = 35.0
        constk_m = 0.5
        cmin0_m = 0.01
        consti_y = 17.3
        constk_y = 0.75
        cmin0_y = 0.03
        if self.cultivarbutton.text() == "Update":
            self.cultivarbutton.blockSignals(True)
            self.cultivarbutton.blockSignals(False)
            if crop == "maize":
                record_tuple = (cultivar, int(self.leavesedit.text()), daylength_v, float(self.ltaredit.text()), \
                               float(self.ltiredit.text()), float(self.tasseledit.text()), float(self.staygreenedit.text()), \
                               lm_min, rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, diffx, diffz, velz, \
                               lsink, rroot, constl_m, constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
                c1 = insertUpdateCultivarMaize(record_tuple,self.cultivarbutton.text())
            elif crop == "potato":
                record_tuple = (self.cultivarnameedit.text(), float(self.dailyAirTempEffectEdit.text()), \
                               float(self.dailyAirTempAmpEffectEdit.text()), float(self.photoEffectEdit.text()), \
                               float(self.highNiEffectEdit.text()), float(self.lowNiEffectEdit.text()), \
                               float(self.determEdit.text()), float(self.maxCanLeafExpRateEdit.text()), \
                               float(self.maxTuberGrowthRateEdit.text()), float(self.specificLeafWeightEdit.text()), rrrm, \
                               rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, diffx, diffz, velz, lsink, rroot, \
                               constl_m, constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
                c1 = insertUpdateCultivarPotato(record_tuple,self.cultivarbutton.text())
            elif crop == "soybean":
                record_tuple = (cultivar, float(self.matGrpEdit.text()), float(self.seedLbEdit.text()), \
                               float(self.fillEdit.text()), float(self.v1Edit.text()), float(self.v2Edit.text()), \
                               float(self.v3Edit.text()), float(self.r1Edit.text()), float(self.r2Edit.text()), \
                               float(self.r3Edit.text()), float(self.r4Edit.text()), float(self.r5Edit.text()), \
                               float(self.r6Edit.text()), float(self.r7Edit.text()), float(self.r8Edit.text()), \
                               float(self.r9Edit.text()), float(self.r10Edit.text()), float(self.r11Edit.text()), \
                               float(self.r12Edit.text()), float(self.g1Edit.text()), float(self.g2Edit.text()), \
                               float(self.g3Edit.text()), float(self.g4Edit.text()), float(self.g5Edit.text()), \
                               float(self.g6Edit.text()), float(self.g7Edit.text()), float(self.g8Edit.text()), \
                               float(self.g9Edit.text()), rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, \
                               courmax, diffx, diffz, velz, lsink, rroot, constl_m, constk_m, cmin0_m, consti_y, \
                               constk_y, cmin0_y)
                c1 = insertUpdateCultivarSoybean(record_tuple,self.cultivarbutton.text())
            elif crop == "cotton":
                record_tuple = (cultivar, float(self.calbrt11Edit.text()), float(self.calbrt12Edit.text()), \
                                float(self.calbrt13Edit.text()), float(self.calbrt15Edit.text()), \
                                float(self.calbrt16Edit.text()), float(self.calbrt17Edit.text()), \
                                float(self.calbrt18Edit.text()), float(self.calbrt19Edit.text()), \
                                float(self.calbrt22Edit.text()), float(self.calbrt26Edit.text()), \
                                float(self.calbrt27Edit.text()), float(self.calbrt28Edit.text()), \
                                float(self.calbrt29Edit.text()), float(self.calbrt30Edit.text()), \
                                float(self.calbrt31Edit.text()), float(self.calbrt32Edit.text()), \
                                float(self.calbrt33Edit.text()), float(self.calbrt34Edit.text()), \
                                float(self.calbrt35Edit.text()), float(self.calbrt36Edit.text()), \
                                float(self.calbrt37Edit.text()), float(self.calbrt38Edit.text()), \
                                float(self.calbrt39Edit.text()), float(self.calbrt40Edit.text()), \
                                float(self.calbrt41Edit.text()), float(self.calbrt42Edit.text()), \
                                float(self.calbrt43Edit.text()), float(self.calbrt44Edit.text()), \
                                float(self.calbrt45Edit.text()), float(self.calbrt47Edit.text()), \
                                float(self.calbrt48Edit.text()), float(self.calbrt49Edit.text()), \
                                float(self.calbrt50Edit.text()), float(self.calbrt52Edit.text()), \
                                float(self.calbrt57Edit.text()))
                c1 = insertUpdateCultivarCotton(record_tuple,self.cultivarbutton.text())
            if not c1:
                return False
        elif self.cultivarbutton.text() == "SaveAs":
            ## check if new name is empty
            if len(self.cultivarnameedit.text()) <= 0:
                self.cultivarbutton.blockSignals(False)
                return messageUser("Cultivar name is empty, please provide a name.")
            else:
                matchedindex = self.cultivarcombo.findText(self.cropcombo.currentText()+":"+self.cultivarnameedit.text())                
                if matchedindex > 0:
                    self.cultivarbutton.blockSignals(False)
                    return messageUser("Cultivar name exist, please use a different name.")
                else:
                    self.cultivarbutton.blockSignals(True)
                    #save the table        
                    cultivartuple = read_cultivar_DB_detailed(self.cultivarnameedit.text(),self.cropcombo.currentText())  
                    if cultivartuple:
                        return False
                    if crop == "maize":
                        record_tuple = (self.cultivarnameedit.text(), int(self.leavesedit.text()), daylength_v, \
                                       float(self.ltaredit.text()), float(self.ltiredit.text()), float(self.tasseledit.text()), \
                                       float(self.staygreenedit.text()), lm_min, rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, \
                                       epsi, iupw, courmax, diffx, diffz, velz, lsink, rroot, constl_m, constk_m, cmin0_m, \
                                       consti_y, constk_y, cmin0_y)
                        c1 = insertUpdateCultivarMaize(record_tuple,self.cultivarbutton.text())
                    elif crop == "potato":
                        record_tuple = (self.cultivarnameedit.text(), float(self.dailyAirTempEffectEdit.text()), \
                                       float(self.dailyAirTempAmpEffectEdit.text()), float(self.photoEffectEdit.text()), \
                                       float(self.highNiEffectEdit.text()), float(self.lowNiEffectEdit.text()), \
                                       float(self.determEdit.text()), float(self.maxCanLeafExpRateEdit.text()), \
                                       float(self.maxTuberGrowthRateEdit.text()), float(self.specificLeafWeightEdit.text()), \
                                       rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, courmax, diffx, diffz, velz, \
                                       lsink, rroot, constl_m, constk_m, cmin0_m, consti_y, constk_y, cmin0_y)
                        c1 = insertUpdateCultivarPotato(record_tuple,self.cultivarbutton.text())
                    elif crop == "soybean":
                        record_tuple = (self.cultivarnameedit.text(), float(self.matGrpEdit.text()), float(self.seedLbEdit.text()), \
                                       float(self.fillEdit.text()), float(self.v1Edit.text()), float(self.v2Edit.text()), \
                                       float(self.v3Edit.text()), float(self.r1Edit.text()), float(self.r2Edit.text()), \
                                       float(self.r3Edit.text()), float(self.r4Edit.text()), float(self.r5Edit.text()), \
                                       float(self.r6Edit.text()), float(self.r7Edit.text()), float(self.r8Edit.text()), \
                                       float(self.r9Edit.text()), float(self.r10Edit.text()), float(self.r11Edit.text()), \
                                       float(self.r12Edit.text()), float(self.g1Edit.text()), float(self.g2Edit.text()), \
                                       float(self.g3Edit.text()), float(self.g4Edit.text()), float(self.g5Edit.text()), \
                                       float(self.g6Edit.text()), float(self.g7Edit.text()), float(self.g8Edit.text()), \
                                       float(self.g9Edit.text()), rrrm, rrry, rvrl, alpm, alpy, rtwl, rtminwt, epsi, iupw, \
                                       courmax, diffx, diffz, velz, lsink, rroot, constl_m, constk_m, cmin0_m, consti_y, \
                                       constk_y, cmin0_y)
                        c1 = insertUpdateCultivarSoybean(record_tuple,self.cultivarbutton.text())
                    elif crop == "cotton":
                        record_tuple = (self.cultivarnameedit.text(), float(self.calbrt11Edit.text()), float(self.calbrt12Edit.text()), \
                                        float(self.calbrt13Edit.text()), float(self.calbrt15Edit.text()), \
                                        float(self.calbrt16Edit.text()), float(self.calbrt17Edit.text()), \
                                        float(self.calbrt18Edit.text()), float(self.calbrt19Edit.text()), \
                                        float(self.calbrt22Edit.text()), float(self.calbrt26Edit.text()), \
                                        float(self.calbrt27Edit.text()), float(self.calbrt28Edit.text()), \
                                        float(self.calbrt29Edit.text()), float(self.calbrt30Edit.text()), \
                                        float(self.calbrt31Edit.text()), float(self.calbrt32Edit.text()), \
                                        float(self.calbrt33Edit.text()), float(self.calbrt34Edit.text()), \
                                        float(self.calbrt35Edit.text()), float(self.calbrt36Edit.text()), \
                                        float(self.calbrt37Edit.text()), float(self.calbrt38Edit.text()), \
                                        float(self.calbrt39Edit.text()), float(self.calbrt40Edit.text()), \
                                        float(self.calbrt41Edit.text()), float(self.calbrt42Edit.text()), \
                                        float(self.calbrt43Edit.text()), float(self.calbrt44Edit.text()), \
                                        float(self.calbrt45Edit.text()), float(self.calbrt47Edit.text()), \
                                        float(self.calbrt48Edit.text()), float(self.calbrt49Edit.text()), \
                                        float(self.calbrt50Edit.text()), float(self.calbrt52Edit.text()), \
                                        float(self.calbrt57Edit.text()))
                        c1 = insertUpdateCultivarCotton(record_tuple,self.cultivarbutton.text())
                    self.cultivarbutton.blockSignals(False)
                    if not c1:
                        return False

        self.cultivarcombo.clear()
        cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
        self.cultivarcombo.addItem("Select Cultivar")    
        self.cultivarcombo.addItem("Add New Cultivar ("+crop+")")
        for key in cultivarlists:            
            key_aux = crop + ":" + str(key)
            self.cultivarcombo.addItem(key_aux)   
        self.cultivarbutton.setText("")
        self.cultivarnameedit.setText("")
        self.cultivarcombo.setVisible(False)
        self.cultivarlistlabel.setVisible(False)
        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarcombo.blockSignals(False)

        if crop == "maize":
            self.cornFieldSwitch(False)
        elif crop == "potato":
            self.potatoFieldSwitch(False)
        elif crop == "soybean":
            self.soybeanFieldSwitch(False)
        elif crop == "cotton":
            self.cottonFieldSwitch(False)

        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        
        self.cropcombo.setCurrentIndex(0)
        return True


    @pyqtSlot()    
    def on_cultivardeletebuttonclick(self, crop, cultivar):
        '''
         Delete record on cultivar table
        '''
        c1 = delete_cultivar(crop,cultivar)

        self.cultivarcombo.blockSignals(True)
        self.cultivarcombo.clear()
        cultivarlists = read_cultivar_DB(self.cropcombo.currentText()) 
        self.cultivarcombo.addItem("Select Cultivar")    
        self.cultivarcombo.addItem("Add New Cultivar ("+crop+")") 
        for key in cultivarlists:            
            key_aux = crop + ":" + str(key)
            self.cultivarcombo.addItem(key_aux)   
        self.cultivarcombo.setVisible(False)
        self.cultivarlistlabel.setVisible(False)
        self.cultivarcombo.blockSignals(False)

        if crop == "maize":
            self.cornFieldSwitch(False)
        elif crop == "potato":
            self.potatoFieldSwitch(False)
        elif crop == "soybean":
            self.soybeanFieldSwitch(False)
        elif crop == "cotton":
            self.cottonFieldSwitch(False)

        self.cultivarnamelabel.setVisible(False)
        self.cultivarnameedit.setVisible(False)
        self.cultivarbutton.setText("")
        self.cultivarbutton.setVisible(False)       
        self.cultivardeletebutton.setVisible(False)        
        self.cropcombo.setCurrentIndex(0)


    def importfaq(self, thetabname=None):        
        cropname = self.cropcombo.currentText()
        faqlist = read_FaqDB(thetabname,cropname)         
        self.faqtree.clear()

        for item in faqlist:
            roottreeitem = QTreeWidgetItem(self.faqtree)
            roottreeitem.setText(0,item[2])
            childtreeitem = QTreeWidgetItem()
            childtreeitem.setText(0,item[3])
            roottreeitem.addChild(childtreeitem)


    def controlfaq(self):                
        if self.helpcheckbox.isChecked():
            self.importfaq("cultivar")              
            self.faqtree.setVisible(True)
        else:
            self.faqtree.setVisible(False)
        

    def resource_path(self,relative_path):
        """
        Get absolute path to resource, works for dev and for PyInstaller 
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)  
