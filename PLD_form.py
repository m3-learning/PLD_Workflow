from PyQt5.QtWidgets import * 
import sys
import json
import datetime
import os

class PLD_dropdown(QWidget):
    def __init__(self):
        super().__init__()
        
        # pre-define inputs
        
        # header part
        self.growth_id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.date_input = QLineEdit(datetime.datetime.today().strftime("%m/%d/%Y"))
        self.save_path_input = QLineEdit()
        
        # lens part
        self.aperture_input = QLineEdit()
        self.focus_position_input = QLineEdit()
        self.target_height_input = QLineEdit()
        
        # chamber part
        self.chamber_ComboBox = QComboBox()  # creating combo box to select degree
        self.chamber_ComboBox.addItems(["Laser 1A", "Laser 1C"])
        self.target_input = QLineEdit()
        self.substrate_input = QLineEdit()
        self.gas_input = QLineEdit()

        # laser part
        self.laser_voltage_input = QLineEdit()
        self.laser_energy_input = QLineEdit()
        self.measured_energy_input = QLineEdit()
        
        # pre-ablation part
        self.pre_temperature_input = QLineEdit()
        self.pre_pressure_input = QLineEdit()
        self.pre_frequency_input = QLineEdit()
        self.pre_number_pulses_input = QLineEdit()
        
        # ablation part
        self.temperature_input = QLineEdit()
        self.pressure_input = QLineEdit()
        self.frequency_input = QLineEdit()
        self.number_pulses_input = QLineEdit()
        
        # notes part        
        self.notes_input = QLineEdit()        
        
        
    
        # define the layout
        self.setWindowTitle("PLD Growth Record")
        
        # Create a top-level layout
        self.layout = QVBoxLayout()
        # Create and connect the combo box to switch between pages
        self.pageCombo = QComboBox()
        self.pageCombo.addItems(["Target 1", "Target 2", "Target 3", "Target 4", "Target 5", "Target 6"])
        self.pageCombo.activated.connect(self.switchPage)
        
        # Create the stacked layout
        self.stackedLayout = QStackedLayout()
        
        # Create the first page
        self.button_t1 = QPushButton(self)
        self.button_t1.setText("save for target 1")
        self.button_t1.clicked.connect(lambda: self.save('t1'))
        self.stackedLayout.addWidget(self.button_t1)
    
        self.button_t2 = QPushButton(self)
        self.button_t2.setText("save for target 2")
        self.button_t2.clicked.connect(lambda: self.save('t2'))
        self.stackedLayout.addWidget(self.button_t2)
        
        self.button_t3 = QPushButton(self)
        self.button_t3.setText("save for target 3")
        self.button_t3.clicked.connect(lambda: self.save('t3'))
        self.stackedLayout.addWidget(self.button_t3)
        
        self.button_t4 = QPushButton(self)
        self.button_t4.setText("save for target 4")
        self.button_t4.clicked.connect(lambda: self.save('t4'))
        self.stackedLayout.addWidget(self.button_t4)
        
        self.button_t5 = QPushButton(self)
        self.button_t5.setText("save for target 5")
        self.button_t5.clicked.connect(lambda: self.save('t5'))
        self.stackedLayout.addWidget(self.button_t5)
        
        self.button_t6 = QPushButton(self)
        self.button_t6.setText("save for target 6")
        self.button_t6.clicked.connect(lambda: self.save('t6'))
        self.stackedLayout.addWidget(self.button_t6)
        
        # Add the combo box and the stacked layout to the top-level layout
        self.layout.addWidget(self.pageCombo)
        self.layout.addLayout(self.stackedLayout)
        
        self.header_form = QGroupBox("Header")
        self.create_header()
        
        self.lens_form = QGroupBox("Lens Parameters")
        self.create_lens()
        
        self.chamber_form = QGroupBox("Chamber Parameters")
        self.create_chamber()
        
        self.laser_form = QGroupBox("Laser Parameters")
        self.create_laser()
        
        self.pre_ablation_form = QGroupBox("Pre-ablation Parameters")
        self.create_pre_ablation()
        
        self.ablation_form = QGroupBox("Ablation Parameters")
        self.create_ablation()
        
        self.notes_form = QGroupBox()
        self.create_notes()

        self.setLayout(self.layout)
        self.setLayout(self.stackedLayout)

        
    def switchPage(self):
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())
    
    def create_header(self):
        header_layout = QFormLayout()
        
        header_layout.addRow(QLabel("Grwoth ID"), self.growth_id_input)
        header_layout.addRow(QLabel("User Name"), self.name_input)
        header_layout.addRow(QLabel("Date"), self.date_input)
        header_layout.addRow(QLabel("Save File (with json format)"), self.save_path_input)

        self.header_form.setLayout(header_layout)
        self.layout.addWidget(self.header_form)

    def create_lens(self):
        lens_layout = QFormLayout()

        lens_layout.addRow(QLabel("Aperture"), self.aperture_input)
        lens_layout.addRow(QLabel("Focus Position"), self.focus_position_input)
        lens_layout.addRow(QLabel("Target Height"), self.target_height_input)

        self.lens_form.setLayout(lens_layout)
        self.layout.addWidget(self.lens_form)
       
    
    def create_chamber(self):
        chamber_layout = QFormLayout()
        
        chamber_layout.addRow(QLabel("Chamber"), self.chamber_ComboBox)
        chamber_layout.addRow(QLabel("Target"), self.target_input)
        chamber_layout.addRow(QLabel("Substrate"), self.substrate_input)
        chamber_layout.addRow(QLabel("Gas"), self.gas_input)

        # setting layout
        self.chamber_form.setLayout(chamber_layout)
        # layout
        self.layout.addWidget(self.chamber_form)
        
        
    def create_laser(self):
        laser_layout = QFormLayout()
                
        laser_layout.addRow(QLabel("Laser Voltage"), self.laser_voltage_input)
        laser_layout.addRow(QLabel("Laser Energy"), self.laser_energy_input)
        laser_layout.addRow(QLabel("Measured Energy"), self.measured_energy_input)
            
        self.laser_form.setLayout(laser_layout)
        self.layout.addWidget(self.laser_form)
       
    
    def create_pre_ablation(self):
        pre_ablation_layout = QFormLayout()

        pre_ablation_layout.addRow(QLabel("Pre-ablation Temperature"), self.pre_temperature_input)
        pre_ablation_layout.addRow(QLabel("Pre-ablation Pressure"), self.pre_pressure_input)
        pre_ablation_layout.addRow(QLabel("Pre-ablation Frequency"), self.pre_frequency_input)
        pre_ablation_layout.addRow(QLabel("Pre-ablation Pulses"), self.pre_number_pulses_input)
        
        # setting layout
        self.pre_ablation_form.setLayout(pre_ablation_layout)
        # layout
        self.layout.addWidget(self.pre_ablation_form)
        
        
    def create_ablation(self):
        ablation_layout = QFormLayout()

        ablation_layout.addRow(QLabel("Temperature"), self.temperature_input)
        ablation_layout.addRow(QLabel("Pressure"), self.pressure_input)
        ablation_layout.addRow(QLabel("Frequency"), self.frequency_input)
        ablation_layout.addRow(QLabel("Ablation Pulses"), self.number_pulses_input)

        # setting layout
        self.ablation_form.setLayout(ablation_layout)
        # layout
        self.layout.addWidget(self.ablation_form)

        
    def create_notes(self):
        notes_layout = QFormLayout()
        notes_layout.addRow(QLabel("Notes"), self.notes_input)
        
        self.notes_form.setLayout(notes_layout)
        self.layout.addWidget(self.notes_form)
    
    
    def get_info(self):
        
        header_dict = {
            "Growth ID": self.growth_id_input.text(),
            "User Name": self.name_input.text(),
            "Date": self.date_input.text(),
            "Path": self.save_path_input.text(),
        }
        
        sub_dict = {
            "Aperture": self.aperture_input.text(),
            "Focus Position": self.focus_position_input.text(),
            "Target Height": self.target_height_input.text(),            
        
            "Chamber": self.chamber_ComboBox.currentText(),
            "Target": self.target_input.text(),
            "Substrate": self.substrate_input.text(),
            "Gas": self.gas_input.text(),

            "Laser Voltage": self.laser_voltage_input.text(),
            "Laser Energy": self.laser_energy_input.text(),
            "Measured Energy": self.measured_energy_input.text(),
        
            "Pre-ablation Temperature": self.pre_temperature_input.text(),
            "Pre-ablation Pressure": self.pre_pressure_input.text(),
            "Pre-ablation Frequency": self.pre_frequency_input.text(),
            "Pre-ablation Pulses": self.pre_number_pulses_input.text(),           
        
            "Ablation Temperature": self.temperature_input.text(),
            "Ablation Pressure": self.pressure_input.text(),
            "Ablation Frequency": self.frequency_input.text(),
            "Ablation Pulses": self.number_pulses_input.text(),            
        
            "Notes": self.notes_input.text()
        }
        return header_dict, sub_dict
        
        
    def save(self, index):
        self.save_path = self.save_path_input.text()
        
        if not os.path.isfile(self.save_path+'.json'):
            self.info_dict = { 'header':{}, 't1':{}, 't2':{}, 't3':{}, 't4':{}, 't5':{}, 't6':{} }
        else:
            with open(self.save_path+'.json', 'r') as file:
                self.info_dict = json.load(file)

        header_dict, sub_dict = self.get_info()   
        self.info_dict['header'] = header_dict
        self.info_dict[index] = sub_dict
        with open(self.save_path+'.json', 'w') as file:
            json.dump(self.info_dict, file)     
    
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PLD_dropdown()
    window.show()
    app.exec_()