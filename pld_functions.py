import shutil
import sys
import json
import datetime
import os, glob, h5py
import numpy as np
import matplotlib.pyplot as plt
from datafed.CommandLib import API

from PyQt5.QtGui import QFont 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 


import os, glob, h5py
import numpy as np
import matplotlib.pyplot as plt
import json # For dealing with metadata
import os # For file level operations
import time # For timing demonstrations
import datetime # To demonstrate conversion between date and time formats
import glob

import matplotlib.pyplot as plt
from datafed.CommandLib import API


class PLD_form(QWidget):
    def __init__(self):
        super().__init__()
        
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
        self.save_path_input = QLineEdit(os.getcwd())
        self.custom_key = QLineEdit()
        self.custom_key.setFixedSize(80, self.window_height)
        self.custom_value = QLineEdit()

        # chamber part
        self.chamber_ComboBox = QComboBox()  # creating combo box to select degree
        chamber_list = ["Laser 1A", "Laser 1C"]
        self.chamber_ComboBox.addItems(chamber_list)
        
        substrate_list = ["", "SrTiO3", "None"]
        self.substrate_1_ComboBox = QComboBox()
        self.substrate_1_ComboBox.addItems(substrate_list)
        self.substrate_2_ComboBox = QComboBox()
        self.substrate_2_ComboBox.addItems(substrate_list)
        self.substrate_3_ComboBox = QComboBox()
        self.substrate_3_ComboBox.addItems(substrate_list)
        self.substrate_4_ComboBox = QComboBox()
        self.substrate_4_ComboBox.addItems(substrate_list)
        
        gas_list = ["Vacuum", "Oxygen", "Argon"]
        self.cool_down_gas = QComboBox()
        self.cool_down_gas.addItems(gas_list)

        # notes part
        self.notes_input = QPlainTextEdit()        
        self.notes_input.setFixedSize(600, self.window_height*3)
        
        
        # target
        self.target_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        # lens part
        self.aperture_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.focus_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.attenuator_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.target_height_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        # laser part
        self.laser_voltage_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.laser_energy_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.energy_mean_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        self.energy_std_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        
        # pre-ablation and ablation
        self.pre_temperature_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pre_pressure_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pre_gas_input = [QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox(), 
                              QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox()]   
        self.pre_frequency_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pre_number_pulses_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        self.temperature_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pressure_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.gas_input = [QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox(), 
                          QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox()]     
        self.frequency_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.number_pulses_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        gas_list = ["", "Vacuum", "Oxygen", "Argon"]
        for combobox in self.pre_gas_input:
            combobox.addItems(gas_list)
        for combobox in self.gas_input:
            combobox.addItems(gas_list)
        
        # define the layout
        self.setWindowTitle("PLD Growth Record")
        
        # Create a top-level layout
        self.toplayout = QVBoxLayout()
        self.setLayout(self.toplayout)

        ## Create the grid layout - second-level
        self.layout = QGridLayout()
        self.toplayout.addLayout(self.layout)

        self.header_form = QGroupBox("Header")
        self.header_layout = self.create_header()
        self.header_form.setLayout(self.header_layout)
        self.layout.addWidget(self.header_form, 0, 0)
        
        self.chamber_form = QGroupBox("Chamber Parameters")
        self.chamber_layout = self.create_chamber()
        self.chamber_form.setLayout(self.chamber_layout)
        self.layout.addWidget(self.chamber_form, 0, 1)
        
        
        ## create QVForm - second level
        self.button_layout = QGridLayout()
        self.toplayout.addLayout(self.button_layout)

            ### Create and connect the combo box to switch between pages
        self.pageCombo = QComboBox()
        self.pageCombo.addItems(["Target_1", "Target_2", "Target_3", "Target_4", "Target_5", 
                                 "Target_6", "Target_7", "Target_8", "Target_9", "Target_10"]) 
        self.pageCombo.activated.connect(self.switchPage)
            ### Add the combo box and the stacked layout to the top-level layout
        self.button_layout.addWidget(self.pageCombo, 0, 0)
      

        
        ## create QGridLayout - second level
        self.multiPages = QFormLayout()
        self.toplayout.addLayout(self.multiPages)
        
            ### Create the forms
        self.Stack = QStackedWidget (self)
        self.multiPages.addWidget(self.Stack)
        for i in range(10):
            self.stack = QWidget()
            self.Stack.addWidget (self.stack)
            stack_layout = self.stackUI(i)
            self.stack.setLayout(stack_layout)
        
        #  save button - second level
        self.button_save = QPushButton(self)
        self.button_save.setText("Save Parameters")
        self.button_save.clicked.connect(lambda: self.save())
        self.toplayout.addWidget(self.button_save)
        
        #  notes - second level
        self.form_notes = QGroupBox()
        self.notes_layout = QFormLayout()
        self.form_notes.setLayout(self.notes_layout)
        self.notes_layout.addRow(QLabel("Notes"), self.notes_input)
        self.toplayout.addWidget(self.form_notes)
        

    def create_header(self):
        header_layout = QFormLayout()
        header_layout.addRow(QLabel("Growth ID"), self.growth_id_input)
        header_layout.addRow(QLabel("User Name"), self.name_input)
        header_layout.addRow(QLabel("Date"), self.date_input)
        header_layout.addRow(QLabel("Directory"), self.save_path_input)
        header_layout.addRow(self.custom_key, self.custom_value)
        return header_layout

    def create_chamber(self):
        chamber_layout = QFormLayout()
        chamber_layout.addRow(QLabel("Chamber"), self.chamber_ComboBox)
        chamber_layout.addRow(QLabel("Substrates"), self.substrate_1_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_2_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_3_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_4_ComboBox)
        chamber_layout.addRow(QLabel("Cool Down Atmosphere"), self.cool_down_gas)
        return chamber_layout    
    
    
    def stackUI(self, create_index):
        layout = QGridLayout()
        
        form_target = QGroupBox()
        layout_target = QFormLayout()
        form_target.setLayout(layout_target)
        layout.addWidget(form_target, 0, 0)
        layout_target.addRow(QLabel("Target:"), self.target_input[create_index])
        
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
        layout_laser.addRow(QLabel("Measured Energy Std(mJ)"), self.energy_std_input[create_index])


        form_pre = QGroupBox("Pre-ablation")
        layout_pre = QFormLayout()
        form_pre.setLayout(layout_pre)
        layout.addWidget(form_pre, 2, 0)
        layout_pre.addRow(QLabel("Temperature (\N{DEGREE SIGN}C)"), self.pre_temperature_input[create_index])
        layout_pre.addRow(QLabel("Pressure (mTorr)"), self.pre_pressure_input[create_index])
        layout_pre.addRow(QLabel("Atmosphere Gas"), self.pre_gas_input[create_index])
        layout_pre.addRow(QLabel("Frequency (Hz)"), self.pre_frequency_input[create_index])
        layout_pre.addRow(QLabel("Pulses"), self.pre_number_pulses_input[create_index])

        
        form_ablation = QGroupBox("Ablation")
        layout_ablation = QFormLayout()
        form_ablation.setLayout(layout_ablation)
        layout.addWidget(form_ablation, 2, 1)
        layout_ablation.addRow(QLabel("Temperature (\N{DEGREE SIGN}C)"), self.temperature_input[create_index])
        layout_ablation.addRow(QLabel("Pressure (mTorr)"), self.pressure_input[create_index])
        layout_ablation.addRow(QLabel("Atmosphere Gas"), self.gas_input[create_index])
        layout_ablation.addRow(QLabel("Frequency (Hz)"), self.frequency_input[create_index])
        layout_ablation.addRow(QLabel("Pulses"), self.number_pulses_input[create_index])
        
        return layout


    def switchPage(self, i):
        self.Stack.setCurrentIndex(i)
        self.current_page = i
    
    def get_info(self):
        
        info_dict = { 'header':{            
                                "Growth ID": self.growth_id_input.text(),
                                "User Name": self.name_input.text(),
                                "Date": self.date_input.text(),
                                "Path": self.save_path_input.text(),
                                self.custom_key.text(): self.custom_value.text(),

                                "Chamber": self.chamber_ComboBox.currentText(),
                                "Substrate_1": self.substrate_1_ComboBox.currentText(),
                                "Substrate_2": self.substrate_2_ComboBox.currentText(),
                                "Substrate_3": self.substrate_3_ComboBox.currentText(),
                                "Substrate_4": self.substrate_3_ComboBox.currentText(),
                                "Cool Down Atmosphere": self.cool_down_gas.currentText(),
                                "Notes": self.notes_input.toPlainText()}
                                }
        

        
        for i in range(10):
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

                        "Temperature(\N{DEGREE SIGN}C)": self.pre_temperature_input[i].text(),
                        "Pressure(mTorr)": self.pre_pressure_input[i].text(),
                        "Gas Atmosphere": self.pre_gas_input[i].currentText(),
                        "Frequency(Hz)": self.pre_frequency_input[i].text(),
                        "Pulses": self.pre_number_pulses_input[i].text(),           

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
        print('Saving dictionary...')
        path = self.save_path_input.text() + '/'
        
        id = self.growth_id_input.text()
        name = self.name_input.text()
        date = ''.join(self.date_input.text().split('/'))
        file_name = id + '_' + name + '_' + date
        
        info_dict = self.get_info()   
        with open(path + '/' + file_name + '.json', 'w') as file:
            json.dump(info_dict, file)     
        print('Done!')




class PLD_Form_with_Plume_Management(QWidget):
    def __init__(self):
        super().__init__()
        
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
        self.save_path_input = QLineEdit(os.getcwd())
        self.custom_key = QLineEdit()
        self.custom_key.setFixedSize(80, self.window_height)
        self.custom_value = QLineEdit()

        # chamber part
        self.chamber_ComboBox = QComboBox()  # creating combo box to select degree
        chamber_list = ["Laser 1A", "Laser 1C"]
        self.chamber_ComboBox.addItems(chamber_list)
        
        substrate_list = ["", "SrTiO3", "None"]
        self.substrate_1_ComboBox = QComboBox()
        self.substrate_1_ComboBox.addItems(substrate_list)
        self.substrate_2_ComboBox = QComboBox()
        self.substrate_2_ComboBox.addItems(substrate_list)
        self.substrate_3_ComboBox = QComboBox()
        self.substrate_3_ComboBox.addItems(substrate_list)
        self.substrate_4_ComboBox = QComboBox()
        self.substrate_4_ComboBox.addItems(substrate_list)
        
        gas_list = ["Vacuum", "Oxygen", "Argon"]
        self.cool_down_gas = QComboBox()
        self.cool_down_gas.addItems(gas_list)

        # notes part
        self.notes_input = QPlainTextEdit()        
        self.notes_input.setFixedSize(600, self.window_height*3)
        
        
        # target
        self.target_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        # lens part
        self.aperture_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.focus_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.attenuator_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.target_height_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        # laser part
        self.laser_voltage_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.laser_energy_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.energy_mean_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        self.energy_std_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        
        # pre-ablation and ablation
        self.pre_temperature_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pre_pressure_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pre_gas_input = [QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox(), 
                              QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox()]   
        self.pre_frequency_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pre_number_pulses_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]

        self.temperature_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.pressure_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.gas_input = [QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox(), 
                          QComboBox(), QComboBox(), QComboBox(), QComboBox(), QComboBox()]     
        self.frequency_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        self.number_pulses_input = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), 
                             QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()]
        
        gas_list = ["", "Vacuum", "Oxygen", "Argon"]
        for combobox in self.pre_gas_input:
            combobox.addItems(gas_list)
        for combobox in self.gas_input:
            combobox.addItems(gas_list)
        
        # define the layout
        self.setWindowTitle("PLD Growth Record")
        
        # Create a top-level layout
        self.toplayout = QVBoxLayout()
        self.setLayout(self.toplayout)

        ## Create the grid layout - second-level
        self.layout = QGridLayout()
        self.toplayout.addLayout(self.layout)

        self.header_form = QGroupBox("Header")
        self.header_layout = self.create_header()
        self.header_form.setLayout(self.header_layout)
        self.layout.addWidget(self.header_form, 0, 0)
        
        self.chamber_form = QGroupBox("Chamber Parameters")
        self.chamber_layout = self.create_chamber()
        self.chamber_form.setLayout(self.chamber_layout)
        self.layout.addWidget(self.chamber_form, 0, 1)
        
        
        ## create QVForm - second level
        self.button_layout = QGridLayout()
        self.toplayout.addLayout(self.button_layout)

            ### Create and connect the combo box to switch between pages
        self.pageCombo = QComboBox()
        self.pageCombo.addItems(["Target_1", "Target_2", "Target_3", "Target_4", "Target_5", 
                                 "Target_6", "Target_7", "Target_8", "Target_9", "Target_10"]) 
        self.pageCombo.activated.connect(self.switchPage)
            ### Add the combo box and the stacked layout to the top-level layout
        self.button_layout.addWidget(self.pageCombo, 0, 0)
      
        self.button_create = QPushButton(self)
        self.button_create.setText("Create Directory")
        self.button_create.clicked.connect(lambda: self.create_folder())
        self.button_layout.addWidget(self.button_create, 0, 1) 
        
        ## create QGridLayout - second level
        self.multiPages = QFormLayout()
        self.toplayout.addLayout(self.multiPages)
        
            ### Create the forms
        self.Stack = QStackedWidget (self)
        self.multiPages.addWidget(self.Stack)
        for i in range(10):
            self.stack = QWidget()
            self.Stack.addWidget (self.stack)
            stack_layout = self.stackUI(i)
            self.stack.setLayout(stack_layout)
        
        #  save button - second level
        self.button_save = QPushButton(self)
        self.button_save.setText("Save Parameters")
        self.button_save.clicked.connect(lambda: self.save())
        self.toplayout.addWidget(self.button_save)
        
        
        self.button_image = QPushButton(self)
        self.button_image.setText("Convert Video to Images")
        self.button_image.clicked.connect(lambda: self.convert_to_image())
        self.toplayout.addWidget(self.button_image)  
        
        
        self.button_pack = QPushButton(self)
        self.button_pack.setText("Save to HDF5 and Upload")
        self.button_pack.clicked.connect(lambda: self.pack_to_hdf5_and_upload())
        self.toplayout.addWidget(self.button_pack)
        
        #  notes - second level
        self.form_notes = QGroupBox()
        self.notes_layout = QFormLayout()
        self.form_notes.setLayout(self.notes_layout)
        self.notes_layout.addRow(QLabel("Notes"), self.notes_input)
        self.toplayout.addWidget(self.form_notes)
        

    def create_folder(self):
        '''
        Run this function before save dictionary and plumes.
        '''
        print('Creating directory...')

        self.path = self.save_path_input.text() + '/'
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        
        id = self.growth_id_input.text()
        name = self.name_input.text()
        date = ''.join(self.date_input.text().split('/'))
        self.file_name = id + '_' + name + '_' + date

        if not os.path.isdir(self.path + self.file_name):
            os.mkdir(self.path + self.file_name)
            
        for i in range(6):
            if self.target_input[i].text():
                pre_ablation_folder = self.path+self.file_name+'/'+str(i)+'-'+self.target_input[i].text()+'_'+'Pre'
                ablation_folder = self.path+self.file_name+'/'+str(i)+'-'+self.target_input[i].text()
                if not os.path.isdir(pre_ablation_folder):
                    os.mkdir(pre_ablation_folder)
                if not os.path.isdir(ablation_folder):
                    os.mkdir(ablation_folder)
        print('Done!')

            

    def move_to_folder(self, pre):
        date_list = self.date_input.text().split('/')
        date_m = date_list[2]+'_'+date_list[0]+'_'+date_list[1]
        
        file_list = glob.glob(self.path + date_m + '/*')
        i = self.current_page
        if pre:
            dst = self.path+self.file_name+'/'+str(i)+'-'+self.target_input[i].text()+'_'+'Pre'
            print('Moving videos to pre-ablation folder...')
        else:
            dst = self.path+self.file_name+'/'+str(i)+'-'+self.target_input[i].text()
            print('Moving videos to ablation folder...')

        for file in file_list:
            shutil.move(file, dst)
            
        print('Done!')

        
            
    def pack_to_hdf5_and_upload(self):
        '''
        This function will read the images in folders(plumes) under "ds_path/BMP/<target_name>" 
        and convert them into a hdf5 file with following data struction:

        file_name:ds_path.h5
            group: PLD_Plumes
                dataset: target_name(SrRuO3) = n_videos*n_frames*H*W (np.float32)
        '''
        print('Packing to HDF5 file...')

        ds_path = self.path + '/' + self.file_name
        print(ds_path)
        
        growth_para = self.get_info()   
        
        
        def upload_to_datafed(file_path, file_name, growth_para):
            '''
            required to setup the endpoint before run this function
            '''
            print('Uploading to Datafed...')
            
            df_api = API()
            dc_resp = df_api.dataCreate(file_name,
                                        metadata=json.dumps(growth_para),
                                        parent_id='c/391937642', # parent collection
                                       )
            rec_id = dc_resp[0].data[0].id
            put_resp = df_api.dataPut(rec_id, # record id
                                      file_path+file_name+'.h5', # path to file
                                      wait=True  # Waitcas until transfer completes.
                                      )
            out = put_resp
            return out
        
        
        # make sure the format is without '/'
        if ds_path[-1] == '/': ds_path[:-1]
            
        # overwrite the original .h5 file
        if os.path.isfile(ds_path + '.h5'): os.remove(ds_path + '.h5')
        with h5py.File(ds_path + '.h5', mode='a') as h5_file:
            h5_group_plume = h5_file.create_group('PLD_Plumes')

            target_list = os.listdir(ds_path+'/')
            for target in target_list:
#                 print(target)
                if target == '.ipynb_checkpoints': continue 
                        
                length_list = []
                target_path = ds_path + '/' + target
                
                if os.listdir(target_path) == []:
                    os.rmdir(target_path)                
                
                for folder in os.listdir(target_path + '/BMP'):

                    
                    length_list.append(len(os.listdir(target_path + '/BMP/' + folder)))
                    img_shape = plt.imread(glob.glob(target_path+'/BMP/'+folder+'/*')[0]).shape

#                 print((len(length_list), max(length_list), img_shape[0], img_shape[1]))
                # assign to hdf5 dataset
                create_data = h5_group_plume.create_dataset(target, dtype=np.uint8, 
                                                            shape=((len(length_list), max(length_list), 
                                                                    img_shape[0], img_shape[1]))) # dtype=np.uint8

                for i, folder in enumerate(os.listdir(target_path + '/BMP')):
                    for j, file in enumerate(glob.glob(target_path + '/BMP/' + folder + '/*')):
#                         print(file)
                        create_data[i, j] = plt.imread(file)
        
       
        if growth_para == None:
            print('Reminder: growth parameters are not recorded.')
        upload_to_datafed(self.path, self.file_name, growth_para)
        
        print('Done!')


    def create_header(self):
        header_layout = QFormLayout()
        header_layout.addRow(QLabel("Growth ID"), self.growth_id_input)
        header_layout.addRow(QLabel("User Name"), self.name_input)
        header_layout.addRow(QLabel("Date"), self.date_input)
        header_layout.addRow(QLabel("Directory"), self.save_path_input)
        header_layout.addRow(self.custom_key, self.custom_value)
        return header_layout

    def create_chamber(self):
        chamber_layout = QFormLayout()
        chamber_layout.addRow(QLabel("Chamber"), self.chamber_ComboBox)
        chamber_layout.addRow(QLabel("Substrates"), self.substrate_1_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_2_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_3_ComboBox)
        chamber_layout.addRow(QLabel("          "), self.substrate_4_ComboBox)
        chamber_layout.addRow(QLabel("Cool Down Atmosphere"), self.cool_down_gas)
        return chamber_layout    
    
    
    def stackUI(self, create_index):
        layout = QGridLayout()
        
        form_target = QGroupBox()
        layout_target = QFormLayout()
        form_target.setLayout(layout_target)
        layout.addWidget(form_target, 0, 0)
        layout_target.addRow(QLabel("Target:"), self.target_input[create_index])
        
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
        layout_laser.addRow(QLabel("Measured Energy Std(mJ)"), self.energy_std_input[create_index])


        form_pre = QGroupBox("Pre-ablation")
        layout_pre = QFormLayout()
        form_pre.setLayout(layout_pre)
        layout.addWidget(form_pre, 2, 0)
        layout_pre.addRow(QLabel("Temperature (\N{DEGREE SIGN}C)"), self.pre_temperature_input[create_index])
        layout_pre.addRow(QLabel("Pressure (mTorr)"), self.pre_pressure_input[create_index])
        layout_pre.addRow(QLabel("Atmosphere Gas"), self.pre_gas_input[create_index])
        layout_pre.addRow(QLabel("Frequency (Hz)"), self.pre_frequency_input[create_index])
        layout_pre.addRow(QLabel("Pulses"), self.pre_number_pulses_input[create_index])
        
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
        
        self.button_move = QPushButton(self)
#         self.button_folder.setFixedSize(300, self.window_height)
        self.button_move.setText("Move Videos To Ablation Folder")
        self.button_move.clicked.connect(lambda: self.move_to_folder(pre=False))
        layout.addWidget(self.button_move, 3, 1)  
        
        return layout


    def switchPage(self, i):
        self.Stack.setCurrentIndex(i)
        self.current_page = i
    
    def get_info(self):
        
        info_dict = { 'header':{            
                                "Growth ID": self.growth_id_input.text(),
                                "User Name": self.name_input.text(),
                                "Date": self.date_input.text(),
                                "Path": self.save_path_input.text(),
                                self.custom_key.text(): self.custom_value.text(),

                                "Chamber": self.chamber_ComboBox.currentText(),
                                "Substrate_1": self.substrate_1_ComboBox.currentText(),
                                "Substrate_2": self.substrate_2_ComboBox.currentText(),
                                "Substrate_3": self.substrate_3_ComboBox.currentText(),
                                "Substrate_4": self.substrate_3_ComboBox.currentText(),
                                "Cool Down Atmosphere": self.cool_down_gas.currentText(),
                                "Notes": self.notes_input.toPlainText()}
                                }
        

        
        for i in range(10):
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

                        "Temperature(\N{DEGREE SIGN}C)": self.pre_temperature_input[i].text(),
                        "Pressure(mTorr)": self.pre_pressure_input[i].text(),
                        "Gas Atmosphere": self.pre_gas_input[i].currentText(),
                        "Frequency(Hz)": self.pre_frequency_input[i].text(),
                        "Pulses": self.pre_number_pulses_input[i].text(),           

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
        print('Saving dictionary...')
        path = self.save_path_input.text() + '/'
        
        id = self.growth_id_input.text()
        name = self.name_input.text()
        date = ''.join(self.date_input.text().split('/'))
        file_name = id + '_' + name + '_' + date
        
        info_dict = self.get_info()   
        with open(path + '/' + file_name + '.json', 'w') as file:
            json.dump(info_dict, file)     
        print('Done!')


    
    
# version that take all images


    
def pack_to_hdf5(ds_path, growth_para=None):
    '''
    This function will read the images in folders(plumes) under "ds_path/BMP/<target_name>" 
    and convert them into a hdf5 file with following data structure:
    
    file_name:ds_path.h5
        group: PLD_Plumes
            dataset: target_name(SrRuO3) = n_videos*n_frames*H*W (np.float32)
    '''
    
    # make sure the format is without '/'
    if ds_path[-1] == '/': ds_path[:-1]
    
    with h5py.File(ds_path + '.h5', mode='a') as h5_file:
        h5_group_plume = h5_file.create_group('PLD_Plumes')
        
        target_list = os.listdir(ds_path+'/')
        for target in target_list:
            if target[-3:] == 'ini': continue # naive way to pass wrong folder
            if target == '.ipynb_checkpoints': continue 
            
            print(target)
            
            length_list = []
            target_path = ds_path + '/' + target
            for folder in os.listdir(target_path + '/BMP'):
                if folder[-15:-9] == 'Camera': # naive way to get right folder name
                    length_list.append(len(os.listdir(target_path + '/BMP/' + folder)))
                    img_shape = plt.imread(glob.glob(target_path+'/BMP/'+folder+'/*')[0]).shape
            
            print((len(length_list), max(length_list), img_shape[0], img_shape[1]))
            # assign to hdf5 dataset
            create_data = h5_group_plume.create_dataset(target, dtype=np.uint8, 
                                                        shape=((len(length_list), max(length_list), 
                                                                img_shape[0], img_shape[1]))) # dtype=np.uint8
            
            for i, folder in enumerate(os.listdir(target_path + '/BMP')):
                for j, file in enumerate(glob.glob(target_path + '/BMP/' + folder + '/*')):
                    if file[-4:] == '.bmp':
#                         print(file)
                        create_data[i, j] = plt.imread(file)
    

# pip install datafed -U

# !globus endpoint activate --web 1fd2cdcc-05da-11ec-b33e-1feaf93e3729

def upload_to_datafed(file_path, file_name, growth_para, parent_id):
    '''
    required to setup the endpoint before run this function
    '''
    df_api = API()
    dc_resp = df_api.dataCreate(file_name,
                                metadata=json.dumps(growth_para),
                                parent_id=parent_id, # parent collection
                               )
    rec_id = dc_resp[0].data[0].id
    put_resp = df_api.dataPut(rec_id, # record id
                              file_path, # path to file
                              wait=True  # Waitcas until transfer completes.
                              )
    out = put_resp
    return out