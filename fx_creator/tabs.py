# fx_creator/tabs.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, 
    QComboBox, QPushButton, QScrollArea, QCheckBox, QDoubleSpinBox, QLabel
)
from constants import TOOLTIPS, KNOWN_PRESETS, EMITTER_TYPES
from components import CurveWidget

class PhysicsTab(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.layout = QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QVBoxLayout(content)

        emit_group = QGroupBox("Emitter / Spawn Area")
        emit_layout = QVBoxLayout()
        
        origin_layout = QHBoxLayout()
        origin_label = QLabel("Quick Spawn Origin:")
        self.combo_origin = QComboBox()
        self.combo_origin.addItems(["Custom / Manual", "Screen Center", "Top Edge", "Bottom Edge", "Left Edge", "Right Edge"])
        self.combo_origin.currentTextChanged.connect(self.editor.apply_spawn_origin)
        origin_layout.addWidget(origin_label)
        origin_layout.addWidget(self.combo_origin)
        emit_layout.addLayout(origin_layout)

        self.editor.check_custom_rect = self.editor.create_checkbox("Use Custom Spawn Region", emit_layout, key="use_custom_rect")
        
        self.editor.add_dropdown("Emitter Shape", "emitter_type", EMITTER_TYPES, emit_layout)

        e_form = QFormLayout()
        self.editor.add_to_form("X Position:", "emitter_x", "int", 400, e_form)
        self.editor.add_to_form("Y Position:", "emitter_y", "int", 300, e_form)
        self.editor.add_to_form("Width:", "emitter_w", "int", 10, e_form)
        self.editor.add_to_form("Height:", "emitter_h", "int", 10, e_form)
        emit_layout.addLayout(e_form)
        
        self.editor.add_section("Geometry Specifics", [
            ("cone_direction", "float", 0.0),
            ("cone_angle", "float", 45.0),
            ("grid_rows", "int", 3),
            ("grid_cols", "int", 3),
            ("spiral_speed", "float", 0.5),
        ], emit_layout)
        
        emit_group.setLayout(emit_layout)
        self.form_layout.addWidget(emit_group)

        self.editor.add_section("Spawn & Life", [
            ("count", "int", 5),
            ("interval", "int", 2),
            ("start_delay", "int", 0),
            ("duration", "float", -1.0), 
            ("life_min", "int", 60),
            ("life_max", "int", 100),
        ], self.form_layout)

        self.editor.inputs["count"].setRange(0, 20) 
        self.editor.inputs["interval"].setRange(1, 600)

        self.editor.add_section("Physics Motion", [
            ("gravity", "float", 0.5),
            ("wind", "float", 0.0),
            ("drag", "float", 0.05),
            ("inherit_velocity", "float", 0.0),
            ("speed_min", "float", 2.0),
            ("speed_max", "float", 5.0),
            ("angle_min", "float", 0.0),
            ("angle_max", "float", 360.0),
        ], self.form_layout)
        
        self.editor.add_section("Advanced Forces", [
            ("radial_accel", "float", 0.0),
            ("tangential_accel", "float", 0.0),
            ("align_rotation", "bool", False),
        ], self.form_layout)
        
        self.editor.add_section("Collision & Interaction", [
            ("collides", "bool", False),
            ("elasticity", "float", 0.7),
            ("friction", "float", 0.5),
            ("accumulate", "bool", False),
            ("wall_bounce", "bool", False),
            ("bounce_factor", "float", 0.8),
        ], self.form_layout)

        sub_group = QGroupBox("Sub-Effects")
        sub_layout = QFormLayout()
        
        self.editor.combo_spawn = QComboBox()
        self.editor.combo_spawn.addItems(KNOWN_PRESETS)
        self.editor.combo_spawn.currentTextChanged.connect(self.editor.refresh_effect)
        self.editor.combo_spawn.setToolTip(TOOLTIPS["on_spawn_effect"])
        self.editor.inputs["on_spawn_effect"] = self.editor.combo_spawn
        sub_layout.addRow("On Spawn:", self.editor.combo_spawn)

        self.editor.combo_collide = QComboBox()
        self.editor.combo_collide.addItems(KNOWN_PRESETS)
        self.editor.combo_collide.currentTextChanged.connect(self.editor.refresh_effect)
        self.editor.combo_collide.setToolTip(TOOLTIPS["on_collide_effect"])
        self.editor.inputs["on_collide_effect"] = self.editor.combo_collide
        sub_layout.addRow("On Collide:", self.editor.combo_collide)

        self.editor.combo_death = QComboBox()
        self.editor.combo_death.addItems(KNOWN_PRESETS)
        self.editor.combo_death.currentTextChanged.connect(self.editor.refresh_effect)
        self.editor.combo_death.setToolTip(TOOLTIPS["on_death_effect"])
        self.editor.inputs["on_death_effect"] = self.editor.combo_death
        sub_layout.addRow("On Death:", self.editor.combo_death)

        sub_group.setLayout(sub_layout)
        self.form_layout.addWidget(sub_group)
        self.form_layout.addStretch()
        
        scroll.setWidget(content)
        self.layout.addWidget(scroll)


class VisualsTab(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.layout = QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QVBoxLayout(content)

        self.editor.add_dropdown("Shape", "shape", 
                         ["circle", "rect", "star", "bubble", "smoke", "image", "text"], 
                         self.form_layout)

        self.editor.add_section("Star Settings", [("star_points", "int", 5)], self.form_layout)

        self.editor.add_section("Dimensions", [
            ("size_min", "float", 3.0), ("size_max", "float", 10.0),
            ("spin_min", "float", -5.0), ("spin_max", "float", 5.0),
            ("stretch_factor", "float", 1.0),
        ], self.form_layout)

        self.editor.inputs["size_min"].setRange(0.1, 200.0)
        self.editor.inputs["size_max"].setRange(0.1, 300.0)
        self.editor.inputs["stretch_factor"].setRange(0.1, 10.0)

        self.editor.add_section("Auto-Fade (Generates Alpha Curve)", [
            ("fade_in_time", "int", 0),
            ("fade_out_time", "int", 0),
        ], self.form_layout)

        img_group = QGroupBox("Image Settings (if Shape=Image)")
        img_layout = QFormLayout()
        
        self.editor.image_combo = QComboBox()
        self.editor.load_image_assets() 
        self.editor.image_combo.currentTextChanged.connect(self.editor.refresh_effect)
        self.editor.image_combo.setToolTip(TOOLTIPS["image_path"])
        img_layout.addRow("Image File:", self.editor.image_combo)

        browse_btn = QPushButton("Browse Custom Image...")
        browse_btn.clicked.connect(self.editor.browse_image)
        img_sub_layout = QHBoxLayout()
        img_sub_layout.addWidget(self.editor.image_combo)
        img_sub_layout.addWidget(browse_btn)
        img_layout.addRow("Image File:", img_sub_layout)
        
        self.editor.check_tint = QCheckBox()
        self.editor.check_tint.setChecked(True)
        self.editor.check_tint.stateChanged.connect(self.editor.refresh_effect)
        self.editor.check_tint.setToolTip(TOOLTIPS["tint_image"])
        img_layout.addRow("Tint Image?", self.editor.check_tint)
        img_group.setLayout(img_layout)
        self.form_layout.addWidget(img_group)
        
        self.editor.add_section("Sprite Animation (Grid)", [
            ("sprite_rows", "int", 1), ("sprite_cols", "int", 1),
            ("anim_speed", "float", 1.0), ("random_start_frame", "bool", False),
        ], self.form_layout)

        self.editor.add_section("Text Settings", [("text_chars", "text", "01")], self.form_layout)
        self.editor.add_dropdown("Blend Mode", "blend_mode", ["normal", "add"], self.form_layout)
        self.editor.add_section("Trails", [
            ("trail_length", "int", 0), 
            ("trail_width", "int", 2), 
            ("trail_opacity", "int", 100),
        ], self.form_layout)

        self.editor.inputs["trail_length"].setRange(0, 5) 
        self.editor.inputs["trail_width"].setRange(1, 5)
        self.editor.inputs["trail_opacity"].setRange(0, 255)

        self.form_layout.addStretch()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

class CurvesTab(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.layout = QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QVBoxLayout(content)

        self.editor.add_section("Spawn Colors", [("color", "text", "#ffffff")], self.form_layout)
        self.editor.add_section("Color Variance", [
            ("hue_variance", "float", 0.0), ("sat_variance", "float", 0.0), ("val_variance", "float", 0.0),
        ], self.form_layout)

        self.editor.wid_scale_curve = CurveWidget(
            "Scale over Life", mode="float", default_vals=[0.5, 1.0, 1.5, 1.0, 0.0],
            parent_callback=self.editor.refresh_effect, tooltip=TOOLTIPS["scale_curve"]
        )
        self.form_layout.addWidget(self.editor.wid_scale_curve)

        self.editor.wid_alpha_curve = CurveWidget(
            "Alpha over Life", mode="int", default_vals=[0, 255, 255, 200, 0],
            parent_callback=self.editor.refresh_effect, tooltip=TOOLTIPS["alpha_curve"]
        )
        self.form_layout.addWidget(self.editor.wid_alpha_curve)

        self.editor.wid_color_curve = CurveWidget(
            "Color Transition", mode="color", default_vals=["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff"],
            parent_callback=self.editor.refresh_effect, 
            tooltip=TOOLTIPS["color_curve"],
            enable_toggle=True, dynamic_count=True
        )
        self.form_layout.addWidget(self.editor.wid_color_curve)
        
        self.form_layout.addStretch()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

class BehaviorsTab(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.layout = QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QVBoxLayout(content)

        b_group = QGroupBox("Behaviors")
        b_layout = QVBoxLayout()
        self.editor.behavior_list = []  

        add_btn = QPushButton("Add Behavior")
        add_btn.clicked.connect(self.editor.add_behavior)
        b_layout.addWidget(add_btn)

        self.editor.behaviors_container = QVBoxLayout()
        b_layout.addLayout(self.editor.behaviors_container)
        b_group.setLayout(b_layout)
        self.form_layout.addWidget(b_group)
        
        self.editor.add_section("Behavior Tuning", [
            ("turbulence_strength", "float", 0.5), ("turbulence_freq", "float", 0.05),
            ("orbit_speed", "float", 0.05), ("vortex_strength", "float", 2.0),
            ("vortex_radius", "float", 300.0),
        ], self.form_layout)

        self.editor.add_section("Vortex/Attraction", [
            ("vortex_center_x", "int", 400), ("vortex_center_y", "int", 300),
            ("attraction_strength", "float", 0.5), ("attraction_radius", "float", 200.0),
        ], self.form_layout)

        self.form_layout.addStretch()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)