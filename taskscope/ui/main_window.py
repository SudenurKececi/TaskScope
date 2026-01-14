from __future__ import annotations
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QStackedWidget, QLabel, QStyle
)

from taskscope.db.database import SessionLocal
from taskscope.repositories.task_repo import TaskRepo
from taskscope.services.notification_service import NotificationWorker
from taskscope.ui.task_editor_dialog import TaskEditorDialog
from taskscope.ui.task_card import TaskCard
from taskscope.ui.kanban_board import KanbanBoard
from taskscope.ui.pomodoro_widget import PomodoroWidget
from taskscope.ui.stats_widget import StatsWidget
from taskscope.ui.themes import Theme 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskScope - Proje Yönetimi")
        self.resize(1280, 850)

        self.session = SessionLocal()
        self.repo = TaskRepo(self.session)
        self.current_project_filter = None
        self.is_dark_mode = False 

        self.init_ui()
        self.apply_theme() 

        self.notification_thread = NotificationWorker()
        self.notification_thread.start()

        self.refresh_data()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === SOL MENÜ ===
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(260)
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(15, 25, 15, 25)
        
        lbl_proj = QLabel("PROJELER")
        lbl_proj.setStyleSheet("font-weight:bold; font-size:12px; opacity:0.7; margin-bottom:10px;")
        sb_layout.addWidget(lbl_proj)
        
        self.project_list = QListWidget()
        self.project_list.setCursor(Qt.PointingHandCursor)
        self.project_list.itemClicked.connect(self.filter_by_project)
        sb_layout.addWidget(self.project_list)
        
        self.stats_lbl = QLabel("Yükleniyor...")
        self.stats_lbl.setStyleSheet("font-size: 12px; margin-top:10px; opacity:0.6;")
        sb_layout.addWidget(self.stats_lbl)
        
        sb_layout.addStretch() 
        self.pomodoro = PomodoroWidget()
        sb_layout.addWidget(self.pomodoro)
        
        main_layout.addWidget(self.sidebar)

        # === SAĞ İÇERİK ===
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # --- ÜST BAR ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Görev Ara...")
        self.search_edit.setFixedHeight(40)
        self.search_edit.textChanged.connect(self.refresh_data)
        
        # Yerleşik İkonları Kullan (Daha Temiz Görünüm)
        icon_size = QSize(18, 18)
        
        # Tema Butonu
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("Temayı Değiştir")
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Görünüm Butonu
        self.view_toggle = QPushButton(" Liste")
        self.view_toggle.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))
        self.view_toggle.setIconSize(icon_size)
        self.view_toggle.setCheckable(True)
        self.view_toggle.setFixedHeight(40)
        self.view_toggle.clicked.connect(self.toggle_view)

        # İstatistik Butonu
        self.stats_btn = QPushButton(" Analiz")
        self.stats_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogInfoView))
        self.stats_btn.setIconSize(icon_size)
        self.stats_btn.setCheckable(True)
        self.stats_btn.setFixedHeight(40)
        self.stats_btn.clicked.connect(self.toggle_stats)
        
        # Yeni Ekle Butonu
        add_btn = QPushButton(" Yeni Görev")
        add_btn.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        add_btn.setIconSize(icon_size)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("background-color:#3CAF8B; color:white; font-weight:bold; padding:0 15px; border-radius:6px;")
        add_btn.clicked.connect(self.add_task)

        top_bar.addWidget(self.search_edit, 1)
        top_bar.addWidget(self.theme_btn)
        top_bar.addWidget(self.view_toggle)
        top_bar.addWidget(self.stats_btn)
        top_bar.addWidget(add_btn)
        content_layout.addLayout(top_bar)

        # --- SAYFALAR ---
        self.stack = QStackedWidget()
        
        self.kanban = KanbanBoard()
        self.kanban.status_changed.connect(self.on_kanban_drop)
        self.stack.addWidget(self.kanban)
        
        self.simple_list = QListWidget()
        self.simple_list.setSpacing(6)
        self.simple_list.setSelectionMode(QListWidget.NoSelection)
        self.stack.addWidget(self.simple_list)

        self.stats_page = StatsWidget()
        self.stack.addWidget(self.stats_page)
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)

    # --- FONKSİYONLAR ---
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        
    def apply_theme(self):
        theme_data = Theme.DARK if self.is_dark_mode else Theme.LIGHT
        qss = Theme.get_style(theme_data)
        self.setStyleSheet(qss)
        
        # Tema ikonunu text yerine stil ile güncellemek daha temiz olabilir ama şimdilik text:
        self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")
        self.theme_btn.setStyleSheet(f"border: 1px solid {theme_data['border']}; border-radius: 20px; font-size: 16px;")

        sb_bg = theme_data["bg_sidebar"]
        txt_main = theme_data["text_main"]
        self.sidebar.setStyleSheet(f"background: {sb_bg}; border-right: 1px solid {theme_data['border']}; color: {txt_main};")
        
        self.stats_page.update_theme(self.is_dark_mode)

    def toggle_view(self):
        self.stats_btn.setChecked(False)
        if self.view_toggle.isChecked():
            self.stack.setCurrentIndex(1)
            self.view_toggle.setText(" Pano")
            self.view_toggle.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        else:
            self.stack.setCurrentIndex(0)
            self.view_toggle.setText(" Liste")
            self.view_toggle.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))
        self.refresh_data()

    def toggle_stats(self):
        if self.stats_btn.isChecked():
            self.view_toggle.setChecked(False)
            self.view_toggle.setText(" Görünüm")
            self.stack.setCurrentIndex(2)
            self.stats_page.refresh_stats()
        else:
            self.stack.setCurrentIndex(0)

    def filter_by_project(self, item):
        txt = item.text()
        self.current_project_filter = None if txt == "Tümü" else txt
        self.refresh_data()

    def refresh_data(self):
        current_row = self.project_list.currentRow()
        self.project_list.clear()
        self.project_list.addItem(QListWidgetItem("Tümü"))
        for p in self.repo.get_projects():
            if p: self.project_list.addItem(p)
        self.project_list.setCurrentRow(current_row if current_row >= 0 else 0)

        tasks = self.repo.list_tasks(self.search_edit.text(), self.current_project_filter)
        self.stats_lbl.setText(f"Toplam: {len(tasks)} görev")

        self.kanban.clear_all()
        self.simple_list.clear()

        for t in tasks:
            card_kanban = TaskCard(t.id, t.title, t.description, t.due_at, t.status, t.priority, t.is_done, t.subtasks)
            card_kanban.request_edit.connect(self.edit_task)
            card_kanban.toggled_done.connect(self.on_task_done)
            self.kanban.add_task(t, card_kanban)
            
            card_list = TaskCard(t.id, t.title, t.description, t.due_at, t.status, t.priority, t.is_done, t.subtasks)
            card_list.request_edit.connect(self.edit_task)
            card_list.toggled_done.connect(self.on_task_done)
            
            item = QListWidgetItem()
            item.setSizeHint(card_list.sizeHint())
            self.simple_list.addItem(item)
            self.simple_list.setItemWidget(item, card_list)
            
        if self.stack.currentIndex() == 2:
            self.stats_page.refresh_stats()

    def on_kanban_drop(self, task_id, new_status):
        self.repo.update_status(task_id, new_status)
        self.refresh_data()

    def on_task_done(self, task_id, is_done):
        self.repo.update_status(task_id, "done" if is_done else "todo")
        self.refresh_data()

    def add_task(self):
        dlg = TaskEditorDialog(self)
        if dlg.exec():
            vals = dlg.get_values()
            self.repo.create_task(*vals)
            self.refresh_data()

    def edit_task(self, task_id):
        t = self.repo.get_task(task_id)
        if not t: return
        dlg = TaskEditorDialog(self, t.title, t.description, t.due_at, t.priority, t.project, t.tags or "", t.recurring or "none")
        if dlg.exec():
            vals = dlg.get_values()
            update_vals = vals[:-1] 
            self.repo.update_task_full(task_id, *update_vals)
            self.refresh_data()

    def closeEvent(self, event):
        self.notification_thread.stop()
        self.session.close()
        super().closeEvent(event)