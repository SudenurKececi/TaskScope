from __future__ import annotations

from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox,
    QPushButton, QSizePolicy, QWidget
)

class TaskCard(QFrame):
    toggled_done = Signal(int, bool)
    toggled_subtask = Signal(int, bool) # Alt görev değişince sinyal
    request_edit = Signal(int)
    request_delete = Signal(int)
    size_changed = Signal(int)
    clicked = Signal(int)

    def __init__(self, task_id: int, title: str, description: str, due_at: datetime | None, is_done: bool, subtasks: list = None):
        super().__init__()
        self.task_id = task_id
        self._expanded = False
        self.subtasks = subtasks or []

        self.setObjectName("TaskCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMinimumHeight(100)

        # Style Propertyleri
        self.setProperty("done", bool(is_done))
        self.setProperty("selected", False)

        # --- Stil Tanımları ---
        # Not: Ana stil theme.qss'den geliyor ama buradaki dinamik propertyler için bu gerekli
        self.setStyleSheet("""
            QFrame#TaskCard {
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
            QFrame#TaskCard[selected="true"] {
                border: 2px solid #3CAF8B;
            }
            QLabel#Title {
                font-size: 15px; font-weight: 700; color: #2D3748;
            }
            QLabel#Meta {
                color: #718096; font-size: 12px;
            }
            QFrame#TaskCard[done="true"] QLabel#Title {
                color: #A0AEC0; text-decoration: line-through;
            }
            /* Subtask Checkbox Style */
            QCheckBox { font-size: 13px; color: #4A5568; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #CBD5E0; }
            QCheckBox::indicator:checked { background: #3CAF8B; border-color: #3CAF8B; }
        """)

        # 1. Ana Checkbox
        self.cb = QCheckBox()
        self.cb.setChecked(is_done)
        self.cb.stateChanged.connect(self._on_done_changed)

        # 2. Başlık ve Bilgi
        self.title_lbl = QLabel(title.strip() if title else "Başlıksız")
        self.title_lbl.setObjectName("Title")

        due_text = due_at.strftime("%d.%m %H:%M") if due_at else ""
        
        # Alt Görev Sayacı (Varsa)
        sub_info = ""
        if self.subtasks:
            done_count = sum(1 for s in self.subtasks if s.is_done)
            sub_info = f" • {done_count}/{len(self.subtasks)} Alt Görev"
        
        self.meta_lbl = QLabel(f"{due_text}{sub_info}")
        self.meta_lbl.setObjectName("Meta")

        # 3. Detay Alanı (Açıklama + Alt Görevler)
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(10, 5, 10, 5)
        self.detail_layout.setSpacing(8)
        self.detail_container.setVisible(False) # Başlangıçta gizli

        # Açıklama Metni
        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setStyleSheet("color:#4A5568; background:#F7FAFC; padding:8px; border-radius:6px;")
            desc_lbl.setWordWrap(True)
            self.detail_layout.addWidget(desc_lbl)
        
        # Alt Görev Listesi (Checkboxlar)
        for st in self.subtasks:
            st_cb = QCheckBox(st.title)
            st_cb.setChecked(st.is_done)
            # Python döngü değişkeni sorununu çözmek için varsayılan argüman kullanımı:
            st_cb.stateChanged.connect(lambda state, sid=st.id: self._on_subtask_changed(state, sid))
            self.detail_layout.addWidget(st_cb)

        # 4. Butonlar
        self.expand_btn = QPushButton("Detay")
        self.expand_btn.setFixedSize(60, 28)
        self.expand_btn.setStyleSheet("font-size:12px;")
        self.expand_btn.clicked.connect(self.toggle_expand)

        self.edit_btn = QPushButton("Düzenle")
        self.edit_btn.setFixedSize(70, 28)
        self.edit_btn.setStyleSheet("font-size:12px; background:#EDF2F7; color:#4A5568;")
        self.edit_btn.clicked.connect(self._emit_edit)

        self.del_btn = QPushButton("Sil")
        self.del_btn.setFixedSize(50, 28)
        self.del_btn.setStyleSheet("font-size:12px; background:#FED7D7; color:#C53030;")
        self.del_btn.clicked.connect(self._emit_delete)

        # --- Layout Yerleşimi ---
        top_row = QHBoxLayout()
        top_row.addWidget(self.cb)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.meta_lbl)
        top_row.addLayout(text_layout)
        
        top_row.addStretch()
        top_row.addWidget(self.expand_btn)

        action_row = QHBoxLayout()
        action_row.addStretch()
        action_row.addWidget(self.edit_btn)
        action_row.addWidget(self.del_btn)
        self.detail_layout.addLayout(action_row)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.detail_container)

        self._apply_font_strike(bool(is_done))

    def set_selected(self, selected: bool):
        self.setProperty("selected", bool(selected))
        self.style().unpolish(self)
        self.style().polish(self)

    def _apply_font_strike(self, done: bool):
        f = self.title_lbl.font()
        f.setStrikeOut(done)
        self.title_lbl.setFont(f)

    def _emit_edit(self):
        self.clicked.emit(self.task_id)
        self.request_edit.emit(self.task_id)

    def _emit_delete(self):
        self.clicked.emit(self.task_id)
        self.request_delete.emit(self.task_id)

    def _on_done_changed(self, state: int):
        self.clicked.emit(self.task_id)
        done = state == Qt.Checked
        self.setProperty("done", bool(done))
        self._apply_font_strike(bool(done))
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled_done.emit(self.task_id, done)

    def _on_subtask_changed(self, state: int, subtask_id: int):
        # Alt görevin durumu değiştiğinde sinyal gönder
        is_checked = state == Qt.Checked
        self.toggled_subtask.emit(subtask_id, is_checked)

    def toggle_expand(self):
        self.clicked.emit(self.task_id)
        self._expanded = not self._expanded
        self.detail_container.setVisible(self._expanded)
        self.expand_btn.setText("Gizle" if self._expanded else "Detay")
        
        # Kartın boyutu değiştiği için listeyi uyar
        self.size_changed.emit(self.task_id)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.task_id)