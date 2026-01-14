class Theme:
    LIGHT = {
        "bg_main": "#F3F4F6",      
        "bg_sidebar": "#FFFFFF",
        "bg_card": "#FFFFFF",
        "text_main": "#1F2937",    
        "text_dim": "#6B7280",
        "accent": "#10B981",       
        "border": "#E5E7EB",
        "hover": "#F9FAFB",
        "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB",
        "btn_bg": "#E5E7EB", 
        "btn_text": "#374151"
    }

    DARK = {
        "bg_main": "#111827",      
        "bg_sidebar": "#1F2937",   
        "bg_card": "#1F2937",      
        "text_main": "#F9FAFB",    
        "text_dim": "#9CA3AF",
        "accent": "#34D399",
        "border": "#374151",
        "hover": "#374151",
        "input_bg": "#111827",
        "input_border": "#4B5563",
        "btn_bg": "#374151",
        "btn_text": "#F9FAFB"
    }

    @staticmethod
    def get_style(theme_dict):
        return f"""
            QMainWindow, QWidget {{ 
                background-color: {theme_dict['bg_main']}; 
                color: {theme_dict['text_main']};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            
            QListWidget {{ border: none; outline: none; }}
            QListWidget::item {{ padding: 8px; border-radius: 6px; }}
            QListWidget::item:selected {{ 
                background-color: {theme_dict['hover']}; 
                color: {theme_dict['accent']};
                border: 1px solid {theme_dict['border']};
            }}
            QListWidget::item:hover {{ background-color: {theme_dict['hover']}; }}
            
            QFrame#TaskCard {{ 
                background-color: {theme_dict['bg_card']}; 
                border: 1px solid {theme_dict['border']}; 
                border-radius: 8px; 
            }}
            
            QLineEdit, QTextEdit, QComboBox {{ 
                background-color: {theme_dict['input_bg']}; 
                color: {theme_dict['text_main']}; 
                border: 1px solid {theme_dict['input_border']}; 
                border-radius: 6px; padding: 6px; 
            }}

            QPushButton {{
                background-color: {theme_dict['btn_bg']};
                color: {theme_dict['btn_text']};
                border: 1px solid {theme_dict['border']};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:checked {{
                background-color: {theme_dict['accent']};
                color: white;
                border: none;
            }}
        """