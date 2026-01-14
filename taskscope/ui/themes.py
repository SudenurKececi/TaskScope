class Theme:
    LIGHT = {
        "bg_main": "#F3F4F6", "bg_sidebar": "#FFFFFF", "bg_card": "#FFFFFF",
        "text_main": "#1F2937", "text_dim": "#6B7280", "accent": "#10B981",
        "border": "#E5E7EB", "hover": "#F9FAFB", "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB", "btn_bg": "#E5E7EB", "btn_text": "#374151"
    }
    DARK = {
        "bg_main": "#111827", "bg_sidebar": "#1F2937", "bg_card": "#1F2937",
        "text_main": "#F9FAFB", "text_dim": "#9CA3AF", "accent": "#34D399",
        "border": "#374151", "hover": "#374151", "input_bg": "#111827",
        "input_border": "#4B5563", "btn_bg": "#374151", "btn_text": "#F9FAFB"
    }

    @staticmethod
    def get_style(theme_dict):
        # Tırnak hatası düzeltildi
        return f"""
            QMainWindow, QWidget {{ background-color: {theme_dict['bg_main']}; color: {theme_dict['text_main']}; font-family: 'Segoe UI'; font-size: 14px; }}
            QListWidget {{ border: none; }}
            QListWidget::item:selected {{ background-color: {theme_dict['hover']}; color: {theme_dict['accent']}; }}
        """
