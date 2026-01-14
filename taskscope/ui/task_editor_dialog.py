from __future__ import annotations
from datetime import datetime
from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QDateTimeEdit, QCheckBox, QPushButton, QMessageBox, QComboBox
)

class TaskEditorDialog(QDialog):
    def __init__(self, parent=None, title: str = "", description: str = "", due_at: datetime | None = None,
                 priority: str = "Orta", tags: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Görev Detayları")
        self.setModal(True)
        self.setMinimumWidth(450)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Görev başlığı (zorunlu)")

        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Açıklama...")
        self.desc_edit.setFixedHeight(60)

        # --- YENİ EKLENEN SATIR (Öncelik ve Etiket) ---
        meta_layout = QHBoxLayout()
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Yüksek", "Orta", "Düşük"])
        self.priority_combo.setCurrentText(priority)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Etiketler (örn: iş, acil)")
        self.tags_edit.setText(tags)
        
        meta_layout.addWidget(QLabel("Öncelik:"))
        meta_layout.addWidget(self.priority_combo)
        meta_layout.addWidget(QLabel("Etiket:"))
        meta_layout.addWidget(self.tags_edit)
        # ---------------------------------------------

        # Alt Görevler
        self.subtasks_edit = QTextEdit()
        self.subtasks_edit.setPlaceholderText("Alt Görevler:\n- Madde 1\n- Madde 2")
        self.subtasks_edit.setFixedHeight(80)
        
        if title:
            self.subtasks_edit.setPlaceholderText("Alt görevler kart üzerinden yönetilir.")
            self.subtasks_edit.setEnabled(False)

        self.has_due_cb = QCheckBox("Tarih Ekle")
        self.due_edit = QDateTimeEdit()
        self.due_edit.setCalendarPopup(True)
        self.due_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.due_edit.setEnabled(False)
        self.due_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        self.save_btn = QPushButton("Kaydet")
        self.cancel_btn = QPushButton("İptal")

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Başlık"))
        layout.addWidget(self.title_edit)
        layout.addWidget(QLabel("Açıklama"))
        layout.addWidget(self.desc_edit)
        
        layout.addLayout(meta_layout) # Meta satırını ekle
        
        layout.addWidget(QLabel("Alt Görevler"))
        layout.addWidget(self.subtasks_edit)
        layout.addWidget(self.has_due_cb)
        layout.addWidget(self.due_edit)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        # Değerleri doldur
        self.title_edit.setText(title)
        self.desc_edit.setPlainText(description)

        if due_at is not None:
            self.has_due_cb.setChecked(True)
            self.due_edit.setEnabled(True)
            qdt = QDateTime.fromSecsSinceEpoch(int(due_at.timestamp()))
            self.due_edit.setDateTime(qdt)

        self.has_due_cb.toggled.connect(self.due_edit.setEnabled)
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._on_save)

    def _on_save(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Uyarı", "Başlık boş olamaz.")
            return
        self.accept()

    def get_values(self) -> tuple:
        title = self.title_edit.text().strip()
        desc = self.desc_edit.toPlainText().strip()
        due_at = self.due_edit.dateTime().toPython() if self.has_due_cb.isChecked() else None
        
        priority = self.priority_combo.currentText()
        tags = self.tags_edit.text().strip()
        
        raw_subs = self.subtasks_edit.toPlainText().split('\n')
        subtasks = [s.strip() for s in raw_subs if s.strip()]
        
        return title, desc, due_at, priority, tags, subtasks
