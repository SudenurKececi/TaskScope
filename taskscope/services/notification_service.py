import time
from datetime import datetime, timedelta
from PySide6.QtCore import QThread
from plyer import notification
from taskscope.db.database import SessionLocal
from taskscope.models.task import Task

class NotificationWorker(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.notified_tasks = set()

    def run(self):
        print("🔔 Bildirim servisi aktif.")
        while self.running:
            try:
                self.check_deadlines()
            except Exception as e:
                print(f"Bildirim hatası: {e}")
            
            # 60 saniye bekle ama her saniye 'kapanma emri geldi mi?' diye kontrol et
            for _ in range(60):
                if not self.running:
                    return
                time.sleep(1)

    def check_deadlines(self):
        session = SessionLocal()
        try:
            now = datetime.now()
            tasks = session.query(Task).filter(
                Task.is_done == False,
                Task.due_at != None
            ).all()

            for task in tasks:
                if not task.due_at: continue
                
                time_left = task.due_at - now
                
                # 15 dakika kala bildirim
                if timedelta(minutes=0) < time_left <= timedelta(minutes=15):
                    if task.id not in self.notified_tasks:
                        self.send_notification(task.title, f"{int(time_left.seconds/60)} dakika kaldı!")
                        self.notified_tasks.add(task.id)
                
                # Süresi dolunca bildirim
                elif timedelta(minutes=-60) < time_left <= timedelta(minutes=0):
                     if task.id not in self.notified_tasks:
                        self.send_notification("Süresi Doldu!", f"'{task.title}' görevinin süresi doldu.")
                        self.notified_tasks.add(task.id)
        finally:
            session.close()

    def send_notification(self, title, message):
        try:
            notification.notify(
                title=f"TaskScope: {title}",
                message=message,
                app_name="TaskScope",
                timeout=5
            )
        except:
            pass # Bildirim gönderilemezse çökmesin

    def stop(self):
        self.running = False
        self.wait() # Thread'in güvenli kapanmasını bekle