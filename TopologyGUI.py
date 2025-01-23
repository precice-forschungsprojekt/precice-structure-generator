import sys
import yaml
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QTabWidget, QDockWidget, QMessageBox)
from PyQt5.QtCore import Qt

class TopologyDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.participants = {}
        self.exchanges = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('preCICE Topology Designer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs for different configuration sections
        config_tabs = QTabWidget()
        
        # Participants Tab
        participants_tab = QWidget()
        participants_layout = QVBoxLayout(participants_tab)
        
        # Participant Input Section
        participant_input_layout = QHBoxLayout()
        
        self.participant_name_input = QLineEdit()
        self.participant_name_input.setPlaceholderText("Participant Name (e.g., Fluid)")
        participant_input_layout.addWidget(QLabel("Name:"))
        participant_input_layout.addWidget(self.participant_name_input)
        
        self.participant_domain_input = QLineEdit()
        self.participant_domain_input.setPlaceholderText("Domain (e.g., SU2)")
        participant_input_layout.addWidget(QLabel("Domain:"))
        participant_input_layout.addWidget(self.participant_domain_input)
        
        add_participant_btn = QPushButton("Add Participant")
        add_participant_btn.clicked.connect(self.add_participant)
        participant_input_layout.addWidget(add_participant_btn)
        
        participants_layout.addLayout(participant_input_layout)
        
        # Participants Table
        self.participants_table = QTableWidget()
        self.participants_table.setColumnCount(2)
        self.participants_table.setHorizontalHeaderLabels(["Name", "Domain"])
        participants_layout.addWidget(self.participants_table)
        
        # Exchanges Tab
        exchanges_tab = QWidget()
        exchanges_layout = QVBoxLayout(exchanges_tab)
        
        # Exchange Input Section
        exchange_input_layout = QHBoxLayout()
        
        self.from_participant_input = QComboBox()
        self.to_participant_input = QComboBox()
        self.from_patch_input = QLineEdit()
        self.to_patch_input = QLineEdit()
        self.data_input = QLineEdit()
        self.exchange_type_input = QComboBox()
        
        self.from_patch_input.setPlaceholderText("From Patch")
        self.to_patch_input.setPlaceholderText("To Patch")
        self.data_input.setPlaceholderText("Data")
        self.exchange_type_input.addItems(["strong", "loose"])
        
        exchange_input_layout.addWidget(QLabel("From:"))
        exchange_input_layout.addWidget(self.from_participant_input)
        exchange_input_layout.addWidget(QLabel("Patch:"))
        exchange_input_layout.addWidget(self.from_patch_input)
        
        exchange_input_layout.addWidget(QLabel("To:"))
        exchange_input_layout.addWidget(self.to_participant_input)
        exchange_input_layout.addWidget(QLabel("Patch:"))
        exchange_input_layout.addWidget(self.to_patch_input)
        
        exchange_input_layout.addWidget(QLabel("Data:"))
        exchange_input_layout.addWidget(self.data_input)
        
        exchange_input_layout.addWidget(QLabel("Type:"))
        exchange_input_layout.addWidget(self.exchange_type_input)
        
        add_exchange_btn = QPushButton("Add Exchange")
        add_exchange_btn.clicked.connect(self.add_exchange)
        exchange_input_layout.addWidget(add_exchange_btn)
        
        exchanges_layout.addLayout(exchange_input_layout)
        
        # Exchanges Table
        self.exchanges_table = QTableWidget()
        self.exchanges_table.setColumnCount(6)
        self.exchanges_table.setHorizontalHeaderLabels(["From", "From Patch", "To", "To Patch", "Data", "Type"])
        exchanges_layout.addWidget(self.exchanges_table)
        
        # Coupling Scheme Tab
        coupling_scheme_tab = QWidget()
        coupling_scheme_layout = QVBoxLayout(coupling_scheme_tab)
        
        # Coupling Scheme Inputs
        self.max_time_input = QLineEdit("1e-1")
        self.time_window_size_input = QLineEdit("1e-3")
        self.relative_accuracy_input = QLineEdit("1e-4")
        
        coupling_scheme_layout.addWidget(QLabel("Max Time:"))
        coupling_scheme_layout.addWidget(self.max_time_input)
        coupling_scheme_layout.addWidget(QLabel("Time Window Size:"))
        coupling_scheme_layout.addWidget(self.time_window_size_input)
        coupling_scheme_layout.addWidget(QLabel("Relative Accuracy:"))
        coupling_scheme_layout.addWidget(self.relative_accuracy_input)
        
        # Add tabs
        config_tabs.addTab(participants_tab, "Participants")
        config_tabs.addTab(exchanges_tab, "Exchanges")
        config_tabs.addTab(coupling_scheme_tab, "Coupling Scheme")
        
        main_layout.addWidget(config_tabs)
        
        # Export Button
        export_btn = QPushButton("Export Topology")
        export_btn.clicked.connect(self.export_topology)
        main_layout.addWidget(export_btn)
        
    def add_participant(self):
        name = self.participant_name_input.text()
        domain = self.participant_domain_input.text()
        
        if name and domain:
            # Add to participants dictionary
            self.participants[name] = domain
            
            # Update participants table
            row = self.participants_table.rowCount()
            self.participants_table.insertRow(row)
            self.participants_table.setItem(row, 0, QTableWidgetItem(name))
            self.participants_table.setItem(row, 1, QTableWidgetItem(domain))
            
            # Update participant dropdowns in exchanges
            self.from_participant_input.addItem(name)
            self.to_participant_input.addItem(name)
            
            # Clear inputs
            self.participant_name_input.clear()
            self.participant_domain_input.clear()
    
    def add_exchange(self):
        from_participant = self.from_participant_input.currentText()
        to_participant = self.to_participant_input.currentText()
        from_patch = self.from_patch_input.text()
        to_patch = self.to_patch_input.text()
        data = self.data_input.text()
        exchange_type = self.exchange_type_input.currentText()
        
        if all([from_participant, to_participant, from_patch, to_patch, data, exchange_type]):
            exchange = {
                "from": from_participant,
                "from-patch": from_patch,
                "to": to_participant,
                "to-patch": to_patch,
                "data": data,
                "type": exchange_type
            }
            
            self.exchanges.append(exchange)
            
            # Update exchanges table
            row = self.exchanges_table.rowCount()
            self.exchanges_table.insertRow(row)
            self.exchanges_table.setItem(row, 0, QTableWidgetItem(from_participant))
            self.exchanges_table.setItem(row, 1, QTableWidgetItem(from_patch))
            self.exchanges_table.setItem(row, 2, QTableWidgetItem(to_participant))
            self.exchanges_table.setItem(row, 3, QTableWidgetItem(to_patch))
            self.exchanges_table.setItem(row, 4, QTableWidgetItem(data))
            self.exchanges_table.setItem(row, 5, QTableWidgetItem(exchange_type))
            
            # Clear inputs
            self.from_patch_input.clear()
            self.to_patch_input.clear()
            self.data_input.clear()
    
    def export_topology(self):
        # Validate inputs
        if not self.participants or not self.exchanges:
            QMessageBox.warning(self, "Export Error", "Please add participants and exchanges first.")
            return
        
        # Create topology dictionary
        topology = {
            "coupling-scheme": {
                "max-time": float(self.max_time_input.text()),
                "time-window-size": float(self.time_window_size_input.text()),
                "relative-accuracy": float(self.relative_accuracy_input.text())
            },
            "participants": self.participants,
            "exchanges": self.exchanges
        }
        
        # Export to YAML
        try:
            with open("topology.yaml", "w") as f:
                yaml.dump(topology, f, default_flow_style=False)
            
            QMessageBox.information(self, "Export Successful", "Topology exported to topology.yaml")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export topology: {str(e)}")

def main():
    app = QApplication(sys.argv)
    topology_designer = TopologyDesigner()
    topology_designer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()