import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QLabel, QGridLayout, QListWidget,
    QListWidgetItem, QSizePolicy, QFrame, QStackedWidget, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QPainter
from PyQt5.QtCore import Qt, QSize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE_URL = 'http://127.0.0.1:8000/api'

# --- Custom Widgets for "Premium" Look ---

class GradientWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        # Subtle mesh-like gradient matching web: slate to white with hint of indigo
        gradient.setColorAt(0.0, QColor("#f8fafc"))
        gradient.setColorAt(1.0, QColor("#eef2ff")) 
        painter.setBrush(QBrush(gradient))
        painter.drawRect(self.rect())

class CardFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.patch.set_alpha(0) # Transparent figure background
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: transparent;")

class App(GradientWidget): # Inherit from GradientWidget
    def __init__(self):
        super().__init__()
        self.title = 'Chemical Equipment Visualizer'
        self.left = 100
        self.top = 100
        self.width = 1280
        self.height = 850
        
        self.current_summary_object = None
        self.current_history_id = None
        self.history_list_data = []

        self.initUI()
        self.fetch_history()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Global Styles
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                color: #1e293b;
            }
            QLabel {
                background: transparent;
            }
            QLabel#HeroTitle {
                font-size: 42px;
                font-weight: 800;
                color: #1e293b;
            }
            QLabel#HeroSubtitle {
                font-size: 18px;
                color: #64748b;
            }
            QLabel#CardTitle {
                font-size: 18px;
                font-weight: 700;
                color: #334155;
                padding-bottom: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                font-weight: 600;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
            QPushButton#UploadHero {
                background-color: #ffffff;
                color: #4f46e5;
                border: 2px dashed #cbd5e1;
                font-size: 18px;
                padding: 40px;
                border-radius: 20px;
            }
            QPushButton#UploadHero:hover {
                border-color: #4f46e5;
                background-color: #f5f3ff;
            }
            QPushButton#DeleteBtn {
                background-color: #fee2e2;
                color: #b91c1c;
            }
            QPushButton#DeleteBtn:hover {
                background-color: #fca5a5;
            }
            QListWidget {
                border: none;
                background: transparent;
            }
            QListWidget::item {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                color: #334155;
            }
            QListWidget::item:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
            QListWidget::item:selected {
                background-color: #eef2ff;
                border-color: #818cf8;
                color: #4f46e5;
            }
            QTableWidget {
                background-color: #ffffff;
                border: none;
                gridline-color: #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #64748b;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Glassmorphism Header
        self.header = QFrame()
        self.header.setStyleSheet("background-color: rgba(255, 255, 255, 0.85); border-bottom: 1px solid #e2e8f0;")
        self.header.setFixedHeight(80)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        header_title = QLabel("Chemical Visualizer")
        header_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #4f46e5; background: transparent;")
        header_layout.addWidget(header_title)
        
        header_layout.addStretch()
        
        # Home Button in Header
        self.btn_home = QPushButton("Dashboard Home")
        self.btn_home.setStyleSheet("background: transparent; color: #64748b; font-weight: 600;")
        self.btn_home.setCursor(Qt.PointingHandCursor)
        self.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        header_layout.addWidget(self.btn_home)
        
        self.layout.addWidget(self.header)

        # Stacked Pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.hero_page = QWidget()
        self.init_hero_page()
        self.stacked_widget.addWidget(self.hero_page)

        self.dashboard_page = QWidget()
        self.init_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)

        self.stacked_widget.setCurrentIndex(0)
        self.showMaximized()

    def init_hero_page(self):
        layout = QVBoxLayout(self.hero_page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # Title Section
        title = QLabel("Visualize your Chemical\nEquipment Parameters")
        title.setObjectName("HeroTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Upload your CSV data to generate instant insights, charts, and reports.")
        subtitle.setObjectName("HeroSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Upload Button
        upload_btn = QPushButton("\n⬆\n\nClick to Upload CSV File\nor drag and drop here\n")
        upload_btn.setObjectName("UploadHero")
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setFixedWidth(500)
        upload_btn.clicked.connect(self.handle_upload)
        layout.addWidget(upload_btn, 0, Qt.AlignCenter)

        layout.addSpacing(30)

        # Recent History Section
        hist_label = QLabel("Recent Uploads")
        hist_label.setStyleSheet("font-weight: 700; font-size: 16px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;")
        hist_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(hist_label)

        self.hero_history_list = QListWidget()
        self.hero_history_list.setFixedWidth(600)
        self.hero_history_list.setFixedHeight(250)
        self.hero_history_list.itemClicked.connect(self.handle_history_click)
        layout.addWidget(self.hero_history_list, 0, Qt.AlignCenter)

    def init_dashboard_page(self):
        # Using a ScrollArea for dashboard could be good, but we'll stick to Grid for now to match web
        layout = QGridLayout(self.dashboard_page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        # 1. Summary Card (Top, Full Width)
        self.summary_card = CardFrame()
        summary_layout = QHBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(24, 24, 24, 24)
        
        # Left: Info
        info_layout = QVBoxLayout()
        title_lbl = QLabel("Data Summary")
        title_lbl.setObjectName("CardTitle")
        self.label_filename = QLabel("File: ...")
        self.label_filename.setStyleSheet("font-size: 15px; color: #64748b; margin-top: 4px;")
        
        info_layout.addWidget(title_lbl)
        info_layout.addWidget(self.label_filename)
        info_layout.addStretch()
        
        self.pdf_button = QPushButton('Download PDF Report')
        self.pdf_button.setCursor(Qt.PointingHandCursor)
        self.pdf_button.clicked.connect(self.handle_pdf)
        info_layout.addWidget(self.pdf_button)
        
        summary_layout.addLayout(info_layout, 1)

        # Right: Stats Grid
        stats_layout = QGridLayout()
        stats_layout.setHorizontalSpacing(40)
        stats_layout.setVerticalSpacing(20)
        
        self.stat_count = self.create_stat_widget("Total Equipment", "0")
        self.stat_flow = self.create_stat_widget("Avg. Flowrate", "0")
        self.stat_pressure = self.create_stat_widget("Avg. Pressure", "0")
        self.stat_temp = self.create_stat_widget("Avg. Temp", "0")

        stats_layout.addLayout(self.stat_count, 0, 0)
        stats_layout.addLayout(self.stat_flow, 0, 1)
        stats_layout.addLayout(self.stat_pressure, 1, 0)
        stats_layout.addLayout(self.stat_temp, 1, 1)
        
        summary_layout.addLayout(stats_layout, 2)
        
        layout.addWidget(self.summary_card, 0, 0, 1, 3)

        # 2. Charts (Left, span 2)
        chart_card = CardFrame()
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        chart_layout.addWidget(QLabel("Equipment Distribution", objectName="CardTitle"))
        
        self.chart_canvas = MplCanvas(self)
        chart_layout.addWidget(self.chart_canvas)
        
        layout.addWidget(chart_card, 1, 0, 1, 2)

        # 3. History Sidebar (Right, span 1)
        hist_card = CardFrame()
        hist_layout = QVBoxLayout(hist_card)
        hist_layout.setContentsMargins(20, 20, 20, 20)
        hist_layout.addWidget(QLabel("Upload History", objectName="CardTitle"))
        
        self.dashboard_history_list = QListWidget()
        self.dashboard_history_list.itemClicked.connect(self.handle_history_click)
        hist_layout.addWidget(self.dashboard_history_list)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setObjectName("DeleteBtn")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(self.handle_delete)
        hist_layout.addWidget(self.delete_btn)

        layout.addWidget(hist_card, 1, 2, 1, 1)

        # 4. Data Table (Bottom, Full Width)
        table_card = CardFrame()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.addWidget(QLabel("Raw Data", objectName="CardTitle"))
        
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.setStyleSheet("""
            QTableWidget { gridline-color: transparent; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f1f5f9; }
        """)
        table_layout.addWidget(self.table_widget)
        
        layout.addWidget(table_card, 2, 0, 1, 3)
        
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(1, 1) # Give chart row expansion space

    def create_stat_widget(self, label, value):
        container = QFrame()
        l = QVBoxLayout(container)
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(4)
        
        val = QLabel(value)
        val.setStyleSheet("font-size: 32px; font-weight: 800; color: #4f46e5;")
        
        lbl = QLabel(label.upper())
        lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px;")
        
        l.addWidget(val)
        l.addWidget(lbl)
        return l

    def update_stat_widget(self, layout_item, value):
        # Layout item is a QLayoutItem (wrapper around QFrame)
        # We need the widget
        widget = layout_item.widget()
        # The value label is the first item in the layout
        val_label = widget.layout().itemAt(0).widget()
        val_label.setText(str(value))

    def fetch_history(self):
        try:
            response = requests.get(f"{API_BASE_URL}/history/")
            if response.status_code == 200:
                self.history_list_data = response.json()
                self.update_history_widgets()
        except:
            pass

    def update_history_widgets(self):
        for widget in [self.hero_history_list, self.dashboard_history_list]:
            widget.clear()
            for item_data in self.history_list_data:
                date_str = item_data['uploaded_at']
                try:
                    # Simple formatting
                    date_part = date_str.split('T')[0]
                    time_part = date_str.split('T')[1][:5]
                    display_text = f"{item_data['filename']}\n{date_part} at {time_part}"
                except:
                    display_text = item_data['filename']
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, item_data['id'])
                widget.addItem(item)

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
                        self.fetch_history()
                        self.stacked_widget.setCurrentIndex(1)
                        self.update_dashboard_ui()
                        QMessageBox.information(self, "Success", "File uploaded successfully!")
                    else:
                        QMessageBox.warning(self, "Error", response.json().get('error', 'Upload failed'))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def handle_history_click(self, item):
        hid = item.data(Qt.UserRole)
        self.load_summary(hid)

    def load_summary(self, hid):
        try:
            r = requests.get(f"{API_BASE_URL}/summary/{hid}/")
            if r.status_code == 200:
                self.current_summary_object = r.json()
                self.current_history_id = hid
                self.stacked_widget.setCurrentIndex(1)
                self.update_dashboard_ui()
        except:
            QMessageBox.critical(self, "Error", "Connection error")

    def handle_delete(self):
        if not self.current_history_id: return
        r = QMessageBox.question(self, "Delete", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            try:
                requests.delete(f"{API_BASE_URL}/summary/{self.current_history_id}/")
                self.current_history_id = None
                self.current_summary_object = None
                self.fetch_history()
                self.stacked_widget.setCurrentIndex(0)
            except:
                pass

    def handle_pdf(self):
        if not self.current_history_id: return
        fn = self.current_summary_object.get('filename', 'report')
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"{fn}_report.pdf", "PDF (*.pdf)")
        if path:
            try:
                r = requests.get(f"{API_BASE_URL}/summary/{self.current_history_id}/report/")
                with open(path, 'wb') as f:
                    f.write(r.content)
                QMessageBox.information(self, "Success", "PDF Saved.")
            except:
                pass

    def update_dashboard_ui(self):
        if not self.current_summary_object: return
        data = self.current_summary_object.get('summary_data', {})
        avg = data.get('averages', {})
        
        self.label_filename.setText(f"File: {self.current_summary_object.get('filename')}")
        
        self.update_stat_widget(self.stat_count, data.get('total_count', 0))
        self.update_stat_widget(self.stat_flow, f"{avg.get('flowrate_avg', 0)}")
        self.update_stat_widget(self.stat_pressure, f"{avg.get('pressure_avg', 0)}")
        self.update_stat_widget(self.stat_temp, f"{avg.get('temperature_avg', 0)} °C")
        
        # Chart
        self.chart_canvas.axes.clear()
        dist = data.get('type_distribution', {})
        if dist:
            colors = ['#4f46e5', '#06b6d4', '#8b5cf6', '#f43f5e', '#10b981']
            self.chart_canvas.axes.bar(dist.keys(), dist.values(), color=colors[:len(dist)])
            self.chart_canvas.axes.tick_params(colors='#64748b')
            for spine in self.chart_canvas.axes.spines.values():
                spine.set_edgecolor('#e2e8f0')
        self.chart_canvas.draw()
        
        # Table
        raw = data.get('raw_data', [])
        self.table_widget.clear()
        if raw:
            headers = list(raw[0].keys())
            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(raw))
            for r, row in enumerate(raw):
                for c, h in enumerate(headers):
                    self.table_widget.setItem(r, c, QTableWidgetItem(str(row.get(h, ''))))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
