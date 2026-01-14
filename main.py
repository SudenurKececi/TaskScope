import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QFile, QTextStream
from taskscope.db.database import init_db
from taskscope.ui.main_window import MainWindow

def main():
    # 1. Yüksek Çözünürlük Ayarları
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 2. Veritabanını Başlat
    init_db()

    app = QApplication(sys.argv)
    
    # 3. Font Ayarı (Senin istediğin Segoe UI)
    font = QFont("Segoe UI", 9)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    # 4. TASARIMI YÜKLE (Kritik Adım)
    # theme.qss dosyasını bulup yüklüyoruz.
    qss_file = QFile("theme.qss")
    # Eğer theme.qss ana dizinde değilse resources altına bakar
    if not qss_file.exists():
        qss_file = QFile("taskscope/resources/theme.qss")
        
    if qss_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(qss_file)
        app.setStyleSheet(stream.readAll())
        print("✅ Tasarım (QSS) başarıyla yüklendi.")
    else:
        print("⚠️ theme.qss bulunamadı! Varsayılan renkler kullanılacak.")

    w = MainWindow()
    w.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
