from __future__ import annotations
from PySide6.QtCore import Qt, Signal, QMimeData, QByteArray, QDataStream, QIODevice
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QListWidgetItem, QLabel, QAbstractItemView)
from PySide6.QtGui import QDrag, QPixmap

class KanbanColumn(QListWidget):
    """Gelişmiş Sürükle-Bırak Destekli Kolon"""
    task_dropped = Signal(int, str) # task_id, new_status_code

    def __init__(self, status_code: str):
        super().__init__()
        self.status_code = status_code
        
        # Sürükle Bırak Ayarları
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        
        # Stil
        self.setSpacing(10)
        self.setStyleSheet("""
            QListWidget { 
                background: #F5F7FA; 
                border-radius: 10px; 
                padding: 5px;
                border: 1px solid #E0E0E0;
            }
            QListWidget::item { background: transparent; }
        """)

    def startDrag(self, supportedActions):
        """Sürükleme başladığında kartın görsel kopyasını al"""
        item = self.currentItem()
        if not item: return

        # Kart Widget'ına eriş
        widget = self.itemWidget(item)
        if not widget: return

        # task_id'yi taşıma çantasına (MimeData) koy
        mime_data = QMimeData()
        mime_data.setText(str(widget.task_id))

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        # Görsel olarak widget'ın fotoğrafını çek
        pixmap = widget.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center()) # Fareyi ortala

        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.source() != self:
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.source() != self:
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Bırakıldığında çalışır"""
        if event.source() == self:
            # Aynı kolon içindeki sıralama değişimi (İstersen buraya da kod yazılabilir)
            super().dropEvent(event)
        else:
            # Başka kolondan geldi!
            task_id_str = event.mimeData().text()
            if task_id_str.isdigit():
                task_id = int(task_id_str)
                # Sinyal gönder: "Bu task ID, benim kolonuma (status_code) düştü"
                self.task_dropped.emit(task_id, self.status_code)
                event.accept()

class KanbanBoard(QWidget):
    status_changed = Signal(int, str) # Ana pencereye iletilecek sinyal

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Kolonları Oluştur
        self.todo_col = self._create_column("YAPILACAK", "todo", "#AECBFA")
        self.prog_col = self._create_column("SÜRÜYOR", "in_progress", "#FDE994")
        self.done_col = self._create_column("BİTTİ", "done", "#A7FFEB")

        layout.addWidget(self.todo_col)
        layout.addWidget(self.prog_col)
        layout.addWidget(self.done_col)

    def _create_column(self, title, code, color_hex):
        # Başlık ve Liste yapısını paketle
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0,0,0,0)
        
        # Başlık Etiketi
        header = QLabel(f"  {title}")
        header.setStyleSheet(f"""
            font-weight: bold; 
            font-size: 13px; 
            color: #444; 
            background: {color_hex}; 
            border-radius: 6px; 
            padding: 8px;
        """)
        
        # Liste (KanbanColumn)
        col_list = KanbanColumn(code)
        col_list.task_dropped.connect(self.status_changed.emit) # Sinyali yukarı taşı
        
        vbox.addWidget(header)
        vbox.addWidget(col_list)
        return container

    def get_column_by_status(self, status):
        if status == "in_progress": return self.findChild(KanbanColumn, "kanban_col_in_progress") # ID ile bulmak zor olabilir, direkt referans:
        # Daha basit yöntem:
        return None # Aşağıdaki add_task fonksiyonunda yöneteceğiz

    def clear_all(self):
        # Children içindeki listeleri bulup temizle
        self.todo_col.findChild(QListWidget).clear()
        self.prog_col.findChild(QListWidget).clear()
        self.done_col.findChild(QListWidget).clear()

    def add_task(self, task, card_widget):
        item = QListWidgetItem()
        item.setSizeHint(card_widget.sizeHint())
        
        # Hangi kolona eklenecek?
        target_list = self.todo_col.findChild(QListWidget)
        if task.status == "in_progress": 
            target_list = self.prog_col.findChild(QListWidget)
        elif task.status == "done": 
            target_list = self.done_col.findChild(QListWidget)
        
        target_list.addItem(item)
        target_list.setItemWidget(item, card_widget)