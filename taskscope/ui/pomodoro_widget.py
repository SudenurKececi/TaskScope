from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class PomodoroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.minutes = 25
        self.seconds = 0
        self.is_running = False
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Başlık
        lbl_title = QLabel("🍅 ODAKLAN")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-weight:bold; color:#E64A19; font-size:12px;")
        layout.addWidget(lbl_title)
        
        # Süre Göstergesi
        self.lbl_time = QLabel("25:00")
        self.lbl_time.setAlignment(Qt.AlignCenter)
        self.lbl_time.setStyleSheet("font-size: 32px; font-weight:bold; color:#444; margin: 10px 0;")
        layout.addWidget(self.lbl_time)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Başlat")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setStyleSheet("background:#3CAF8B; color:white; border-radius:15px; padding:5px;")
        self.btn_start.clicked.connect(self.toggle_timer)
        
        self.btn_reset = QPushButton("↺")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setFixedSize(30, 30)
        self.btn_reset.setStyleSheet("background:#E0E0E0; border-radius:15px; color:#555;")
        self.btn_reset.clicked.connect(self.reset_timer)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_reset)
        layout.addLayout(btn_layout)
        
        # Kutu Görünümü
        self.setStyleSheet("""
            PomodoroWidget {
                background: white;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
            }
        """)

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.btn_start.setText("Devam")
            self.btn_start.setStyleSheet("background:#2196F3; color:white; border-radius:15px; padding:5px;")
        else:
            self.timer.start(1000) # 1 saniye
            self.btn_start.setText("Durdur")
            self.btn_start.setStyleSheet("background:#E57373; color:white; border-radius:15px; padding:5px;")
        
        self.is_running = not self.is_running

    def update_timer(self):
        if self.seconds == 0:
            if self.minutes == 0:
                self.timer.stop()
                self.is_running = False
                self.lbl_time.setText("Bitti!")
                self.btn_start.setText("Başlat")
                # Buraya bir ses veya bildirim eklenebilir
                return
            else:
                self.minutes -= 1
                self.seconds = 59
        else:
            self.seconds -= 1
            
        self.lbl_time.setText(f"{self.minutes:02}:{self.seconds:02}")

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.minutes = 25
        self.seconds = 0
        self.lbl_time.setText("25:00")
        self.btn_start.setText("Başlat")
        self.btn_start.setStyleSheet("background:#3CAF8B; color:white; border-radius:15px; padding:5px;")