"""
Sleek, high-density professional light theme for PyQt5.
Adheres strictly to modern desktop design principles (refined typography, compact density,
restrained neutral palette with subtle borders, and professional metric boxes).
"""

APP_STYLESHEET = """
/* Global Window & Fonts */
QMainWindow, QDialog, QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif;
    font-size: 11px;
}

/* Tab Widget Styling - Sleek Segmented Style */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 6px;
    padding: 6px;
}

QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
}

QTabBar::tab {
    background-color: #f1f5f9;
    color: #64748b;
    padding: 6px 14px;
    margin-right: 3px;
    border: 1px solid #e2e8f0;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-weight: 600;
    font-size: 11px;
    min-height: 18px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0f172a;
    border-bottom: 2px solid #0f172a;
    font-weight: 700;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #0f172a;
}

/* Professional Boxes (QGroupBox) */
QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 12px;
    padding-bottom: 8px;
    padding-left: 10px;
    padding-right: 10px;
    font-weight: 600;
    font-size: 11px;
    color: #334155;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    background-color: #ffffff;
    border-radius: 3px;
    color: #334155;
    font-size: 11px;
    font-weight: 600;
}

/* Sleek Buttons */
QPushButton {
    background-color: #0f172a;
    color: #ffffff;
    border: 1px solid #0f172a;
    padding: 5px 12px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 11px;
    min-height: 16px;
}

QPushButton:hover {
    background-color: #1e293b;
    border-color: #1e293b;
}

QPushButton:pressed {
    background-color: #334155;
}

QPushButton:disabled {
    background-color: #f1f5f9;
    color: #94a3b8;
    border: 1px solid #e2e8f0;
}

/* Secondary Button - Subtle Clean Border */
QPushButton#secondaryBtn {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
}
QPushButton#secondaryBtn:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}
QPushButton#secondaryBtn:pressed {
    background-color: #f1f5f9;
}

/* Danger Button */
QPushButton#dangerBtn {
    background-color: #ef4444;
    color: #ffffff;
    border: 1px solid #dc2626;
}
QPushButton#dangerBtn:hover {
    background-color: #dc2626;
}

/* Success Button */
QPushButton#successBtn {
    background-color: #10b981;
    color: #ffffff;
    border: 1px solid #059669;
}
QPushButton#successBtn:hover {
    background-color: #059669;
}

/* Input Fields & Combos */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    min-height: 18px;
    selection-background-color: #e2e8f0;
    selection-color: #0f172a;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2563eb;
    background-color: #ffffff;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
    border: 1px solid #cbd5e1;
    padding: 3px;
    font-size: 11px;
}

/* Compact High-Readability Table */
QTableWidget, QTableView {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    color: #1e293b;
    gridline-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 11px;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
}

QTableWidget::item {
    padding: 3px 6px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #eff6ff;
    color: #1d4ed8;
    font-weight: 600;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 5px 6px;
    border: none;
    border-bottom: 1px solid #cbd5e1;
    border-right: 1px solid #f1f5f9;
    font-weight: 700;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* Minimalist Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #f8fafc;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar:horizontal {
    border: none;
    background-color: #f8fafc;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-width: 24px;
}

/* Progress Bar */
QProgressBar {
    background-color: #f1f5f9;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    text-align: center;
    font-weight: 600;
    font-size: 10px;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #0f172a;
    border-radius: 3px;
}

/* Text Edit / Logs */
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    font-family: 'Consolas', 'Cascadia Code', 'Courier New', monospace;
    font-size: 11px;
    padding: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    font-size: 11px;
    min-height: 22px;
}

/* Tooltips */
QToolTip {
    background-color: #0f172a;
    color: #ffffff;
    border: 1px solid #0f172a;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 10px;
}

/* Metric Display Cards */
QLabel#cardTitle {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel#cardValue {
    color: #0f172a;
    font-size: 17px;
    font-weight: 700;
}

QLabel#metricTitle {
    color: #64748b;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel#metricValue {
    color: #0f172a;
    font-size: 12px;
    font-weight: 700;
}
"""
