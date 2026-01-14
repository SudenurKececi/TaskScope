import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from taskscope.db.database import init_db
from taskscope.ui.main_window import MainWindow

def main():
    # 1. Yüksek Çözünürlük (High DPI) Ayarı - Bulanıklığı Giderir
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 2. Veritabanını Başlat
    init_db()

    app = QApplication(sys.argv)
    
    # 3. Modern Font Zorlaması
    # Segoe UI Windows için en temiz fonttur.
    font = QFont("Segoe UI", 9)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()