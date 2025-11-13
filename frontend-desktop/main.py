import sys
import os
import requests
import io
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QLabel, QGridLayout, QListWidget,
    QListWidgetItem, QSizePolicy, QSpacerItem, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize

# Import Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE_URL = 'http://127.0.0.1:8000/api'

class MplCanvas(FigureCanvas):
    """Matplotlib canvas widget to embed in PyQt5."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #FFFFFF;")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Chemical Equipment Visualizer (Desktop)'
        self.left = 100
        self.top = 100
        self.width = 1200
        self.height = 800
        
        # Application State
        self.current_summary_object = None
        self.current_history_id = None
        self.history_list_data = []
        
        self.initUI()
        self.fetch_history()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7f6;
                font-family: Arial;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f9f9f9;
                padding: 4px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #3498db;
                margin-bottom: 10px;
            }
        """)

        #Main Layout
        main_layout = QVBoxLayout(self)
        
        #Top Bar: Upload Button
        self.upload_button = QPushButton('1. Upload New CSV File')
        self.upload_button.setFont(QFont('Arial', 12, QFont.Bold))
        self.upload_button.setFixedHeight(40)
        self.upload_button.clicked.connect(self.handle_upload)
        main_layout.addWidget(self.upload_button)

        #Content Area: Grid Layout
        content_layout = QGridLayout()

        #Row 0, Column 0: History List
        history_layout = QVBoxLayout()
        history_layout.addWidget(QLabel("2. Upload History (Last 5)", objectName="title"))
        self.history_widget = QListWidget()
        self.history_widget.itemClicked.connect(self.handle_history_click)
        history_layout.addWidget(self.history_widget)
        
        self.delete_button = QPushButton('Delete Selected')
        self.delete_button.clicked.connect(self.handle_delete)
        history_layout.addWidget(self.delete_button)

        content_layout.addLayout(history_layout, 0, 0)

        # Row 0, Column 1: Summary Stats
        stats_frame = QFrame()
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.addWidget(QLabel("3. Data Summary", objectName="title"))
        
        self.label_filename = QLabel("File: N/A")
        self.label_filename.setWordWrap(True)
        self.label_count = QLabel("Total Count: N/A")
        self.label_flow = QLabel("Avg. Flowrate: N/A")
        self.label_pressure = QLabel("Avg. Pressure: N/A")
        self.label_temp = QLabel("Avg. Temperature: N/A")
        
        font = QFont('Arial', 12)
        for label in [self.label_filename, self.label_count, self.label_flow, self.label_pressure, self.label_temp]:
            label.setFont(font)
            stats_layout.addWidget(label)
        
        stats_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.pdf_button = QPushButton('Download PDF Report')
        self.pdf_button.clicked.connect(self.handle_pdf)
        stats_layout.addWidget(self.pdf_button)
        
        content_layout.addWidget(stats_frame, 0, 1)

        # Row 0, Column 2: Chart
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.addWidget(QLabel("4. Equipment Distribution", objectName="title"))
        self.chart_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        chart_layout.addWidget(self.chart_canvas)
        
        content_layout.addWidget(chart_frame, 0, 2)
        
        # Row 1, Columns 0-2: Data Table
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.addWidget(QLabel("5. Raw Data", objectName="title"))
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.table_widget.setAlternatingRowColors(True)
        table_layout.addWidget(self.table_widget)
        
        content_layout.addWidget(table_frame, 1, 0, 1, 3)
        
        # Set column/row stretch factors
        content_layout.setColumnStretch(0, 1) # History list
        content_layout.setColumnStretch(1, 1) # Stats
        content_layout.setColumnStretch(2, 2) # Chart
        content_layout.setRowStretch(0, 1) # Top row (history, stats, chart)
        content_layout.setRowStretch(1, 1) # Bottom row (table)

        main_layout.addLayout(content_layout)
        
        self.update_ui_state()
        self.showMaximized()

    def fetch_history(self):
        try:
            response = requests.get(f"{API_BASE_URL}/history/")
            if response.status_code == 200:
                self.history_list_data = response.json()
                self.update_history_widget()
            else:
                QMessageBox.warning(self, "Error", "Could not fetch history.")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Connection Failed: Is the Django backend server running?")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_history_widget(self):
        self.history_widget.clear()
        for item_data in self.history_list_data:
            date = item_data['uploaded_at'].split('T')[0]
            text = f"{item_data['filename']}\n{date}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, item_data['id'])
            self.history_widget.addItem(item)
            item.setSizeHint(QSize(item.sizeHint().width(), 45))

    def handle_history_click(self, item):
        history_id = item.data(Qt.UserRole)
        self.current_history_id = history_id
        self.load_summary(history_id)

    def load_summary(self, summary_id):
        try:
            response = requests.get(f"{API_BASE_URL}/summary/{summary_id}/")
            if response.status_code == 200:
                self.current_summary_object = response.json()
                self.update_ui_state()
            else:
                QMessageBox.warning(self, "Error", "Could not load that summary.")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Connection Failed.")

    def handle_upload(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)

        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, 'text/csv')}
                    response = requests.post(f"{API_BASE_URL}/upload/", files=files)

                    if response.status_code == 201:
                        data = response.json()
                        self.current_summary_object = data
                        self.current_history_id = data.get('id')
                        self.update_ui_state()
                        self.fetch_history()
                        QMessageBox.information(self, "Success", "File uploaded!")
                    else:
                        error_msg = response.json().get('error', 'Unknown upload error')
                        QMessageBox.warning(self, "Upload Failed", f"Error: {error_msg}")
            
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Error", "Connection Failed: Is the Django backend server running?")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def handle_delete(self):
        if not self.current_history_id:
            QMessageBox.warning(self, "No Item Selected", "Please select an item from the history list to delete.")
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     "Are you sure you want to delete this item?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                response = requests.delete(f"{API_BASE_URL}/summary/{self.current_history_id}/")
                if response.status_code == 204:
                    QMessageBox.information(self, "Success", "Item deleted.")
                    self.current_summary_object = None
                    self.current_history_id = None
                    self.fetch_history()
                    self.update_ui_state()
                else:
                    QMessageBox.warning(self, "Error", "Could not delete the item.")
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Error", "Connection Failed.")

    def handle_pdf(self):
        if not self.current_history_id:
            QMessageBox.warning(self, "No Item Selected", "Please select an item to generate a report.")
            return

        filename = self.current_summary_object.get('filename', 'report')
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", f"{filename}_report.pdf", "PDF Files (*.pdf)")

        if save_path:
            try:
                response = requests.get(f"{API_BASE_URL}/summary/{self.current_history_id}/report/")
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Success", f"Report saved to {save_path}")
                else:
                    QMessageBox.warning(self, "Error", "Could not generate PDF report.")
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Error", "Connection Failed.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def update_ui_state(self):
        if self.current_summary_object and 'summary_data' in self.current_summary_object:
            # Get the data from the correct nested objects
            summary_data = self.current_summary_object['summary_data']
            avg = summary_data['averages']
            
            self.delete_button.setEnabled(True)
            self.pdf_button.setEnabled(True)
            
            # Access the data correctly
            self.label_filename.setText(f"File: {self.current_summary_object['filename']}")
            self.label_count.setText(f"Total Count: {summary_data['total_count']}")
            self.label_flow.setText(f"Avg. Flowrate: {avg['flowrate_avg']}")
            self.label_pressure.setText(f"Avg. Pressure: {avg['pressure_avg']}")
            self.label_temp.setText(f"Avg. Temperature: {avg['temperature_avg']} °C")
            
            self.update_chart(summary_data.get('type_distribution', {}))
            self.update_table_widget(summary_data.get('raw_data', []))
        
        else:
            self.delete_button.setEnabled(False)
            self.pdf_button.setEnabled(False)
            
            self.label_filename.setText("File: N/A")
            self.label_count.setText("Total Count: N/A")
            self.label_flow.setText("Avg. Flowrate: N/A")
            self.label_pressure.setText("Avg. Pressure: N/A")
            self.label_temp.setText("Avg. Temperature: N/A")
            
            self.update_chart(None)
            self.update_table_widget(None) 

    def update_chart(self, distribution):
        self.chart_canvas.axes.clear()
        
        if distribution:
            names = list(distribution.keys())
            values = list(distribution.values())
            
            self.chart_canvas.axes.bar(names, values, color='#3498db')
            self.chart_canvas.axes.set_title('Equipment Type Distribution')
            self.chart_canvas.axes.set_ylabel('# of Equipment')
            self.chart_canvas.figure.autofmt_xdate()
        else:
            self.chart_canvas.axes.set_title('Equipment Type Distribution')
            self.chart_canvas.axes.text(0.5, 0.5, 'No data loaded', 
                                        horizontalalignment='center', 
                                        verticalalignment='center', 
                                        transform=self.chart_canvas.axes.transAxes,
                                        fontsize=12, color='gray')

        self.chart_canvas.draw()
        
    def update_table_widget(self, raw_data):
        """Populates the QTableWidget with raw data."""
        self.table_widget.clear()
        
        if not raw_data or len(raw_data) == 0:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return

        try:
            headers = list(raw_data[0].keys())
            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)
            
            self.table_widget.setRowCount(len(raw_data))
            
            for row_idx, row_data in enumerate(raw_data):
                for col_idx, header in enumerate(headers):
                    cell_value = str(row_data.get(header, ''))
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(cell_value))
        
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
        except Exception as e:
            QMessageBox.critical(self, "Table Error", f"Failed to display data table: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())