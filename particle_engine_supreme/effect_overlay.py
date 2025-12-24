# particle_engine_supreme/effect_overlay.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import Qt, QEvent, QRect
from particle_engine_supreme.particle_engine import VisualEffectLayer
from particle_engine_supreme.particle_behaviors import ForceFieldBehavior, AttractionBehavior

try:
    from particle_engine_supreme.physics_engine import PymunkPhysicsEngine
    PYMUNK_AVAILABLE = True
except ImportError:
    PYMUNK_AVAILABLE = False

class GlobalEffectOverlay(QWidget):
    """
    Enhanced overlay for full-window particle effects with physics.
    
    Usage:
        overlay = GlobalEffectOverlay(main_window, use_physics=True)
        overlay.add_global_effect("snow")
        overlay.add_target_effect(my_button, "fire")
        overlay.add_collision_widget(my_label)
    """
    
    def __init__(self, parent_window, use_physics=True):
        super().__init__(parent_window)
        
        # Make overlay transparent to mouse events
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Initialize physics engine
        self.phys_engine = None
        if use_physics and PYMUNK_AVAILABLE:
            self.phys_engine = PymunkPhysicsEngine()
        
        # Create particle layer
        self.layer = VisualEffectLayer(self, physics_engine=self.phys_engine)
        
        # Track widgets for collision
        self.tracked_widgets = []
        
        # Setup parent monitoring
        if parent_window:
            parent_window.installEventFilter(self)
            
            parent_window.setMouseTracking(True) 
            
            # Also handle the Central Widget automatically
            if isinstance(parent_window, QMainWindow) and parent_window.centralWidget():
                cw = parent_window.centralWidget()
                cw.installEventFilter(self)
                cw.setMouseTracking(True)

            self.resize(parent_window.size())
            self.layer.resize(parent_window.size())
            self.raise_()

    def set_global_environment(self, wind, gravity):
        """
        Set global wind and gravity using the high-performance native system.
        """
        self.layer.set_global_forces(wind, gravity)

    def add_collision_widget(self, widget):
        """
        Register a widget as a collision barrier for particles.
        
        Args:
            widget: QWidget to create collision box around
        """
        if not self.phys_engine:
            return
        
        if widget not in self.tracked_widgets:
            self.tracked_widgets.append(widget)
            widget.installEventFilter(self)
            self._update_collision_barrier(widget)

    def remove_collision_widget(self, widget):
        """Remove widget from collision tracking."""
        if widget in self.tracked_widgets:
            self.tracked_widgets.remove(widget)
            if self.phys_engine:
                self.phys_engine.remove_static_barrier(id(widget))

    def add_global_effect(self, effect_name, **kwargs):
        """
        Add an effect that spawns across the entire window.
        
        Args:
            effect_name: Name from EFFECT_PRESETS
            **kwargs: Override any preset settings
        
        Example:
            overlay.add_global_effect("snow", count=3, size_min=6)
        """
        self.layer.add_emitter(effect_name, self, **kwargs)

    def add_target_effect(self, target_widget, effect_name, **kwargs):
        """
        Attach an effect to a specific widget.
        
        Args:
            target_widget: QWidget to spawn particles from
            effect_name: Name from EFFECT_PRESETS
            **kwargs: Override any preset settings
        
        Example:
            overlay.add_target_effect(my_button, "fire", count=10)
        """
        self.layer.add_emitter(effect_name, target_widget, **kwargs)

    def add_custom_effect(self, target, **settings):
        """
        Create a fully custom effect.
        
        Args:
            target: Widget or QRect to spawn from (or self for global)
            **settings: All particle settings
        
        Example:
            overlay.add_custom_effect(
                self,
                count=5,
                gravity=0.3,
                color=["#ff0000", "#00ff00"],
                size_min=10,
                size_max=20,
                shape="star",
                blend_mode="add"
            )
        """
        self.layer.add_emitter("rain", target, **settings)

    def trigger_burst(self, x, y, effect="explosion", **kwargs):
        """
        Create a one-time burst effect at a position.
        
        Args:
            x, y: Position in overlay coordinates
            effect: Effect preset name
            **kwargs: Override settings
        
        Example:
            overlay.trigger_burst(100, 200, "sparkles", count=20)
        """
        self.layer.trigger_sub_emitter(effect, x, y)

    def add_force_field(self, x, y, width, height, field_type="wind", strength=0.5, angle=0):
        """
        Add a static force field zone (Wind, Gravity, Slowdown).
        
        Args:
            x, y, width, height: The zone definition (Rect).
            field_type: "wind", "attract", "repel", or "slow".
            strength: Force intensity.
            angle: Direction in degrees (for "wind" type).
        
        Returns:
            ForceFieldBehavior instance (can be used to remove later)
        """
        field = ForceFieldBehavior(x, y, width, height, field_type, strength, angle)
        self.layer.add_global_behavior(field)
        return field

    def add_attraction_point(self, x, y, strength=0.5, radius=None, widget=None):
        """
        Add a static attraction point that pulls particles toward it.
        
        Args:
            x, y: Position in overlay coordinates (or widget center if widget provided)
            strength: Pull force (0.1 = gentle, 2.0 = strong)
            radius: Maximum distance affected (None = infinite)
            widget: Optional widget to track (will follow widget center)
        
        Returns:
            AttractionBehavior instance (can be used to remove later)
        
        Examples:
            # Static attraction at position
            overlay.add_attraction_point(400, 300, strength=1.0, radius=200)
            
            # Attraction following a widget
            overlay.add_attraction_point(0, 0, strength=0.8, radius=150, widget=my_button)
        """
        if widget:
            try:
                global_pos = widget.mapToGlobal(widget.rect().center())
                local_pos = self.mapFromGlobal(global_pos)
                x, y = local_pos.x(), local_pos.y()
            except:
                pass
        
        attraction = AttractionBehavior(
            point=(x, y),
            strength=strength,
            radius=radius
        )
        
        if widget:
            attraction._tracked_widget = widget
            attraction._overlay = self
        
        self.layer.add_global_behavior(attraction)
        
        return attraction

    def update_attraction_point(self, attraction_behavior):
        """
        Update attraction point position if tracking a widget.
        Call this in your update loop if you have moving widgets.
        
        Args:
            attraction_behavior: The AttractionBehavior instance returned from add_attraction_point
        """
        if hasattr(attraction_behavior, '_tracked_widget') and attraction_behavior._tracked_widget:
            widget = attraction_behavior._tracked_widget
            try:
                global_pos = widget.mapToGlobal(widget.rect().center())
                local_pos = attraction_behavior._overlay.mapFromGlobal(global_pos)
                attraction_behavior.point = (local_pos.x(), local_pos.y())
            except:
                pass

    def clear_effects(self):
        """Remove all active emitters and particles."""
        self.layer.emitters.clear()
        self.layer.particles.clear()

        self.layer.global_behaviors.clear()
        self.layer.mouse_behavior = None
        
        if self.phys_engine:
            self.phys_engine.clear_particles()

    def pause(self):
        """Pause all particle updates."""
        self.layer.timer.stop()

    def resume(self):
        """Resume particle updates."""
        if not self.layer.timer.isActive():
            self.layer.timer.start(16)

    def set_mouse_interactive(self, enabled=True, effect="splash"):
        """Enable/disable particle bursts on mouse clicks."""
        self._click_effect_enabled = enabled
        if enabled:
            self._click_effect = effect
    
    def enable_mouse_interaction(self, mode="attract", strength=1.0, radius=300, 
                                falloff="smooth", click_only=False):
        """
        Enable advanced mouse interaction with particles.
        
        Args:
            mode: Interaction type:
                - "attract": Pull particles toward mouse
                - "repel": Push particles away from mouse
                - "orbit": Particles circle around mouse
                - "vortex": Spiral particles toward mouse
                - "avoid": Particles flee but maintain distance
                - "tunnel": Suck particles through mouse like a portal
                - "chaos": Random chaotic forces
            strength: Force multiplier (0.1 = gentle, 5.0 = extreme)
            radius: Effect radius in pixels
            falloff: Distance falloff curve:
                - "linear": Constant decrease
                - "quadratic": Faster falloff
                - "inverse": Slower falloff
                - "smooth": Smoothstep interpolation
            click_only: Only apply effect when mouse button is held
        
        Example:
            # Gentle attraction
            overlay.enable_mouse_interaction("attract", strength=0.5, radius=400)
            
            # Strong repulsion on click only
            overlay.enable_mouse_interaction("repel", strength=3.0, click_only=True)
            
            # Vortex effect
            overlay.enable_mouse_interaction("vortex", strength=2.0, radius=500)
        """
        self.layer.enable_mouse_interaction(mode, strength, radius, falloff, click_only)
    
    def disable_mouse_interaction(self):
        """Disable mouse interaction with particles."""
        self.layer.disable_mouse_interaction()
    
    def set_mouse_mode(self, mode):
        """
        Change mouse interaction mode without recreating behavior.
        
        Args:
            mode: New mode (attract, repel, orbit, vortex, avoid, tunnel, chaos)
        """
        self.layer.set_mouse_mode(mode)

    def mousePressEvent(self, event):
        """Handle mouse clicks if interactive mode enabled."""
        if hasattr(self, '_click_effect'):
            self.trigger_burst(event.pos().x(), event.pos().y(), self._click_effect)

    def _update_collision_barrier(self, widget):
        """Update physics barrier for a widget."""
        if not self.phys_engine:
            return

        if not widget.isVisible():
            self.phys_engine.remove_static_barrier(id(widget))
            return

        try:
            global_pos = widget.mapToGlobal(widget.rect().topLeft())
            local_pos = self.mapFromGlobal(global_pos)
            rect = QRect(local_pos, widget.size())
            
            self.phys_engine.add_static_barrier(id(widget), rect)
        except:
            pass

    def eventFilter(self, source, event):
        """Monitor parent window and tracked widgets."""
        input_sources = [self.parent()]
        if isinstance(self.parent(), QMainWindow) and self.parent().centralWidget():
            input_sources.append(self.parent().centralWidget())
        
        if source in input_sources:
            if event.type() == QEvent.Type.Resize and source == self.parent():
                self.resize(source.size())
                self.layer.resize(source.size())
                for w in self.tracked_widgets:
                    self._update_collision_barrier(w)
            
            elif event.type() == QEvent.Type.MouseMove:
                if hasattr(event, "globalPosition"):
                    global_pos = event.globalPosition().toPoint()
                else:
                    global_pos = event.globalPos()
                
                local_pos = self.mapFromGlobal(global_pos)
                self.layer.update_mouse_state(local_pos, self.layer.mouse_pressed)

            elif event.type() == QEvent.Type.MouseButtonPress:
                if hasattr(event, "globalPosition"):
                    global_pos = event.globalPosition().toPoint()
                else:
                    global_pos = event.globalPos()
                local_pos = self.mapFromGlobal(global_pos)
                
                self.layer.update_mouse_state(local_pos, True)
                
                if getattr(self, '_click_effect_enabled', False):
                    self.layer.burst_at(local_pos.x(), local_pos.y(), getattr(self, '_click_effect', 'splash'))

            elif event.type() == QEvent.Type.MouseButtonRelease:
                if hasattr(event, "globalPosition"):
                    global_pos = event.globalPosition().toPoint()
                else:
                    global_pos = event.globalPos()
                local_pos = self.mapFromGlobal(global_pos)
                
                self.layer.update_mouse_state(local_pos, False)

        elif source in self.tracked_widgets:
            if event.type() in (QEvent.Type.Show, QEvent.Type.Resize, 
                               QEvent.Type.Move, QEvent.Type.Hide):
                self._update_collision_barrier(source)
        
        return super().eventFilter(source, event)

    def get_particle_count(self):
        """Get current active particle count."""
        return len(self.layer.particles)

    def get_emitter_count(self):
        """Get current emitter count."""
        return len(self.layer.emitters)