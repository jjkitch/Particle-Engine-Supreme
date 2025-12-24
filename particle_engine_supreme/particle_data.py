# particle_engine_supreme/particle_data.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

DEFAULT_PROFILE = {
    # --- SPAWN SETTINGS ---
    "count": 1,              # Particles per emission
    "interval": 1,           # Frames between emissions
    "start_delay": 0,        # Frames to wait before starting
    
    # --- EMITTER GEOMETRY ---
    # rect, circle, ring, line, point, cone, grid, spiral
    "emitter_type": "rect",
    
    # Cone-specific (NEW)
    "cone_direction": 0,     # Center direction in degrees (0 = right)
    "cone_angle": 45,        # Spread angle in degrees
    
    # Grid-specific (NEW)
    "grid_rows": 3,          # Number of rows in grid pattern
    "grid_cols": 3,          # Number of columns in grid pattern
    
    # Spiral-specific (NEW)
    "spiral_speed": 0.5,     # How fast spiral rotates per emission

    # --- EMITION TIMING ---
    "duration": -1,          # -1 = Infinite
    
    # --- LIFETIME ---
    "life_min": 50,
    "life_max": 100,
    
    # --- PHYSICS BASICS ---
    "gravity": 0.5,
    "wind": 0.0,             # Horizontal push
    "drag": 0.0,             # Air resistance (0.0 - 1.0)
    
    # --- ADVANCED PHYSICS ---
    "radial_accel": 0.0,     # Push outward from center (Explosions)
    "tangential_accel": 0.0, # Push sideways relative to center (Tornadoes)
    "align_rotation": False, # Rotate sprite to face travel direction
    "inherit_velocity": 0.0, # Inherit velocity from moving widget (0.0 - 1.0)
    
    # --- VELOCITY ---
    "speed_min": 1.0,
    "speed_max": 3.0,
    "angle_min": 0,
    "angle_max": 360,
    
    # --- COLLISION / WALLS ---
    "collides": False,       # Rigid body physics (Pymunk)
    "elasticity": 0.5,       # Bounciness (Pymunk)
    "friction": 0.5,         # Surface friction (Pymunk)
    "wall_bounce": False,    # Screen edge containment
    "bounce_factor": 0.8,    # Energy retained after wall bounce (1.0 = 100%)
    
    # --- APPEARANCE ---
    "shape": "circle",       # circle, rect, image, text, star, bubble
    "size_min": 5,
    "size_max": 10,
    "color": ["#FFFFFF"],
    
    # --- COLOR VARIANCE ---
    "hue_variance": 0.0,
    "sat_variance": 0.0,
    "val_variance": 0.0,
    
    # --- SPRITE ANIMATION ---
    "sprite_rows": 1,
    "sprite_cols": 1,
    "anim_speed": 1.0,
    "random_start_frame": False,
    
    # --- ANIMATION CURVES ---
    "spin_min": 0,
    "spin_max": 0,
    "scale_curve": None,     # List of values or None
    "alpha_curve": None,
    "color_curve": None,
    
    # --- FADE HELPERS (NEW) ---
    "fade_in_time": 0,       # Frames to fade in (auto-generates alpha_curve)
    "fade_out_time": 0,      # Frames to fade out (auto-generates alpha_curve)
    
    # --- RENDERING ---
    "blend_mode": "normal",  # "normal" or "add"
    "trail_length": 0,
    "trail_width": 2,
    "trail_opacity": 100,
    "stretch_factor": 1.0,   # Elongate in direction of travel (motion blur)
    
    # --- SHAPE SPECIFICS ---
    "star_points": 5,
    "image_path": "",
    "tint_image": True,
    "text_chars": "0123456789",
    
    # --- LOGIC ---
    "accumulate": False,     # Snow piling up
    "on_spawn_effect": None, # Sub-emitter triggered at particle birth
    "on_collide_effect": None,
    "on_death_effect": None,
    
    # --- BEHAVIORS ---
    "behaviors": [],         # List of strings: ["turbulence", "orbit", ...]
    
    # Behavior Params
    "turbulence_strength": 0.3,
    "turbulence_freq": 0.05,
    
    "orbit_speed": 0.05,
    
    "vortex_strength": 2.0,
    "vortex_radius": 300,
    "vortex_center": (0, 0),
    
    "attraction_strength": 0.5,
    "attraction_radius": 200,
    
    # --- MOUSE INTERACTION ---
    "mouse_mode": "attract", # attract, repel, orbit, vortex, avoid, tunnel
    "mouse_strength": 1.0,
    "mouse_radius": 300,
    "mouse_falloff": "smooth",
    "mouse_click_only": False
}