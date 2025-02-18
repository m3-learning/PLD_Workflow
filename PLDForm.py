
import shutil
import sys
import json
import datetime
import os, glob, h5py
import numpy as np
import matplotlib.pyplot as plt
from datafed.CommandLib import API
import operator
import functools
from collections import OrderedDict



# save parameters 
# commit with User_Name and Date and Time and unique id

df_api = API()

df_api.setContext('p/2022_pld_plume_recording')

ls_resp = df_api.collectionItemsList('root')


import re #regular expressions

import getpass
import subprocess
from platform import platform

import datetime

import time

from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
from PyQt5.Qt import QStandardItemModel, QStandardItem

sys.path.append("/home/jgoddy2/Documents/Research_Agar/PLD_Form/PLD_Workflow/")
from ManagePlume import remove_desktop_ini, pack_to_hdf5_and_upload, pack_to_hdf5, upload_to_datafed

class message_window(QWidget):
    def __init__(self, message):
        super().__init__()
        self.message = '\n    '+message
        self.initUI()
    def initUI(self):
        lblName = QLabel(self.message, self)

        
 #for creating the folders (treeview) to view the data from Datafed
class StandardItem(QStandardItem):
    def __init__(self,txt='',fontsize=12,set_bold=False,color=QColor(0,0,0)):
        super().__init__()
        fnt = QFont('Times', fontsize)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)  
                 
                 
                                

    

        
class GenerateForm(QWidget):
    '''
    This is the digital form to record PLD experiment parameters mainly, 
    with additional feature features to manage, pack, and upload recorded plumes along with recorded parameters. 
    :param version: input variable used to determine user want to open which version of digital form, defaults to "parameter" 
    :type version: str
    '''
    def __init__(self, version='parameter'):
        super().__init__()
        self.version = version
        
        # setting the minimum size
        width = 700
        height = 800
        self.setMinimumSize(width, height)
        self.window_height = 22
        self.button_height = 28
        self.current_page = 0
        
        # pre-define inputs
        # header part
        self.growth_id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.date_input = QLineEdit(datetime.datetime.today().strftime("%m/%d/%Y"))
        self.time_input = QLineEdit(datetime.datetime.now().strftime("%H:%M:%S"))
        self.save_path_input = QLineEdit(os.getcwd()) 
#         self.save_path_input = QLineEdit('C:/Image/') 

        self.custom_key = QLineEdit()
        self.custom_key.setFixedSize(80, self.window_height)
        self.custom_value = QLineEdit()

        # chamber part
       # chamber part
        self.chamber_ComboBox = QComboBox()  # creating combo box to select degree
        self.chamber_ComboBox.setFixedSize(100, self.window_height)
        chamber_list = ["","Laser 1A", "Laser 1C"]
        self.chamber_ComboBox.addItems(chamber_list)
        
       # self.chamber_ComboBox.setCurrentText("Laser 1C")
        
        #the substrate part
        substrate_list = ["", "SrTiO3", "None"]   
        
        self.substrate_1_ComboBox = QComboBox()
        self.substrate_1_ComboBox.setFixedSize(100, self.window_height)
        self.substrate_1_ComboBox.addItems(substrate_list)
        
        self.substrate_2_ComboBox = QComboBox()
        self.substrate_2_ComboBox.setFixedSize(100, self.window_height)
        self.substrate_2_ComboBox.addItems(substrate_list)
        
        self.substrate_3_ComboBox = QComboBox()
        self.substrate_3_ComboBox.setFixedSize(100, self.window_height)
        self.substrate_3_ComboBox.addItems(substrate_list)
        
        self.substrate_4_ComboBox = QComboBox()
        self.substrate_4_ComboBox.setFixedSize(100, self.window_height)
        self.substrate_4_ComboBox.addItems(substrate_list)

        
        
        
        self.base_pressure_input = QLineEdit()

        gas_list = ["","Vacuum", "Oxygen", "Argon"]
        self.cool_down_gas = QComboBox()
        self.cool_down_gas.setFixedSize(100, self.window_height)
        self.cool_down_gas.addItems(gas_list)

        #the search part 
        self.search_input = QLineEdit()
        
        
    
        
        
       # prior_list = projects
    #    self.prior_session =  QTreeView()
     #   self.prior_session.addItems(prior_list)

        
        self.prior_session =  QTreeWidget() #QTreeView()
        #self.prior_session.addItems(prior_list)
        
        treeView =  self.prior_session #QTreeView()
        #self.prior_session = treeView
        treeView.setHeaderHidden(True)
        
        
        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()
        
        
        
        #input list of records from previous sessions
        #the below steps come from the Datafed Jupyter notebook tutorial: 
        #https://ornl.github.io/DataFed/user/python/notebooks.html
        #see the tutorial for help installing Datafed if necessary;
        #the below assumes everything is working properly 
        
        df_api = API()

        df_api.setContext('p/2022_pld_plume_recording')

        ls_resp = df_api.collectionItemsList('root')
        
      #  projects=[]
        
         
        for record in ls_resp[0].item:
#             
            folder = record.title #for example Datasets 
            a = QTreeWidgetItem([folder])
            treeView.addTopLevelItem(a)
            
            ID = record.id 
            ls_resp_2 = df_api.collectionItemsList(ID,count = 1000) # listing children of folder, which I call 'session'  
            
            for record2 in ls_resp_2[0].item:
                session = (QTreeWidgetItem([record2.title]))
                a.insertChild(0,session)
                
                Id2 =  record2.id 
                #add scan, then label,then value
                try:
                    metaData = json.loads(df_api.dataView(Id2)[0].data[0].metadata) # get metadata for session

                    keys = metaData.keys()
                    
                    
                    for key in keys:
                        scan = QTreeWidgetItem([key]) #Header, target_NUM, etc. 
                        session.addChild(scan) 
  
                        
                        if type(metaData[key]) == str:
                            scan.addChild(QTreeWidgetItem([metaData[key]])) #target material, etc. 
                            
                        else: #type == dict
                            for val in metaData[key]:
                                value = QTreeWidgetItem([val])
                                scan.addChild(value)
                                try: 
                                    #value.addChild(QTreeWidgetItem([str(metaData[key][val])]))
                                    if type(metaData[key][val]) == dict:
                                       # print(metaData[key][val])
                                        for key2 in metaData[key][val]:
                                            # VALUE2 IS A BAD NAME
                                            new_key = QTreeWidgetItem([key2])
                                            #label.addChild(value)
                                          #  print('key2',key2)
                                           # print(metaData[key][val][key2])
                                            value.addChild(new_key)
                                            new_key.addChild(QTreeWidgetItem([str(metaData[key][val][key2])]))
                                    else:
                                        value.addChild(QTreeWidgetItem([str(metaData[key][val])]))



                                except Exception as err:
                                    label.addChild(QTreeWidgetItem([f"{type(err).__name__} was raised: {err}"]))
                                   
                except: # if no metaData
                    session.addChild(QTreeWidgetItem(['no metadata found']))
        
            
  
   
        
        # notes part
        self.notes_input = QPlainTextEdit()        
        self.notes_input.setFixedSize(600, self.window_height*3) #3
        
        
        # target
        self.target_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        # lens part
        self.aperture_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.focus_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.attenuator_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.target_height_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        # laser part
        self.laser_voltage_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.laser_energy_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.energy_mean_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        self.energy_std_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        
        # pre-ablation and ablation
        self.pre_temperature_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.pre_pressure_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.pre_gas_input = [QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox(),QComboBox(),
                              QComboBox(),QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox()]   
        
        self.pre_frequency_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.pre_number_pulses_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        self.temperature_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.pressure_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.gas_input = [QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox(),QComboBox(),
                              QComboBox(),QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox()]
        
        self.frequency_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        self.number_pulses_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit(),  
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        gas_list = ["", "Vacuum", "Oxygen", "Argon"]
       
        for combobox in self.pre_gas_input:
            combobox.addItems(gas_list)
            combobox.setFixedSize(100, self.window_height)

            
        for combobox in self.gas_input:
            combobox.addItems(gas_list)
            combobox.setFixedSize(100, self.window_height)
          

        
        # define the layout
        self.setWindowTitle("PLD Growth Record")
        
        self.toplayout = QVBoxLayout()
        self.setLayout(self.toplayout)

        ## Create the grid layout - second-level
        self.layout = QGridLayout()
        self.toplayout.addLayout(self.layout)

        self.header_form = QGroupBox("Header")
        self.header_layout = self.create_header()
        self.header_form.setLayout(self.header_layout)
        self.layout.addWidget(self.header_form, 0, 0)
  #      self.layout.setColumnStretch(0,1)

        self.chamber_form = QGroupBox("Chamber Parameters")
        self.chamber_layout = self.create_chamber()
        self.chamber_form.setLayout(self.chamber_layout)
        self.layout.addWidget(self.chamber_form, 0, 1)
  #      self.layout.setColumnStretch(1,0)
        
        self.prior_scans = treeView  #QGroupBox("Prior Scans")
        self.prior_layout = self.create_prior()
        self.prior_scans.setLayout(self.prior_layout)
        #self.prior_scans.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.prior_scans, 0, 2,4,-1) #0,2,4,-1
        self.layout.setColumnStretch(2,10)
        
        # Ensure search_input is initialized before it's used
        self.search_input = QLineEdit()  # This line ensures search_input exists
    
        #search box
        self.search_form = QGroupBox("Search")
        self.search_layout = self.create_search()
        self.search_form.setLayout(self.search_layout)
        self.search_input.returnPressed.connect( self.onChanged )
#       
        self.search_input.setFixedSize(150, self.window_height)
        self.layout.addWidget(self.search_form, 1, 1)
        

      
            ### Create and connect the combo box to switch between pages
        target_list = ["Target_1", "Target_2", "Target_3", "Target_4", "Target_5", "Target_6", 
                       "Target_7", "Target_8", "Target_9","Target_10","Target_11", "Target_12"]
        self.target_ComboBox = QComboBox()

        self.target_ComboBox.addItems(target_list)
        self.target_ComboBox.activated.connect(self.switchPage)
        
            ### Add the combo box and the stacked layout to the top-level layout
            
        self.target_form= QGroupBox("Target")
        self.target_layout = self.create_target()
        self.target_form.setLayout(self.target_layout)
        self.layout.addWidget(self.target_form, 1, 0)
        
        
#         ## create QVForm - second level
        self.button_layout = QGridLayout()
        self.toplayout.addLayout(self.button_layout)

#         if self.version == 'plume':
#             self.button_create = QPushButton(self)
#             self.button_create.setText("Create Directory")
#             self.button_create.clicked.connect(lambda: self.create_folder())
#             self.button_layout.addWidget(self.button_create, 0, 1) 

#         ## create QGridLayout - second level 
        self.multiPages = QFormLayout()
        self.toplayout.addLayout(self.multiPages)
        
            ### Create the forms
        self.Stack = QStackedWidget (self)
        self.multiPages.addWidget(self.Stack)  
        for i in range(len(target_list)):
            self.stack = QWidget()
            self.Stack.addWidget (self.stack)
            stack_layout = self.stackUI(i)
            self.stack.setLayout(stack_layout)
        
       
        
       
        
        #  save button - second level
        self.button_save = QPushButton(self)
        self.button_save.setText("Save Parameters")
        self.button_save.clicked.connect(lambda: self.save())
        self.toplayout.addWidget(self.button_save)
        
        if self.version == 'plume':
        
            self.button_image = QPushButton(self)
            self.button_image.setText("Convert Video to Images (Not Functional)")
            self.button_image.clicked.connect(lambda: self.convert_to_image())
            self.toplayout.addWidget(self.button_image)  
            
            self.button_pack = QPushButton(self)
            self.button_pack.setText("Save to HDF5 and Upload")
            self.button_pack.clicked.connect(lambda: self.pack_to_hdf5_and_upload_with_popwindow(self.path, self.file_name, self.info_dict))
            self.toplayout.addWidget(self.button_pack)
        
        #  notes - second level
        self.form_notes = QGroupBox()
        self.notes_layout = QFormLayout()
        self.form_notes.setLayout(self.notes_layout)
        self.notes_layout.addRow(QLabel("Notes"), self.notes_input)
        self.toplayout.addWidget(self.form_notes)

#     def getValue(self,treeView):
#         item = treeView.currentItem()
#         #    return val.data()

#when an item in the tree is double clicked, import stuff to the form 
        treeView.doubleClicked.connect(self.onItemClicked)

    def onItemClicked(self,treeView):
    def onItemClicked(self,treeView):
      
        #first, define clicked on item
        item=self.prior_session.currentItem()    
        
        
#       then, clear everything from previously click so it is less confusing
#      unless the curent click doesn't do anything (i.e. it is on the top level (Datasets, etc)  or individual items
#level (i.e. aperture or 100)
# for top level, there are different sessions so it is unclear what to input
#for top level, parents are none. for individual items, no grandchildren (i.e. child(0).childCount()=0) 
        
    
        if item.parent() != None and int(item.childCount())>0 and int(item.child(0).childCount())>0:

            #the relevant header parameters
            self.growth_id_input.setText("")
            self.name_input.setText("")
            self.save_path_input.setText("")

            #chamber parameters (called "header" in dataFed)
            self.chamber_ComboBox.setCurrentText("")
            self.substrate_1_ComboBox.setCurrentText("")
            self.substrate_2_ComboBox.setCurrentText("")
            self.substrate_3_ComboBox.setCurrentText("")
            self.substrate_4_ComboBox.setCurrentText("")
            self.base_pressure_input.setText("")
            self.cool_down_gas.setCurrentText("")
            
            #notes section at bottom of form
            self.notes_input.clear()

            #target material

            for i in range(12):
                self.target_input[i].setText("")

                  #lens parameters
                self.aperture_input[i].setText("")
                self.focus_input[i].setText("")
                self.attenuator_input[i].setText("")
                self.target_height_input[i].setText("")

               #laser parameters
                self.laser_voltage_input[i].setText("")
                self.laser_energy_input[i].setText("")
                self.energy_mean_input[i].setText("")
                self.energy_std_input[i].setText("")
                
                #pre-ablation parameters
                self.pre_temperature_input[i].setText("")
                self.pre_pressure_input[i].setText("")
                self.pre_gas_input[i].setCurrentText("")
                self.pre_frequency_input[i].setText("")
                self.pre_number_pulses_input[i].setText("")
                
                #ablation parameters
                self.temperature_input[i].setText("")
                self.pressure_input[i].setText("")
                self.gas_input[i].setCurrentText("")
                self.frequency_input[i].setText("")
                self.number_pulses_input[i].setText("")




                 #make the children arrays for iterating and printing 
                 #I have to iterate over each of the children of the item to get the text of each one
                #and then control where its decendents go
            item_children = []
            for i in range(int(item.childCount())):



                item_children.append(item.child(i).text(0))



                #each session has its own set of targets, so that is the farthest up the 
                #chain it make sense to input stuff to form 
                #for now just putting it in the first target (see how they want to handle target matching)

                #these are for if you click on an individual target 

                #the relevant header parameters 

                if 'Growth_ID' in str(item.child(i).text(0)):
                    self.growth_id_input.setText(str(item.child(i).child(0).text(0)))

                elif 'User_Name' in str(item.child(i).text(0)):
                    self.name_input.setText(str(item.child(i).child(0).text(0)))    

                elif 'Path' in str(item.child(i).text(0)):
                    self.save_path_input.setText(str(item.child(i).child(0).text(0)))    


                 #chamber parameters (also maybe called 'header' in dataFed)

                elif 'Chamber' in str(item.child(i).text(0)) and "1a" in str(item.child(i).child(0).text(0)).lower():
                    self.chamber_ComboBox.setCurrentText("Laser 1A")

                elif 'Chamber' in str(item.child(i).text(0)) and "1c" in str(item.child(i).child(0).text(0)).lower():
                    self.chamber_ComboBox.setCurrentText("Laser 1C")

                                        
                elif 'Substrate_1' in str(item.child(i).text(0)):
                    if "srtio3" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_1_ComboBox.setCurrentText("SrTiO3")
                    elif "none" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_1_ComboBox.setCurrentText("None") 


                elif 'Substrate_2' in str(item.child(i).text(0)):
                    if "srtio3" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_2_ComboBox.setCurrentText("SrTiO3")
                    elif "none" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_2_ComboBox.setCurrentText("None")  

                elif 'Substrate_3' in str(item.child(i).text(0)):
                    if "srtio3" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_3_ComboBox.setCurrentText("SrTiO3")
                    elif "none" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_3_ComboBox.setCurrentText("None")

                elif 'Substrate_4' in str(item.child(i).text(0)):
                    if "srtio3" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_4_ComboBox.setCurrentText("SrTiO3")
                    elif "none" in str(item.child(i).child(0).text(0)).lower(): 
                        self.substrate_4_ComboBox.setCurrentText("None")            
  


                elif 'Base_Pressure' in str(item.child(i).text(0)):
                    self.base_pressure_input.setText(str(item.child(i).child(1).child(0).text(0)))

                elif 'Cool_Down_Atmosphere' in str(item.child(i).text(0)):
                    self.cool_down_gas.setCurrentText(str(item.child(i).child(0).text(0)).capitalize())


                #notes section at bottom of form
                elif "Notes" in str(item.child(i).text(0)):
                    self.notes_input.appendPlainText(str(item.child(i).child(0).text(0)))

                  #Target Material
                #the re.split is because there is a header and sometime user name field 
         #to iterate over before getting to the targets 
                elif 'Target_Material' in str(item.child(i).text(0)):
                    self.target_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))


                #lens parameters 

                elif 'Aperture' in str(item.child(i).text(0)):
                    self.aperture_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif 'Focus' in str(item.child(i).text(0)):
                    self.focus_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif "Attenuator" in str(item.child(i).text(0)):
                    self.attenuator_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif "Target_Height" in str(item.child(i).text(0)):
                    self.target_height_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                    #laser parameters 

                elif 'Laser_Voltage' in str(item.child(i).text(0)):
                    self.laser_voltage_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif 'Laser_Energy' in str(item.child(i).text(0)):
                    self.laser_energy_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif "Measured_Energy_Mean" in str(item.child(i).text(0)):
                    self.energy_mean_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif "Measured_Energy_Std" in str(item.child(i).text(0)):
                    self.energy_std_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))



           #pre-ablation parameters 

                elif 'Pre-Temperature' in str(item.child(i).text(0)) or "Pre_Ablation_Temperature" in str(item.child(i).text(0)):
                    self.pre_temperature_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                # elif 'Pre-Pressure' in str(item.child(i).text(0)) or "Pre-Ablation-Pressure" in str(item.child(i).text(0)):
                #     self.pre_pressure_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Pre-Gas" in str(item.child(i).text(0)) or "Pre-Ablation-Gas" in str(item.child(i).text(0)) or "Pre-Atmosphere" in str(item.child(i).text(0)) or "Pre_Ablation_Atmosphere_Gas" in str(item.child(i).text(0)):
                    self.pre_gas_input[int(re.split("_",str(item.text(0)))[1])-1].setCurrentText(str(item.child(i).child(0).text(0)).capitalize())

                elif "Pre-Frequency" in str(item.child(i).text(0)) or "Pre_Ablation_Frequency" in str(item.child(i).text(0)):
                    self.pre_frequency_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif "Pre-Pulses" in str(item.child(i).text(0)) or "Pre_Ablation_Pulses" in str(item.child(i).text(0)):
                    self.pre_number_pulses_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))     



                #                       #ablation parameters 

                elif re.search('^Temperature', str(item.child(i).text(0))) or "Ablation_Temperature" in str(item.child(i).text(0)):
                    self.temperature_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif re.search('^Pressure' , str(item.child(i).text(0))) or "Ablation_Pressure" in str(item.child(i).text(0)):
                    self.pressure_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif re.search("^Atmosphere" , str(item.child(i).text(0))) or "Ablation_Atmosphere_Gas" in str(item.child(i).text(0)) or re.search("^Gas",str(item.child(i).text(0))) or "Ablation-Gas-Atmosphere" in str(item.child(i).text(0)):
                    self.gas_input[int(re.split("_",str(item.text(0)))[1])-1].setCurrentText(str(item.child(i).child(0).text(0)).capitalize())

                elif re.search("^Frequency" , str(item.child(i).text(0))) or "Ablation_Frequency" in str(item.child(i).text(0)):
                    self.frequency_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(1).child(0).text(0)))

                elif re.search("^Pulses" , str(item.child(i).text(0))) or "Ablation_Pulses" in str(item.child(i).text(0)):
                    self.number_pulses_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))               

                #if instead, you click on a session, we need to go one step further:
                #to the grandchildren of the item clicked on and its value
                #otherwise, the logic is the same. I think I have to iterate again even though it is repetitive
                #because I need to pull out children in one case and grandchildren in the other. 
                elif int(item.child(i).childCount())>0:
                    item_grandChildren = []
                    for j in range(int(item.child(i).childCount())):
                        item_grandChildren.append(item.child(i).child(j).text(0))

                      #  self.base_pressure_input.setText(str(re.split("_",str(item.child(i).text(0)))[1])) 
                    #the relevant header parameters 

                        if 'Growth_ID' in str(item.child(i).child(j).text(0)):
                            self.growth_id_input.setText("")
                            self.growth_id_input.setText(str(item.child(i).child(j).child(0).text(0)))

                        elif 'User_Name' in str(item.child(i).child(j).text(0)):
                            self.name_input.setText(str(item.child(i).child(j).child(0).text(0)))    

                        elif 'Path' in str(item.child(i).child(j).text(0)):
                            self.save_path_input.setText(str(item.child(i).child(j).child(0).text(0)))    


                    #chamber parameters (also maybe called 'header' in dataFed)
                        elif 'Chamber' in str(item.child(i).child(j).text(0)) and "1a" in str(item.child(i).child(j).child(0).text(0)).lower():
                            self.chamber_ComboBox.setCurrentText("Laser 1A")

                        elif 'Chamber' in str(item.child(i).child(j).text(0)) and "1c" in str(item.child(i).child(j).child(0).text(0)).lower():
                            self.chamber_ComboBox.setCurrentText("Laser 1C")

                                                
                        elif 'Substrate_1' in str(item.child(i).child(j).text(0)):
                            if "srtio3" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_1_ComboBox.setCurrentText("SrTiO3")
                            elif "none" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_1_ComboBox.setCurrentText("None") 


                        elif 'Substrate_2' in str(item.child(i).child(j).text(0)):
                            if "srtio3" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_2_ComboBox.setCurrentText("SrTiO3")
                            elif "none" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_2_ComboBox.setCurrentText("None")  

                        elif 'Substrate_3' in str(item.child(i).child(j).text(0)):
                            if "srtio3" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_3_ComboBox.setCurrentText("SrTiO3")
                            elif "none" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_3_ComboBox.setCurrentText("None")

                        elif 'Substrate_4' in str(item.child(i).child(j).text(0)):
                            if "srtio3" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_4_ComboBox.setCurrentText("SrTiO3")
                            elif "none" in str(item.child(i).child(j).child(0).text(0)).lower(): 
                                self.substrate_4_ComboBox.setCurrentText("None")            

                    
                        elif 'Base_Pressure' in str(item.child(i).child(j).text(0)):
                            self.base_pressure_input.setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif 'Cool_Down_Atmosphere' in str(item.child(i).child(j).text(0)):
                            self.cool_down_gas.setCurrentText(str(item.child(i).child(j).child(0).text(0)).capitalize())


                         #notes section at bottom of form
                        elif "Notes" in str(item.child(i).child(j).text(0)):
                            self.notes_input.appendPlainText(str(item.child(i).child(j).child(0).text(0)))        

                       #Target Material
                          #the regex is because there is a header and sometime user name field 
         #to iterate over before getting to the targets 
                        elif 'Target_Material' in str(item.child(i).child(j).text(0)):
                            self.target_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))


                    #lens parameters 

                        elif 'Aperture' in str(item.child(i).child(j).text(0)):
                            self.aperture_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif 'Focus' in str(item.child(i).child(j).text(0)):
                            self.focus_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif "Attenuator" in str(item.child(i).child(j).text(0)):
                            self.attenuator_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif "Target_Height" in str(item.child(i).child(j).text(0)):
                            self.target_height_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                    #laser parameters 

                        elif 'Laser_Voltage' in str(item.child(i).child(j).text(0)):
                            self.laser_voltage_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif 'Laser_Energy' in str(item.child(i).child(j).text(0)):
                            self.laser_energy_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif "Measured_Energy_Mean" in str(item.child(i).child(j).text(0)) or re.search("Measured Energy$",str(item.child(i).child(j).text(0))):
                            self.energy_mean_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif "Measured_Energy_Std" in str(item.child(i).child(j).text(0)):
                            self.energy_std_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

#                       #pre-ablation parameters 

                        elif 'Pre-Temperature' in str(item.child(i).child(j).text(0)) or "Pre_Ablation_Temperature" in str(item.child(i).child(j).text(0)):
                            self.pre_temperature_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif 'Pre-Pressure' in str(item.child(i).child(j).text(0)) or "Pre_Ablation_Pressure" in str(item.child(i).child(j).text(0)):
                            self.pre_pressure_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif "Pre-Gas" in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Gas" in str(item.child(i).child(j).text(0)) or "Pre-Atmosphere" in str(item.child(i).child(j).text(0)) or "Pre_Ablation_Atmosphere_Gas" in str(item.child(i).child(j).text(0)):
                            self.pre_gas_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setCurrentText(str(item.child(i).child(j).child(0).text(0)).capitalize())

                        elif "Pre-Frequency" in str(item.child(i).child(j).text(0)) or "Pre_Ablation_Frequency" in str(item.child(i).child(j).text(0)):
                            self.pre_frequency_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif "Pre-Pulses" in str(item.child(i).child(j).text(0)) or "Pre_Ablation_Pulses" in str(item.child(i).child(j).text(0)):
                            self.pre_number_pulses_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))     



                #                       #ablation parameters 

                        elif re.search('^Temperature', str(item.child(i).child(j).text(0))) or "Ablation_Temperature" in str(item.child(i).child(j).text(0)):
                            self.temperature_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif re.search('^Pressure' , str(item.child(i).child(j).text(0))) or "Ablation_Pressure" in str(item.child(i).child(j).text(0)):
                            self.pressure_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif re.search("^Atmosphere" , str(item.child(i).child(j).text(0))) or "Ablation_Atmosphere_Gas" in str(item.child(i).child(j).text(0)) or re.search("^Gas" , str(item.child(i).child(j).text(0))) or "Ablation-Gas-Atmosphere" in str(item.child(i).child(j).text(0)):
                            self.gas_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setCurrentText(str(item.child(i).child(j).child(0).text(0)).capitalize())

                        elif re.search("^Frequency" , str(item.child(i).child(j).text(0))) or "Ablation_Frequency" in str(item.child(i).child(j).text(0)):
                            self.frequency_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(1).child(0).text(0)))

                        elif re.search("^Pulses" , str(item.child(i).child(j).text(0))) or "Ablation_Pulses" in str(item.child(i).child(j).text(0)):
                            self.number_pulses_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))     

                        


    def create_header(self):

        '''
        This is a function to create header part of the form.
        '''

        header_layout = QFormLayout()
        header_layout.addRow(QLabel("Growth ID"), self.growth_id_input)
        header_layout.addRow(QLabel("User Name"), self.name_input)
        header_layout.addRow(QLabel("Date"), self.date_input)
        header_layout.addRow(QLabel("Time"), self.time_input)
        header_layout.addRow(QLabel("Directory"), self.save_path_input)
        header_layout.addRow(self.custom_key, self.custom_value)
        return header_layout

    def create_chamber(self):
        '''
        This is a function to create chamber part of the form.
        '''
        
        chamber_layout = QFormLayout()
        chamber_layout.addRow(QLabel("Chamber"), self.chamber_ComboBox)
        chamber_layout.addRow(QLabel("Substrates"), self.substrate_1_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_2_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_3_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_4_ComboBox)
        chamber_layout.addRow(QLabel("Base Pressure (Torr)"), self.base_pressure_input)

        chamber_layout.addRow(QLabel("Cool Down Atmosphere"), self.cool_down_gas)
        return chamber_layout    
    
    
    def create_prior(self):
        
        prior_layout = QFormLayout()
       # prior_layout.addRow(QLabel("Prior Session"), self.prior_session)
        
        
        return prior_layout
    
    def create_target(self):
        
        target_layout = QFormLayout()
        target_layout.addRow(QLabel("Target"), self.target_ComboBox)
        self.target_ComboBox.setFixedSize(100, self.window_height)

        
        return target_layout
    
    #MAYBE TRY TO CREATE A STACKING ITEM IN THE SAME GRID AS UP TOP AND SEE IF IT
    #UPDATES WHEN TARGET CHANGES. THEN CAN BREAK UP stackUI
    
    
    def create_search(self):
        search_layout = QFormLayout()
        search_layout.addRow(QLabel("Search"), self.search_input)
       # search = self.search_input.text()
        return search_layout
    
   
    # function to perform the relational searching 
    # of data records
    #NOTE: 
    # the first 3 or 4 letters of a quantity will work 
    #   - "Temp" is the same as "Temperature"
    # the searching ignores any units you put
    #  - "700 °C" is the same as "700"
    # - only relational searching works 
    #   - "Temp > 700" will work, but "Temp" or "700" will not
    #   - but you can pick any number to search, so "Temp > -1000"
    #   - for example, will select all temperatures

    # - relational operators (>, <, >=,<=,!=,==) work
    #   - any number of equals signs will work for equality search
    # - you can do multiple searches at ones using "and" , "or", "xor"
    #    - you can use '&' instead of "and" and "|" instead of "or" and "^" instead of "xor"
    #    - you can use parenthesis to control order in which parts of search get evaluated 
    # - YOU MUST SEPARATE EVERYTHING BY A SPACE , for example:  temp > 700 NOT temp>700   
    #   THIS IS FOR LEGIBILITY AND TO AVOID CONFUSION WITH INTERPRETING PARTS OF WORDS AS THEIR OWN ENTRY  
    # FOR EXAMPLE, 'OR' IN 'ATTENUATOR' DOES NOT MEAN "ATTENUAT" "OR"

    def onChanged(self):
        
        #create dictionary to select relational operator since a relOp b doesn't work
        # define a different dictionary for numbers, strings, and dates because they require 
        # different operators to check for equality 
        # for numbers, perform valid float comparisons so that, for example, 0.1 + 0.2 == 0.3
        # for strings, check that the search is in the data records instead of doing an exact match
        # this allows you to, for example, search for "1A" instead of "Laser_1A"
        # it is also especially useful for searching the "Notes," which is often 
        # a long sequence of words and you probably want to know if a keywords is in the 
        # sequence rather than guess the exact sequence. This is the main reason I have created
        # my own search rather than using datafed queries (datafed requires exact matches)
        # for dates, equality means the exact date, so search for equality, not contains

        ops_num = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge ,
            "<=": operator.le,
            "==": np.isclose, # operator.eq,
            "!=": operator.ne #or operator.abs(a-b)>1e-9,
        }


        ops_str = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.contains, # operator.eq,
            "!=": operator.ne #or operator.abs(a-b)>1e-9,
        }


        ops_date = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq, # operator.eq,
            "!=": operator.ne #or operator.abs(a-b)>1e-9,
        }

        # create a dictionary for "and", "or" and "xor"
        # for similar reasons as the operational operators:
        # to programatically create a string that then gets evaluated
        # to determine the truth of the match for each data record
        # for "xor", first search if the fields match using "or" to not eliminate matches and the evaluate the fields using "xor"
        # for example, if the search is "temp > 700 xor pres > 100", first match where either temp or pres occur, 
        # then evaluate whether the matched temp > 700 xor the matched pres > 100. But if the matching is done using xor, then any record that has both 
        # a recorded temperature and a recorded pressure will evaluate to false, even if only one of the values match the search and so should evaluate 
        # to true according to the logic of "xor"
        # this is uncessesary for "and" and "or" since they are not exclusive 
        conj_dict1 = {
            "and": '&',
            "or": '|',
            "xor": ["|","^"]  
        } 



        # if there is a parenthesis, (temp > 700 or pulse > 10) and chamber=1A 
        # I need to keep track of how many searches are in the parenthesis (maybe count the conj terms)
        # and then wrap the appropriate terms in the parenthesis, the built-in eval function will take care of the rest 

        # input the search as a string
        searchStr = str(self.search_input.text() ).lower()

        # FOR TESTING: put the search string in the name text box
        #self.name_input.setText(searchStr)
       
       # make sure something has been searched before trying to parse it 
        if len(searchStr)>0:

            
            # for ease of matching, standardize everything. 
            #replace all instances of '&' with 'and' and '|' with 'or' 
            # "|" is a special regex character, so use "\|"
            # also replace all instances of "^" with "xor" 


            
            searchStr = re.sub("(?<!>|<|!) & +"," and ",searchStr)
            searchStr = re.sub("(?<!>|<|!) \| +"," or ",searchStr)
            searchStr = re.sub("(?<!>|<|!) ^ +"," xor ",searchStr)

            
            # split the search string into the component searches
            # by "and" or "or" or "xor" and remove blank spaces before and after 

            searchArray = re.split('( and | or | xor )',searchStr.strip())
            searchArray = [item.strip() for item in searchArray]
            
            
            # find the indices of the beginning and ending parentheses
            beginning_parens_indices = []
            ending_parens_indices = []
            if "(" in searchStr:
             
                for index, search in enumerate(searchArray):
                    print(index,search,("(" in search))

                    if ("(") in search:
                        beginning_parens_indices.append(index)
                    if (")") in search:
                        ending_parens_indices.append(index)
                



            # define lists for the relational operators, quantities (Temperature, etc. ), and conjuctions (and, or)
            relOp = []

            quantity_list = []
            conj_list = []
            search_array_without_conj = []


            # loop through the split searchArray and fill the above lists 
            for search in searchArray:
                # separate the conjuctions 
                if search != "and" and search != "or" and search !="xor":
                    #identify and isolate the relational operator
                    relational_operators = [] 
                    #this allows any number of equals signs
                    for relational_operator in ['>','<','>=','<=','=','!=']:
                        if relational_operator in search:
                            relational_operators.append(relational_operator)

                    #isolate the relational operator 
                    if len(relational_operator) >0 : 
                        relop = sorted(relational_operators,key=len)[-1]
                        if re.search("(?<!>|<|!)=+",relop):
                            # find all instances of any number of equal signs
                            # but not combined with anything else, no "=" and "===" but not ">="
                            # and replace with "==" to allow any number of equal signs and format the
                            # result to evaluate correctly
                            search = re.sub("(?<!>|<|!)=+","==",search)
                            relop = re.sub("(?<!>|<|!)=+","==",relop)

                        
                        relOp.append(relop)
                        search_array_without_conj.append(search)
                        
                    else:
                        relOp.append("")


                    quantity_list.append(search[0:search.find(relOp[-1])])
                else:
                    conj_list.append(search)

            # FOR TESTING: print out these arrays 
            # print("search_array_without_conj",search_array_without_conj)
            # print("quantity_list",quantity_list)
            # print('relOp:',relOp)
            # print("conj_list",conj_list)


            # loop over the quantities and replace them with the standarized version from DataFed
            # this allows the user to not type the full keyword, for example "temp" instead of "Ablation_Temperature" and "Pre_Ablation_Temperature"
            # the string_value_array is because I handle strings and numbers differently, to ignore units. 

            quantity_array = []
    
            string_value_array = []
            
           

            for quantity in quantity_list:
                print("quantity:",quantity)
                #Chamber
            
                if 'cham' in quantity:    
                    quantity_array.append(["Chamber"])
                    string_value_array.append(True) 

                #Cool_Down_Atmosphere, Ablation_Atmosphere_Gas, Pre_Ablation_Atmosphere_Gas
                elif 'atm' in quantity or 'gas' in quantity:
                    string_value_array.append(True) 
                    if 'coo' in quantity or 'dow' in quantity:
                        quantity_array.append(["Cool_Down_Atmosphere"])
                    elif 'pre' in quantity:
                        quantity_array.append(["Pre_Ablation_Atmosphere_Gas"])
                    elif "abl" in quantity:
                        quantity_array.append(["Ablation_Atmosphere_Gas"])
                    else:
                        quantity_array.append(["Cool_Down_Atmosphere","Ablation_Atmosphere_Gas", "Pre_Ablation_Atmosphere_Gas"])

                #Date
                elif 'dat' in quantity:
                    string_value_array.append(True) 
                    quantity_array.append(["Date"])

                #Time
                elif 'tim' in quantity:
                    string_value_array.append(True) 
                    quantity_array.append(["Time"])  

                #Growth_ID
                elif 'grow' in quantity or 'id' in quantity:   
                    string_value_array.append(True) 
                    quantity_array.append(["Growth_ID"])   

                #Notes
                elif 'note' in quantity: 
                    string_value_array.append(True) 
                    quantity_array.append(["Notes"])

                #Path
                elif 'path' in quantity: 
                    string_value_array.append(True) 
                    quantity_array.append(["Path"])   

                #substrate (could be Substrate_1...Substrate_4 )
                elif 'subs' in quantity:
                    string_value_array.append(True) 
                    if '1' in quantity:     
                        quantity_array.append(["Substrate_1"])
                    elif '2' in quantity:     
                        quantity_array.append(["Substrate_2"])
                    elif '3' in quantity:     
                        quantity_array.append(["Substrate_3"]) 
                    elif '4' in quantity:     
                        quantity_array.append(["Substrate_4"]) 
                    else:
                        quantity_array.append(["Substrate_1","Substrate_2","Substrate_3","Substrate_4"])

                #User_Name
                elif 'user' in quantity or 'name' in quantity:
                    string_value_array.append(True) 
                    quantity_array.append(["User_Name"])  
                    

                #The quantities with ablation and pre-ablation 
                
                #temperature
                elif 'temp' in quantity: #.lower():
                    print("temp in quantity")
                    string_value_array.append(False) 
                
                    if 'pre' in quantity:
                        print("pre in quantity")
                        quantity_array.append(["Pre_Ablation_Temperature"])
                    elif 'abl' in quantity:
                        print("abl in quantity")
                        quantity_array.append(["Ablation_Temperature"])
                    else:
                        print("neither pre nor abl in quantity")
                        quantity_array.append(["Ablation_Temperature","Pre_Ablation_Temperature"])
                #Pressure
                elif 'pres' in quantity:
                    string_value_array.append(False) 

                    #pressure is more complicated b/c "pre" is in "pressure"
                    quantity_without_pressure = quantity.replace('pres','')
                    if 'pre' in quantity_without_pressure:
                        quantity_array.append(["Pre_Ablation_Pressure"])
                    elif 'abl' in quantity_without_pressure:
                        quantity_array.append(["Ablation_Pressure"])

                    elif "bas" in quantity_without_pressure:
                        quantity_array.append(["Base_Pressure"])
                    else:
                        quantity_array.append(["Base_Pressure","Ablation_Pressure","Pre_Ablation_Pressure"])
                #Frequency
                elif 'freq' in quantity:
                    string_value_array.append(False) 
            
                    if 'pre' in quantity:
                        quantity_array.append(["Pre_Ablation_Frequency"])
                    elif 'abl' in quantity:
                        quantity_array.append(["Ablation_Frequency"])
                    
                    else:
                        quantity_array.append(["Ablation_Frequency","Pre_Ablation_Frequency"])

                #Pulses
                elif 'pul' in quantity: 
                    string_value_array.append(False)
                    print("pul in quantity") 
            
                    if 'pre' in quantity:
                        print("pre in quantity")
                        quantity_array.append(["Pre_Ablation_Pulses"])
                    elif 'abl' in quantity:
                        print("abl in quantity")
                        quantity_array.append(["Ablation_Pulses"])
                    else:
                        print("neither pre nor abl in quantity")
                        quantity_array.append(["Ablation_Pulses","Pre_Ablation_Pulses"])

                #Laser Voltage and Laser Energy
                elif 'las' in quantity:
                    string_value_array.append(False) 
            
                    if 'volt' in quantity:
                        quantity_array.append(["Laser_Voltage"])
                    elif 'ener' in quantity:
                        quantity_array.append(["Laser_Energy"])
                    else:
                        quantity_array.append(["Laser_Energy","Laser_Voltage"])

                #Measured Energy Std and Measured Energy Mean
                elif 'ene' in quantity:
                    string_value_array.append(False) 
                
                    if 'std' in quantity:
                        quantity_array.append(["Measured_Energy_Std"])
                    elif 'mea' in quantity:
                        quantity_array.append(["Measured_Energy_Mean"])
                    else:
                        quantity_array.append(["Measured_Energy_Mean","Measured_Energy_Std"]) 
                #Aperture
                elif 'aper' in quantity:
                    string_value_array.append(False) 
            
                    quantity_array.append(["Aperture"])

                #Attenuator
                elif 'att' in quantity:
                    # string_value_array.append(False) 
                    #some of these values are strings, like "1thin"
                    # but some could be numbers in mm, so decide if it is a string later
            
                    quantity_array.append(["Attenuator"])

                #Focus
                elif 'foc' in quantity:
                    string_value_array.append(False) 
                
                    quantity_array.append(["Focus"])

                #Target height and Target material
                elif 'tar' in quantity:

                    if 'hei' in quantity: 
                        string_value_array.append(False) 
   
                        quantity_array.append(["Target_Height"])
                    elif 'mat' in quantity: 
                        string_value_array.append(True) 

                        quantity_array.append(["Target_Material"])
                    else:
                        #if 
                        quantity_array.append(["Target_Height","Target_Material"])


                #now isolate the number from the unit 
            #FOR TESTING: PRINT THE QUANTITY_ARRAY
           # print("quantity_array:",quantity_array)
            
            #number 

            number_array= []

            for i in range(len(quantity_array)): 
                # "Target_Height" values are numbers, but "Target_Material" values are strings
                # use the value after this quantity to determine which one to use
                if quantity_array[i] == ["Target_Height","Target_Material"]:
                    try:
                        float(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):])
                        string_value_array.insert(i,False)
                    except:
                        string_value_array.insert(i,True)
                
                # do the same thing for "Attenuator," since some are strings, for example, "1thin" but some could be floats 
                elif quantity_array[i] == ['Attenuator']:
                    try:
                        float(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):])
                        string_value_array.insert(i,False)
                    except:
                        string_value_array.insert(i,True)
                        

    

                # create a list of the values (called numbers). 
                # Convert to datetime.datetime.date if it is a date, 
                # ignore units if it is a number
                # use .casefold() to allow it to match caselessly if it is a string

                if string_value_array[i] == True and quantity_array[i] != ['Date']:
                    number_array.append(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):].strip().replace(" ","_").casefold())

                elif quantity_array[i] == ["Date"]:
                    number_array.append(datetime.datetime.strptime(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):].strip(),"%m/%d/%Y").date())
                else:
                    print("number_array is numeric")
                    try:
                        number_array.append(float(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):]))
                    except:
                        print('cannot convert to float; assuming b/c units')
                        for j in range(len(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):])):
                            try:
                            # print(i)
                                #print(searchStr[searchStr.find(relOp)+len(relOp):-i])
                                number_array.append(float(search_array_without_conj[i][search_array_without_conj[i].find(relOp[i])+len(relOp[i]):-j]))
                                break
                            except:
                                continue

            # FOR TESTING: print out the array of numbers                 
            # print("NUMBER_array:",number_array)
            
            #make some dictionaries, to match stuff based on quantity 
            relOp_dict = {}
            conj_dict = {}
            number_dict ={}
        
            #convert these lists into dictionaries
            for q in range(len(quantity_array)):
                # if you search or the term multiple times 
                # for example temp > 600 or temp < 800 that
                # if the key already exists, make a list with both values 
                # so for example example, 
                # number_dict = {'Ablation_Temperature': [600,800] }
                # relOp_dict = {'Ablation_Temperature':['>','<']}
                # conj_dict = {'Ablation_Temperature':or}
                #
                # then later, loop over the value list to build the 
                # metadata_eval_str 

                # if one of the quantities above is a list,
                # pick the shortest element to be the dictionary key
                # for simplicity 
                quantity_unique = sorted(quantity_array[q],key=len)[0]
                if quantity_unique not in relOp_dict.keys():
                    relOp_dict.update({quantity_unique:[]})
                    number_dict.update({quantity_unique:[]})


                relOp_dict[quantity_unique].append(relOp[q])
                number_dict[quantity_unique].append( number_array[q])

                if q < len(quantity_array)-1:
                    if quantity_unique not in conj_dict.keys():
                        conj_dict.update({quantity_unique:[]})
                    if conj_list[q] == "xor":
                        conj_dict[quantity_unique].append(" ^ ") 
                    else:
                        conj_dict[quantity_unique].append(conj_list[q] ) 

            # FOR TESTING: PRINT THESE DICTIONARIES
            # print("relOp_dict:", relOp_dict)
            # print("number_dict", number_dict)
            # print("conj_dict",conj_dict)

            #define a flattened quantity_array, to loop over each value instead of the nested lists
            quantity_array_flattened = functools.reduce(operator.iconcat,quantity_array,[])
            # FOR TESTING: PRINT OUT THIS LIST
            # print("quantity_array_flattened",quantity_array_flattened)


        #hide the non-matching records

        # get the tree of records from DataFed that are in the form 
        treeView = self.prior_session

        # if the searchstr is empty, i.e. nothing has been searched, unhide everything to reset
        if len(searchStr.strip()) == 0:
            for val in treeView.findItems("", Qt.MatchRecursive | Qt.MatchContains):
                val.setHidden(False)

        # otherwise, do the matching 
        else:
            #only loop over top level items at this level 
            # so that it is just "Datasets" for example, and then
            # the child is 'HP_0613_1_Hao_Pan_06132022
            # the grandchild is 'Header','Target_1'
            # the great-grandchild is 'Ablation_Temperature' or "Ablation_Atmosphere_Gas" 
            # the great-great grandchild is 'Value' or "Oxygen"
            # if the great-great grandchild is "Value", then there are units
            # and in this example great-great-great grandchild is 700 
            # so if great-grandchild is in quantity and number relOp great-great-great grandchild 
            #unhide  

            for val in treeView.findItems("", Qt.MatchContains): 
                # unhide the top level 
                val.setHidden(False)
                
                # loop over the children, these are the individual data records
                for childNum in range(int(val.childCount())):
                        # unhide the child
                        val.child(childNum).setHidden(False)
                        # for each record, create a some dictionaries and lists to hold the data and perform the iterating 
                        metadata = {}
                        #metadata = []
                        q_array = [] 
                        metadata_matches = []
                        metadata_dict = {}
                        eval_strings = [] 


                        # FOR TESTING, print out the child and number of grandchildren 
                        child = val.child(childNum).text(0)
                        print("child:", val.child(childNum).text(0))
                        print("num of grandchildren:", int(val.child(childNum).childCount()))

                        # loop over the grandchildren ("Header","Target_1",etc. )
                        for grandchildNum in range(int(val.child(childNum).childCount())):
                            #FOR TESTING: print out the number of the grandchild
                            print("grandchildNum:" ,grandchildNum)

                            #define and unhide the grandchild
                            grandchild = val.child(childNum).child(grandchildNum).text(0)
                            val.child(childNum).child(grandchildNum).setHidden(False)
                            greatGrandchild_list = []
                        

                            #someone probably won't search for a grandchild, so loop over the great-grandchildren, 
                            # i.e. "User_Name", Ablation-Temperature", etc.

                            for greatGrandchildNum in range(int(val.child(childNum).child(grandchildNum).childCount())):
                                #these great-grandchildren are what someone would probably search, if it is in the quantity_array,
                                #then loop over the great-great-grandchildren. 
                                # But first, define and unhide it
                                val.child(childNum).child(grandchildNum).child(greatGrandchildNum).setHidden(False)

                                greatGrandchild = val.child(childNum).child(grandchildNum).child(greatGrandchildNum).text(0)
                               # print("great Grandchild:", val.child(childNum).child(grandchildNum).child(greatGrandchildNum).text(0))
                                greatGrandchild_list.append(greatGrandchild)
                            # add the list of great grandchildren to the metadata_dict and FOR TESTING, print it out
                            metadata_dict[grandchild] = greatGrandchild_list 

                            # print("*"*25)
                            # print('metadata_dict',metadata_dict)

                            # if there is no metadata, hide the child (the data record), since this is a metadata search
                            if 'no metadata found' in metadata_dict.keys():
                                val.child(childNum).setHidden(True)
                            else:
                                    # make a list of the greatgrandchildren that includes the header so that it always shows
                                    # or example quantities in "Header" and "Target_1", then "Header" and "Target_2", etc. 
                                    # and then if the search is for something in the target, it will show the header as well. 
                                    
                                    print("metadata_dict:",metadata_dict)
                                    concatinated_greatGrandchildren = metadata_dict['Header'] + metadata_dict[grandchild]
                                    # FOR TESTING, print out this concatinated list
                                    # print('concatinated_greatGrandchildren',concatinated_greatGrandchildren)

                                    # create a string to evaluate to determine if the searched quantity is in the quantities from DataFed 
                                    eval_str = ""

                                    for i in range(len(conj_list)):
                                        if conj_list[i] == "xor":
                                            
                                            eval_str = eval_str + f"bool(set({quantity_array[i]}) & set(concatinated_greatGrandchildren)) {conj_dict1[conj_list[i]][0]} "
                                            # not necessary since just for the end. 
                                            #eval_str = eval_str + f"bool(set({quantity_array[-1]}) & set(concatinated_greatGrandchildren))"
                                
                                        else:
                                            eval_str = eval_str + f"bool(set({quantity_array[i]}) & set(concatinated_greatGrandchildren)) {conj_dict1[conj_list[i]]} "
                                    eval_str = eval_str + f"bool(set({quantity_array[-1]}) & set(concatinated_greatGrandchildren))"

                                    # one problem is that the xor here matches removes terms that have both. If I search "temp = 625 xor pres = 200", it will 
                                    # remove everything with both temp and pres, but if Ablation_Temperature==625 and Ablation_Pressure=210, it should return True. 

                                    # for some reason goes through the target out of order of > 10 i.e. Target_1,Target_10,Target_11,Target_12,Target_2, etc. 

                                    # I think I have to be more flexible if a target gets skipped, i.e. no Target_3 

                                    # FOR TESTING, print stuff out  
                                    #  make a list out of these eval_strings,
                                    # print(eval_str)
                                    # print("*"*20)
                                    # print(concatinated_greatGrandchildren)

                                    # print(eval(eval_str))
                                    eval_strings.append(eval(eval_str))
                    
                    
                        # print("eval_strings",eval_strings) 

                        # loop over the grandchildren again, this time to ensure that the eval_str is True, so there is a match 
                        for grandchildNuM in range(1,int(val.child(childNum).childCount())):
                                
                            if len(eval_strings) > 0 and eval_strings[grandchildNuM] == True: 
                                for grandchildNum in np.unique([0,grandchildNuM]):
                                    # define the grandchild 
                                    grandchild = val.child(childNum).child(grandchildNum).text(0)

                                    print("grandChildNum:" ,grandchildNum)
                                    print('grandchilD',grandchild)      


                                    # want: metadata: ['Header','Target_1','Header','Target_2','Header','Target_3']

                                    # metadata_matches: ['False','True','False','True','False','False']
                                    # so append the header to the targets 
                                    if grandchild == "Header":
                                        concatinated_greatGrandchildren = metadata_dict['Header']
                                    else:
                                        # FOR TESTING: print out some header and target info 
                                        # print("metadata_dict:",metadata_dict)
                                        # print("types:")
                                        # print(type(metadata_dict['Header']))
                                        # print(metadata_dict['Header'])
                                        # print(type(metadata_dict[grandchild]))
                                        # print(metadata_dict[grandchild])

                                        concatinated_greatGrandchildren = metadata_dict['Header'] + metadata_dict[grandchild]
                                    # print out this new concatinated_greatGrandchildren list, which has matches. 
                                    print("concatinated_greatGrandchildren in new loop", concatinated_greatGrandchildren)

                                    # since there are matches, continue to the Greatgrandchildren ("Chamber", "Ablation_Temperature", etc. )
                                    for greatGrandchildNum in range(int(val.child(childNum).child(grandchildNum).childCount())):
                                        #define the greatGrandchild
                                        greatGrandchild = val.child(childNum).child(grandchildNum).child(greatGrandchildNum).text(0)
                                        # FOR TESTING, print uot the greatGrandchild
                                        # print("greatGrandchildNum",greatGrandchildNum)
                                        # print("quantity_array:",quantity_array)
                                        # print("greatGranchild",greatGrandchild)
                                        
                                        #if this greatGrandchild is the match, proceed trying to match it  
                                        if greatGrandchild in functools.reduce(operator.iconcat,quantity_array,[]):
                                            # for each greatGrandchild that has a match, loop over the search and find the match
                                            for concatinated_greatGrandchild in concatinated_greatGrandchildren:
                                                for q in range(len(quantity_array)):
                                                    # print("q not matched:",q)
                                                    # print('quantity_array not matched',quantity_array[q])
                                                    
                                                    # if there is a match, save this iteration index and proceed with the match
                                                    if greatGrandchild == concatinated_greatGrandchild and concatinated_greatGrandchild in quantity_array[q]:
                                                        print("concatinated_greatGrandchild:",concatinated_greatGrandchild)
                                                        print('q:',q)
                                                        q_array.append(q)

                                
                                        
                                                        if greatGrandchild == concatinated_greatGrandchild:
                                                            # FOR TESTING: print out some stuff 
                                                            print("greatgrandchild",greatGrandchild)
                                                            print("greatgrandchildnum",greatGrandchildNum)
                                                            
                                                            #since this is a match, proceed to the greatgreatGrandchildren ("Oxygen","Laser_1C","Value", etc. )

                                                            for greatGreatGrandchildNum in range(int(val.child(childNum).child(grandchildNum).child(greatGrandchildNum).childCount())):
                                                                # unhide the greatgreatGrandchild 
                                                                val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).setHidden(False)
                                                                
                                                                #if there are no great-great-great-grandchildren, the metadata has no units 
                                                                if int(val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).childCount()) ==0: 
                                                                        
                                                                    #units = False
                                                                    # first, check if the greatgreatGrandchild is a number by trying to convert it to a float 
                                                                    try:
                                                                        #but first, define the greatGrandchild
                                                                        greatGreatGrandchild = val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).text(0)


                                                                        # for testing, print out some stuff 
                                                                        # print("no units")

                                                                        # print("Relop:",ops_str[relOp[q]])
                                                                        # print("great-great-grandchild:",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).text(0))
                                                                        # print("number array",number_array)
                                                                        # print("number:",number_array[q])

                                                                            
                                                                        #make sure greatGreatGrandchild is a float, use this to trigger the "except" if not
                                                                        float(greatGreatGrandchild)

                                                                        # since this is the match, append True or False to the metadata_matches dictionary and 
                                                                        # the number to the metadata dictionary 
                                                                        metadata_matches.append(ops_num[relOp[q]](float(greatGreatGrandchild),number_array[q]))

                                                                        if grandchild not in metadata.keys():
                                                                            metadata.update({grandchild:{}})
                                                                        #     print(f"adding grandchild {grandchild} to metadata")
                                                                        #print("adding the inner dict")
                                                                        metadata[grandchild].update({greatGrandchild:float(greatGreatGrandchild)})


                                                                    except:
                                                                        # in the except, the float conversion has failed, so the greatgreatGrandchild is not numeric 
                                                                        # one reason is that it is a date, so check that 
                                                                        if greatGrandchild == "Date": 
                                                                            metadata_matches.append(ops_date[relOp[q]](datetime.datetime.strptime(greatGreatGrandchild,"%m/%d/%Y").date(),number_array[q]))

                                                                            if grandchild not in metadata.keys():
                                                                                metadata.update({grandchild:{}})

                                                                            metadata[grandchild].update({greatGrandchild: datetime.datetime.strptime(greatGreatGrandchild,"%m/%d/%Y").date()})

                                                                            # print("date:",datetime.datetime.strptime(greatGreatGrandchild,"%m/%d/%Y").date())
                                                                    # otherwise it is a string  
                                                                        else:

                                                                            greatGreatGrandchild = val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).text(0).casefold()
                                                                            
                                                                            metadata_matches.append(ops_str[relOp[q]](greatGreatGrandchild,str(number_array[q])))

                                                                            if grandchild not in metadata.keys():
                                                                                metadata.update({grandchild:{}})
                                                                            #      print(f"adding grandchild {grandchild} to metadata 2")
                                                                            # print("adding the inner dict 2")

                                                                            metadata[grandchild].update({greatGrandchild:greatGreatGrandchild.casefold()})
                                                                else:
                                                                    #there is a great-great-great-grandchild, so the metadata has units 
                                                                    #units = True
                                                                    
                                                                    # loop over the greatGreatGreatGrandchildren, where is where the numbers are 
                                                                    for greatGreatGreatGrandchildNum in range(int(val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).childCount())):
                                                                        # unhide the greatGreatGreatGrandchildren 
                                                                        val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).child(greatGreatGreatGrandchildNum).setHidden(False)

                                                                        
                                                                        # print("great-great-great-grandchild:",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).child(greatGreatGreatGrandchildNum).text(0))
                                                                        # print("number_array",number_array)

                                                                        # ensure that the greatGreatGrandchild is "Value", to more efficiently get to the number. 
                                                                        # It would be pointless to search to for unit, since everything with this quantity has the same unit, so we can just skip over that 
                                                                        if val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).text(0) == "Value":
                                                                            # check if it is actually a number by trying to convert to a float. If it is somehow not, convert to a caseless string. 
                                                                            # either way, append to the metadata and metadata_matches dictionaries. 
                                                                            # and FOR TESTING print out a bunch of stuff along the way


                                                                            try:
                                                                                greatGreatGreatGrandchild = val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).child(greatGreatGreatGrandchildNum).text(0)
                                                                                # print("Relop:",ops_num[relOp[q]])
                                                                                # print('number:', number_array[q])

                                                                                
                                                                                metadata_matches.append(ops_num[relOp[q]](float(greatGreatGreatGrandchild),number_array[q]))

                                                                                
                                                                                # print("val:",val.text(0))
                                                                                # print("val hidden?",val.isHidden())
                                                                                # # val.child(childNum).setHidden(True)
                                                                                # print("child:",val.child(childNum).text(0))
                                                                                # print("child hidden?",val.child(childNum).isHidden())
                                                                                # #val.child(childNum).child(grandchildNum).setHidden(True)
                                                                                # print("grandchild:",val.child(childNum).child(grandchildNum).text(0))
                                                                                # print("grandchild hidden?",val.child(childNum).child(grandchildNum).isHidden())

                                                                                # #val.child(childNum).child(grandchildNum).child(greatGrandchildNum).setHidden(True)
                                                                                # print("great-grandchild:",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).text(0))
                                                                                # print("great-grandchild hidden?",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).isHidden())
                                                                                # #val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).setHidden(True)
                                                                                # print("great-great-grandchild:",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).text(0))
                                                                                # print("great-great-grandchild hidden?",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).isHidden())
                                                                                # #val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).child(greatGreatGreatGrandchildNum).setHidden(True)
                                                                                # print("great-great-great-grandchild:",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).child(greatGreatGreatGrandchildNum).text(0))
                                                                                # print("great-great-great-grandchild hidden?",val.child(childNum).child(grandchildNum).child(greatGrandchildNum).child(greatGreatGrandchildNum).child(greatGreatGreatGrandchildNum).isHidden())

                                                                                if grandchild not in metadata.keys():
                                                                                    print("creating new metadata key:", grandchild)
                                                                                    metadata.update({grandchild:{}})
                                                                                
                                                                                metadata[grandchild].update( {greatGrandchild:float(greatGreatGreatGrandchild)})



                                                                            except:
                                                                                print("could not convert value with unit to a float. Proceeding assuming a string")
                                                                                #metadata.append(grandchild)
                                                                                if grandchild not in metadata.keys():
                                                                                    print("Creating a new metadata key:", grandchild)
                                                                                    metadata.update({grandchild:{}})
                                                                                metadata[grandchild].update({greatGrandchild:greatGreatGreatGrandchild.casefold()})

                                                                                metadata_matches.append(ops_str[relOp[q]](str(greatGreatGreatGrandchild),str(number_array[q])))                                                                                                                                                                                                                                                 
                            # if there is not a match, hide the grandchild 
                            # and record that it is not a match  in the metadata_matches dict                                    
                            else:
                                val.child(childNum).child(grandchildNum).setHidden(True)
                                metadata_matches.append(False)
                                
                                if val.child(childNum).child(grandchildNum).text(0) != "Header":

                                    metadata_matches.append(False)


                        #FOR TESTING print out the metadata and metadata_matches dictionaries
                        # before create the eval_strings 
                       # print('metadata:',metadata)
                        # print('metadata_matches',metadata_matches)

                        # create a dictionary connect each match with the quantity and construct strings that can be evaluated
                        # to determine whether the match is True or False 

                        metadata_eval_dict = {}
                        # loop over the metadata dictionary 
                        for key1 in metadata.keys():
                        
                            metadata_eval_str = ""
                            # FOR TESTING: print out the key 
                            # print("key1",key1)
                            # print(metadata[key1])
                            # print(metadata[key1].values())
                            # print(len(metadata[key1]))
                            
                            # loop over the nested dictionary, and format the eval strings 
                            for index2,key2 in enumerate(metadata[key1].keys()):
                                metadata_eval_str = ""

                               # key2_2 = key2

                                # print("key2:",key2)
                                # print("value2",metadata[key1][key2])

                                # the below keys are more complicated because there multiple 
                                # quantities that could be matched, so pick the shorted one to match
                                # with the searched quantity 

                                if key2 not in number_dict.keys():
                                    if key2 == "Ablation_Atmosphere_Gas" and "Ablation_Atmosphere_Gas" not in relOp_dict.keys(): #FINISH THE NEXT ELIF AND ADD ONE TO MATCH PRESSURE 
                                        key2_1 = "Cool_Down_Atmosphere"
                                    elif key2 == "Pre_Ablation_Atmosphere_Gas":
                                        if "Ablation_Atmosphere_Gas" in relOp_dict.keys():
                                            key2_1 = "Ablation_Atmosphere_Gas"
                                    
                                    
                                    elif key2 == "Ablation_Pressure" and "Ablation_Pressure" not in relOp_dict.keys():
                                        key2_1 = "Base_Pressure"
                                    
                                    elif key2 == "Pre_Ablation_Pressure" and "Ablation_Pressure" not in relOp_dict.keys() and "Pre_Ablation_Pressure" not in relOp_dict.keys():
                                        key2_1 = "Base_Pressure"
                                    elif key2 == "Pre_Ablation_Pressure" and "Ablation_Pressure" in relOp_dict.keys() and "Pre_Ablation_Pressure" not in relOp_dict.keys():
                                        key2_1 = "Ablation_Pressure"

                                    elif key2 == "Target_Material":
                                        key2_1 = "Target_Height"

                                    elif key2 == "Laser_Voltage":
                                        key2_1 = "Laser_Energy"

                                    # this one is for if the pre-ablation quantity has been searched ("Pre-")

                                    elif key2[4:] in number_dict.keys():
                                        key2_1 = key2[4:]
                                    
                                    else:
                                        #continue or 
                                        key2_1 = key2
                                      #  continue
                                else:
                                    key2_1 = key2

                                # each set of quantities have to be formatted separately, so do that     
                                for i in range(len(number_dict[key2_1])):
                                    key2_2 = key2
                                    if key2 == 'Cool_Down_Atmosphere':
                                        if 'Ablation_Atmosphere_Gas' not in quantity_array_flattened or 'Pre_Ablation_Atmosphere_Gas' not in quantity_array_flattened:
                                            # in this 'if' statement, 'cool_down_atmosphere' has been specified, so do it separately
                                            #continue
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                        elif "Ablation_Atmosphere_Gas" in relOp_dict.keys() or "Pre_Ablation_Atmosphere_Gas" in relOp_dict.keys():
                                            # this 'if statement is another way to confirm that 'Cool_Down_Atmosphere' has been specified, so do it separately
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "

                                    elif key2 == "Ablation_Atmosphere_Gas":
                                        if "Ablation_Atmosphere_Gas" in relOp_dict.keys():
                                            # "Ablation_Atmosphere_Gas" has been specified, so do it separately 
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                        else:
                                            if ("Header" in metadata.keys()) and ('Cool_Down_Atmosphere' in metadata['Header'].keys()):
                                                # the type of atmosphere has not been specified, so do an "or" search with all three 
                                                if "Pre_Ablation_Atmosphere_Gas" in metadata[key1].keys():
                                                    try:
                                                        index_ablation_atm_gas = np.where(np.array(quantity_array_flattened) == 'Ablation_Atmosphere_Gas')[0]

                                                        if index_ablation_atm_gas.size > 0 and index_ablation_atm_gas[0] + 1 < len(quantity_array_flattened):
                                                            next_element = quantity_array_flattened[index_ablation_atm_gas[0] + 1]

                                                            if next_element == "Pre_Ablation_Atmosphere_Gas":
                                                                metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata['Header']['Cool_Down_Atmosphere']}','{number_dict['Cool_Down_Atmosphere'][i]}') or "
                                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata[key1]['Ablation_Atmosphere_Gas']}','{number_dict['Cool_Down_Atmosphere'][i]}') or "
                                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata[key1]['Pre_Ablation_Atmosphere_Gas']}','{number_dict['Cool_Down_Atmosphere'][i]}')) "
                                                            else:
                                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}) "
                                                    except:
                                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                                else:
                                                    if "Ablation_Atmosphere_Gas" in relOp_dict.keys():
                                                        # "Ablation_Atmosphere_Gas" has been specified, so do it separately 

                                                        metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                                    else:
                                                        # "Pre_Ablation_Atmosphere_Gas" is not in the metadata, so do the "or" search without that one 
                                                        metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata['Header']['Cool_Down_Atmosphere']}','{number_dict['Cool_Down_Atmosphere'][i]}') or "
                                                        metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata[key1]['Ablation_Atmosphere_Gas']}','{number_dict['Cool_Down_Atmosphere'][i]}')) "
                                                    
                                            else:
                                                if 'Pre_Ablation_Atmosphere_Gas' in metadata[key1].keys():
                                                    try:
                                                        index_pre_ablation_pressure = np.where(np.array(quantity_array_flattened) == 'Pre_Ablation_Pressure')[0]

                                                        if index_pre_ablation_pressure.size > 0 and index_pre_ablation_pressure[0] + 1 < len(quantity_array_flattened):
                                                            next_element = quantity_array_flattened[index_pre_ablation_pressure[0] + 1]

                                                            if next_element == "Ablation_Pressure":
                                                                metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata[key1]['Ablation_Atmosphere_Gas']}','{number_dict['Cool_Down_Atmosphere'][i]}') or "
                                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata[key1]['Pre_Ablation_Atmosphere_Gas']}','{number_dict['Cool_Down_Atmosphere'][i]}')) "
                                                            else:
                                                                #pre_ablation-pressure is specified, so just do "Ablation_Atmosphere_Gas" separately 
                                                                # base pressure is also in metadata, and it is matched, but do it separately
                                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                                    except:
                                                        # pre ablation atmosphere gas is matched but it must be specified before in the search string for the except to trigger. 
                                                        # Ablation_atmosphere gas must last entry of quantity_array_flattened, so cannot to [i+1]. so do it separately.                 
                                                        metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                                else:
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                                
                                    
                                    elif key2 == "Pre_Ablation_Atmosphere_Gas":
                                        index_ablation_atm_gas = np.where(np.array(quantity_array_flattened) == 'Ablation_Atmosphere_Gas')[0]

                                        if "Pre_Ablation_Atmosphere_Gas" in relOp_dict.keys():
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "
                                        elif "Ablation_Atmosphere_Gas" in metadata[key1].keys() and index_ablation_atm_gas.size > 0 and index_ablation_atm_gas[0] + 1 < len(quantity_array_flattened):
                                            next_element = quantity_array_flattened[index_ablation_atm_gas[0] + 1]

                                            if next_element == "Pre_Ablation_Atmosphere_Gas":
                                                continue
                                        elif "Cool_Down_Atmosphere" in relOp_dict.keys():
                                            if "Pre_Ablation_Atmosphere_Gas" in relOp_dict.keys():
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Ablation_Atmosphere_Gas'][i]}'] ('{metadata[key1]['Ablation_Atmosphere_Gas']}','{number_dict['Ablation_Atmosphere_Gas'][i]}') "
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata['Header']['Cool_Down_Atmosphere']}','{number_dict['Cool_Down_Atmosphere'][i]}') or "
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Cool_Down_Atmosphere'][i]}'] ('{metadata[key1]['Pre_Ablation_Atmosphere_Gas']}','{number_dict['Cool_Down_Atmosphere'][i]}')) "
                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Ablation_Atmosphere_Gas'][i]}'] ('{metadata[key1]['Ablation_Atmosphere_Gas']}','{number_dict['Ablation_Atmosphere_Gas'][i]}') "


                                    elif key2 == "Base_Pressure":
                                        if 'Ablation_Pressure' not in quantity_array_flattened or 'Pre_Ablation_Pressure' not in quantity_array_flattened:

                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "

                                        elif "Ablation_Pressure" in relOp_dict.keys() and "Pre_Ablation_Pressure" in relOp_dict.keys():
                                          
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "

                                    elif key2 == "Ablation_Pressure":
                                        if "Ablation_Pressure" in relOp_dict.keys(): 
                                           
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "
                                        else:
                                         
                                            if ('Header' in metadata.keys() and 'Base_Pressure' in metadata['Header'].keys()):
                                                if 'Pre_Ablation_Pressure' in metadata[key1].keys():
                                                    try:
                                                        index_ablation_pressure = np.where(np.array(quantity_array_flattened) == 'Ablation_Pressure')[0]

                                                        
                                                        if index_ablation_pressure.size > 0 and index_ablation_pressure[0] + 1 < len(quantity_array_flattened):
                                                            next_element = quantity_array_flattened[index_ablation_pressure[0] + 1]

                                                            if next_element == "Pre_Ablation_Pressure":                                                            
                                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata['Header']['Base_Pressure']},{number_dict['Base_Pressure'][i]}) or "
                                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata[key1]['Ablation_Pressure']},{number_dict['Base_Pressure'][i]}) or "
                                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata[key1]['Pre_Ablation_Pressure']},{number_dict['Base_Pressure'][i]})) "
                                                            else:
                                                                #pre_ablation-pressure and base pressure are matched, so do all separately 
                                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "
                                                    except:
                                                        # pre ablation pressure is matched but it must be before in the searchStr for the except to trigger.
                                                        #  Ablation_pressure must last entry of quantity_array_flattened, so cannot to [i+1] so specify separately 
                                                        metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "

                                                else:
                                                    if "Ablation_Pressure" in relOp_dict.keys():
                                                        metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "
                                                    else:
                                                        metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata['Header']['Base_Pressure']},{number_dict['Base_Pressure'][i]}) or "
                                                        metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata[key1]['Ablation_Pressure']},{number_dict['Base_Pressure'][i]})) "
                                            
                                            else:
                                                if 'Pre_Ablation_Pressure' in metadata[key1].keys():
                                                    try:
                                                        index_ablation_atm_gas = np.where(np.array(quantity_array_flattened) == 'Ablation_Atmosphere_Gas')[0]

                                                        if index_ablation_atm_gas.size > 0 and index_ablation_atm_gas[0] + 1 < len(quantity_array_flattened):
                                                            next_element = quantity_array_flattened[index_ablation_atm_gas[0] + 1]

                                                            if next_element == "Pre_Ablation_Atmosphere_Gas":
                                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata[key1]['Ablation_Pressure']},{number_dict['Base_Pressure'][i]}) or "
                                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata[key1]['Pre_Ablation_Pressure']},{number_dict['Base_Pressure'][i]})) "
                                                            else:
                                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "
                                                    except:
                                                        # pre ablation pressure is matched but it must be before in the searchStr for the except to trigger.
                                                        #  Ablation_pressure must last entry of quantity_array_flattened, so cannot to [i+1] so specify separately              
                                                        metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "
                                                else:
                                                    metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "
            
                                         
                                    elif key2 == "Pre_Ablation_Pressure":


                                        # find the indices of Ablation_Pressure and Pre_Ablation_Pressure in quantity_array_flattened
                                        # because if they are not next to each other than they had to have been specified separately in the search query
                                        index_ablation_pressure = np.where(np.array(quantity_array_flattened) == 'Ablation_Pressure')[0]

                                        if "Pre_Ablation_Pressure" in relOp_dict.keys():
                                            # the only way this can happen is if it is specified 
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Pre_Ablation_Pressure'][i]}'] ({metadata[key1]['Pre_Ablation_Pressure']},{number_dict['Pre_Ablation_Pressure'][i]}) "



                                        elif "Ablation_Pressure" in metadata[key1].keys() and index_ablation_pressure.size > 0 and index_ablation_pressure[0]+ 1 < len(quantity_array_flattened): 
                                            if next_element == "Pre_Ablation_Pressure":
                                            # in this case, "Pre_Ablation_Pressure" is not in relOp_dict.keys()
                                            # and Ablation_Pressure is in metadata
                                            # so pre-ablation not specified and ablation can take care of it
                                                continue

                                        elif "Base_Pressure" in relOp_dict.keys(): 
                                            if "Pre_Ablation_Pressure" in relOp_dict.keys():
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Ablation_Pressure'][i]}'] ({metadata[key1]['Ablation_Pressure']},{number_dict['Ablation_Pressure'][i]})) "
                                            
                                            else:
                                            # in this case, type of pressure is not specified, 
                                            # but pre ablation pressure is not in metadata but base pressure is 

                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata['Header']['Base_Pressure']},{number_dict['Base_Pressure'][i]}) or "
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Base_Pressure'][i]}'] ({metadata[key1]['Pre_Ablation_Pressure']},{number_dict['Base_Pressure'][i]})) "
                                        else:
                                            # Pre-ablation pressure is not in relOp_dict.keys()
                                            # ablation_pressure is not in metadata[key1].keys()
                                            # Base pressure is not in relOp_dict.keys()

                                            # so Ablation_and pre_ablation are specified,
                                            # but ablation_pressure is not in metadata 
                                            #  
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Ablation_Pressure'][i]}'] ({metadata[key1]['Pre_Ablation_Pressure']},{number_dict['Ablation_Pressure'][i]}) "

                                                                        
                                    elif key2 == "Substrate_1":
                                        #print("key2 == substrate_1")
                                        
                                        
                                        if 'Substrate_1' in quantity_array_flattened and 'Substrate_2' in quantity_array_flattened and 'Substrate_3' in quantity_array_flattened and 'Substrate_4' in quantity_array_flattened:
                                        # either all or none were specified
                                            if "Substrate_1" in relOp_dict.keys() and "Substrate_2" not in relOp_dict.keys() and "Substrate_3" not in relOp_dict.keys() and "Substrate_4" not in relOp_dict.keys():
                                                # this means that none were specified, so do an "or" search with however many are present in the metadata 
                                                if "Substrate_4" in metadata[key1].keys():
                                                    metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_1']}','{number_dict[key2][i]}') or "
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_2']}','{number_dict[key2][i]}') or "
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_3']}','{number_dict[key2][i]}') or "
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_4']}','{number_dict[key2][i]}'))"
                                                elif "Substrate_3" in metadata[key1].keys():
                                                    metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_1']}','{number_dict[key2][i]}') or "
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_2']}','{number_dict[key2][i]}') or "
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_3']}','{number_dict[key2][i]}')) "
                                                elif "Substrate_2" in metadata[key1].keys():
                                                    metadata_eval_str = metadata_eval_str + f" (ops_str['{relOp_dict[key2][i]}'] ({metadata[key1]['Substrate_1']}','{number_dict[key2][i]}') or "
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ({metadata[key1]['Substrate_2']}','{number_dict[key2][i]}')) "
                                                else:
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_1']}','{number_dict[key2][i]}') "
     
                                            else:
                                                #this means that none were specified or present in the metadata, so do substrate_1 separately 
                                                print("substrate_1 only in metadata")
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_1']}','{number_dict[key2][i]}') "

                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1]['Substrate_1']}','{number_dict[key2]}') "
                                    elif key2 == "Substrate_2":
                                        if 'Substrate_1' in quantity_array_flattened and 'Substrate_2' in quantity_array_flattened and 'Substrate_3' in quantity_array_flattened and 'Substrate_4' in quantity_array_flattened:
                                        
                                            if "Substrate_1" in relOp_dict.keys() and "Substrate_2" not in relOp_dict.keys() and "Substrate_3" not in relOp_dict.keys() and "Substrate_4" not in relOp_dict.keys():
                                                continue
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "

                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "


                                    elif key2 == "Substrate_3":
                                        if 'Substrate_1' in quantity_array_flattened and 'Substrate_2' in quantity_array_flattened and 'Substrate_3' in quantity_array_flattened and 'Substrate_4' in quantity_array_flattened:
                                        
                                            if "Substrate_1" in relOp_dict.keys() and "Substrate_2" not in relOp_dict.keys() and "Substrate_3" not in relOp_dict.keys() and "Substrate_4" not in relOp_dict.keys():
                                                continue
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2[i]]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "

                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "

                                    elif key2 == "Substrate_4":
                                        if 'Substrate_1' in quantity_array_flattened and 'Substrate_2' in quantity_array_flattened and 'Substrate_3' in quantity_array_flattened and 'Substrate_4' in quantity_array_flattened:
                                        
                                            if "Substrate_1" in relOp_dict.keys() and "Substrate_2" not in relOp_dict.keys() and "Substrate_3" not in relOp_dict.keys() and "Substrate_4" not in relOp_dict.keys():
                                                continue
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "

                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}') "

                                    elif key2 == "Laser_Energy":
                                        if "Laser_Voltage" in relOp_dict.keys():
                                    
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "
                                        else:
                                            if "Laser_Voltage" in metadata[key1].keys():
                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) or "
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1]['Laser_Voltage']},{number_dict[key2][i]})) "
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "
                                    
                                    elif key2 == "Laser_Voltage":
                                        if key2 not in relOp_dict.keys(): 
                                            if "Laser_Energy" in metadata[key1].keys():
                                                continue
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Laser_Energy'][i]}'] ({metadata[key1][key2]},{number_dict['Laser_Energy'][i]}) "

                                        else:
                                        
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2_1][i]}) "

                                    elif key2 == "Measured_Energy_Std":
                                        if "Measured_Energy_Mean" in relOp_dict.keys():
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "
                                        else:
                                            if "Measured_Energy_Mean" in metadata[key1].keys():
                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) or "
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1]['Measured_Energy_Mean']},{number_dict[key2][i]})) "
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "
                                    elif key2 == "Measured_Energy_Mean":
                                        if key2 not in relOp_dict.keys():
                                            if "Measured_Energy_Std" in metadata[key1].keys():
                                                continue
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict['Measured_Energy_Std'][i]}'] ({metadata[key1][key2]},{number_dict['Measured_Energy_Std'][i]})) "
                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "

                                    elif key2 == "Target_Height":
                                        if "Target_Material" in relOp_dict.keys():
                                            metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "
                                        else:
                                            if "Target_Material" in metadata[key1].keys():
                                                try:
                                                    #if "Target_Material" is not in relOp_dict.keys() then the type of target is not specified
                                                    #this 'if' statement is for when both 'Target_Material' and "Target_Height" are in the metadata
                                                    # normally, we would do an 'or' search with both, However, since "Target_Material" is a string, while "Target_Height" is a  float
                                                    # it doesn't make sense to search for both. Thus, we select the one that matches the type of the searched value. 
                                                    # First, check if the searched value is a number by trying to convert to a float

                                                    float(number_dict[key2][i])

                                                    metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2_1][i]}'] ({metadata[key1][key2]},{number_dict[key2][i]}) "
                                                except:
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1]['Target_Material']}','{number_dict[key2_1][i]}') "
                                            else:
                                                # in this situation:
                                                # the metadata key is "Target_Height"
                                                #  Target_Material is not in relOp_dict.keys(), so it has not been specifically searched for 
                                                #     -either only target has been specified for target_height has been specified
                                                # Target_Material is not in metadata keys, so the metadata is for Target_Material
                                                #     -this is a string, so use ops_str 
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                                    
                                    elif key2 == "Target_Material":
                                        if key2 not in relOp_dict.keys(): 
                                            if "Target_Height" in metadata[key1].keys():
                                                continue
                                            else:
                                                metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict['Target_Height'][i]}'] ('{metadata[key1][key2]}','{number_dict['Target_Height'][i]}') "
                                        else:
                                            metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2_1][i]}'] ('{metadata[key1][key2]}','{number_dict[key2_1][i]}') "
                          
                                    elif "Pre_" in key2:
                                        key2_2 = key2[4:]
                                        print("key2",key2)
                                        print(metadata[key1][key2])
                                        print(type(metadata[key1][key2]))
                                        print("key2_2",key2_2)
                                      
                                        
                                        if key2_2 in metadata[key1].keys() and type(metadata[key1][key2_2]) == list:
                                                print("T1")
                                                print(metadata[key1][key2])
                                                metadata[key1][key2_2] = metadata[key1][key2_2][0]
                                        if type(metadata[key1][key2]) == list:
                                                print(metadata[key1][key2_2])
                                                metadata[key1][key2] = metadata[key1][key2][0]
                                        if  key2 not in relOp_dict.keys():
                                            #so Ablation_Pulses is in relOp_dict but not Pre-Ablation_Pulses, for example
                                            # but pre-pulses is in metadata, so didn't specify 
                                        
                                            
                                            if key2_2 in metadata[key1].keys(): 
                                                try:
                                                    metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2_2][i]}'] (float({metadata[key1][key2_2]}),{number_dict[key2[4:]][i]}) or"
                                                    metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_2][i]}'] (float({metadata[key1][key2]}),{number_dict[key2[4:]][i]}))"
                                                except:
                                                    metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2[4:]][i]}'] ('{metadata[key1][key2[4:]]}','{number_dict[key2[4:]][i]}') or"
                                                    metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2[4:]][i]}'] ('{metadata[key1][key2]}','{number_dict[key2[4:]][i]}'))"
                                            else:
                                                try:
                                                    metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_2][i]}'] (float({metadata[key1][key2]}),{number_dict[key2_2][i]})"
                                                except:
                                                    metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2_2][i]}'] ('{metadata[key1][key2]}', '{number_dict[key2_2][i]}')"


                                        else: #key2 in relOp.keys(), so specified Pre-Ablation_Pulses, or example 
                                            try:
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] (float({metadata[key1][key2]}),{number_dict[key2][i]})"
                                            except:
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}', '{number_dict[key2][i]}')"


                                            

                                        

                                    else:
                                        #this is for Date, Growth_ID, Time, things specified separately?, etc. 
                                        #append to metadata_eval_str based on type
                                        if "Pre_"+key2 in metadata[key1].keys():
                                            try:
                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2][i]}'] (float({metadata[key1]['Pre_'+key2]}),{number_dict[key2][i]}) or"
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] (float({metadata[key1][key2]}),{number_dict[key2][i]}))"
                                            except:
                                                metadata_eval_str = metadata_eval_str + f" (ops_num['{relOp_dict[key2][i]}'] ('{metadata[key1]['Pre_'+key2]}','{number_dict[key2][i]}') or"
                                                metadata_eval_str = metadata_eval_str + f" ops_num['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}'))"    
                                        else:
                                            try:
                                                if type(metadata[key1][key2]) == list:
                                                   # if the metadata is a list, just select the first element for now                                             
                                                    metadata[key1][key2] = metadata[key1][key2][0]
                                                    #print("T3",metadata[key1][key2])

                                                metadata_eval_str = metadata_eval_str + f"ops_num['{relOp_dict[key2][i]}'] ({float(metadata[key1][key2])},{number_dict[key2][i]}) "
                                            except:
                                                if key2 == 'Date':
                                                    #perform date comparison
                                                    metadata_eval_str = metadata_eval_str + f" ops_date['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}')"

                                                else:
                                                    metadata_eval_str = metadata_eval_str + f" ops_str['{relOp_dict[key2][i]}'] ('{metadata[key1][key2]}','{number_dict[key2][i]}')"

                                    
                                    if len(metadata_eval_str) > 0:
                                        if 'Pressure' in key2 and metadata_eval_str.count("or") == 2:
                                            print("Y")
                                        

                                        if key2 == key2_2:
                                            if "Atmosphere" in key2 and "Cool_Down_Atmosphere" in relOp_dict.keys() and "Ablation_Atmosphere_Gas" not in relOp_dict.keys() and "Pre_Ablation_Atmosphere_Gas" not in relOp_dict.keys(): #metadata_eval_str.count("or") ==2:
                                                if "Cool_Down_Atmosphere" not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({"Cool_Down_Atmosphere":{}})
                                                metadata_eval_dict["Cool_Down_Atmosphere"].update({key1:metadata_eval_str})
                                            
                                            elif 'Pressure' in key2 and "Base_Pressure" in relOp_dict.keys() and "Ablation_Pressure" not in relOp_dict.keys() and "Pre_Ablation_Pressure" not in relOp_dict.keys(): #metadata_eval_str.count("or") == 2:
                                                print("Y")
                                                if "Base_Pressure" not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({"Base_Pressure":{}})
                                                metadata_eval_dict["Base_Pressure"].update({key1:metadata_eval_str})

                                            elif key2 == "Target_Material" and key2 not in relOp_dict.keys():
                                                if "Target_Height" not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({"Target_Height":{}})
                                                metadata_eval_dict["Target_Height"].update({key1:metadata_eval_str})


                                            elif key2 == "Laser_Voltage" and key2 not in relOp_dict.keys():
                                                if "Laser_Energy" not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({"Laser_Energy":{}})
                                                metadata_eval_dict["Laser_Energy"].update({key1:metadata_eval_str})

                                            
                                            else:
                                                if key2 not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({key2:{}})

                                                metadata_eval_dict[key2].update({key1:metadata_eval_str})
                                        else:
                                            if key2_2 in relOp_dict.keys():
                                                if key2_2 not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({key2_2:{}})

                                                metadata_eval_dict[key2_2].update({key1:metadata_eval_str})

                                            if key2 in relOp_dict.keys():
                                                if key2 not in metadata_eval_dict.keys():
                                                    metadata_eval_dict.update({key2:{}})

                                                metadata_eval_dict[key2].update({key1:metadata_eval_str})
                                    
                                    if i < len(number_dict[key2_1])-1 and key2_1 in conj_dict:
                                        metadata_eval_str = metadata_eval_str + f" {conj_dict[key2_1][i-1]} "
                                    elif i== len(number_dict[key2_1])-1:
                                        metadata_eval_str = metadata_eval_str + ") "                                                        

                        

                        print('metadata_eval_dict',metadata_eval_dict) 

                        # change the order of metadata_eval_dict to be in numerical order instead of string order, so 
                        # Header, Target_1, Target_2, Target_3, Target_4, Target_5, Target_6, Target_7, Target_8, Target_9, Target_10, Target_11,Target_12
                        # instead of 
                        # Header, Target_1, Target_10, Target_11, Target_12, Target_2 ... 
                        # for ease of iterating later 

                        for key in metadata_eval_dict.keys():
                            sorted_items = sorted(metadata_eval_dict[key].items(), key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x[0])])


                            metadata_eval_dict[key] = OrderedDict(sorted_items)


                        # now actually evaluate each of these metadata_eval_strings (stored in metadata_eval_dict) 
                    
                        if (metadata_eval_dict) != {}:
                            # initialize the eval strings. 
                            metadata_eval_dict2 = {}

                            metadata_eval_str2 = ""

                            Metadata_eval_str_1 = ""

                            Metadata_eval_str_2 = ""
                            Metadata_eval_str_3 = ""
                            Metadata_eval_str_4 = ""
                            Metadata_eval_str_5 = ""
                            Metadata_eval_str_6 = ""
                            Metadata_eval_str_7 = ""
                            Metadata_eval_str_8 = ""
                            Metadata_eval_str_9 = ""
                            Metadata_eval_str_10 = ""
                            Metadata_eval_str_11 = ""
                            Metadata_eval_str_12 = ""


                            length_list = [] 

                            print("metadata_eval_dict sorted", metadata_eval_dict)

                            metadata_eval_str2 = ""
                            key1_list = []
                            # loop over search and the metadata to find matches 
                            for index1, key1 in enumerate(relOp_dict.keys()):
                                print("key1",key1)
                                if key1 not in metadata_eval_dict.keys():
                                    # if this metadata only has some of the quantities required to match
                                    # but not all of them, set the eval to False 
                                    if key1 in conj_dict and 'and' in conj_dict[key1]:                                           
                                        Metadata_eval_str_1 = "False"
                                        Metadata_eval_str_2 = "False"
                                        Metadata_eval_str_3 = "False"
                                        Metadata_eval_str_4 = "False"
                                        Metadata_eval_str_5 = "False"
                                        Metadata_eval_str_6 = "False"
                                        Metadata_eval_str_7 = "False"
                                        Metadata_eval_str_8 = "False"
                                        Metadata_eval_str_9 = "False"
                                        Metadata_eval_str_10 = "False"
                                        Metadata_eval_str_11 = "False"
                                        Metadata_eval_str_12 = "False"
                                    continue
                                # print("index1",index1)
                                # print('value1:',metadata_eval_dict[key1])

                                # print("length",len(metadata_eval_dict[key1].keys()))
                                length_list.append(len(metadata_eval_dict[key1].keys()))
                                counter1=0
                                counter2=1
                                key2_list= [] 
                                key1_list.append(key1)
                                count = 0
                                counted = False
                                # loop over however many Header, Target_i there are 
                                for index2,key2 in enumerate(metadata_eval_dict[key1].keys()):
        
                                    # print('index2:',index2,'key2:',key2)
                                    # print(metadata_eval_dict[key1][key2])
                                    # print("key1",key1)
                                    
                    
                                    metadata_eval_dict2[key2] = metadata_eval_dict[key1][key2]
                    #                print("key1",key1)
                                    key2_list.append(key2)
                                    if index2 == 0:
                                        if key1 in conj_dict.keys() and index2 < len(relOp_dict.keys())-1:
                    
                                            try:
                                                Metadata_eval_str_1 = Metadata_eval_str_1 + metadata_eval_dict[key1][key2]
                                                Metadata_eval_str_1 = Metadata_eval_str_1 + " " + conj_dict[key1][index2-1] + " " 
                                            except:
                                                Metadata_eval_str_1 = Metadata_eval_str_1 + metadata_eval_dict[key1][key2]
                                                Metadata_eval_str_1 = Metadata_eval_str_1 + " " +conj_dict[key1][index2-1]+ " " 
                                        else:
                                            Metadata_eval_str_1 = Metadata_eval_str_1 + " " + metadata_eval_dict[key1][key2]



                                        if key2 == "Header":
                                            # make sure that the eval strings have a header 
                                            Metadata_eval_str_2 = Metadata_eval_str_2 + " " + metadata_eval_dict[key1][key2]

                                            Metadata_eval_str_3 = Metadata_eval_str_3 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_4 = Metadata_eval_str_4 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_5 = Metadata_eval_str_5 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_6 = Metadata_eval_str_6 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_7 = Metadata_eval_str_7 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_8 = Metadata_eval_str_8 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_9 = Metadata_eval_str_9 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_10 = Metadata_eval_str_10 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_11 = Metadata_eval_str_11 + " " + metadata_eval_dict[key1][key2]
                                            Metadata_eval_str_12 = Metadata_eval_str_12 + " " + metadata_eval_dict[key1][key2]

                                            if key1 in conj_dict.keys(): 
                                                Metadata_eval_str_2 = Metadata_eval_str_2 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_3 = Metadata_eval_str_3 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_4 = Metadata_eval_str_4 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_5 = Metadata_eval_str_5 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_6 = Metadata_eval_str_6 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_7 = Metadata_eval_str_7 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_8 = Metadata_eval_str_8 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_9 = Metadata_eval_str_9 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_10 = Metadata_eval_str_10 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_11 = Metadata_eval_str_11 + " " + conj_dict[key1][index2-1]

                                                Metadata_eval_str_12 = Metadata_eval_str_12 + " " + conj_dict[key1][index2-1]

                                                
                                         

        
                                    elif index2 == 1:
                                        
                                        Metadata_eval_str_2 = Metadata_eval_str_2 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): #and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_2 = Metadata_eval_str_2 + " " + conj_dict[key1][count]+ " "
                                            counted = True
                                    
                                    elif index2 == 2:
                                        
                                        Metadata_eval_str_3 = Metadata_eval_str_3 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_3 = Metadata_eval_str_3 + " " + conj_dict[key1][count]+ " "
                                            counted = True

                                    elif index2 == 3:
                                        
                                        Metadata_eval_str_4 = Metadata_eval_str_4 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_4 = Metadata_eval_str_4 + " " + conj_dict[key1][count]+ " "
                                            counted = True
                                    
                                    elif index2 == 4:
                                        
                                        Metadata_eval_str_5 = Metadata_eval_str_5 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_5 = Metadata_eval_str_5 + " " + conj_dict[key1][count]+ " "
                                            counted = True

                                    elif index2 == 5:
                                        
                                        Metadata_eval_str_6 = Metadata_eval_str_6 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_6 = Metadata_eval_str_6 + " " + conj_dict[key1][count]+ " "
                                            counted = True

                                    elif index2 == 6:
                                        
                                        Metadata_eval_str_7 = Metadata_eval_str_7 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_7 = Metadata_eval_str_7 + " " + conj_dict[key1][count]+ " "
                                            counted = True

                                    elif index2 == 7:
                                        
                                        Metadata_eval_str_8 = Metadata_eval_str_8 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_8 = Metadata_eval_str_8 + " " + conj_dict[key1][count]+ " "
                                            counted = True  

                                    elif index2 == 8:
                                        
                                        Metadata_eval_str_9 = Metadata_eval_str_9 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_9 = Metadata_eval_str_9 + " " + conj_dict[key1][count]+ " "
                                            counted = True 

                                    elif index2 == 9:
                                        
                                        Metadata_eval_str_10 = Metadata_eval_str_10 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_10 = Metadata_eval_str_10 + " " + conj_dict[key1][count]+ " "
                                            counted = True

                                    elif index2 == 10:
                                        
                                        Metadata_eval_str_11 = Metadata_eval_str_11 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_11 = Metadata_eval_str_11 + " " + conj_dict[key1][count]+ " "
                                            counted = True

                                    elif index2 == 11:
                                        
                                        Metadata_eval_str_12 = Metadata_eval_str_12 + metadata_eval_dict[key1][key2]
                                        if key1 in conj_dict.keys(): # and index2 < len(relOp_dict.keys())-1:
                                            Metadata_eval_str_12 = Metadata_eval_str_12 + " " + conj_dict[key1][count]+ " "
                                            counted = True
                                    
                                if counted == True:
                                    count+=1


                            # if the eval strings evaluate to False, remove the Header, Target_i from the metadata dictionary                 
                            Metadata_eval_str_ = "Metadata_eval_str_"
                            deleted_stuff = False
                         #   Metadata_eval_str_with_parens = ""
                            for i in [1,10,11,12,2,3,4,5,6,7,8,9]:#range(1,13):
                                # print('label: ',f"{Metadata_eval_str_}{i}")
                                # print("metadata_eval_str:", Metadata_eval_str_+str(i))
                                try:
                                    # print("try1")
                                    # print("EVAL: ",eval(Metadata_eval_str_+str(i)))

                                    if len(eval(Metadata_eval_str_+str(i))) >0 :

                                        print(f"Metadata_eval_str_{i}"," {eval(Metadata_eval_str_+str(i))}")
                                        # insert the opening or closing parenthesis in the appropriate index, 
                                        # I want to wait until it becomes True/False because that is one word instead of 
                                        # 3.(IS IT ALWAYS 3???) but now it is a string so it doesn't have indices anymore...
                                        # I think the Metadata_eval_str is in format "700 == 700" 
                                        # I think I have to split it and reform it anyway, but that's fine 

                                        # but what if the searched term is greater than 1 word, for example
                                        # "pre ablation pressure" (I split on relOp), then the indices will change. 
                                        # I could reformat and then count, but idk. Note if a parenthesis is in the term when
                                        # rewrite? Or a space/underscore in the searchStr? If specify pre or whatever
                                        # I could decrease the index of the parenthesis that come after it, but I don't like that. 
                                        # idk.
                                        # # but maybe it doesn't matter 

                                        Metadata_eval_array = re.split('( and | or )', eval(Metadata_eval_str_+str(i)))
                                        print("Metadata_eval_array",Metadata_eval_array)

                                        for j in range(len(Metadata_eval_array)):
                                            if j in beginning_parens_indices:
                                                Metadata_eval_array[j] = "(" + Metadata_eval_array[j]
                                            if j in ending_parens_indices:
                                                Metadata_eval_array[j] = Metadata_eval_array[j] + ")"

                                        Metadata_eval_str_with_parens = " ".join([str(elem) for elem in Metadata_eval_array])    
                                        print(eval(f"{Metadata_eval_str_}{i}"))
                                        print("eval",eval(eval(f"{Metadata_eval_str_}{i}")))

                                        #if eval(eval(f"{Metadata_eval_str_}{i}")) == False:
                                        if eval(Metadata_eval_str_with_parens) == False: 
                                            try:
                                                # print("eval = False")
                                                del metadata[f'Target_{i}']
                                                deleted_stuff = True
                                            except:
                                                print("could not delete key")
                                                if 'Target_1' not in metadata.keys():
                                                    try: 
                                                     #   print("deleting header")
                                                        del metadata['Header'] 
                                                        deleted_stuff = True
                                                    except:
                                                        pass 
                                                       # print("could not delete header")
                                            
                                                continue
                                    else:
                                            #print("length eval = 0 ")
                                            try:
                                             #   print("trying to delete ")
                                                del metadata[f'Target_{i}']
                                                
                                            except:
                                              #  print("could not delete ")
                                                continue
                                except:
                                 #   print("except1")
                                    try:
                                  #          print("Trying to delete")
                                            if f'Target_{i}' in metadata.keys():
                                                del metadata[f'Target_{i}']
                                            elif 'Target_1' not in metadata.keys():
                                                del metadata['Header'] 
                                            deleted_stuff = True
                                            
                                    except:
                                   #     print("Could not delete")
                                        continue
                                # make sure the header also gets deleted             
                                if str(metadata.keys()) == "dict_keys(['Header'])" and deleted_stuff == True:
                                #    print("deleting Header")
                                    del metadata['Header'] 

                       # print('metadata',metadata)

                        # hide the grandchildren not in the pruned metadata dictionary 
                        for grandchildNum in range(int(val.child(childNum).childCount())):
                            print("grandchildNum:" ,grandchildNum)
                            grandchild = val.child(childNum).child(grandchildNum).text(0)
                            print("grandchild:",grandchild)

                        
                            if grandchild not in metadata.keys():
                                
                                val.child(childNum).child(grandchildNum).setHidden(True)
                            else:
                                #Show Header if search for something in Target, i.e. temperature? 
                                val.child(childNum).child(0).setHidden(False) #assume Header is the first one

                                        
                #print("vaL:", val.text(0))

                # the rest of the function is to hide the records that don't match 
                for childNum in range(int(val.childCount())):
                    
                  #  print("child:",val.child(childNum).text(0))
                    grandChildrenHidden = []

                    for grandChildNum in range(int(val.child(childNum).childCount())):
                        # print("grandchild:", val.child(childNum).child(grandChildNum).text(0))
                        # print("val.grandchild hidden?",val.child(childNum).child(grandChildNum).isHidden())

                        grandChildrenHidden.append(val.child(childNum).child(grandChildNum).isHidden())
                

                    print("grandchildrenHidden?:", grandChildrenHidden)
                
                    if False not in grandChildrenHidden: #and val.isHidden() == 
                        print("Child:", val.child(childNum).text(0))
                        val.child(childNum).setHidden(True)
            
                
                childrenHidden = []
                for childNum in range(int(val.childCount())):

                    # print("childnum", childNum)
                    # print("val.child hidden?",val.child(childNum).isHidden())
                    childrenHidden.append(val.child(childNum).isHidden())

              #  print("childrenHidden?:", childrenHidden)
                if False not in childrenHidden: #and val.isHidden() == 
                    print("VAL:", val.text(0))
                    val.setHidden(True)

        

    def stackUI(self, create_index):
        '''
        This is a function to create stacking pages of the form.
        '''
        
        layout = QGridLayout()
        
        form_target = QGroupBox()
        layout_target = QFormLayout()
        form_target.setLayout(layout_target)
        layout.addWidget(form_target, 0, 0)
        layout_target.addRow(QLabel("Target Material:"), self.target_input[create_index])
        #self.target_input[create_index].setText(str(create_index))
        
        
        form_button = QGroupBox()
        layout_button = QFormLayout()
        form_button.setLayout(layout_button)
        layout.addWidget(form_button, 0, 1)
 
        form_lens = QGroupBox("Lens Parameters")
        layout_lens = QFormLayout()
        form_lens.setLayout(layout_lens)
        layout.addWidget(form_lens, 1, 0)
        layout_lens.addRow(QLabel("Aperture (mm)"), self.aperture_input[create_index])
        layout_lens.addRow(QLabel("Focus (mm)"), self.focus_input[create_index])
        layout_lens.addRow(QLabel("Attenuator (mm)"), self.attenuator_input[create_index])
        layout_lens.addRow(QLabel("Target Height (mm)"), self.target_height_input[create_index])
        
        form_laser = QGroupBox("Laser Parameters")
        layout_laser = QFormLayout()
        form_laser.setLayout(layout_laser)
        layout.addWidget(form_laser, 1, 1)
        layout_laser.addRow(QLabel("Laser Voltage (kV)"), self.laser_voltage_input[create_index])
        layout_laser.addRow(QLabel("Laser Energy (mJ)"), self.laser_energy_input[create_index])
        layout_laser.addRow(QLabel("Measured Energy Mean(mJ)"), self.energy_mean_input[create_index])
        layout_laser.addRow(QLabel("Measured Energy Std"), self.energy_std_input[create_index])


        form_pre = QGroupBox("Pre-ablation")
        layout_pre = QFormLayout()
        form_pre.setLayout(layout_pre)
        layout.addWidget(form_pre, 2, 0)
        #layout_pre.setSpacing(10)
        #layout_pre.setFixedSize(100,self.window_height)
       
        layout_pre.addRow(QLabel("Temperature (\N{DEGREE SIGN}C)"), self.pre_temperature_input[create_index])
        layout_pre.addRow(QLabel("Pressure (mTorr)"), self.pre_pressure_input[create_index])
        layout_pre.addRow(QLabel("Atmosphere Gas"), self.pre_gas_input[create_index])
        layout_pre.addRow(QLabel("Frequency (Hz)"), self.pre_frequency_input[create_index])
        layout_pre.addRow(QLabel("Pulses"), self.pre_number_pulses_input[create_index])
        
        if self.version == 'plume':
            self.button_move_pre = QPushButton(self)
    #         self.button_folder.setFixedSize(300, self.window_height)
            self.button_move_pre.setText("Move Videos To Pre-ablation Folder")
            self.button_move_pre.clicked.connect(lambda: self.move_to_folder(pre=True))
            layout.addWidget(self.button_move_pre, 3, 0)  
        
        form_ablation = QGroupBox("Ablation")
        layout_ablation = QFormLayout()
        form_ablation.setLayout(layout_ablation)
        layout.addWidget(form_ablation, 2, 1)
        layout_ablation.addRow(QLabel("Temperature (\N{DEGREE SIGN}C)"), self.temperature_input[create_index])
        layout_ablation.addRow(QLabel("Pressure (mTorr)"), self.pressure_input[create_index])
        layout_ablation.addRow(QLabel("Atmosphere Gas"), self.gas_input[create_index])
        layout_ablation.addRow(QLabel("Frequency (Hz)"), self.frequency_input[create_index])
        layout_ablation.addRow(QLabel("Pulses"), self.number_pulses_input[create_index])
        
        if self.version == 'plume':
            self.button_move = QPushButton(self)
    #         self.button_folder.setFixedSize(300, self.window_height)
            self.button_move.setText("Move Videos To Ablation Folder")
            self.button_move.clicked.connect(lambda: self.move_to_folder(pre=False))
            layout.addWidget(self.button_move, 3, 1)  
        
        return layout

    

    def pack_to_hdf5_and_upload_with_popwindow(self, path, file_name, info_dict):
        self.show_message_window('Hdf5 file packed and uploaded to datafed!')
        pack_to_hdf5_and_upload(path, file_name, info_dict)
    

        
    def show_message_window(self, message):
        self.exPopup = message_window(message)
        self.exPopup.setGeometry(200, 200, 600, 300)
        self.exPopup.show()
    
    
    def convert_to_image(self):

        '''
        This is a function to convert raw plume file to readable images.
        '''
        print('This button is not functional yet, please convert manually with README instruction.')
        self.show_message_window('This is button is not functional yet, please convert manually with README instruction.')
        
    
    
    def metadata_to_form(self):
        #this is a function to input the selected item in the Datafed treeview into the form  
        
        print("This button is not yet functional. Please try again later.")
        self.show_message_window("This button is not yet functional. Please try again later.")
    
    
    def move_to_folder(self, pre):

        '''
        This is a function to move plumes in default folder of acquisition software to target folder.
        :param pre: if True, plume images will be moved to pre-ablation folder
        :type pre: bool
        '''

        self.path = self.save_path_input.text() + '/'
        
        id = self.growth_id_input.text()
        name = self.name_input.text()
        date = ''.join(self.date_input.text().split('/'))
        self.file_name = id + '_' + name + '_' + date

        if not os.path.isdir(self.path+self.file_name):
            os.mkdir(self.path+self.file_name)
        
        date_list = self.date_input.text().split('/')
        date_m = date_list[2]+'_'+date_list[0]+'_'+date_list[1]
        remove_desktop_ini(self.path)

        file_list = glob.glob(self.path + date_m + '/*')
        i = self.current_page
        if pre:
            dst = self.path+self.file_name+'/'+str(i+1)+'-'+self.target_input[i].text()+'_'+'Pre'
            print('Saving videos to pre-ablation folder...')
            
        else:
            dst = self.path+self.file_name+'/'+str(i+1)+'-'+self.target_input[i].text()
            print('Saving videos to ablation folder...')
            
        if not os.path.isdir(dst):
            os.mkdir(dst)
            remove_desktop_ini(dst)
#             print('The target directory is not created, please "Create Directory" first.')
#             return 
           
        # remove desktop.ini file from all sub-directory

        for file in file_list:
            shutil.move(file, dst)
            
        print('Done!')
        self.show_message_window('Recorded videos moved to target folder!')


    def switchPage(self, i):
        '''
        This is a function to switch page index of stacking pages in the form.
        '''
        self.Stack.setCurrentIndex(i)
        self.current_page = i
    
    def get_info(self):
        '''
        This is a function to fetch parameters from form and make a dictionary.
        '''
        info_dict = { 'header':{            
                                "Growth ID": self.growth_id_input.text(),
                                "User Name": self.name_input.text(),
                                "Date": self.date_input.text(),
                                "time": self.time_input.text(),
                                "Path": self.save_path_input.text(),
                                self.custom_key.text(): self.custom_value.text(),

                                "Chamber": self.chamber_ComboBox.currentText(),
                                "Substrate_1": self.substrate_1_ComboBox.currentText(),
                                "Substrate_2": self.substrate_2_ComboBox.currentText(),
                                "Substrate_3": self.substrate_3_ComboBox.currentText(),
                                "Substrate_4": self.substrate_3_ComboBox.currentText(),
                                "Base Pressure (Torr)": self.base_pressure_input.text(),
                                "Cool Down Atmosphere": self.cool_down_gas.currentText(),
                                "Notes": self.notes_input.toPlainText()}
                                }
        

        
        for i in range(12):
            info_dict['target_'+str(i+1)] = {
                                        "Target Material": self.target_input[i].text(),

                                        "Aperture": self.aperture_input[i].text(),
                                        "Focus(mm)": self.focus_input[i].text(),
                                        "Attenuator(mm)": self.attenuator_input[i].text(),
                                        "Target Height(mm)": self.target_height_input[i].text(),           

                                        "Laser Voltage(kV)": self.laser_voltage_input[i].text(),
                                        "Laser Energy(mJ)": self.laser_energy_input[i].text(),
                                        "Measured Energy Mean(mJ)": self.energy_mean_input[i].text(),
                                        "Measured Energy Std(mJ)": self.energy_std_input[i].text(),

                                        "Pre-Temperature(\N{DEGREE SIGN}C)": self.pre_temperature_input[i].text(),
                                        "Pre-Pressure(mTorr)": self.pre_pressure_input[i].text(),
                                        "Pre-Gas Atmosphere": self.pre_gas_input[i].currentText(),
                                        "Pre-Frequency(Hz)": self.pre_frequency_input[i].text(),
                                        "Pre-Pulses": self.pre_number_pulses_input[i].text(),           

                                        "Temperature(\N{DEGREE SIGN}C)": self.temperature_input[i].text(),
                                        "Pressure(mTorr)": self.pressure_input[i].text(),
                                        "Atmosphere Gas": self.gas_input[i].currentText(),
                                        "Frequency(Hz)": self.frequency_input[i].text(),
                                        "Pulses": self.number_pulses_input[i].text(),            
                                            }
        # clean the empty pairs
        for name in info_dict.keys():
            info_dict[name] = {k: v for k, v in info_dict[name].items() if v}
        info_dict = {k: v for k, v in info_dict.items() if v}
        
        return info_dict

    
    def save(self):
        '''
        This is a function to save parameter dictionary to json file.
        '''
        
        print('Saving dictionary...')
        self.path = self.save_path_input.text() + '/'
        
        id = self.growth_id_input.text()
        name = self.name_input.text()
        date = ''.join(self.date_input.text().split('/'))
        self.file_name = id + '_' + name + '_' + date
        
        self.info_dict = self.get_info()   
        with open(self.path + '/' + self.file_name + '.json', 'w') as file:
            json.dump(self.info_dict, file)     
        print('Done!')
        
        self.show_message_window('Parameters saved!')
