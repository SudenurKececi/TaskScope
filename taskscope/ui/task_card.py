from __future__ import annotations
from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox,
    QPushButton, QSizePolicy, QWidget
)

class TaskCard(QFrame):
    toggled_done = Signal(int, bool)
    toggled_subtask = Signal(int, bool)
    request_edit = Signal(int)
    request_delete = Signal(int)
    size_changed = Signal(int)
    clicked = Signal(int)

    def __init__(self, task_id: int, title: str, description: str, due_at: datetime | None, 
                 is_done: bool, priority: str, tags: str, subtasks: list = None):
        super().__init__()
        self.task_id = task_id
        self._expanded = False
        self.subtasks = subtasks or []

        self.setObjectName("TaskCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setProperty("done", bool(is_done))
        
        # Önceliğe göre kenar rengi belirleyelim
        border_color = "#86CDB9" # Varsayılan (Orta/Düşük)
        if priority == "Yüksek":
            border_color = "#E53E3E" # Kırmızı
        elif priority == "Düşük":
            border_color = "#38A169" # Yeşil

        self.setStyleSheet(f"""
            QFrame#TaskCard {{
                background: #FFFFFF;
                border: 1px solid {border_color};
                border-left: 5px solid {border_color};
                border-radius: 8px;
            }}
            QLabel#Title {{ font-size: 15px; font-weight: 700; color: #0F1E19; }}
            QLabel#Meta {{ color: #718096; font-size: 11px; }}
            QFrame#TaskCard[done="true"] QLabel#Title {{ color: #A0AEC0; text-decoration: line-through; }}
        """)

        self.cb = QCheckBox()
        self.cb.setChecked(is_done)
        self.cb.stateChanged.connect(self._on_done_changed)

        self.title_lbl = QLabel(title.strip() if title else "")
        self.title_lbl.setObjectName("Title")

        # Meta Bilgisi: Tarih | Etiketler | Alt Görevler
        meta_parts = []
        if due_at: meta_parts.append(due_at.strftime("%d.%m %H:%M"))
        if tags: meta_parts.append(f"🏷️ {tags}")
        if self.subtasks:
            done_count = sum(1 for s in self.subtasks if s.is_done)
            meta_parts.append(f"✅ {done_count}/{len(self.subtasks)}")
            
        self.meta_lbl = QLabel("  |  ".join(meta_parts))
        self.meta_lbl.setObjectName("Meta")
        
        # --- Detay Alanı ---
        self.detail_widget = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_widget)
        self.detail_layout.setContentsMargins(25, 5, 5, 5)
        self.detail_widget.setVisible(False)
        
        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setStyleSheet("color:#4A5568; font-style:italic;")
            desc_lbl.setWordWrap(True)
            self.detail_layout.addWidget(desc_lbl)
            
        for st in self.subtasks:
            st_cb = QCheckBox(st.title)
            st_cb.setChecked(st.is_done)
            st_cb.stateChanged.connect(lambda state, sid=st.id: self.toggled_subtask.emit(sid, state == Qt.Checked))
            self.detail_layout.addWidget(st_cb)

        # Butonlar
        action_row = QHBoxLayout()
        self.edit_btn = QPushButton("Düzenle")
        self.edit_btn.setFixedSize(60,25)
        self.edit_btn.clicked.connect(self._emit_edit)
        
        self.del_btn = QPushButton("Sil")
        self.del_btn.setFixedSize(40,25)
        self.del_btn.setStyleSheet("color:#E53E3E;")
        self.del_btn.clicked.connect(self._emit_delete)
        
        action_row.addStretch()
        action_row.addWidget(self.edit_btn)
        action_row.addWidget(self.del_btn)
        self.detail_layout.addLayout(action_row)

        # Layout
        top = QHBoxLayout()
        top.addWidget(self.cb)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.title_lbl)
        vbox.addWidget(self.meta_lbl)
        top.addLayout(vbox)
        
        self.expand_btn = QPushButton("Detay")
        self.expand_btn.setFixedSize(50, 24)
        self.expand_btn.clicked.connect(self.toggle_expand)
        top.addWidget(self.expand_btn)

        main = QVBoxLayout(self)
        main.addLayout(top)
        main.addWidget(self.detail_widget)

        self._apply_font_strike(bool(is_done))

    def _apply_font_strike(self, done: bool):
        f = self.title_lbl.font()
        f.setStrikeOut(done)
        self.title_lbl.setFont(f)

    def _on_done_changed(self, state: int):
        self.clicked.emit(self.task_id)
        done = state == Qt.Checked
        self.setProperty("done", bool(done))
        self._apply_font_strike(bool(done))
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled_done.emit(self.task_id, done)

    def toggle_expand(self):
        self._expanded = not self._expanded
        self.detail_widget.setVisible(self._expanded)
        self.size_changed.emit(self.task_id)

    def _emit_edit(self): self.request_edit.emit(self.task_id)
    def _emit_delete(self): self.request_delete.emit(self.task_id)
    def mousePressEvent(self, event):
        self.clicked.emit(self.task_id)
        super().mousePressEvent(event)
