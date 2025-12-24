# fx_creator/creator.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

import sys
import os
import random
import pprint
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, 
    QPushButton, QLineEdit, QGroupBox, QSlider, QCheckBox,
    QTabWidget, QFileDialog
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor
from shiboken6 import isValid

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from particle_engine_supreme import GlobalEffectOverlay
from particle_engine_supreme import EFFECT_PRESETS
from particle_engine_supreme import DEFAULT_PROFILE

from constants import TOOLTIPS
from tabs import PhysicsTab, VisualsTab, CurvesTab, BehaviorsTab

PARTICLES_DIR = "" # Add path to your particle images


class ParticleEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Particle Engine Supreme - FX Creator App")
        self.resize(1600, 950)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #aaa;")

        self.inputs = {}
        self.global_env_behavior = None
        
        self.setup_canvas_area()
        self.overlay = GlobalEffectOverlay(self.canvas_widget, use_physics=True)
        self.canvas_widget.setMouseTracking(True)
        
        self.setup_controls_area() 
        
        self.refresh_effect()

    def setup_canvas_area(self):
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        self.canvas_widget = QWidget()
        self.canvas_widget.setStyleSheet("background-color: #1a1a1a;")
        self.canvas_widget.setMinimumSize(800, 600)
        
        bg_controls = QHBoxLayout()
        bg_label = QLabel("Canvas Color:")
        self.bg_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_slider.setRange(0, 359)
        self.bg_slider.setValue(0)
        self.bg_slider.valueChanged.connect(self.update_canvas_color)
        bg_controls.addWidget(bg_label)
        bg_controls.addWidget(self.bg_slider)

        env_group = QGroupBox("Global Environment (Preview)")
        env_layout = QFormLayout()
        
        self.global_wind = QDoubleSpinBox()
        self.global_wind.setRange(-5.0, 5.0)
        self.global_wind.setSingleStep(0.1)
        self.global_wind.setValue(0.0)
        self.global_wind.valueChanged.connect(self.update_global_environment)
        
        self.global_gravity = QDoubleSpinBox()
        self.global_gravity.setRange(-2.0, 2.0)
        self.global_gravity.setSingleStep(0.1)
        self.global_gravity.setValue(0.0)
        self.global_gravity.valueChanged.connect(self.update_global_environment)
        
        env_layout.addRow("Global Wind:", self.global_wind)
        env_layout.addRow("Global Gravity:", self.global_gravity)
        env_group.setLayout(env_layout)

        btn_spawn = QPushButton("🧱 Spawn Physics Obstacle")
        btn_spawn.clicked.connect(self.spawn_random_obstacle)
        
        btn_clear = QPushButton("🧹 Clear Obstacles")
        btn_clear.clicked.connect(self.clear_obstacles)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(btn_spawn)
        btns_layout.addWidget(btn_clear)

        left_layout.addWidget(self.canvas_widget, stretch=3)
        left_layout.addWidget(env_group)
        left_layout.addLayout(bg_controls)
        left_layout.addLayout(btns_layout)
        
        self.main_layout.addWidget(left_container, stretch=3)

    def setup_controls_area(self):
        """Clean Setup using Modular Tabs"""
        tabs = QTabWidget()
        
        self.tab_physics = PhysicsTab(self)
        
        tabs.addTab(self.tab_physics, "Physics")
        tabs.addTab(VisualsTab(self), "Visuals")
        tabs.addTab(CurvesTab(self), "Curves")
        tabs.addTab(BehaviorsTab(self), "Behaviors")

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.addWidget(tabs)
        right_layout.addWidget(self.status_label)

        preset_group = QGroupBox("Load Preset")
        preset_layout = QVBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("None")
        self.preset_combo.addItems(list(EFFECT_PRESETS.keys()))
        self.preset_combo.currentTextChanged.connect(self.load_builtin_preset)
        preset_layout.addWidget(self.preset_combo)
        preset_group.setLayout(preset_layout)
        right_layout.addWidget(preset_group)

        btn_reset = QPushButton("🧹 Reset to Clean Slate")
        btn_reset.setStyleSheet("background-color: #8B0000; color: white; padding: 10px;")
        btn_reset.clicked.connect(self.reset_to_clean_slate)
        right_layout.addWidget(btn_reset)

        btn_refresh = QPushButton("🔄 Force Refresh")
        btn_refresh.clicked.connect(self.refresh_effect)
        right_layout.addWidget(btn_refresh)

        btn_export = QPushButton("💾 Print Config to Console")
        btn_export.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        btn_export.clicked.connect(self.export_code)
        right_layout.addWidget(btn_export)

        btn_save = QPushButton("Save Preset")
        btn_save.clicked.connect(self.save_preset)
        right_layout.addWidget(btn_save)

        btn_load = QPushButton("Load Preset")
        btn_load.clicked.connect(self.load_preset)
        right_layout.addWidget(btn_load)

        self.main_layout.addWidget(right_container, stretch=1)

    def apply_spawn_origin(self, mode):
        """Auto-calculate emitter rect based on screen position."""
        if mode == "Custom / Manual":
            return
            
        w = self.canvas_widget.width()
        h = self.canvas_widget.height()
        
        x, y, ew, eh = 0, 0, 10, 10
        
        if mode == "Screen Center":
            x = (w // 2) - 5
            y = (h // 2) - 5
            ew, eh = 10, 10
        elif mode == "Top Edge":
            x, y = 0, 0
            ew, eh = w, 10
        elif mode == "Bottom Edge":
            x, y = 0, h - 10
            ew, eh = w, 10
        elif mode == "Left Edge":
            x, y = 0, 0
            ew, eh = 10, h
        elif mode == "Right Edge":
            x, y = w - 10, 0
            ew, eh = 10, h
            
        self.inputs["emitter_x"].setValue(x)
        self.inputs["emitter_y"].setValue(y)
        self.inputs["emitter_w"].setValue(ew)
        self.inputs["emitter_h"].setValue(eh)
        
        self.check_custom_rect.setChecked(True)

    def update_global_environment(self):
        """Apply global environment using the OPTIMIZED native system."""
        wind = self.global_wind.value()
        grav = self.global_gravity.value()
        self.overlay.set_global_environment(wind, grav)

    def update_canvas_color(self, value):
        color = QColor.fromHsv(value, 200, 50) 
        self.canvas_widget.setStyleSheet(f"background-color: {color.name()};")

    def spawn_random_obstacle(self):
        w, h = self.canvas_widget.width(), self.canvas_widget.height()
        x = random.randint(50, w - 100)
        y = random.randint(50, h - 100)
        obstacle = QPushButton("🧱", self.canvas_widget)
        obstacle.setStyleSheet("background: #555; border: 2px solid #888; font-size: 20px;")
        obstacle.setGeometry(x, y, random.randint(80, 400), random.randint(10, 60))
        obstacle.show()
        self.overlay.add_collision_widget(obstacle)

    def clear_obstacles(self):
        for child in self.canvas_widget.findChildren(QPushButton):
            if child.text() == "🧱":
                self.overlay.remove_collision_widget(child)
                child.deleteLater()
        self.refresh_effect()

    def add_to_form(self, label, key, dtype, default, layout):
        widget = None
        if dtype == "int":
            widget = QSpinBox()
            widget.setRange(-9999, 9999)
            widget.setValue(default)
            widget.valueChanged.connect(self.refresh_effect)
        elif dtype == "float":
            widget = QDoubleSpinBox()
            widget.setRange(-9999.0, 9999.0)
            widget.setSingleStep(0.1)
            widget.setValue(default)
            widget.valueChanged.connect(self.refresh_effect)
        if key in TOOLTIPS: widget.setToolTip(TOOLTIPS[key])
        layout.addRow(label, widget)
        self.inputs[key] = widget

    def add_dropdown(self, label, key, items, layout):
        group = QGroupBox(label)
        l = QVBoxLayout()
        combo = QComboBox()
        combo.addItems(items)
        combo.currentTextChanged.connect(self.refresh_effect)
        if key in TOOLTIPS: combo.setToolTip(TOOLTIPS[key])
        l.addWidget(combo)
        group.setLayout(l)
        layout.addWidget(group)
        self.inputs[key] = combo

    def add_section(self, title, items, parent_layout):
        group = QGroupBox(title)
        layout = QFormLayout()
        for name, dtype, default in items:
            widget = None
            if dtype == "int":
                widget = QSpinBox()
                widget.setRange(-9999, 9999)
                widget.setValue(default)
                widget.valueChanged.connect(self.refresh_effect)
            elif dtype == "float":
                widget = QDoubleSpinBox()
                widget.setRange(-9999.0, 9999.0)
                widget.setSingleStep(0.1)
                widget.setValue(default)
                widget.valueChanged.connect(self.refresh_effect)
            elif dtype == "text":
                widget = QLineEdit()
                widget.setText(default)
                widget.editingFinished.connect(self.refresh_effect)
            elif dtype == "bool":
                widget = QCheckBox()
                widget.setChecked(default)
                widget.stateChanged.connect(self.refresh_effect)
            
            if name in TOOLTIPS: widget.setToolTip(TOOLTIPS[name])
            layout.addRow(name.replace("_", " ").title() + ":", widget)
            self.inputs[name] = widget
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_checkbox(self, label, layout, key=None):
        box = QCheckBox(label)
        box.stateChanged.connect(self.refresh_effect)
        lookup = key if key else label
        if lookup in TOOLTIPS: 
            box.setToolTip(TOOLTIPS[lookup])
        layout.addWidget(box)
        return box

    def load_image_assets(self):
        self.image_combo.addItem("None")
        if PARTICLES_DIR.exists():
            for f in os.listdir(str(PARTICLES_DIR)):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.image_combo.addItem(f)
        else:
            self.image_combo.addItem("Assets/Particles not found")
            
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            if file_path not in [self.image_combo.itemText(i) for i in range(self.image_combo.count())]:
                self.image_combo.addItem(file_path)
            self.image_combo.setCurrentText(file_path)
            self.refresh_effect()

    def add_behavior(self):
        combo = QComboBox()
        combo.addItems(["turbulence", "orbit", "vortex", "attraction", "mouse_interaction"])
        combo.currentTextChanged.connect(self.refresh_effect)
        
        params_widget = QWidget()
        params_layout = QFormLayout(params_widget)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.remove_behavior(combo, params_widget))
        
        row = QHBoxLayout()
        row.addWidget(combo)
        row.addWidget(remove_btn)
        self.behaviors_container.addLayout(row)
        self.behaviors_container.addWidget(params_widget)
        
        self.behavior_list.append((combo, params_widget))
        self.update_behavior_params(combo)
        combo.currentTextChanged.connect(lambda: self.update_behavior_params(combo))
        self.refresh_effect()

    def update_behavior_params(self, combo):
        type_ = combo.currentText()
        params_widget = next(pw for c, pw in self.behavior_list if c == combo)
        layout = params_widget.layout()
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                keys_to_remove = [k for k, v in self.inputs.items() if v is widget]
                for k in keys_to_remove: 
                    del self.inputs[k]
                widget.setParent(None)
                widget.deleteLater()
        
        if type_ == "turbulence":
            self.add_to_form("Strength:", f"{id(combo)}_turb_strength", "float", 0.5, layout)
            self.add_to_form("Frequency:", f"{id(combo)}_turb_freq", "float", 0.05, layout)
        elif type_ == "vortex":
            self.add_to_form("Strength:", f"{id(combo)}_vort_strength", "float", 2.0, layout)
            self.add_to_form("Radius:", f"{id(combo)}_vort_radius", "float", 300.0, layout)
        elif type_ == "orbit":
            self.add_to_form("Speed:", f"{id(combo)}_orbit_speed", "float", 0.05, layout)
        elif type_ == "attraction":
            self.add_to_form("Strength:", f"{id(combo)}_attr_strength", "float", 0.5, layout)
            self.add_to_form("Radius:", f"{id(combo)}_attr_radius", "float", 200.0, layout)
        elif type_ == "mouse_interaction":
            mode_combo = QComboBox()
            mode_combo.addItems(["attract", "repel", "orbit", "vortex", "avoid", "tunnel", "chaos"])
            mode_combo.setCurrentText("attract")
            mode_combo.currentTextChanged.connect(self.refresh_effect)
            layout.addRow("Mode:", mode_combo)
            self.inputs[f"{id(combo)}_mouse_mode"] = mode_combo
            
            strength_sb = QDoubleSpinBox()
            strength_sb.setRange(0.1, 10.0)
            strength_sb.setSingleStep(0.1)
            strength_sb.setValue(1.0)
            strength_sb.valueChanged.connect(self.refresh_effect)
            layout.addRow("Strength:", strength_sb)
            self.inputs[f"{id(combo)}_mouse_strength"] = strength_sb
            
            radius_sb = QDoubleSpinBox()
            radius_sb.setRange(50.0, 1000.0)
            radius_sb.setValue(300.0)
            radius_sb.valueChanged.connect(self.refresh_effect)
            layout.addRow("Radius:", radius_sb)
            self.inputs[f"{id(combo)}_mouse_radius"] = radius_sb
            
            falloff_combo = QComboBox()
            falloff_combo.addItems(["smooth", "linear", "quadratic", "inverse"])
            falloff_combo.setCurrentText("smooth")
            falloff_combo.currentTextChanged.connect(self.refresh_effect)
            layout.addRow("Falloff:", falloff_combo)
            self.inputs[f"{id(combo)}_mouse_falloff"] = falloff_combo
            
            click_cb = QCheckBox("Click Only (Hold to Activate)")
            click_cb.setChecked(False)
            click_cb.stateChanged.connect(self.refresh_effect)
            layout.addRow(click_cb)
            self.inputs[f"{id(combo)}_mouse_click_only"] = click_cb
        
        self.refresh_effect()

    def remove_behavior(self, combo, params_widget):
        for i in reversed(range(self.behaviors_container.count())):
            item = self.behaviors_container.itemAt(i)
            layout = item.layout()
            if layout is not None:
                for j in range(layout.count()):
                    if layout.itemAt(j).widget() is combo:
                        while layout.count():
                            sub_item = layout.takeAt(0)
                            if sub_item.widget(): sub_item.widget().deleteLater()
                        layout.deleteLater()
                        self.behaviors_container.takeAt(i).layout().deleteLater()
                        break
        
        layout = params_widget.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                keys_to_remove = [k for k, v in self.inputs.items() if v is widget]
                for k in keys_to_remove: 
                    del self.inputs[k]

                widget.deleteLater()
        params_widget.deleteLater()
        self.behavior_list = [(c, pw) for c, pw in self.behavior_list if c != combo]
        combo.deleteLater()
        self.refresh_effect()

    def refresh_effect(self):
        self.overlay.clear_effects()
        self.update_global_environment()
        
        try:
            config = self.get_current_config()
            if config.get("count", 0) <= 0: 
                return
            
            if self.check_custom_rect.isChecked():
                x = self.inputs["emitter_x"].value()
                y = self.inputs["emitter_y"].value()
                w = self.inputs["emitter_w"].value()
                h = self.inputs["emitter_h"].value()
                target = QRect(x, y, w, h)
            else:
                target = self.canvas_widget

            self.overlay.add_custom_effect(target=target, **config)
            for child in self.canvas_widget.findChildren(QPushButton):
                if child.text() == "🧱": self.overlay.add_collision_widget(child)
            self.status_label.setText("Effect refreshed.")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def get_current_config(self):
        cfg = {}
        for key, widget in self.inputs.items():
            if widget is None or not isValid(widget): 
                continue
            if any(key.startswith(f"{id(combo)}_") for combo, _ in self.behavior_list): 
                continue
            
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                val = widget.value()
                val = round(val, 4)
                if key == "duration": 
                    cfg[key] = -1 if val < 0 else int(val * 60)
                else: 
                    cfg[key] = val
            elif isinstance(widget, QCheckBox): cfg[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                val = widget.currentText()
                cfg[key] = None if val in ("None", "") else val
            elif isinstance(widget, QLineEdit):
                txt = widget.text()
                if key == "color": 
                    cfg[key] = [c.strip() for c in txt.split(",") if c.strip()]
                else: 
                    cfg[key] = txt
        
        selected_image = self.image_combo.currentText()
        if selected_image and selected_image not in ["None", "Assets/Particles not found"]:
            if os.path.isabs(selected_image): 
                cfg["image_path"] = selected_image
            else: 
                cfg["image_path"] = str((PARTICLES_DIR / selected_image).resolve())
        else: 
            cfg["image_path"] = ""
        
        if cfg.get("shape") == "image" and not cfg.get("image_path"): 
            cfg["shape"] = "circle"

        cfg["tint_image"] = self.check_tint.isChecked()
        
        behaviors = []
        for combo, pw in self.behavior_list:
            type_ = combo.currentText()
            behaviors.append(type_)
            prefix = f"{id(combo)}_"
            for key, widget in self.inputs.items():
                if key.startswith(prefix) and widget is not None and not isValid(widget):
                    raw_sub_key = key[len(prefix):]
                    if type_ == "mouse_interaction": 
                        final_key = raw_sub_key
                    else:
                        mapping = {
                            "turb_strength": "turbulence_strength", "turb_freq": "turbulence_freq",
                            "vort_strength": "vortex_strength", "vort_radius": "vortex_radius",
                            "attr_strength": "attraction_strength", "attr_radius": "attraction_radius",
                        }
                        final_key = mapping.get(raw_sub_key, raw_sub_key)
                    
                    if isinstance(widget, QCheckBox): 
                        val = widget.isChecked()
                    elif isinstance(widget, QComboBox): 
                        val = widget.currentText()
                    else: 
                        val = widget.value()

                        if isinstance(val, float):
                            val = round(val, 4)

                    cfg[final_key] = val
        cfg["behaviors"] = behaviors
        
        if "vortex" in behaviors:
            cfg["vortex_center"] = (cfg.get("vortex_center_x", 400), cfg.get("vortex_center_y", 300))
        
        range_pairs = [("life_min", "life_max"), ("speed_min", "speed_max"), ("size_min", "size_max"), ("spin_min", "spin_max"), ("angle_min", "angle_max")]
        for min_key, max_key in range_pairs:
            if min_key in cfg and max_key in cfg and cfg[min_key] > cfg[max_key]: 
                cfg[max_key] = cfg[min_key]
        
        cfg["scale_curve"] = self.wid_scale_curve.get_values()
        cfg["alpha_curve"] = [int(x) for x in self.wid_alpha_curve.get_values()]
        colors = self.wid_color_curve.get_values()
        cfg["color_curve"] = colors if colors else None
        
        return cfg

    def reset_inputs_to_defaults(self):
        """Hard reset of all input widgets to DEFAULT_PROFILE values."""
        config = DEFAULT_PROFILE
        
        for key, widget in self.inputs.items():
            if widget is None or isValid(widget):
                continue
            
            if any(key.startswith(f"{id(combo)}_") for combo, _ in self.behavior_list):
                continue

            val = config.get(key)
            
            if val is not None:
                if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    if key == "duration" and val == -1:
                        widget.setValue(-1.0)
                    else:
                        widget.setValue(float(val) if isinstance(widget, QDoubleSpinBox) else int(val))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(val))
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(str(val) if val else "None")
                elif isinstance(widget, QLineEdit):
                    if key == "color" and isinstance(val, list):
                        widget.setText(", ".join(val))
                    else:
                        widget.setText(str(val))
            else:
                if isinstance(widget, QCheckBox): widget.setChecked(False)
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)): widget.setValue(0)
                elif isinstance(widget, QComboBox): widget.setCurrentIndex(0)
                elif isinstance(widget, QLineEdit): widget.setText("")

    def reset_to_clean_slate(self):
        self.clear_all_dynamic()
        self.reset_inputs_to_defaults()
        self.load_builtin_preset(None)
        self.refresh_effect()

    def clear_all_dynamic(self):
        while self.behavior_list:
            combo, pw = self.behavior_list.pop()
            self.remove_behavior(combo, pw)

        for curve_wid in [self.wid_scale_curve, self.wid_alpha_curve, self.wid_color_curve]:
            while len(curve_wid.inputs) > 2: curve_wid.remove_point()
            if curve_wid.toggle_cb: curve_wid.toggle_cb.setChecked(True)

        self.image_combo.blockSignals(True)
        self.image_combo.setCurrentText("None")
        self.image_combo.blockSignals(False)
        self.check_custom_rect.setChecked(False)

    def load_builtin_preset(self, preset_name):
        self.clear_all_dynamic()
        
        self.reset_inputs_to_defaults()
        
        if not preset_name or preset_name == "None": 
            return
        
        config = EFFECT_PRESETS.get(preset_name, {}).copy()
        config.setdefault("use_custom_rect", False)
        
        self.set_config_from_preset(config)

    def save_preset(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Preset", "", "JSON (*.json)")
        if file_path:
            with open(file_path, 'w') as f: 
                json.dump(self.get_current_config(), f, indent=4)

    def load_preset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Preset", "", "JSON (*.json)")
        if file_path:
            with open(file_path, 'r') as f:
                self.reset_inputs_to_defaults()
                self.set_config_from_preset(json.load(f))
            self.refresh_effect()

    def set_config_from_preset(self, config):
        if "vortex_center" in config and isinstance(config["vortex_center"], (list, tuple)):
            vx, vy = config["vortex_center"]
            if "vortex_center_x" in self.inputs: self.inputs["vortex_center_x"].setValue(int(vx))
            if "vortex_center_y" in self.inputs: self.inputs["vortex_center_y"].setValue(int(vy))

        for key, val in config.items():
            if key in self.inputs:
                widget = self.inputs[key]
                if widget is None or not isValid(widget): continue
                
                if isinstance(widget, (QSpinBox, QDoubleSpinBox)): 
                    widget.setValue(float(val) if isinstance(widget, QDoubleSpinBox) else int(val))
                elif isinstance(widget, QCheckBox): 
                    widget.setChecked(bool(val))
                elif isinstance(widget, QComboBox): 
                    widget.setCurrentText(str(val))
                elif isinstance(widget, QLineEdit): 
                    if key == "color" and isinstance(val, list):
                        widget.setText(", ".join(val))
                    else:
                        widget.setText(str(val))

        if "image_path" in config:
            path = config["image_path"]
            if path not in [self.image_combo.itemText(i) for i in range(self.image_combo.count())]: 
                self.image_combo.addItem(path)
            self.image_combo.setCurrentText(path)
        if "tint_image" in config: 
            self.check_tint.setChecked(bool(config["tint_image"]))
        
        def set_curve(widget, key):
            if key in config:
                vals = config[key]
                if vals is None: 
                    if widget.toggle_cb: widget.toggle_cb.setChecked(False)
                else:
                    while len(widget.inputs) < len(vals): 
                        widget.add_point()
                    while len(widget.inputs) > len(vals): 
                        widget.remove_point()
                    for i, inp in enumerate(widget.inputs):
                        if isinstance(inp, (QSpinBox, QDoubleSpinBox)): 
                            inp.setValue(vals[i])
                        elif isinstance(inp, QPushButton):
                            hex_c = vals[i]
                            inp.setStyleSheet(f"background-color: {hex_c}; border: 1px solid #555;")
                            inp.setProperty("hex_color", hex_c)
                    if widget.toggle_cb: widget.toggle_cb.setChecked(True)

        set_curve(self.wid_scale_curve, "scale_curve")
        set_curve(self.wid_alpha_curve, "alpha_curve")
        set_curve(self.wid_color_curve, "color_curve")

        if "behaviors" in config:
            for beh in config["behaviors"]:
                self.add_behavior()
                new_combo, new_pw = self.behavior_list[-1]
                new_combo.setCurrentText(beh)
                self.update_behavior_params(new_combo)
                
                param_map = {}
                if beh == "turbulence":
                    param_map = {
                        "turbulence_strength": "turb_strength", 
                        "turbulence_freq": "turb_freq"
                    }
                elif beh == "vortex":
                    param_map = {
                        "vortex_strength": "vort_strength", 
                        "vortex_radius": "vort_radius"
                    }
                elif beh == "orbit":
                    param_map = {
                        "orbit_speed": "orbit_speed"
                    }
                elif beh == "attraction":
                    param_map = {
                        "attraction_strength": "attr_strength", 
                        "attraction_radius": "attr_radius"
                    }
                elif beh == "mouse_interaction":
                    param_map = {
                        "mouse_mode": "mouse_mode",
                        "mouse_strength": "mouse_strength",
                        "mouse_radius": "mouse_radius",
                        "mouse_falloff": "mouse_falloff",
                        "mouse_click_only": "mouse_click_only"
                    }
                
                for cfg_key, ui_suffix in param_map.items():
                    if cfg_key in config:
                        val = config[cfg_key]
                        ui_key = f"{id(new_combo)}_{ui_suffix}"
                        if ui_key in self.inputs:
                            w = self.inputs[ui_key]
                            if isinstance(w, (QSpinBox, QDoubleSpinBox)):
                                w.setValue(float(val) if isinstance(w, QDoubleSpinBox) else int(val))
                            elif isinstance(w, QCheckBox):
                                w.setChecked(bool(val))
                            elif isinstance(w, QComboBox):
                                w.setCurrentText(str(val))

    def export_code(self):
        pprint.pprint(self.get_current_config(), indent=2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParticleEditor()
    window.show()
    app.exec()