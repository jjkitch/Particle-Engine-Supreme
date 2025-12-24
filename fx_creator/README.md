```markdown
# Particle Engine Supreme - FX Creator

A powerful, visual particle effect editor built in Python using PySide6 and the custom `particle_engine_supreme` backend. This tool allows you to create, tweak, preview, and export highly customizable real-time particle effects suitable for games, UI enhancements, visualisations, or creative projects.

## Features

- **Real-time preview** on a large canvas with dark/light background control
- **Four intuitive tabs**: Physics, Visuals, Curves, Behaviors
- **Dozens of built-in presets** (snow, fire, rain, confetti, explosion, portal, etc.)
- **Full parameter control** including spawn rate, lifetime, velocity, gravity, wind, drag, radial/tangential forces, collision, trails, fades, sprite animation, and more
- **Advanced emitter shapes**: rect, circle, ring, line, point, cone, grid, spiral
- **Curve-based control** over scale, alpha, and color throughout particle lifetime
- **Dynamic behaviors**: turbulence, orbit, vortex, attraction, mouse interaction (attract/repel/orbit/vortex/avoid/tunnel/chaos)
- **Mouse interaction modes** with customizable strength, radius, and falloff
- **Sub-effects**: trigger secondary effects on spawn, collision, or death
- **Image and sprite sheet support** with optional tinting
- **Physics obstacles**: spawn draggable barriers that particles can bounce off or accumulate on
- **Global environment**: preview global wind/gravity that can be applied in your final integration
- **Save/Load custom presets** as JSON
- **Export current configuration** to console (ready to copy into code)
- **Quick spawn origin presets** (center, top/bottom/left/right edges)

## Requirements

- Python 3.12+
- PySide6 (`pip install PySide6`)
- The companion module `particle_engine_supreme` (must be in the parent directory or installed)
- Project structure expected:
  ```
  Qt_Praticle_Engine/
  ├── particle_engine_supreme/    # the engine module
  ├── fx_creator/
  │   ├── __init__.py
  │   ├── creator.py
  │   ├── tabs.py
  │   ├── constants.py
  │   ├── components.py
  │   └── assets/particles/       # optional folder for built-in particle images
  ```

## Installation & Running

1. Clone or download the project.
2. Ensure `particle_engine_supreme` is in the parent directory (as shown above).
3. Install PySide6:
   ```bash
   pip install PySide6
   ```
4. Run the editor:
   ```bash
   cd fx_creator
   python creator.py
   ```

The window will open at 1600×950 with the canvas on the left and controls on the right.

## Usage Guide

### Canvas Area (Left Side)
- Watch your effect in real time.
- Click **Spawn Physics Obstacle** to drop random barriers (particles can collide with them).
- Click **Clear Obstacles** to remove all barriers.
- Adjust **Canvas Color** slider for dark or coloured backgrounds.
- **Global Environment** spinboxes let you preview global wind/gravity (useful for final integration).

### Controls Area (Right Side)

#### Physics Tab
- Set spawn count, interval, lifetime, emitter shape and position.
- Quick **Spawn Origin** dropdown instantly moves the emitter to common positions.
- Physics forces: gravity, wind, drag, radial/tangential acceleration.
- Collision settings: bounce, friction, accumulation, wall bounce.
- Sub-effects: choose secondary presets triggered on spawn/collide/death.

#### Visuals Tab
- Choose particle shape: circle, rect, star, bubble, smoke, image, text.
- Size, spin, stretch, trails, blend mode (additive for glow).
- Image selector (built-in assets or browse custom).
- Sprite sheet animation grid support.
- Auto-fade controls (generates alpha curve).

#### Curves Tab
- Initial spawn colors (comma-separated hex list).
- Color variance (hue/sat/val).
- **Scale over Life**: 5-point curve (default: birth → growth → shrink → death).
- **Alpha over Life**: 5-point curve (0-255).
- **Color Transition**: dynamic number of color stops (click + to add).

#### Behaviors Tab
- Add multiple behaviors (turbulence, orbit, vortex, attraction, mouse interaction).
- Each behavior shows relevant parameters.
- Global tuning values are also available.

#### Bottom Buttons
- **Load Preset**: choose from built-in effects.
- **Reset to Clean Slate**: clears everything and returns to defaults.
- **Force Refresh**: manually re-apply current settings.
- **Print Config to Console**: outputs full Python dict ready for `add_custom_effect()`.
- **Save Preset / Load Preset**: store or recall your own JSON presets.

### Creating Your First Effect

1. Choose a built-in preset (e.g., "fire") to see something instantly.
2. Tweak parameters in any tab – changes apply immediately.
3. Add mouse interaction → select "mouse_interaction" behavior → choose "attract" mode → move your cursor over the canvas.
4. When satisfied, click **Print Config to Console** → copy the printed dictionary into your game/project where you call `overlay.add_custom_effect(**config)`.

### Exporting for Use

The printed configuration is a direct Python dictionary compatible with `GlobalEffectOverlay.add_custom_effect()`. Example output snippet:
```python
{
  'count': 8,
  'interval': 2,
  'life_min': 80,
  'life_max': 120,
  'emitter_type': 'cone',
  'cone_direction': 270.0,
  'cone_angle': 30.0,
  'speed_min': 3.0,
  'speed_max': 6.0,
  'gravity': 0.3,
  'shape': 'circle',
  'size_min': 4.0,
  'size_max': 12.0,
  'color_curve': ['#ff0000', '#ff8800', '#ffff00', '#000000'],
  'behaviors': ['mouse_interaction'],
  'mouse_mode': 'repel',
  'mouse_strength': 5.0,
  ...
}
```

You can also save/load JSON files for reuse across projects.

## Tips & Best Practices

- Keep `count` × `interval` reasonable (≤100 particles) for smooth performance in the editor.
- Trail length is capped at 5 for safety; increase in engine if needed.
- Additive blend (`add`) + white-to-coloured particles = glowing effects.
- Use negative `radial_accel` for implosions, positive for explosions.
- Combine sub-effects for complex results (e.g., explosion → on_death → smoke).

## Contributing

Feel free to open issues or pull requests in the repository. Suggested improvements:
- More built-in presets
- Export as animated GIF/video
- Undo/redo support
- Additional emitter shapes or behaviors

Enjoy creating spectacular particle effects!
```