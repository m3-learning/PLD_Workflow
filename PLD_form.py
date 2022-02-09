from PyQt5.QtWidgets import * 
import sys
import json
import datetime
import os

class PLD_Form(QDialog):
  
    def __init__(self):
        super(PLD_Form, self).__init__()
        
        # header of the form
        self.name_input = QLineEdit()
        self.date_input = QLineEdit(datetime.datetime.today().strftime("%m/%d/%Y"))
        
        self.chamber_ComboBox = QComboBox()  # creating combo box to select degree
        self.chamber_ComboBox.addItems(["Laser 1A", "Laser 1C"])
        
        self.save_path_input = QLineEdit()
        
        # main part for create form function
        self.target_input = QLineEdit()
        self.substrate_input = QLineEdit()
        
        self.temperature_input = QLineEdit()
        self.pressure_input = QLineEdit()
        self.frequency_input = QLineEdit()

        self.laser_voltage_input = QLineEdit()
        self.laser_energy_input = QLineEdit()

        self.aperture_input = QLineEdit()
        self.focus_input = QLineEdit()
        self.focus_position_input = QLineEdit()
        self.target_height_input = QLineEdit()

        self.measured_energy_input = QLineEdit()
        self.number_pulses_input = QLineEdit()
        self.preablation_pulses_input = QLineEdit()
        
        self.notes_input = QLineEdit()
        
        # main
        # if it uses multiple targets, design multiple button to create save to the main dictionary 
        # different target label will be different nested dictionary 
        
        self.setWindowTitle("PLD Growth")
        self.setGeometry(200,200,200,200)  
        self.formGroupBox = QGroupBox("PLD Growth Record")
        
        # creating a vertical layout
        mainLayout = QVBoxLayout()

        # calling the method that create the form
        self.createForm()
        
        # adding form group box to the layout
        mainLayout.addWidget(self.formGroupBox)
  
        self.button_t1 = QPushButton(self)
        self.button_t1.setText("save for target 1")
        self.button_t1.clicked.connect(lambda: self.save(1))
        mainLayout.addWidget(self.button_t1)

        self.button_t2 = QPushButton(self)
        self.button_t2.setText("save for target 2")
        self.button_t2.clicked.connect(lambda: self.save(2))
        mainLayout.addWidget(self.button_t2)

        self.button_t3 = QPushButton(self)
        self.button_t3.setText("save for target 3")
        self.button_t3.clicked.connect(lambda: self.save(3))
        mainLayout.addWidget(self.button_t3)

        self.button_t4 = QPushButton(self)
        self.button_t4.setText("save for target 4")
        self.button_t4.clicked.connect(lambda: self.save(4))
        mainLayout.addWidget(self.button_t4)

        self.button_t5 = QPushButton(self)
        self.button_t5.setText("save for target 5")
        self.button_t5.clicked.connect(lambda: self.save(5))
        mainLayout.addWidget(self.button_t5)

        self.button_t6 = QPushButton(self)
        self.button_t6.setText("save for target 6")
        self.button_t6.clicked.connect(lambda: self.save(6))
        mainLayout.addWidget(self.button_t6)
 
        # setting lay out
        self.setLayout(mainLayout)

        
    def createForm(self):
        layout = QFormLayout()
        
        layout.addRow(QLabel("Name"), self.name_input)
        layout.addRow(QLabel("Date"), self.date_input)
        layout.addRow(QLabel("Chamber"), self.chamber_ComboBox)
        layout.addRow(QLabel("Save File (with json format)"), self.save_path_input)
        
        layout.addRow(QLabel("Target"), self.target_input)
        layout.addRow(QLabel("Substrate"), self.substrate_input)
        
        layout.addRow(QLabel("Temperature"), self.temperature_input)
        layout.addRow(QLabel("Pressure"), self.pressure_input)
        layout.addRow(QLabel("Frequency"), self.frequency_input)
        
        layout.addRow(QLabel("Laser Voltage"), self.laser_voltage_input)
        layout.addRow(QLabel("Laser Energy"), self.laser_energy_input)
        
        layout.addRow(QLabel("Aperture"), self.aperture_input)
        layout.addRow(QLabel("Focus"), self.focus_input)
        layout.addRow(QLabel("Focus Position"), self.focus_position_input)
        layout.addRow(QLabel("Target Height"), self.target_height_input)

        layout.addRow(QLabel("Measured Energy"), self.measured_energy_input)
        layout.addRow(QLabel("Number of Pulses"), self.number_pulses_input)
        layout.addRow(QLabel("Pre-ablation Pulses"), self.preablation_pulses_input)
        
        layout.addRow(QLabel("Notes"), self.notes_input)

        # setting layout
        self.formGroupBox.setLayout(layout)
        
        
    def get_info(self):
        
        header_dict = {
            "User Name": self.name_input.text(),
            "Date": self.date_input.text(),
            "Chamber": self.chamber_ComboBox.currentText(),
            "Path": self.save_path_input.text(),
           }
        
        
        sub_dict = {
            "Target": self.target_input.text(),
            "Substrate": self.substrate_input.text(),

            "Temperature": self.temperature_input.text(),
            "Pressure": self.pressure_input.text(),
            "Frequency": self.frequency_input.text(),

            "Laser Voltage": self.laser_voltage_input.text(),
            "Laser Energy": self.laser_energy_input.text(),

            "Aperture": self.aperture_input.text(),
            "Focus": self.focus_input.text(),
            "Focus Position": self.focus_position_input.text(),
            "Target Height": self.target_height_input.text(),

            "Measured Energy": self.measured_energy_input.text(),
            "Number of Pulses": self.number_pulses_input.text(),
            "Pre-ablation Pulses": self.preablation_pulses_input.text(),
            
            "Notes": self.notes_input.text()
            }
        return header_dict, sub_dict
        
        
    def save(self, index):
        self.save_path = self.save_path_input.text()
        
        if not os.path.isfile(self.save_path+'.json'):
            self.info_dict = { 'header':{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{} } 
        else:
            with open(self.save_path+'.json', 'r') as file:
                self.info_dict = json.load(file)

        header_dict, sub_dict = self.get_info()   
        self.info_dict['header'] = header_dict
        self.info_dict[index] = sub_dict

        with open(self.save_path+'.json', 'w') as file:
            json.dump(self.info_dict, file) 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PLD_Form()
    window.show()
    sys.exit(app.exec())
#     app.exec()