# particle_engine_supreme/physics_engine.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

import pymunk

class PymunkPhysicsEngine:
    """Enhanced physics engine with better collision handling."""
    
    def __init__(self, gravity=(0, 900)):
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.damping = 0.95
        
        self.bodies = []
        self.static_bodies = {}
        
        self.PARTICLE_TYPE = 1
        self.BARRIER_TYPE = 2

    def step(self, dt=1/60.0):
        """Advance physics simulation."""
        self.space.step(dt)

    def add_static_barrier(self, widget_id, rect):
        """Create a solid wall that particles can collide with."""
        if widget_id in self.static_bodies:
            self.remove_static_barrier(widget_id)

        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        cx = rect.x() + rect.width() / 2
        cy = rect.y() + rect.height() / 2
        body.position = (cx, cy)

        shape = pymunk.Poly.create_box(body, (rect.width(), rect.height()))
        shape.elasticity = 0.2
        shape.friction = 1.0
        shape.collision_type = self.BARRIER_TYPE
        
        self.space.add(body, shape)
        self.static_bodies[widget_id] = (body, shape)

    def remove_static_barrier(self, widget_id):
        """Remove a collision barrier."""
        if widget_id in self.static_bodies:
            body, shape = self.static_bodies[widget_id]
            self.space.remove(body, shape)
            del self.static_bodies[widget_id]

    def spawn_particle(self, x, y, velocity=(0, 0), radius=5, mass=1, physics_profile=None):
        """
        Create a physics-enabled particle.
        
        Args:
            x, y: Position
            velocity: Initial velocity (vx, vy)
            radius: Collision radius
            mass: Particle mass
            physics_profile: Dict with 'friction', 'elasticity', 'density'
        
        Returns:
            (body, shape) tuple
        """
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = x, y
        body.velocity = velocity

        shape = pymunk.Circle(body, radius)
        
        shape.elasticity = 0.6
        shape.friction = 0.3
        shape.collision_type = self.PARTICLE_TYPE
        
        if physics_profile:
            if "elasticity" in physics_profile:
                shape.elasticity = physics_profile["elasticity"]
            if "friction" in physics_profile:
                shape.friction = physics_profile["friction"]
            if "density" in physics_profile:
                shape.density = physics_profile["density"]

        self.space.add(body, shape)
        self.bodies.append(body)
        
        return body, shape

    def remove_particle(self, body, shape):
        """Safely remove a particle from simulation."""
        try:
            self.space.remove(body, shape)
            if body in self.bodies:
                self.bodies.remove(body)
        except:
            pass

    def clear_particles(self):
        """Remove all dynamic particles."""
        for body in self.bodies[:]:
            try:
                for shape in body.shapes:
                    self.space.remove(shape)
                self.space.remove(body)
            except:
                pass
        self.bodies.clear()

    def clear_all(self):
        """Wipe entire physics world."""
        self.clear_particles()
        
        for widget_id in list(self.static_bodies.keys()):
            self.remove_static_barrier(widget_id)