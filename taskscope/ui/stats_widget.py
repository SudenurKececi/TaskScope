from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from collections import Counter

from taskscope.db.database import SessionLocal
from taskscope.repositories.task_repo import TaskRepo

class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.session = SessionLocal()
        self.repo = TaskRepo(self.session)
        self.current_theme_is_dark = False 
        
        self.init_ui()
        # İlk açılışta refresh yapmıyoruz, main_window yapacak

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Başlık
        self.title = QLabel("📊 Verimlilik Analizi")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title)

        # Grafikler Yan Yana
        charts_layout = QHBoxLayout()
        
        # 1. Grafik: Proje Dağılımı
        self.fig1 = Figure(figsize=(4, 3), dpi=100)
        self.canvas1 = FigureCanvas(self.fig1)
        charts_layout.addWidget(self.canvas1)

        # 2. Grafik: Statü Durumu
        self.fig2 = Figure(figsize=(4, 3), dpi=100)
        self.canvas2 = FigureCanvas(self.fig2)
        charts_layout.addWidget(self.canvas2)
        
        layout.addLayout(charts_layout)

    def update_theme(self, is_dark):
        """Temaya göre grafik renklerini güncelle"""
        self.current_theme_is_dark = is_dark
        
        # Grafiklerin arka plan rengi
        bg_color = '#2D3748' if is_dark else '#F5F7FA'
        
        self.fig1.patch.set_facecolor(bg_color)
        self.fig2.patch.set_facecolor(bg_color)
        
        # Yeniden çiz
        self.refresh_stats()

    def refresh_stats(self):
        tasks = self.repo.list_tasks()
        
        # Tema Renkleri
        text_color = '#E2E8F0' if self.current_theme_is_dark else '#333333'
        
        # --- Grafik 1: Pasta ---
        self.fig1.clear()
        ax1 = self.fig1.add_subplot(111)
        
        projects = [t.project for t in tasks if t.project]
        proj_counts = Counter(projects)
        colors = ['#FFB7B2', '#B5EAD7', '#C7CEEA', '#E2F0CB', '#FFDAC1']
        
        if proj_counts:
            wedges, texts, autotexts = ax1.pie(proj_counts.values(), labels=proj_counts.keys(), autopct='%1.1f%%', startangle=90, colors=colors)
            
            # Yazı renkleri
            for t in texts: t.set_color(text_color)
            for t in autotexts: t.set_color('#333') # İç yazılar her zaman koyu
            
            ax1.set_title("Proje Dağılımı", fontsize=10, color=text_color)
        else:
            ax1.text(0.5, 0.5, "Veri Yok", ha='center', color=text_color)
            
        self.canvas1.draw()

        # --- Grafik 2: Sütun ---
        self.fig2.clear()
        ax2 = self.fig2.add_subplot(111)
        
        # Eksen renkleri
        ax2.spines['bottom'].set_color(text_color)
        ax2.spines['top'].set_color('none') 
        ax2.spines['left'].set_color(text_color)
        ax2.spines['right'].set_color('none')
        ax2.tick_params(axis='x', colors=text_color)
        ax2.tick_params(axis='y', colors=text_color)
        ax2.set_facecolor("none") # Plot alanı şeffaf
        
        status_map = {'todo': 'Yapılacak', 'in_progress': 'Sürüyor', 'done': 'Bitti'}
        statuses = [t.status for t in tasks]
        status_counts = Counter(statuses)
        
        if status_counts:
            labels = [status_map.get(k, k) for k in status_counts.keys()]
            values = list(status_counts.values())
            ax2.bar(labels, values, color=['#AECBFA', '#FDE994', '#A7FFEB'])
            ax2.set_title("Görev Durumu", fontsize=10, color=text_color)
            
        self.canvas2.draw()