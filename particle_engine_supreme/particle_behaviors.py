# particle_engine_supreme/particle_behaviors.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

import math
import random


class ParticleBehavior:
    """Base class for particle behaviors that modify motion/appearance."""
    def apply(self, particle, dt, layer):
        pass

class TurbulenceBehavior(ParticleBehavior):
    """Adds chaotic, swirling motion to particles."""
    def __init__(self, strength=1.0, frequency=0.1):
        self.strength = strength
        self.frequency = frequency
        self.time = 0
    
    def apply(self, particle, dt, layer):
        self.time += dt
        noise_x = math.sin(particle["x"] * self.frequency + self.time) * self.strength
        noise_y = math.cos(particle["y"] * self.frequency + self.time * 0.7) * self.strength
        
        if "body" not in particle:
            particle["vx"] += noise_x
            particle["vy"] += noise_y

class AttractionBehavior(ParticleBehavior):
    """Attracts particles to a point."""
    def __init__(self, point, strength=0.5, radius=None):
        self.point = point
        self.strength = strength
        self.radius = radius
    
    def apply(self, particle, dt, layer):
        dx = self.point[0] - particle["x"]
        dy = self.point[1] - particle["y"]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 1:
            return
        
        if self.radius and dist > self.radius:
            return
        
        force = self.strength / (dist * 0.1)
        
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point((dx * force, dy * force))
        else:
            particle["vx"] += (dx / dist) * force
            particle["vy"] += (dy / dist) * force

class VortexBehavior(ParticleBehavior):
    """Creates spiral motion around a point."""
    def __init__(self, center, strength=2.0, radius=300):
        self.center = center
        self.strength = strength
        self.radius = radius
    
    def apply(self, particle, dt, layer):
        dx = particle["x"] - self.center[0]
        dy = particle["y"] - self.center[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > self.radius or dist < 1:
            return
        
        force = self.strength * (1.0 - dist / self.radius)
        tx = -dy / dist * force
        ty = dx / dist * force
        
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point((tx * 10, ty * 10))
        else:
            particle["vx"] += tx
            particle["vy"] += ty

class OrbitBehavior(ParticleBehavior):
    """Makes particles orbit around their spawn point."""
    def __init__(self, speed=0.05, radius_variance=0.1):
        self.speed = speed
        self.radius_variance = radius_variance
    
    def apply(self, particle, dt, layer):
        if "orbit_angle" not in particle:
            particle["orbit_angle"] = 0
            particle["orbit_center"] = (particle["x"], particle["y"])
            particle["orbit_radius"] = particle.get("size_base", 10) * (1.0 + random.uniform(-self.radius_variance, self.radius_variance))
        
        particle["orbit_angle"] += self.speed
        cx, cy = particle["orbit_center"]
        
        particle["x"] = cx + math.cos(particle["orbit_angle"]) * particle["orbit_radius"]
        particle["y"] = cy + math.sin(particle["orbit_angle"]) * particle["orbit_radius"]

class MouseInteractionBehavior(ParticleBehavior):
    """Makes particles react to mouse position with various modes."""
    def __init__(self, mode="attract", strength=1.0, radius=300, falloff="linear", click_only=False):
        self.mode = mode
        self.strength = strength
        self.radius = radius
        self.falloff = falloff
        self.click_only = click_only
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
    
    def update_mouse(self, x, y, pressed=False):
        """Update mouse position and state."""
        self.mouse_pos = (x, y)
        self.mouse_pressed = pressed
    
    def apply(self, particle, dt, layer):
        if hasattr(layer, 'last_mouse_pos'):
            mx, my = layer.last_mouse_pos
            pressed = layer.mouse_pressed
        else:
            mx, my = self.mouse_pos
            pressed = self.mouse_pressed

        dx = mx - particle["x"]
        dy = my - particle["y"]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 0.1 or dist > self.radius:
            return
        
        if self.click_only and not pressed:
            return

        force_mult = self._calculate_falloff(dist)

        if self.mode == "attract":
            self._apply_attraction(particle, dx, dy, dist, force_mult)
        elif self.mode == "repel":
            self._apply_repulsion(particle, dx, dy, dist, force_mult)
        elif self.mode == "orbit":
            self._apply_orbit(particle, dx, dy, dist, force_mult)
        elif self.mode == "vortex":
            self._apply_vortex(particle, dx, dy, dist, force_mult)
        elif self.mode == "avoid":
            self._apply_avoidance(particle, dx, dy, dist, force_mult)
        elif self.mode == "tunnel":
            self._apply_tunnel(particle, dx, dy, dist, force_mult)
        elif self.mode == "chaos":
            self._apply_chaos(particle, dx, dy, dist, force_mult)
    
    def _calculate_falloff(self, dist):
        """Calculate force multiplier based on distance."""
        t = 1.0 - (dist / self.radius)
        
        if self.falloff == "linear":
            return t
        elif self.falloff == "quadratic":
            return t * t
        elif self.falloff == "inverse":
            return 1.0 / (1.0 + dist * 0.01)
        elif self.falloff == "smooth":
            return t * t * (3.0 - 2.0 * t)
        return t
    
    def _apply_attraction(self, particle, dx, dy, dist, force_mult):
        """Pull particles toward mouse."""
        force = self.strength * force_mult
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point((dx * force, dy * force))
        else:
            particle["vx"] += (dx / dist) * force
            particle["vy"] += (dy / dist) * force
    
    def _apply_repulsion(self, particle, dx, dy, dist, force_mult):
        """Push particles away from mouse."""
        force = self.strength * force_mult
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point((-dx * force, -dy * force))
        else:
            particle["vx"] -= (dx / dist) * force
            particle["vy"] -= (dy / dist) * force
    
    def _apply_orbit(self, particle, dx, dy, dist, force_mult):
        """Make particles orbit around mouse."""
        force = self.strength * force_mult
        tx = -dy / dist * force
        ty = dx / dist * force
        
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point((tx * 10, ty * 10))
        else:
            particle["vx"] += tx
            particle["vy"] += ty
    
    def _apply_vortex(self, particle, dx, dy, dist, force_mult):
        """Spiral particles toward mouse."""
        force = self.strength * force_mult
        attract_x = (dx / dist) * force * 0.3
        attract_y = (dy / dist) * force * 0.3
        tx = -dy / dist * force * 0.7
        ty = dx / dist * force * 0.7
        
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point(((attract_x + tx) * 10, (attract_y + ty) * 10))
        else:
            particle["vx"] += attract_x + tx
            particle["vy"] += attract_y + ty
    
    def _apply_avoidance(self, particle, dx, dy, dist, force_mult):
        """Particles flee from mouse but maintain distance."""
        if dist < self.radius * 0.3:
            force = self.strength * force_mult * 2.0
            if "body" in particle:
                particle["body"].apply_impulse_at_local_point((-dx * force, -dy * force))
            else:
                particle["vx"] -= (dx / dist) * force
                particle["vy"] -= (dy / dist) * force
    
    def _apply_tunnel(self, particle, dx, dy, dist, force_mult):
        """Suck particles through mouse position like a tunnel."""
        if dist < 50:
            force = self.strength * 5.0
            if "body" in particle:
                particle["body"].velocity = (dx * force, dy * force)
            else:
                particle["vx"] = (dx / dist) * force if dist > 0.1 else 0
                particle["vy"] = (dy / dist) * force if dist > 0.1 else 0
        else:
            force = self.strength * force_mult * 2.0
            if "body" in particle:
                particle["body"].apply_impulse_at_local_point((dx * force, dy * force))
            else:
                particle["vx"] += (dx / dist) * force
                particle["vy"] += (dy / dist) * force
    
    def _apply_chaos(self, particle, dx, dy, dist, force_mult):
        """Random chaotic forces."""
        force = self.strength * force_mult
        rx = random.uniform(-1, 1) * force
        ry = random.uniform(-1, 1) * force
        
        if "body" in particle:
            particle["body"].apply_impulse_at_local_point((rx * 10, ry * 10))
        else:
            particle["vx"] += rx
            particle["vy"] += ry

        
class ForceFieldBehavior(ParticleBehavior):
    """
    A static zone in the world that affects particles passing through it.
    Can be a 'Wind' zone (directional) or a 'Gravity Well' (radial).
    """
    def __init__(self, x, y, width, height, field_type="wind", strength=0.5, angle=0):
        self.rect = (x, y, width, height)
        self.field_type = field_type
        self.strength = strength
        self.angle_rad = math.radians(angle)
        
        self.wind_x = math.cos(self.angle_rad) * strength
        self.wind_y = math.sin(self.angle_rad) * strength

    def apply(self, particle, dt, layer):
        px, py = particle["x"], particle["y"]
        rx, ry, rw, rh = self.rect

        if not (rx <= px <= rx + rw and ry <= py <= ry + rh):
            return

        if self.field_type == "wind":
            if "body" in particle:
                particle["body"].apply_impulse_at_local_point((self.wind_x * 10, self.wind_y * 10))
            else:
                particle["vx"] += self.wind_x
                particle["vy"] += self.wind_y

        elif self.field_type == "slow":
            factor = 1.0 - (0.1 * self.strength)
            if "body" not in particle:
                particle["vx"] *= factor
                particle["vy"] *= factor

        elif self.field_type in ["attract", "repel"]:
            cx = rx + rw / 2
            cy = ry + rh / 2
            dx = cx - px
            dy = cy - py
            dist = math.sqrt(dx*dx + dy*dy) + 0.1
            
            direction = 1 if self.field_type == "attract" else -1
            force = (self.strength * direction) / (dist * 0.05)
            
            if "body" in particle:
                 particle["body"].apply_impulse_at_local_point((dx/dist * force * 10, dy/dist * force * 10))
            else:
                particle["vx"] += (dx / dist) * force
                particle["vy"] += (dy / dist) * force