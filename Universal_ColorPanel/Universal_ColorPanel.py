# Universal Color Panel – Full Production Build
# Nuke / PySide (1 / 2 / 6) / Python 3
# Author: Nitin Kashyap

import nuke
import os
# ------------------------------------------------------------
# PySide Compatibility (Nuke 9 → 17)
# ------------------------------------------------------------

try:
    # PySide6 (Nuke 15+ some builds)
    from PySide6 import QtWidgets, QtGui, QtCore
    from PySide6.QtWidgets import QLabel, QCheckBox
    from PySide6.QtCore import Qt
    PYSIDE_VERSION = 6

except ImportError:
    try:
        # PySide2 (Nuke 10 → 15)
        from PySide2 import QtWidgets, QtGui, QtCore
        from PySide2.QtWidgets import QLabel, QCheckBox
        from PySide2.QtCore import Qt
        PYSIDE_VERSION = 2

    except ImportError:
        # PySide (Qt4 – Nuke 9)
        from PySide import QtGui, QtCore
        QtWidgets = QtGui
        QLabel = QtGui.QLabel
        QCheckBox = QtGui.QCheckBox
        Qt = QtCore.Qt
        PYSIDE_VERSION = 1


# ------------------------------------------------------------

WINDOW_NAME = "Universal_ColorPanel"
INSTALLER_VERSION = "1.0.0"

# ------------------------------------------------------------
# Utils
# ------------------------------------------------------------

def rgba_to_nuke_color(color):
    return (
        (color.red() << 24) |
        (color.green() << 16) |
        (color.blue() << 8) |
        255
    )

def selected_nodes():
    try:
        return nuke.selectedNodes()
    except Exception:
        return []

def group_selected_nodes(node):
    """Apply color to selected nodes inside Group if present"""
    if node.Class() != "Group":
        return [node]

    try:
        node.begin()
        inside = nuke.selectedNodes()
        node.end()
        return inside if inside else [node]
    except Exception:
        return [node]

def color_from_hex(text):
    if not text:
        return None

    t = text.strip()
    c = QtGui.QColor(t)
    if c.isValid():
        return c

    if t.startswith("#"):
        t = t[1:]

    if len(t) == 3:
        r, g, b = t
        t = f"{r}{r}{g}{g}{b}{b}"

    if len(t) == 6:
        return QtGui.QColor("#" + t)

    return None

# ------------------------------------------------------------
# Styles
# ------------------------------------------------------------

APP_STYLE = """
QWidget {
    background-color: #1c1c1c;
    color: #e0e0e0;
    font-size: 11px;
}
QLineEdit {
    background-color: #2f2f2f;
    border: 1px solid #1c1c1c;
    border-radius: 4px;
    padding: 6px;
    color: #f0f0f0;
}
"""

BUTTON_STYLE = """
QPushButton {
    background-color: #444444;
    border: 1px solid #333333;
    border-radius: 14px;
    padding: 10px;
    color: white;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover { background-color: #d4aa0c; }
QPushButton:pressed { background-color: #117a05; }
"""

COLOR_BUTTON_STYLE = """
QPushButton {
    border-radius: 4px;
    border: 1px solid #111;
}
QPushButton:hover { border: 1px solid #ddd; }
"""

# ------------------------------------------------------------
# Button Helpers
# ------------------------------------------------------------

def shadow_button(text, callback, width=None):
    btn = QtWidgets.QPushButton(text)
    btn.setStyleSheet(BUTTON_STYLE)
    btn.clicked.connect(callback)

    if width:
        btn.setFixedWidth(width)

    shadow = QtWidgets.QGraphicsDropShadowEffect(btn)
    shadow.setBlurRadius(6)
    shadow.setOffset(2, 2)
    shadow.setColor(QtGui.QColor(0, 0, 0, 160))
    btn.setGraphicsEffect(shadow)

    return btn

class ColorButton(QtWidgets.QPushButton):
    def __init__(self, panel, rgb):
        super().__init__()
        self.panel = panel
        self.color = QtGui.QColor(*rgb)

        self.setFixedSize(72, 28)
        self.setStyleSheet(
            COLOR_BUTTON_STYLE +
            f"QPushButton {{ background-color: {self.color.name()}; }}"
        )

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setOffset(2, 2)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        self.clicked.connect(self.apply_color)

    def apply_color(self):
        for node in selected_nodes():
            for target in group_selected_nodes(node):
                target["tile_color"].setValue(
                    rgba_to_nuke_color(self.color)
                )

        if self.panel.auto_close.isChecked():
            self.panel.close()

# ------------------------------------------------------------
# Main Panel
# ------------------------------------------------------------

class Universal_ColorPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Universal Color Panel v1.0.0 | | Author: Nitin Kashyap")
        self.setObjectName(WINDOW_NAME)
        self.resize(390, 980)
        self.setStyleSheet(APP_STYLE)


        #self.setWindowTitle("Universal Color Panel – Nitin Kashyap color:white; font-weight:bold; font-size:16px;")


        self.clipboard_color = None
        self.build_ui()

    def build_ui(self):
        main = QtWidgets.QVBoxLayout(self)
        main.setSpacing(10)

        # ---- Color Grids ----

        label = QLabel("Universal Color")
        label.setStyleSheet("font-weight:bold; font-size:20px; color:white")
        main.addWidget(label)


        # -------- Divider --------
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setStyleSheet("color:#333;")
        main.addWidget(divider)


        main.addLayout(self.color_grid(self.nuke_colors()))
        label = QLabel("Colors = (216)")
        label.setStyleSheet("font-weight:bold; font-size:20px; color:white")
        main.addWidget(label)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(520)
        

        container = QtWidgets.QWidget()
        container.setLayout(self.color_grid(self.web_safe_colors()))
        scroll.setWidget(container)
        main.addWidget(scroll)

        self.add_divider(main)


        # ---- HEX ----
        label = QLabel("HEX / Named Color")
        label.setStyleSheet("font-weight:bold; font-size:14px; color:white")
        main.addWidget(label)
        hex_row = QtWidgets.QHBoxLayout()
        self.hex_input = QtWidgets.QLineEdit("#0c7800")
        hex_row.addWidget(self.hex_input)
        main.addLayout(hex_row)

        apply_row = QtWidgets.QHBoxLayout()
        apply_row.addStretch()
        apply_row.addWidget(shadow_button("Apply", self.apply_hex_color, 80))
        main.addLayout(apply_row)

        self.add_divider(main)

        main.addWidget(shadow_button("Custom Color Picker", self.pick_custom_color))

        self.add_divider(main)

        # ---- Copy / Paste ----
        copy_btn = shadow_button("Copy", self.copy_color)
        paste_btn = shadow_button("Paste", self.paste_color)

        cp_row = QtWidgets.QHBoxLayout()
        cp_row.addWidget(copy_btn)
        cp_row.addStretch()
        cp_row.addWidget(paste_btn)
        main.addLayout(cp_row)

        self.add_divider(main)

        main.addWidget(shadow_button("Restore Default", self.restore_color))

        self.add_divider(main)

        #main.addWidget(shadow_button("Github / Tools Update", self.open_website))

        github_btn = shadow_button("Github / Page", self.open_website)
        
        github_btn.setStyleSheet("""
        QPushButton {
            background-color: #333333;
            border: 1px solid #333333;
            border-radius: 16px;
            padding: 10px;
            color: white;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #696968;
        }
        QPushButton:pressed {
            background-color: #008009;
        }
        """)
        
        main.addWidget(github_btn)

        self.add_divider(main)

        # -------- Divider --------
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setStyleSheet("color:#333;")
        main.addWidget(divider)

        # -------- Footer --------
        footer = QtWidgets.QHBoxLayout()

        version_label = QtWidgets.QLabel(
            f"Version {INSTALLER_VERSION} | Nuke 10 → 17 | Author: Nitin Kashyap"
        )
        version_label.setStyleSheet(
            "color:#bfbfbf; font-size:12px; font-weight:500;"
        )

        footer.addWidget(version_label)
        footer.addStretch()

        close_btn = shadow_button("Close", self.close, 220)
        close_btn.setStyleSheet("""
        QPushButton {
            background-color: #400101;
            border: 1px solid #1f1f1f;
            border-radius: 16px;
            padding: 10px;
            color: white;
            font-weight: bold;
            font-size: 13px;
            letter-spacing: 1px;
        }
        QPushButton:hover { background-color: #400101; }
        QPushButton:pressed { background-color: #187302; }
        """)
        footer.addWidget(close_btn)
        main.addLayout(footer)

        self.auto_close = QCheckBox("Close window after color pick")
        self.auto_close.setStyleSheet("""
            QCheckBox {
            
                font-weight: bold;
                font-size: 14px;
                color: white;
            }
        """)
        
        main.addWidget(self.auto_close)


    # --------------------------------------------------------

    def add_divider(self, layout):
        d = QtWidgets.QFrame()
        d.setFrameShape(QtWidgets.QFrame.HLine)
        d.setStyleSheet("color:#333;")
        layout.addWidget(d)

    def section(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet("font-weight:bold; padding-top:4px;")
        return lbl

    def color_grid(self, colors):
        grid = QtWidgets.QGridLayout()
        for i, rgb in enumerate(colors):
            grid.addWidget(ColorButton(self, rgb), i // 8, i % 8)
        return grid

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------

    def apply_hex_color(self):
        color = color_from_hex(self.hex_input.text())
        if not color:
            return
        for n in selected_nodes():
            for t in group_selected_nodes(n):
                t["tile_color"].setValue(rgba_to_nuke_color(color))

    def pick_custom_color(self):
        c = QtWidgets.QColorDialog.getColor(parent=self)
        if c.isValid():
            for n in selected_nodes():
                for t in group_selected_nodes(n):
                    t["tile_color"].setValue(rgba_to_nuke_color(c))

    def copy_color(self):
        n = selected_nodes()
        if n:
            self.clipboard_color = n[0]["tile_color"].value()

    def paste_color(self):
        if self.clipboard_color is None:
            return
        for n in selected_nodes():
            for t in group_selected_nodes(n):
                t["tile_color"].setValue(self.clipboard_color)

    def restore_color(self):
        for n in selected_nodes():
            for t in group_selected_nodes(n):
                t["tile_color"].setValue(0)

    def open_website(self):
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl("https://github.com/Nitinkashyap96")
        )

    # --------------------------------------------------------

    def nuke_colors(self):
        return [
            (192,128,64),(180,200,240),(100,120,200),
            (180,120,200),(220,220,120),(200,80,120),
            (120,220,120),(40,180,40),(0,0,140),
            (230,230,230),(180,40,40),(240,240,0)
        ]

    def web_safe_colors(self):
        steps = [0x00,0x33,0x66,0x99,0xCC,0xFF]
        return [(r,g,b) for r in steps for g in steps for b in steps]

# ------------------------------------------------------------
# Show
# ------------------------------------------------------------

def show():
    for w in QtWidgets.QApplication.allWidgets():
        if w.objectName() == WINDOW_NAME:
            w.close()
    panel = Universal_ColorPanel()
    panel.show()
    return panel

#show()
