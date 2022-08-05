
import shutil
import sys
import json
import datetime
import os, glob, h5py
import numpy as np
import matplotlib.pyplot as plt
from datafed.CommandLib import API
import re #regular expressions

import getpass
import subprocess
from platform import platform



from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
from PyQt5.Qt import QStandardItemModel, QStandardItem
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
#         self.save_path_input = QLineEdit(os.getcwd()) 
        self.save_path_input = QLineEdit('C:/Image/') 

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
                                label = QTreeWidgetItem([val])
                                scan.addChild(label) #PZO, 700, etc. 
                                try: 
                                    label.addChild(QTreeWidgetItem([str(metaData[key][val])]))
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

                if 'Growth ID' in str(item.child(i).text(0)):
                    self.growth_id_input.setText(str(item.child(i).child(0).text(0)))

                elif 'User Name' in str(item.child(i).text(0)):
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
  


                elif 'Base Pressure' in str(item.child(i).text(0)):
                    self.base_pressure_input.setText(str(item.child(i).child(0).text(0)))

                elif 'Cool Down Atmosphere' in str(item.child(i).text(0)):
                    self.cool_down_gas.setCurrentText(str(item.child(i).child(0).text(0)).capitalize())


                #notes section at bottom of form
                elif "Notes" in str(item.child(i).text(0)):
                    self.notes_input.appendPlainText(str(item.child(i).child(0).text(0)))

                  #Target Material
                #the re.split is because there is a header and sometime user name field 
         #to iterate over before getting to the targets 
                elif 'Target Material' in str(item.child(i).text(0)):
                    self.target_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))


                #lens parameters 

                elif 'Aperture' in str(item.child(i).text(0)):
                    self.aperture_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif 'Focus' in str(item.child(i).text(0)):
                    self.focus_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Attenuator" in str(item.child(i).text(0)):
                    self.attenuator_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Target Height" in str(item.child(i).text(0)):
                    self.target_height_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                    #laser parameters 

                elif 'Laser Voltage' in str(item.child(i).text(0)):
                    self.laser_voltage_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif 'Laser Energy' in str(item.child(i).text(0)):
                    self.laser_energy_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Measured Energy Mean" in str(item.child(i).text(0)):
                    self.energy_mean_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Measured Energy Std" in str(item.child(i).text(0)):
                    self.energy_std_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))



           #pre-ablation parameters 

                elif 'Pre-Temperature' in str(item.child(i).text(0)) or "Pre-Ablation-Temperature" in str(item.child(i).text(0)):
                    self.pre_temperature_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif 'Pre-Pressure' in str(item.child(i).text(0)) or "Pre-Ablation-Pressure" in str(item.child(i).text(0)):
                    self.pre_pressure_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Pre-Gas" in str(item.child(i).text(0)) or "Pre-Ablation-Gas" in str(item.child(i).text(0)) or "Pre-Atmosphere" in str(item.child(i).text(0)) or "Pre-Ablation-Atmosphere" in str(item.child(i).text(0)):
                    self.pre_gas_input[int(re.split("_",str(item.text(0)))[1])-1].setCurrentText(str(item.child(i).child(0).text(0)).capitalize())

                elif "Pre-Frequency" in str(item.child(i).text(0)) or "Pre-Ablation-Frequency" in str(item.child(i).text(0)):
                    self.pre_frequency_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif "Pre-Pulses" in str(item.child(i).text(0)) or "Pre-Ablation-Pulses" in str(item.child(i).text(0)):
                    self.pre_number_pulses_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))     



                #                       #ablation parameters 

                elif re.search('^Temperature', str(item.child(i).text(0))) or "Ablation-Temperature" in str(item.child(i).text(0)):
                    self.temperature_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif re.search('^Pressure' , str(item.child(i).text(0))) or "Ablation-Pressure" in str(item.child(i).text(0)):
                    self.pressure_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif re.search("^Atmosphere" , str(item.child(i).text(0))) or "Ablation-Atmosphere" in str(item.child(i).text(0)) or re.search("^Gas",str(item.child(i).text(0))) or "Ablation-Gas-Atmosphere" in str(item.child(i).text(0)):
                    self.gas_input[int(re.split("_",str(item.text(0)))[1])-1].setCurrentText(str(item.child(i).child(0).text(0)).capitalize())

                elif re.search("^Frequency" , str(item.child(i).text(0))) or "Ablation-Frequency" in str(item.child(i).text(0)):
                    self.frequency_input[int(re.split("_",str(item.text(0)))[1])-1].setText(str(item.child(i).child(0).text(0)))

                elif re.search("^Pulses" , str(item.child(i).text(0))) or "Ablation-Pulses" in str(item.child(i).text(0)):
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

                        if 'Growth ID' in str(item.child(i).child(j).text(0)):
                            self.growth_id_input.setText("")
                            self.growth_id_input.setText(str(item.child(i).child(j).child(0).text(0)))

                        elif 'User Name' in str(item.child(i).child(j).text(0)):
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

                    
                        elif 'Base Pressure' in str(item.child(i).child(j).text(0)):
                            self.base_pressure_input.setText(str(item.child(i).child(j).child(0).text(0)))

                        elif 'Cool Down Atmosphere' in str(item.child(i).child(j).text(0)):
                            self.cool_down_gas.setCurrentText(str(item.child(i).child(j).child(0).text(0)).capitalize())


                         #notes section at bottom of form
                        elif "Notes" in str(item.child(i).child(j).text(0)):
                            self.notes_input.appendPlainText(str(item.child(i).child(j).child(0).text(0)))        

                       #Target Material
                          #the regex is because there is a header and sometime user name field 
         #to iterate over before getting to the targets 
                        elif 'Target Material' in str(item.child(i).child(j).text(0)):
                            self.target_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))


                    #lens parameters 

                        elif 'Aperture' in str(item.child(i).child(j).text(0)):
                            self.aperture_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif 'Focus' in str(item.child(i).child(j).text(0)):
                            self.focus_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif "Attenuator" in str(item.child(i).child(j).text(0)):
                            self.attenuator_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif "Target Height" in str(item.child(i).child(j).text(0)):
                            self.target_height_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                    #laser parameters 

                        elif 'Laser Voltage' in str(item.child(i).child(j).text(0)):
                            self.laser_voltage_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif 'Laser Energy' in str(item.child(i).child(j).text(0)):
                            self.laser_energy_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif "Measured Energy Mean" in str(item.child(i).child(j).text(0)) or re.search("Measured Energy$",str(item.child(i).child(j).text(0))):
                            self.energy_mean_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif "Measured Energy Std" in str(item.child(i).child(j).text(0)):
                            self.energy_std_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

#                       #pre-ablation parameters 

                        elif 'Pre-Temperature' in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Temperature" in str(item.child(i).child(j).text(0)):
                            self.pre_temperature_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif 'Pre-Pressure' in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Pressure" in str(item.child(i).child(j).text(0)):
                            self.pre_pressure_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif "Pre-Gas" in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Gas" in str(item.child(i).child(j).text(0)) or "Pre-Atmosphere" in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Atmosphere" in str(item.child(i).child(j).text(0)):
                            self.pre_gas_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setCurrentText(str(item.child(i).child(j).child(0).text(0)).capitalize())

                        elif "Pre-Frequency" in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Frequency" in str(item.child(i).child(j).text(0)):
                            self.pre_frequency_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif "Pre-Pulses" in str(item.child(i).child(j).text(0)) or "Pre-Ablation-Pulses" in str(item.child(i).child(j).text(0)):
                            self.pre_number_pulses_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))     



                #                       #ablation parameters 

                        elif re.search('^Temperature', str(item.child(i).child(j).text(0))) or "Ablation-Temperature" in str(item.child(i).child(j).text(0)):
                            self.temperature_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif re.search('^Pressure' , str(item.child(i).child(j).text(0))) or "Ablation-Pressure" in str(item.child(i).child(j).text(0)):
                            self.pressure_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif re.search("^Atmosphere" , str(item.child(i).child(j).text(0))) or "Ablation-Atmosphere" in str(item.child(i).child(j).text(0)) or re.search("^Gas" , str(item.child(i).child(j).text(0))) or "Ablation-Gas-Atmosphere" in str(item.child(i).child(j).text(0)):
                            self.gas_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setCurrentText(str(item.child(i).child(j).child(0).text(0)).capitalize())

                        elif re.search("^Frequency" , str(item.child(i).child(j).text(0))) or "Ablation-Frequency" in str(item.child(i).child(j).text(0)):
                            self.frequency_input[int(re.split("_",str(item.child(i).text(0)))[1])-1].setText(str(item.child(i).child(j).child(0).text(0)))

                        elif re.search("^Pulses" , str(item.child(i).child(j).text(0))) or "Ablation-Pulses" in str(item.child(i).child(j).text(0)):
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
  
