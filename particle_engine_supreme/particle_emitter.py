# particle_engine_supreme/particle_emitter.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

import os
import math
import random

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtCore import QRect

from particle_engine_supreme.particle_presets import EFFECT_PRESETS
from particle_engine_supreme.particle_data import DEFAULT_PROFILE
from particle_engine_supreme.particle_behaviors import (
    TurbulenceBehavior, OrbitBehavior, MouseInteractionBehavior, VortexBehavior
)

INTERNAL_ASSETS_DIR = "" # Add path to your particle images

try:
    import pymunk
    PYMUNK_AVAILABLE = True
except ImportError:
    PYMUNK_AVAILABLE = False


class ParticleEmitter:
    def __init__(self, preset_name, target_source, overrides=None):
        self.active = True
        self.target_source = target_source
        self.preset_name = preset_name
        
        self.settings = DEFAULT_PROFILE.copy()
        preset = EFFECT_PRESETS.get(preset_name, {})
        self.settings.update(preset)
        if overrides:
            self.settings.update(overrides)

        self.color_curve = self.settings.get("color_curve")
        self.palette = [QColor(c) for c in self.settings.get("color", ["#FFFFFF"])]
        
        self.cached_pixmap = None
        if self.settings.get("shape") == "image":
            self._load_image()

        self.behaviors = []
        self._setup_behaviors()

        self.tick_timer = 0

        self.duration = self.settings.get("duration", -1)
        

    def _load_image(self):
        """Load and cache particle image."""
        raw_path = self.settings.get("image_path", "")
        final_path = raw_path
        
        if INTERNAL_ASSETS_DIR:
            config_path = str(INTERNAL_ASSETS_DIR / raw_path)
            if os.path.exists(config_path):
                final_path = config_path
        
        pix = QPixmap(final_path)
        if not pix.isNull():
            self.cached_pixmap = pix
        else:
            print(f"[PARTICLE] Failed to load: {final_path}")

    def _setup_behaviors(self):
        """Initialize particle behaviors."""
        behavior_names = self.settings.get("behaviors", [])
        
        for name in behavior_names:
            if name == "turbulence":
                self.behaviors.append(TurbulenceBehavior(
                    strength=self.settings.get("turbulence_strength", 0.3),
                    frequency=self.settings.get("turbulence_freq", 0.05)
                ))
            elif name == "orbit":
                self.behaviors.append(OrbitBehavior(
                    speed=self.settings.get("orbit_speed", 0.05)
                ))
            elif name == "vortex":
                vortex_center = self.settings.get("vortex_center", (0, 0))
                vortex_strength = self.settings.get("vortex_strength", 2.0)
                vortex_radius = self.settings.get("vortex_radius", 300)
                
                self.behaviors.append(VortexBehavior(
                    center=vortex_center,
                    strength=vortex_strength,
                    radius=vortex_radius
                ))
            
            elif name == "mouse_interaction":
                self.behaviors.append(MouseInteractionBehavior(
                    mode=self.settings.get("mouse_mode", "attract"),
                    strength=self.settings.get("mouse_strength", 1.0),
                    radius=self.settings.get("mouse_radius", 300),
                    falloff=self.settings.get("mouse_falloff", "smooth"),
                    click_only=self.settings.get("mouse_click_only", False)
                ))

    def get_spawn_pos(self, layer):
        """Advanced spawning logic for different shapes."""
        if isinstance(self.target_source, QRect):
            rect = self.target_source
        elif isinstance(self.target_source, QWidget):
            try:
                p = self.target_source.mapToGlobal(self.target_source.rect().topLeft())
                local = layer.mapFromGlobal(p)
                rect = QRect(local, self.target_source.size())
            except: rect = layer.rect()
        else: rect = layer.rect()

        mode = self.settings.get("emitter_type", "rect")
        x, y = 0, 0
        
        if mode == "rect":
            x = random.uniform(rect.left(), rect.right())
            y = random.uniform(rect.top(), rect.bottom())
            
        elif mode in ["circle", "ring"]:
            cx = rect.center().x()
            cy = rect.center().y()
            max_r = min(rect.width(), rect.height()) / 2
            angle = random.uniform(0, 2 * math.pi)
            
            if mode == "ring":
                r = max_r
            else:
                r = max_r * math.sqrt(random.random())
                
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            
        elif mode == "line":
            t = random.random()
            x = rect.left() + t * rect.width()
            y = rect.top() + t * rect.height()
            
        elif mode == "point":
            x = rect.center().x()
            y = rect.center().y()
        
        elif mode == "cone":
            cx = rect.center().x()
            cy = rect.center().y()
            x, y = cx, cy
            
        elif mode == "grid":
            grid_rows = self.settings.get("grid_rows", 3)
            grid_cols = self.settings.get("grid_cols", 3)
            
            cell_w = rect.width() / grid_cols
            cell_h = rect.height() / grid_rows
            
            col = random.randint(0, grid_cols - 1)
            row = random.randint(0, grid_rows - 1)
            
            x = rect.left() + col * cell_w + random.uniform(0, cell_w)
            y = rect.top() + row * cell_h + random.uniform(0, cell_h)
        
        elif mode == "spiral":
            if not hasattr(self, '_spiral_angle'):
                self._spiral_angle = 0
            
            cx = rect.center().x()
            cy = rect.center().y()
            max_r = min(rect.width(), rect.height()) / 2
            
            spiral_speed = self.settings.get("spiral_speed", 0.5)
            self._spiral_angle += spiral_speed
            
            r = (self._spiral_angle % (2 * math.pi)) / (2 * math.pi) * max_r
            
            x = cx + r * math.cos(self._spiral_angle)
            y = cy + r * math.sin(self._spiral_angle)
            
        return x, y, rect

    def emit(self, layer, particle_list):
        """Spawn new particles."""
        if not self.active:
            return
        
        if self.duration != -1:
            self.duration -= 1
            if self.duration <= 0:
                self.active = False
                return
        
        if getattr(self, 'start_delay', 0) > 0:
            self.start_delay -= 1
            return
            
        self.tick_timer += 1
        if self.tick_timer < self.settings.get("interval", 1):
            return
        self.tick_timer = 0
        
        for _ in range(self.settings.get("count", 1)):
            self._spawn_single(layer, particle_list)

    def _spawn_single(self, layer, particle_list):
        s = self.settings
        x, y, rect = self.get_spawn_pos(layer)
        
        emitter_type = s.get("emitter_type", "rect")
        
        if emitter_type == "cone":
            cone_direction = s.get("cone_direction", 0)
            cone_angle = s.get("cone_angle", 45)
            
            half_spread = cone_angle / 2
            angle_deg = cone_direction + random.uniform(-half_spread, half_spread)
            angle_rad = math.radians(angle_deg)
        else:
            angle_rad = math.radians(random.uniform(s.get("angle_min", 0), s.get("angle_max", 360)))
        
        speed = random.uniform(s["speed_min"], s["speed_max"])
        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed
        
        inherit_velocity = s.get("inherit_velocity", 0.0)
        if inherit_velocity > 0 and isinstance(self.target_source, QWidget):
            if hasattr(self, '_last_widget_pos'):
                try:
                    current_pos = self.target_source.mapToGlobal(self.target_source.rect().center())
                    widget_vx = (current_pos.x() - self._last_widget_pos[0]) * inherit_velocity
                    widget_vy = (current_pos.y() - self._last_widget_pos[1]) * inherit_velocity
                    vx += widget_vx
                    vy += widget_vy
                except:
                    pass
            
            try:
                pos = self.target_source.mapToGlobal(self.target_source.rect().center())
                self._last_widget_pos = (pos.x(), pos.y())
            except:
                pass
        
        base_color = random.choice(self.palette)
        h_var = s.get("hue_variance", 0.0)
        s_var = s.get("sat_variance", 0.0)
        v_var = s.get("val_variance", 0.0)
        
        if h_var > 0 or s_var > 0 or v_var > 0:
            h = base_color.hueF()
            sat = base_color.saturationF()
            val = base_color.valueF()
            
            h = (h + random.uniform(-h_var, h_var)) % 1.0
            sat = max(0.0, min(1.0, sat + random.uniform(-s_var, s_var)))
            val = max(0.0, min(1.0, val + random.uniform(-v_var, v_var)))
            
            spawn_color = QColor.fromHsvF(h, sat, val, base_color.alphaF())
        else:
            spawn_color = base_color

        size = random.uniform(s["size_min"], s["size_max"])
        
        alpha_curve = s.get("alpha_curve")
        if not alpha_curve:
            fade_in = s.get("fade_in_time", 0)
            fade_out = s.get("fade_out_time", 0)
            
            if fade_in > 0 or fade_out > 0:
                life_span = random.randint(s.get("life_min", 50), s.get("life_max", 100))
                curve = []
                
                if fade_in > 0:
                    for i in range(int(fade_in)):
                        curve.append(int(255 * (i / fade_in)))
                
                hold_time = life_span - fade_in - fade_out
                if hold_time > 0:
                    curve.extend([255] * int(hold_time))
                
                if fade_out > 0:
                    for i in range(int(fade_out)):
                        curve.append(int(255 * (1 - i / fade_out)))
                
                s = s.copy()
                s["alpha_curve"] = curve

        p = {
            "emitter": self,
            "settings": s,
            "layer": layer,
            
            "gravity": s.get("gravity", 0.5),
            "wind": s.get("wind", 0.0),
            "drag": s.get("drag", 0.0),
            "radial_accel": s.get("radial_accel", 0.0),
            "tangential_accel": s.get("tangential_accel", 0.0),
            "wall_bounce": s.get("wall_bounce", False),
            "bounce_factor": s.get("bounce_factor", 0.8),
            "align_rotation": s.get("align_rotation", False),
            
            "shape": s.get("shape", "circle"),
            "blend_mode": s.get("blend_mode", "normal"),
            "sprite_rows": s.get("sprite_rows", 1),
            "sprite_cols": s.get("sprite_cols", 1),
            "tint_image": s.get("tint_image", True),
            "star_points": s.get("star_points", 5),
            
            "stretch_factor": s.get("stretch_factor", 1.0),
            
            "trail_length": s.get("trail_length", 0),
            "trail_width": s.get("trail_width", 2),
            "trail_opacity": s.get("trail_opacity", 100),
            
            "color": spawn_color,
            "size_base": size,
            "size": size,
            "rotation": random.uniform(0, 360),
            "spin": random.uniform(s.get("spin_min", 0), s.get("spin_max", 0)),
            "life": 0,
            "max_life": random.randint(s.get("life_min", 50), s.get("life_max", 100)),
            "accumulates": s.get("accumulate", False),
            "char": random.choice(s.get("text_chars", "0")) if s.get("shape") == "text" else None,
            "trail": [] if s.get("trail_length", 0) > 0 else None,
            
            "anim_frame": 0.0 if s.get("sprite_rows", 1) > 1 else 0,
            "anim_speed": s.get("anim_speed", 1.0),
            
            "spawn_x": x,
            "spawn_y": y,
            "x": x, 
            "y": y, 
            "vx": vx, 
            "vy": vy
        }
        
        if s.get("random_start_frame"):
            total_frames = s.get("sprite_rows", 1) * s.get("sprite_cols", 1)
            p["anim_frame"] = random.randint(0, total_frames - 1)

        if layer.physics_engine and PYMUNK_AVAILABLE and s.get("collides"):
            body, shape = layer.physics_engine.spawn_particle(
                x, y, 
                (vx * 60, vy * 60), 
                size / 2, 
                mass=1.0,
                physics_profile={
                    "friction": s.get("friction", 0.5), 
                    "elasticity": s.get("elasticity", 0.5)
                }
            )
            shape.particle_data = p
            p["body"] = body
            p["shape"] = shape

        if s.get("on_spawn_effect"):
            layer.trigger_sub_emitter(s["on_spawn_effect"], x, y)

        particle_list.append(p)