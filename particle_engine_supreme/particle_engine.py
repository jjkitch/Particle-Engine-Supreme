# particle_engine_supreme/particle_engine.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRectF, QRect, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QRadialGradient, QCursor

from particle_engine_supreme.particle_emitter import ParticleEmitter
from particle_engine_supreme.particle_presets import EFFECT_PRESETS
from particle_engine_supreme.particle_behaviors import(
    MouseInteractionBehavior,
    TurbulenceBehavior,
    OrbitBehavior,
    VortexBehavior,
    AttractionBehavior
)
from particle_engine_supreme.particle_utilities import interpolate_curve

try:
    import pymunk
    PYMUNK_AVAILABLE = True
except ImportError:
    PYMUNK_AVAILABLE = False


class VisualEffectLayer(QWidget):
    def __init__(self, parent, physics_engine=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMouseTracking(False)
        
        self.particles = []
        self.emitters = []
        self.physics_engine = physics_engine
        self.global_behaviors = []

        self.global_wind = 0.0
        self.global_gravity = 0.0
        
        self.mouse_behavior = None
        self.last_mouse_pos = (0, 0)
        self.mouse_pressed = False
        
        if self.physics_engine and PYMUNK_AVAILABLE:
            self._setup_collision_handler()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_loop)
        

    def _setup_collision_handler(self):
        """Setup collision callbacks using pymunk 7+ API."""
        def on_begin(arbiter, space, data):
            particle_shape = next((s for s in arbiter.shapes if hasattr(s, 'particle_data')), None)
            if particle_shape:
                p = particle_shape.particle_data
                s = p.get("settings", {})
                if s.get("on_collide_effect"):
                    x, y = p["x"], p["y"]
                    if arbiter.contact_point_set.points:
                        pt = arbiter.contact_point_set.points[0].point_a
                        x, y = pt.x, pt.y
                    self.trigger_sub_emitter(s["on_collide_effect"], x, y)
            return True
        
        self.physics_engine.space.on_collision(
            collision_type_a=1,
            collision_type_b=2,
            begin=on_begin
        )

    def enable_mouse_interaction(self, mode="attract", strength=1.0, radius=300, 
                                 falloff="smooth", click_only=False):
        """
        Enable mouse interaction globally for all particles.
        """
        if self.mouse_behavior in self.global_behaviors:
            self.global_behaviors.remove(self.mouse_behavior)
            
        self.mouse_behavior = MouseInteractionBehavior(mode, strength, radius, falloff, click_only)
        self.mouse_click_only = click_only
        self.add_global_behavior(self.mouse_behavior)
    
    def disable_mouse_interaction(self):
        """Disable global mouse interaction."""
        if self.mouse_behavior in self.global_behaviors:
            self.global_behaviors.remove(self.mouse_behavior)
        self.mouse_behavior = None
    
    def set_mouse_mode(self, mode):
        """Change mouse interaction mode dynamically."""
        if self.mouse_behavior:
            self.mouse_behavior.mode = mode

    def update_mouse_state(self, pos, pressed):
        """
        Manually update mouse state from external source (e.g. parent overlay).
        This allows interaction without blocking mouse events from reaching UI below.
        """
        self.last_mouse_pos = (pos.x(), pos.y())
        self.mouse_pressed = pressed
        if self.mouse_behavior:
            self.mouse_behavior.update_mouse(pos.x(), pos.y(), pressed)
    
    def mouseMoveEvent(self, event):
        self.update_mouse_state(event.pos(), self.mouse_pressed)
    
    def mousePressEvent(self, event):
        self.update_mouse_state(event.pos(), True)
    
    def mouseReleaseEvent(self, event):
        self.update_mouse_state(event.pos(), False)

    def add_emitter(self, preset, target, **kwargs):
        full_settings = {}
        if preset in EFFECT_PRESETS:
            full_settings.update(EFFECT_PRESETS[preset])
        full_settings.update(kwargs)

        if "duration" in full_settings:
            d = full_settings["duration"]
            if d > 0 and d < 60:
                full_settings["duration"] = int(d * 60)
        
        emitter = ParticleEmitter(preset, target, overrides=full_settings)
        self.emitters.append(emitter)
        
        for beh in full_settings.get("behaviors", []):
            
            if beh == "turbulence":
                emitter.behaviors.append(TurbulenceBehavior(
                    strength=full_settings.get("turbulence_strength", 1.0),
                    frequency=full_settings.get("turbulence_freq", 0.1)
                ))
                
            elif beh == "orbit":
                emitter.behaviors.append(OrbitBehavior(
                    speed=full_settings.get("orbit_speed", 0.05)
                ))

            elif beh == "vortex":
                emitter.behaviors.append(VortexBehavior(
                    strength=full_settings.get("vortex_strength", 2.0),
                    radius=full_settings.get("vortex_radius", 300.0),
                    center_pos=full_settings.get("vortex_center", (0,0))
                ))

            elif beh == "attraction":
                emitter.behaviors.append(AttractionBehavior(
                    strength=full_settings.get("attraction_strength", 0.5),
                    radius=full_settings.get("attraction_radius", 200.0),
                    center_pos=full_settings.get("vortex_center", (0,0)) 
                ))
            
            elif beh == "mouse_interaction":
                self.enable_mouse_interaction(
                    mode=full_settings.get("mouse_mode", "attract"),
                    strength=full_settings.get("mouse_strength", 1.0),
                    radius=full_settings.get("mouse_radius", 300),
                    falloff=full_settings.get("mouse_falloff", "smooth"),
                    click_only=full_settings.get("mouse_click_only", False)
                )
        
        if not self.timer.isActive():
            self.timer.start(16)

    def add_global_behavior(self, behavior):
        """Add a behavior that affects all particles."""
        self.global_behaviors.append(behavior)
    
    def set_global_forces(self, wind, gravity):
        """High-performance setter for global environment."""
        self.global_wind = wind
        self.global_gravity = gravity

    def trigger_sub_emitter(self, preset_name, x, y):
        """Trigger a one-time burst effect."""
        e = ParticleEmitter(
            preset_name,
            QRect(int(x), int(y), 1, 1),
            overrides={"interval": 1, "collides": False}
        )
        
        for _ in range(e.settings.get("count", 1)):
            e._spawn_single(self, self.particles)

    def burst_at(self, x, y, effect="splash"):
        """Create particle burst at position."""
        self.trigger_sub_emitter(effect, x, y)

    def _update_loop(self):
        """Main update loop."""
        dt = 1.0 / 60.0
        
        try:
            global_pos = QCursor.pos()
            local_pos = self.mapFromGlobal(global_pos)
            self.update_mouse_state(local_pos, self.mouse_pressed)
        except Exception:
            pass

        if self.physics_engine:
            self.physics_engine.step(dt)
        
        self.emitters = [e for e in self.emitters if e.active or len(self.particles) > 0]

        if not self.particles and not self.emitters:
            self.timer.stop()

        for e in self.emitters:
            if e.active:
                e.emit(self, self.particles)

        self._update_particles(dt)
        
        self.update()

    def _update_particles(self, dt):
        """Update all particles - OPTIMIZED with flattened data access."""
        active = []
        w, h = self.width(), self.height()
        
        for p in self.particles:
            s = p["settings"]
            p["life"] += 1
            progress = p["life"] / p["max_life"]
            
            if p["shape"] == "image":
                rows = p["sprite_rows"]
                cols = p["sprite_cols"]
                if rows > 1 or cols > 1:
                    p["anim_frame"] += p.get("anim_speed", 1.0)
            
            self._apply_visual_curves(p, progress)
            
            for behavior in p["emitter"].behaviors:
                behavior.apply(p, dt, self)
            
            for behavior in self.global_behaviors:
                behavior.apply(p, dt, self)
            
            if "body" in p:
                pos = p["body"].position
                p["x"], p["y"] = pos.x, pos.y
                p["rotation"] = math.degrees(p["body"].angle)
                
                if p.get("accumulates"):
                    vel = p["body"].velocity
                    speed = math.sqrt(vel.x**2 + vel.y**2)
                    
                    if speed < 5: 
                        if p["life"] > 200:
                            p["size"] -= 0.05
                            if p["size"] <= 0:
                                self.physics_engine.space.remove(p["body"], p["shape"])
                                continue
                    else:
                        p["life"] = max(0, p["life"] - 1)
            else:
                spawn_x = p.get("spawn_x", p["x"])
                spawn_y = p.get("spawn_y", p["y"])
                dx = p["x"] - spawn_x
                dy = p["y"] - spawn_y
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq)

                if dist > 0.1:
                    rad_accel = p["radial_accel"]
                    if rad_accel != 0:
                        p["vx"] += (dx / dist) * rad_accel
                        p["vy"] += (dy / dist) * rad_accel

                    tan_accel = p["tangential_accel"]
                    if tan_accel != 0:
                        p["vx"] += -(dy / dist) * tan_accel
                        p["vy"] += (dx / dist) * tan_accel

                p["vy"] += p["gravity"] + self.global_gravity
                p["vx"] += p["wind"] + self.global_wind
                
                drag = p["drag"]
                if drag > 0:
                    p["vx"] *= (1.0 - drag)
                    p["vy"] *= (1.0 - drag)
                
                p["x"] += p["vx"]
                p["y"] += p["vy"]

                if p["wall_bounce"]:
                    bounce_factor = p["bounce_factor"]
                    
                    if p["x"] < 0:
                        p["x"] = 0
                        p["vx"] *= -bounce_factor
                    elif p["x"] > w:
                        p["x"] = w
                        p["vx"] *= -bounce_factor
                    
                    if p["y"] < 0:
                        p["y"] = 0
                        p["vy"] *= -bounce_factor
                    elif p["y"] > h:
                        p["y"] = h
                        p["vy"] *= -bounce_factor
                
                if p["align_rotation"]:
                    p["rotation"] = math.degrees(math.atan2(p["vy"], p["vx"]))
                else:
                    p["rotation"] += p["spin"]

            if p.get("trail") is not None:
                p["trail"].append(QPointF(p["x"], p["y"])) 
                
                max_trail = p["trail_length"]
                if len(p["trail"]) > max_trail:
                    p["trail"] = p["trail"][-max_trail:]
            
            if (p["y"] > h + 200 or p["y"] < -200 or 
                p["x"] < -200 or p["x"] > w + 200):
                if "body" in p:
                    self.physics_engine.space.remove(p["body"], p["shape"])
                continue

            if p["life"] >= p["max_life"] and not p.get("accumulates"):
                if s.get("on_death_effect"):
                    self.trigger_sub_emitter(s["on_death_effect"], p["x"], p["y"])
                
                if "body" in p:
                    self.physics_engine.space.remove(p["body"], p["shape"])
                continue

            active.append(p)
        
        self.particles = active

    def _apply_visual_curves(self, particle, progress):
        """Apply interpolated curves to particle properties."""
        s = particle["settings"]
        
        if "scale_curve" in s:
            scale_val = interpolate_curve(s["scale_curve"], progress)
            if isinstance(scale_val, QColor):
                scale = (scale_val.red() + scale_val.green() + scale_val.blue()) / (3.0 * 255.0)
            else:
                scale = float(scale_val)
            particle["size"] = particle["size_base"] * scale
        
        base_color = particle["color"]
        if particle["emitter"].color_curve:
            color_val = interpolate_curve(particle["emitter"].color_curve, progress)
            if isinstance(color_val, QColor):
                base_color = color_val
        
        alpha = 255
        if "alpha_curve" in s:
            alpha_val = interpolate_curve(s["alpha_curve"], progress)
            if isinstance(alpha_val, QColor):
                alpha = alpha_val.alpha()
            else:
                alpha = int(float(alpha_val))
        
        final_color = QColor(base_color)
        final_color.setAlpha(alpha)
        particle["draw_color"] = final_color

    def paintEvent(self, event):
        """Render all particles."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        for p in self.particles:
            self._draw_particle(painter, p)

    def _draw_particle(self, painter, p):
        """Draw a single particle - OPTIMIZED with flattened data."""
        s = p["settings"]
        
        if p.get("trail") and len(p["trail"]) > 1:
            t_width = p["trail_width"]
            t_alpha = p["trail_opacity"]
            
            c = p["draw_color"]
            trail_color = QColor(c.red(), c.green(), c.blue(), t_alpha)
            
            painter.setPen(QPen(trail_color, t_width, Qt.PenStyle.SolidLine, 
                              Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            
            painter.drawPolyline(p["trail"])
        
        if p["blend_mode"] == "add":
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        else:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.PenStyle.NoPen)
        
        painter.save()
        painter.translate(p["x"], p["y"])
        painter.rotate(p["rotation"])
        
        sz = p["size"]
        stretch = p["stretch_factor"]
        
        if stretch != 1.0 and p["shape"] in ["circle", "rect", "image"]:
            speed = math.sqrt(p["vx"]**2 + p["vy"]**2)
            if speed > 0.1:
                painter.scale(stretch, 1.0 / stretch)
        
        offset = -sz / 2
        
        shape = p["shape"]
        
        if shape == "image":
            self._draw_image_particle(painter, p, sz, offset)
        elif shape == "text":
            self._draw_text_particle(painter, p, sz, offset)
        elif shape == "rect":
            painter.setBrush(p["draw_color"])
            painter.drawRect(QRectF(offset, offset, sz, sz))
        elif shape == "star":
            self._draw_star_particle(painter, p, sz)
        elif shape == "bubble":
            self._draw_bubble_particle(painter, p, sz)
        else:
            painter.setBrush(p["draw_color"])
            painter.drawEllipse(QRectF(offset, offset, sz, sz))
        
        painter.restore()

    def _draw_image_particle(self, painter, p, sz, offset):
        """Draw image-based particle with Sprite Sheet support."""
        pix = p["emitter"].cached_pixmap
        if pix and not pix.isNull():
            painter.setOpacity(p["draw_color"].alpha() / 255.0)
            target_color = p["draw_color"]
            
            rows = p["sprite_rows"]
            cols = p["sprite_cols"]
            
            if rows > 1 or cols > 1:
                total_frames = rows * cols
                current_frame = int(p["anim_frame"]) % total_frames
                
                row = current_frame // cols
                col = current_frame % cols
                
                frame_w = pix.width() / cols
                frame_h = pix.height() / rows
                
                source_rect = QRectF(col * frame_w, row * frame_h, frame_w, frame_h)
                target_rect = QRectF(offset, offset, sz, sz)
                
                painter.drawPixmap(target_rect, pix, source_rect)
            else:
                if p["tint_image"]:
                    target_rect = QRectF(offset, offset, sz, sz)
                    
                    if rows > 1 or cols > 1:
                        painter.drawPixmap(target_rect, pix, source_rect)
                    else:
                        painter.drawPixmap(target_rect, pix, QRectF(pix.rect()))
                    
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    painter.fillRect(target_rect, p["draw_color"])
                    
                    if p["blend_mode"] == "add":
                        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
                    else:
                        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

    def _draw_text_particle(self, painter, p, sz, offset):
        """Draw text-based particle."""
        if sz < 1:
            return
        painter.setPen(p["draw_color"])
        font = painter.font()
        font.setPixelSize(int(sz))
        painter.setFont(font)
        painter.drawText(
            QRectF(offset, offset, sz * 2, sz * 2),
            Qt.AlignmentFlag.AlignCenter,
            p.get("char", "0")
        )

    def _draw_star_particle(self, painter, p, sz):
        """Draw star-shaped particle with dynamic points."""
        from PyQt6.QtGui import QPolygonF
        
        num_points = p["star_points"]
        num_points = max(3, num_points)
        
        points = []
        total_vertices = num_points * 2
        
        for i in range(total_vertices):
            angle = math.radians(i * (360 / total_vertices) - 90)
            radius = sz / 2 if i % 2 == 0 else sz / 4
            
            points.append(QPointF(
                math.cos(angle) * radius,
                math.sin(angle) * radius
            ))
        
        painter.setBrush(p["draw_color"])
        painter.drawPolygon(QPolygonF(points))

    def _draw_bubble_particle(self, painter, p, sz):
        """Draw bubble with gradient."""
        gradient = QRadialGradient(0, -sz/4, sz)
        color = p["draw_color"]
        gradient.setColorAt(0, QColor(255, 255, 255, color.alpha()))
        gradient.setColorAt(0.4, QColor(color.red(), color.green(), color.blue(), color.alpha()))
        gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QRectF(-sz/2, -sz/2, sz, sz))