# fx_creator/components.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QPushButton, QDoubleSpinBox, QSpinBox, QColorDialog
)
from PySide6.QtGui import QColor


class CurveWidget(QWidget):
    """
    A custom widget to edit a curve.
    Now supports Toggling (Optional) and Dynamic Length (Add/Remove points).
    """
    def __init__(self, label, mode="float", default_vals=None, parent_callback=None, 
                 tooltip=None, enable_toggle=False, dynamic_count=False):
        super().__init__()
        self.mode = mode
        self.callback = parent_callback
        self.dynamic_count = dynamic_count
        self.inputs = []
        
        if tooltip:
            self.setToolTip(tooltip)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 15)
        
        header_layout = QHBoxLayout()
        lbl = QLabel(f"<b>{label}</b> (Start → End)")
        header_layout.addWidget(lbl)
        
        self.toggle_cb = None
        if enable_toggle:
            self.toggle_cb = QCheckBox("Enable")
            self.toggle_cb.setChecked(True)
            self.toggle_cb.stateChanged.connect(self._on_toggle)
            header_layout.addWidget(self.toggle_cb)
            
        layout.addLayout(header_layout)

        self.points_layout = QHBoxLayout()
        layout.addLayout(self.points_layout)
        
        if self.dynamic_count:
            btn_layout = QHBoxLayout()
            btn_add = QPushButton("+ Add Stop")
            btn_add.setFixedSize(80, 20)
            btn_add.clicked.connect(self.add_point)
            
            btn_rem = QPushButton("- Remove")
            btn_rem.setFixedSize(80, 20)
            btn_rem.clicked.connect(self.remove_point)
            
            btn_layout.addWidget(btn_add)
            btn_layout.addWidget(btn_rem)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)

        if not default_vals:
            default_vals = [1.0] * 5 if mode == "float" else ["#ffffff"] * 2
            
        if not self.dynamic_count:
            while len(default_vals) < 5:
                default_vals.append(default_vals[-1])
            default_vals = default_vals[:5]
        
        for val in default_vals:
            self._create_input(val)

    def _create_input(self, val):
        """Create a single input widget and add to layout."""
        if self.mode == "float":
            sb = QDoubleSpinBox()
            sb.setRange(0.0, 10.0)
            sb.setSingleStep(0.1)
            sb.setValue(float(val))
            sb.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            sb.valueChanged.connect(self._on_change)
            self.points_layout.addWidget(sb)
            self.inputs.append(sb)
            
        elif self.mode == "int":
            sb = QSpinBox()
            sb.setRange(0, 255)
            sb.setValue(int(val))
            sb.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            sb.valueChanged.connect(self._on_change)
            self.points_layout.addWidget(sb)
            self.inputs.append(sb)

        elif self.mode == "color":
            btn = QPushButton()
            btn.setFixedSize(40, 30)
            c = str(val)
            btn.setStyleSheet(f"background-color: {c}; border: 1px solid #555;")
            btn.setProperty("hex_color", c) 
            btn.clicked.connect(lambda checked, b=btn: self._pick_color(b))
            self.points_layout.addWidget(btn)
            self.inputs.append(btn)
    
    def add_point(self):
        """Add a new point duplicating the last value."""
        if not self.inputs:
            default = 1.0 if self.mode == "float" else "#ffffff"
        else:
            if self.mode == "color":
                default = self.inputs[-1].property("hex_color")
            else:
                default = self.inputs[-1].value()
        
        self._create_input(default)
        self._on_change()

    def remove_point(self):
        """Remove the last point (min 2)."""
        if len(self.inputs) > 2:
            widget = self.inputs.pop()
            self.points_layout.removeWidget(widget)
            widget.deleteLater()
            self._on_change()

    def _on_toggle(self):
        """Enable/Disable all inputs."""
        enabled = self.toggle_cb.isChecked()
        for inp in self.inputs:
            inp.setEnabled(enabled)
        self._on_change()

    def _on_change(self):
        if self.callback: self.callback()

    def _pick_color(self, btn):
        curr = QColor(btn.property("hex_color"))
        c = QColorDialog.getColor(curr, self, "Pick Curve Color")
        if c.isValid():
            hex_c = c.name()
            btn.setStyleSheet(f"background-color: {hex_c}; border: 1px solid #555;")
            btn.setProperty("hex_color", hex_c)
            self._on_change()

    def get_values(self):
        if self.toggle_cb and not self.toggle_cb.isChecked():
            return None
            
        if self.mode == "color":
            return [btn.property("hex_color") for btn in self.inputs]
        else:
            return [inp.value() for inp in self.inputs]