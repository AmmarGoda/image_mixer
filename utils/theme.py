# utils/theme.py
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def apply_dark_theme():
    dark_palette = QPalette()

    # Background
    dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.WindowText, Qt.white)

    # Base color
    dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))

    # Tooltips
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)

    # Text
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)

    # Highlight
    dark_palette.setColor(QPalette.Highlight, QColor(100, 100, 200))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    QApplication.setPalette(dark_palette)

    # Apply the global stylesheet
    QApplication.instance().setStyleSheet("""
        QWidget {
            background-color: #2D2D2D;
            color: #FFFFFF;
            font-family: Arial;
        }

        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #3A0CA3, stop:1 #4361EE);
            border: 1px solid #4C4C4C;
            padding: 10px;
            border-radius: 8px;
            color: #E0E0E0;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #480CA8, stop:1 #4CC9F0);
            border: 1px solid #77B;
        }

        QPushButton:pressed {
            background-color: #3A0CA3;
        }

        QGroupBox {
            font-size: 15px;
            font-weight: bold;
            color: #BB86FC;
            border: 2px solid #555;
            border-radius: 10px;
            margin-top: 10px;
        }

        QGroupBox:title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
            background-color: #2D2D2D;
        }

        QLabel {
            font-size: 13px;
            color: #FFFFFF;
        }

        QSlider::handle:horizontal {
            background: #7209B7;
            border: 2px solid #BB86FC;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }

        QSlider::groove:horizontal {
            background: #4C4C4C;
            height: 8px;
            border-radius: 4px;
        }

        QProgressBar {
            border: 2px solid #555;
            border-radius: 5px;
            background-color: #444;
            text-align: center;
            color: #FFFFFF;
            font-weight: bold;
        }

        QProgressBar::chunk {
            background-color: #3A0CA3;
            width: 20px;
        }
    """)