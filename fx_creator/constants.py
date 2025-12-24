# fx_creator/constants.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

KNOWN_PRESETS = [
    "None", "snow", "fire", "inferno", "rain", "smoke", 
    "sparkles", "magic", "confetti", "bubbles", "energy", 
    "explosion", "matrix", "nova", "portal", "laser_wall", 
    "fairy_dust", "splash", "mouse_trail_magic", "starfield",
    "aurora", "glowing_trail", "fairy_swarm", "energy_orbs",
    "tornado", "flamethrower", "laser_bolt", "pixel_explosion",
    "spiral_galaxy", "rocket_trail", "gentle_smoke", "machinegun",
    "warp_portal"
]

MOUSE_MODES = ["attract", "repel", "orbit", "vortex", "avoid", "tunnel", "chaos"]
FALLOFF_MODES = ["smooth", "linear", "quadratic", "inverse"]

EMITTER_TYPES = ["rect", "circle", "ring", "line", "point", "cone", "grid", "spiral"]

TOOLTIPS = {
    # Spawn
    "count": "Number of particles to spawn per emission cycle.",
    "interval": "Frames between emissions (1 = every frame, 2 = every other frame).",
    "start_delay": "Wait this many frames before starting emission.",
    "duration": "Duration in SECONDS. (1.5 = 1.5 seconds). Set to -1.0 for Infinite.",
    "life_min": "Minimum lifetime of a particle in frames (60 frames ≈ 1 second).",
    "life_max": "Maximum lifetime of a particle in frames.",
    
    # Emitter Area
    "use_custom_rect": "If checked, spawns particles in the specific box defined below. If unchecked, uses the entire canvas.",
    "emitter_type": "Shape of the spawn area (Rect, Circle, Ring, Cone, Grid, etc).",
    "emitter_x": "X position of the spawn area center/top-left.",
    "emitter_y": "Y position of the spawn area center/top-left.",
    "emitter_w": "Width/Diameter of the spawn area.",
    "emitter_h": "Height/Diameter of the spawn area.",
    
    # New Emitter Params
    "cone_direction": "Direction of the cone center in degrees (0 = Right, 90 = Down).",
    "cone_angle": "Spread of the cone in degrees (e.g. 30 for a narrow spray).",
    "grid_rows": "Number of rows for Grid emitter.",
    "grid_cols": "Number of columns for Grid emitter.",
    "spiral_speed": "Rotation speed of the Spiral emitter.",

    # Physics
    "gravity": "Downward force applied to particles. Positive is down, negative is up.",
    "wind": "Horizontal force applied to particles (Positive = Right, Negative = Left).",
    "drag": "Air resistance. 0.0 = no drag, 1.0 = immediate stop.",
    "speed_min": "Minimum starting speed of particles.",
    "speed_max": "Maximum starting speed of particles.",
    "angle_min": "Minimum spawn angle in degrees (0 = Right, 90 = Down).",
    "angle_max": "Maximum spawn angle in degrees.",
    "inherit_velocity": "How much of the parent widget's movement is passed to the particle (0.0 to 1.0).",
    
    # Advanced Physics
    "radial_accel": "Force pushing particles outward from center (Explosions). Negative sucks inward.",
    "tangential_accel": "Force pushing particles sideways relative to center (Tornadoes/Vortices).",
    "align_rotation": "If checked, sprite rotates to face its direction of travel.",

    # Collision
    "collides": "Enable physics collisions with barriers (walls, buttons, etc.).",
    "elasticity": "Bounciness. 0.0 = no bounce (thud), 1.0 = perfect bounce (rubber).",
    "friction": "Surface friction. 0.0 = ice, 1.0 = sticky sandpaper.",
    "accumulate": "If True, particles pile up like snow instead of vanishing on contact.",
    "wall_bounce": "If True, particles bounce off the edges of the canvas.",
    "bounce_factor": "Energy retained after a wall bounce (1.0 = 100%).",
    
    # Sub Effects
    "on_spawn_effect": "Trigger this effect immediately when a particle is born (e.g. trails).",
    "on_collide_effect": "Trigger this effect when a particle hits a wall.",
    "on_death_effect": "Trigger this effect when a particle expires.",
    
    # Visuals
    "shape": "The visual style of the particle.",
    "size_min": "Minimum starting size in pixels.",
    "size_max": "Maximum starting size in pixels.",
    "spin_min": "Minimum rotation speed.",
    "spin_max": "Maximum rotation speed.",
    "stretch_factor": "Elongate particle in direction of travel (Motion Blur). 1.0 = Normal.",
    
    "image_path": "The image file to use (if Shape is 'image').",
    "tint_image": "If checked, the white parts of the image will be colored by the particle color.",
    "text_chars": "A string of characters to randomly pick from (if Shape is 'text').",
    "blend_mode": "'Add' creates glowing light effects. 'Normal' paints standard pixels.",
    "trail_length": "Number of previous positions to draw (creates a motion blur trail).",
    "trail_width": "Thickness of the motion trail in pixels.",
    "trail_opacity": "Transparency of the trail (0-255). Lower is more subtle.",
    "star_points": "Number of points on the star shape (min 3).",
    
    # Fades
    "fade_in_time": "Number of frames to fade in from 0 alpha.",
    "fade_out_time": "Number of frames to fade out to 0 alpha.",
    
    # Sprite Animation
    "sprite_rows": "Number of rows in the sprite sheet grid.",
    "sprite_cols": "Number of columns in the sprite sheet grid.",
    "anim_speed": "Animation playback speed (Frames per tick).",
    "random_start_frame": "Start animation at a random frame instead of frame 0.",
    
    # Curves & Colors
    "color": "A list of colors to randomly choose from when spawning.",
    "hue_variance": "Randomly shift Hue (+/- 0.0 to 1.0).",
    "sat_variance": "Randomly shift Saturation (+/- 0.0 to 1.0).",
    "val_variance": "Randomly shift Brightness (+/- 0.0 to 1.0).",
    "scale_curve": "Multipliers for size over time. Left is birth, Right is death.",
    "alpha_curve": "Opacity (0-255) over time. Left is birth, Right is death.",
    "color_curve": "Color transition over time. Particles morph through these colors.",
    
    # Behaviors
    "turbulence": "Adds chaotic, noise-based movement.",
    "orbit": "Particles circle around their original spawn point.",
    "vortex": "Particles spiral around the center of the screen.",
    "turbulence_strength": "How strong the chaotic noise force is.",
    "turbulence_freq": "How tight/frequent the noise waves are.",
    "orbit_speed": "How fast particles orbit their center.",
    "vortex_strength": "Strength of the pull towards the vortex center.",
    "vortex_radius": "Distance from center where the vortex is effective.",
    
    # Mouse Interaction
    "Enable Mouse Interaction": "Allow particles to react to the mouse cursor.",
    "mouse_mode": "How particles react to the mouse (Attract, Repel, etc.).",
    "mouse_strength": "Force multiplier for mouse interaction.",
    "mouse_radius": "Radius in pixels around the mouse where particles are affected.",
    "mouse_falloff": "How the force fades with distance (Smooth is usually best).",
    "mouse_click_only": "If checked, interaction only happens when holding the mouse button."
}