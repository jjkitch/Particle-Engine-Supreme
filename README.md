# Particle Engine Supreme - Comprehensive Architecture Documentation

**Version:** 2.5.1 (CPU-Optimized, Native Forces, Hybrid Physics, Enhanced Features)  
**Dependencies:** `PySide6` (Required), `pymunk` (Optional - for rigid body physics)  
**Target Performance:** 2500+ particles @ 60 FPS  
**License:** Custom (See project root)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Directory Structure](#2-directory-structure)
3. [Core Architecture](#3-core-architecture)
4. [Module Reference](#4-module-reference)
5. [Physics System](#5-physics-system)
6. [Emitter Geometries](#6-emitter-geometries)
7. [Particle Shapes](#7-particle-shapes)
8. [Behavior System](#8-behavior-system)
9. [Visual Effects](#9-visual-effects)
10. [Performance Optimization](#10-performance-optimization)
11. [Integration Guide](#11-integration-guide)
12. [Preset System](#12-preset-system)
13. [Advanced Features](#13-advanced-features)
14. [Troubleshooting](#14-troubleshooting)
15. [API Reference](#15-api-reference)

---

## 1. Overview

### What is Particle Engine Supreme?

`particle_engine_supreme` is a high-performance, modular 2D particle system designed specifically for PySide6 (or PyQt6) applications. It renders visual effects as a transparent overlay on top of standard UI widgets, enabling rich feedback, environmental effects, and gamification elements without disrupting the underlying user interface.

### Key Features

- **Transparent Overlay Architecture** - Non-blocking particle effects over any PySide6 widget
- **Hybrid Physics Engine** - Lightweight atmospheric physics + optional rigid body collisions
- **7 Emitter Geometries** - Point, Rect, Circle, Ring, Line, Cone, Grid, Spiral
- **6+ Particle Shapes** - Circle, Rectangle, Star, Bubble, Image (sprite sheets), Text
- **8+ Behavior Systems** - Turbulence, Orbit, Vortex, Attraction, Mouse Interaction, Force Fields
- **Advanced Rendering** - Color/alpha/scale curves, trails, blend modes, motion blur
- **CPU-Optimized** - Flattened data structure achieving 10x performance improvement
- **Widget Integration** - Direct attachment to buttons, labels, or any QWidget

### Design Philosophy

1. **Performance First** - Optimized for 2000+ particles at 60 FPS using CPU rendering
2. **Modular Design** - Each component (emitter, behavior, renderer) operates independently
3. **Artist-Friendly** - JSON-compatible preset system with sensible defaults
4. **Non-Invasive** - Particles never block mouse events or interfere with UI interaction
5. **Extensible** - Strategy pattern for behaviors, easy to add custom effects

---

## 2. Directory Structure

```text
particle_engine_supreme/
├── __init__.py                # Package initialization, exposes GlobalEffectOverlay
├── effect_overlay.py          # Main Controller - Window management & input handling
├── particle_engine.py         # Core Renderer - Update loop & drawing (VisualEffectLayer)
├── particle_emitter.py        # Spawner Factory - Geometry handling & particle creation
├── particle_behaviors.py      # Strategy Pattern - Modular particle logic
├── particle_data.py           # Configuration Contract - Default settings profile
├── particle_presets.py        # Preset Library - Pre-configured effects (rain, fire, etc)
├── particle_utilities.py      # Helper Functions - Curve interpolation, color utilities
└── physics_engine.py          # Pymunk Wrapper - Optional rigid body physics integration
```

### File Responsibilities

| File                    | Purpose                                            | Lines | Complexity |
| ----------------------- | -------------------------------------------------- | ----- | ---------- |
| `effect_overlay.py`     | User-facing API, event filtering, widget tracking  | ~350  | Medium     |
| `particle_engine.py`    | Render loop, physics integration, particle updates | ~600  | High       |
| `particle_emitter.py`   | Particle spawning, geometry calculations           | ~400  | Medium     |
| `particle_behaviors.py` | Behavior implementations (8+ classes)              | ~500  | Medium     |
| `particle_data.py`      | Default configuration dictionary                   | ~100  | Low        |
| `particle_presets.py`   | Effect preset definitions                          | ~300  | Low        |
| `particle_utilities.py` | Interpolation and helper functions                 | ~100  | Low        |
| `physics_engine.py`     | Pymunk space management                            | ~200  | Medium     |

---

## 3. Core Architecture

### Layer Hierarchy

```
┌─────────────────────────────────────────┐
│   Parent QMainWindow / QWidget          │
│   (Your Application)                     │
│                                          │
│   ┌──────────────────────────────────┐  │
│   │  GlobalEffectOverlay (QWidget)   │  │ ← Transparent, non-blocking
│   │  WA_TransparentForMouseEvents    │  │
│   │                                   │  │
│   │  ┌────────────────────────────┐  │  │
│   │  │ VisualEffectLayer (QWidget)│  │  │ ← Rendering canvas
│   │  │                             │  │  │
│   │  │  Particles: [...]           │  │  │
│   │  │  Emitters: [...]            │  │  │
│   │  │  Behaviors: [...]           │  │  │
│   │  └────────────────────────────┘  │  │
│   └──────────────────────────────────┘  │
│                                          │
│   [Your UI Widgets]                      │ ← Fully interactive
└─────────────────────────────────────────┘
```

### Data Flow

```
User Action (Click Button)
    ↓
EventFilter (effect_overlay.py)
    ↓
GlobalEffectOverlay.add_target_effect()
    ↓
VisualEffectLayer.add_emitter()
    ↓
ParticleEmitter.emit() ──→ _spawn_single() × count
    ↓                          ↓
Timer (60 FPS)            Particle Dict Created
    ↓                          ↓
_update_loop()            Flattened Data (gravity, wind, etc)
    ↓                          ↓
_update_particles()       Added to particle_list
    ↓
Apply Behaviors → Update Physics → Check Bounds → Render
    ↓
paintEvent() → _draw_particle() → QPainter draws to screen
```

### Thread Model

**Single-threaded, event-driven architecture:**

- Main thread runs Qt event loop
- `QTimer` triggers `_update_loop()` every ~16ms (60 FPS)
- All particle updates occur synchronously in the timer callback
- No thread safety concerns, no locks needed

**Why single-threaded?**

- QPainter is not thread-safe
- Physics updates must be atomic
- 60 FPS sufficient for visual feedback
- Simplicity and debuggability

---

## 4. Module Reference

### 4.1 GlobalEffectOverlay (`effect_overlay.py`)

**Purpose:** Primary user-facing interface. Manages the transparent overlay, event filtering, and widget collision tracking.

**Key Responsibilities:**

- Automatically resizes to fit parent window
- Intercepts mouse events without blocking UI interaction
- Maps Qt widgets to physics barriers
- Provides high-level API for effect management

**Initialization:**

```python
overlay = GlobalEffectOverlay(parent_window, use_physics=True)
```

**Public Methods:**

| Method                                      | Purpose                           | Example                                           |
| ------------------------------------------- | --------------------------------- | ------------------------------------------------- |
| `add_global_effect(name, **kwargs)`         | Spawn effect across entire window | `overlay.add_global_effect("snow")`               |
| `add_target_effect(widget, name, **kwargs)` | Attach effect to specific widget  | `overlay.add_target_effect(btn, "fire")`          |
| `add_custom_effect(target, **settings)`     | Create fully custom effect        | `overlay.add_custom_effect(self, count=10, ...)`  |
| `trigger_burst(x, y, effect, **kwargs)`     | One-time burst at position        | `overlay.trigger_burst(100, 200, "explosion")`    |
| `add_force_field(x, y, w, h, type, ...)`    | Add static force zone             | `overlay.add_force_field(0, 0, 100, 100, "wind")` |
| `add_attraction_point(x, y, strength, ...)` | Add particle magnet               | `overlay.add_attraction_point(400, 300, 1.0)`     |
| `enable_mouse_interaction(mode, ...)`       | Enable mouse particle effects     | `overlay.enable_mouse_interaction("attract")`     |
| `add_collision_widget(widget)`              | Register widget as barrier        | `overlay.add_collision_widget(label)`             |
| `clear_effects()`                           | Remove all particles/emitters     | `overlay.clear_effects()`                         |
| `pause()` / `resume()`                      | Control update loop               | `overlay.pause()`                                 |

**Event Filtering:**

The overlay installs an event filter on the parent window and central widget to capture mouse events:

```python
def eventFilter(self, source, event):
    if event.type() == QEvent.Type.MouseMove:
        # Convert global position to overlay coordinates
        local_pos = self.mapFromGlobal(event.globalPosition().toPoint())
        self.layer.update_mouse_state(local_pos, pressed)
    # ... handle clicks, resize, etc
```

This allows particles to react to mouse without consuming events.

---

### 4.2 VisualEffectLayer (`particle_engine.py`)

**Purpose:** Core rendering and update engine. Runs the 60 FPS loop and manages particle lifecycle.

**Key Responsibilities:**

- QTimer-based update loop (16ms intervals)
- Particle physics integration
- Behavior application
- Global Wind/Gravity setting
- QPainter-based rendering
- Collision detection (if pymunk enabled)

**Architecture:**

```python
class VisualEffectLayer(QWidget):
    def __init__(self, parent, physics_engine=None):
        self.particles = []        # Active particle list
        self.emitters = []         # Active emitter list
        self.global_behaviors = [] # Behaviors affecting all particles
        self.global_wind = 0.0     # High-performance native wind
        self.global_gravity = 0.0  # High-performance native gravity
        self.timer = QTimer()      # 60 FPS update timer
```

**Update Loop Flow:**

```python
def _update_loop(self):
    1. Update mouse position (from global cursor)
    2. Step physics engine (if enabled)
    3. Emit new particles from active emitters
    4. Update existing particles:
       - Apply behaviors (turbulence, mouse, etc)
       - Update position/velocity
       - Check wall bounce
       - Update visuals (curves, trails)
       - Check death conditions
    5. Trigger paintEvent() for rendering
```

**Rendering Pipeline:**

```python
def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    for particle in self.particles:
        # 1. Draw trail (if enabled)
        # 2. Set blend mode (normal/additive)
        # 3. Apply transforms (translate, rotate, scale)
        # 4. Apply stretch/squash (if moving fast)
        # 5. Draw shape (circle, rect, image, etc)
```

**Performance Critical Sections:**

- `_update_particles()` - Called 60x/sec, processes all particles
- `_draw_particle()` - Called for each particle every frame
- Behavior.apply() - Called for each particle per behavior

**Optimization:** Particles use flattened data to avoid dictionary lookups in these hot paths.

---

### 4.3 ParticleEmitter (`particle_emitter.py`)

**Purpose:** Particle spawning factory. Handles geometry calculations and initial particle state.

**Key Responsibilities:**

- Interpret emitter geometry (rect, circle, ring, cone, etc)
- Calculate spawn positions based on widget location
- Apply velocity based on angle/speed settings
- Generate particle initial state (color, size, rotation)
- Handle velocity inheritance from moving widgets

**Emitter Lifecycle:**

```python
1. Emitter created: ParticleEmitter(preset_name, target, overrides)
2. Load settings: Merge DEFAULT_PROFILE → preset → overrides
3. Cache resources: Load images, generate color palette
4. Setup behaviors: Instantiate behavior classes
5. Activation: emit() called by VisualEffectLayer every frame
6. Spawn check: Respect interval, duration, start_delay
7. Particle creation: _spawn_single() for each count
8. Deactivation: When duration expires or manually cleared
```

**Geometry Calculation (`get_spawn_pos`):**

Each emitter type calculates spawn position differently:

```python
"rect"   → Random (x, y) within bounding box
"circle" → Random point within circle (uniform distribution)
"ring"   → Random angle on circle perimeter
"line"   → Interpolate along line segment
"point"  → Exact center of target
"cone"   → Center, velocity determines direction
"grid"   → Random position within grid cell
"spiral" → Rotating position along spiral path
```

**Particle Initialization:**

When a particle spawns, the emitter:

1. Calculates position from geometry
2. Determines velocity (speed + angle/cone)
3. Applies color variance (HSV adjustments)
4. Generates fade curves (if fade_in/out specified)
5. Flattens frequently-accessed settings
6. Creates physics body (if collides=True)
7. Triggers sub-emitter (if on_spawn_effect set)

---

### 4.4 ParticleBehavior System (`particle_behaviors.py`)

**Purpose:** Modular strategy pattern for particle motion/appearance modification.

**Base Class:**

```python
class ParticleBehavior:
    def apply(self, particle, dt, layer):
        pass  # Override in subclasses
```

**Available Behaviors:**

| Behavior                   | Effect                       | Parameters                     | Use Case                 |
| -------------------------- | ---------------------------- | ------------------------------ | ------------------------ |
| `TurbulenceBehavior`       | Adds chaotic swirling motion | `strength`, `frequency`        | Wind, magic, chaos       |
| `AttractionBehavior`       | Pulls toward point           | `point`, `strength`, `radius`  | Gravity wells, magnets   |
| `VortexBehavior`           | Spiral motion around point   | `center`, `strength`, `radius` | Tornadoes, portals       |
| `OrbitBehavior`            | Circle spawn point           | `speed`, `radius_variance`     | Orbiting effects         |
| `MouseInteractionBehavior` | 7 mouse modes                | `mode`, `strength`, `radius`   | Interactive particles    |
| `ForceFieldBehavior`       | Static zones                 | `rect`, `field_type`, `angle`  | Wind tunnels, slow zones |

**Behavior Application:**

Behaviors can be:

1. **Emitter-specific** - Added via preset `"behaviors": ["turbulence"]`
2. **Global** - Added via `layer.add_global_behavior(behavior)`
3. **Dynamic** - Added/removed at runtime

**Example: Custom Behavior**

```python
class GravityWellBehavior(ParticleBehavior):
    def __init__(self, wells):
        self.wells = wells  # List of (x, y, strength)

    def apply(self, particle, dt, layer):
        for wx, wy, strength in self.wells:
            dx = wx - particle["x"]
            dy = wy - particle["y"]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 200:
                force = strength / (dist + 1)
                particle["vx"] += (dx / dist) * force
                particle["vy"] += (dy / dist) * force
```

---

## 5. Physics System

### Hybrid Architecture

The engine supports **two physics modes** that can coexist:

#### 5.1 Atmospheric Physics (Default)

**Lightweight, CPU-friendly physics for high particle counts.**

**Properties:**

- Gravity, wind, drag (air resistance)
- Radial acceleration (explosions)
- Tangential acceleration (spiral forces)
- Wall bounce with energy loss
- Rotation and spin

**Implementation:**

```python
# In _update_particles():
particle["vy"] += particle["gravity"]  # Apply gravity
particle["vx"] += particle["wind"]     # Apply wind
particle["vx"] *= (1.0 - particle["drag"])  # Apply drag
particle["x"] += particle["vx"]        # Integrate position
particle["y"] += particle["vy"]
particle["vy"] += particle["gravity"] + self.global_gravity # Apply emitter settings and global environment directly
particle["vx"] += particle["wind"] + self.global_wind
```

**Wall Bounce Algorithm:**

```python
if particle["wall_bounce"]:
    if particle["x"] < 0:
        particle["x"] = 0
        particle["vx"] *= -particle["bounce_factor"]  # Reverse + damping
    elif particle["x"] > width:
        particle["x"] = width
        particle["vx"] *= -particle["bounce_factor"]
    # Same for top/bottom
```

**Performance:** ~0.01ms per particle per frame

---

#### 5.2 Rigid Body Physics (Optional, Pymunk)

**Full collision detection with UI widgets.**

**Activation:**

```python
overlay = GlobalEffectOverlay(parent_window, use_physics=True)
overlay.add_collision_widget(my_button)
overlay.add_target_effect(my_button, "bouncing_ball", collides=True)
```

**Features:**

- Accurate collision response
- Friction and elasticity
- Angular momentum
- Static barriers from widgets

**Physics Bodies:**

Each physics particle gets:

- `pymunk.Body` - Position, velocity, mass
- `pymunk.Circle` - Collision shape
- Collision type IDs (particle=1, barrier=2)

**Collision Handling:**

```python
def on_begin(arbiter, space, data):
    particle_shape = arbiter.shapes[0]
    p = particle_shape.particle_data
    if p["settings"].get("on_collide_effect"):
        layer.trigger_sub_emitter(effect_name, x, y)
    return True
```

**Performance:** ~0.5ms per particle per frame (heavier, use sparingly)

---

### Physics Comparison

| Feature          | Atmospheric     | Rigid Body        |
| ---------------- | --------------- | ----------------- |
| Particle Count   | 2500+           | 500 max           |
| Wall Bounce      | ✅               | ✅                 |
| Widget Collision | ❌               | ✅                 |
| Friction         | ❌               | ✅                 |
| Angular Momentum | ❌               | ✅                 |
| CPU Usage        | Low             | High              |
| Use Case         | Ambient effects | Interactive games |

---

## 6. Emitter Geometries

### 6.1 Point Emitter

**Spawns from a single point.**

```python
"emitter_type": "point"
```

**Calculation:**

```python
x = rect.center().x()
y = rect.center().y()
```

**Use Cases:**

- Explosions
- Single-source bursts
- Widget center effects

---

### 6.2 Rect Emitter

**Spawns randomly within a rectangle.**

```python
"emitter_type": "rect"
```

**Calculation:**

```python
x = random.uniform(rect.left(), rect.right())
y = random.uniform(rect.top(), rect.bottom())
```

**Use Cases:**

- Rain over window
- Snow across screen
- Area-fill effects

---

### 6.3 Circle Emitter

**Spawns within a circular area (uniform distribution).**

```python
"emitter_type": "circle"
```

**Calculation:**

```python
angle = random.uniform(0, 2π)
r = max_radius * sqrt(random())  # Uniform area distribution
x = center_x + r * cos(angle)
y = center_y + r * sin(angle)
```

**Use Cases:**

- Radial bursts
- Circular zones
- Spotlight effects

---

### 6.4 Ring Emitter

**Spawns on circle perimeter (shockwave pattern).**

```python
"emitter_type": "ring"
```

**Calculation:**

```python
angle = random.uniform(0, 2π)
r = max_radius  # Fixed radius
x = center_x + r * cos(angle)
y = center_y + r * sin(angle)
```

**Use Cases:**

- Explosions
- Shockwaves
- Expanding rings

---

### 6.5 Line Emitter

**Spawns along a line segment.**

```python
"emitter_type": "line"
```

**Calculation:**

```python
t = random.random()  # 0.0 to 1.0
x = start_x + t * (end_x - start_x)
y = start_y + t * (end_y - start_y)
```

**Use Cases:**

- Laser sweeps
- Barrier effects
- Edge highlights

---

### 6.6 Cone Emitter (NEW v2.5)

**Directional burst with angular spread.**

```python
"emitter_type": "cone",
"cone_direction": 0,    # Degrees (0=right, 90=down)
"cone_angle": 45        # Spread angle
```

**Calculation:**

```python
x, y = center  # Spawn at center
half_spread = cone_angle / 2
angle = cone_direction + random.uniform(-half_spread, half_spread)
velocity = speed * (cos(angle), sin(angle))
```

**Use Cases:**

- Fire/flamethrowers
- Shotgun blasts
- Directional magic
- Muzzle flashes

---

### 6.7 Grid Emitter (NEW v2.5)

**Spawns in structured grid pattern.**

```python
"emitter_type": "grid",
"grid_rows": 5,
"grid_cols": 5
```

**Calculation:**

```python
cell_w = rect.width / grid_cols
cell_h = rect.height / grid_rows
col = random.randint(0, grid_cols - 1)
row = random.randint(0, grid_rows - 1)
x = rect.left + col * cell_w + random.uniform(0, cell_w)
y = rect.top + row * cell_h + random.uniform(0, cell_h)
```

**Use Cases:**

- Pixel art explosions
- Matrix-style effects
- Tile breaks
- Digital glitches

---

### 6.8 Spiral Emitter (NEW v2.5)

**Spawns along rotating spiral path.**

```python
"emitter_type": "spiral",
"spiral_speed": 0.5  # Radians per emission
```

**Calculation:**

```python
self._spiral_angle += spiral_speed
r = (angle % 2π) / (2π) * max_radius  # Radius grows
x = center_x + r * cos(angle)
y = center_y + r * sin(angle)
```

**Use Cases:**

- Galaxy effects
- DNA helixes
- Vortex portals
- Decorative animations

---

## 7. Particle Shapes

### 7.1 Circle (Default)

**Simple filled circle.**

```python
"shape": "circle"
```

**Rendering:**

```python
painter.drawEllipse(QRectF(-size/2, -size/2, size, size))
```

---

### 7.2 Rectangle

**Filled rectangle.**

```python
"shape": "rect"
```

**Rendering:**

```python
painter.drawRect(QRectF(-size/2, -size/2, size, size))
```

---

### 7.3 Star

**Multi-pointed star with configurable points.**

```python
"shape": "star",
"star_points": 5  # Number of points (min 3)
```

**Rendering:**

```python
# Alternating outer/inner radii create star shape
for i in range(star_points * 2):
    angle = i * (360 / (star_points * 2)) - 90
    radius = size/2 if i % 2 == 0 else size/4
    points.append((cos(angle)*radius, sin(angle)*radius))
painter.drawPolygon(points)
```

---

### 7.4 Bubble

**Circle with radial gradient (3D effect).**

```python
"shape": "bubble"
```

**Rendering:**

```python
gradient = QRadialGradient(0, -size/4, size)
gradient.setColorAt(0, bright_center)
gradient.setColorAt(0.4, particle_color)
gradient.setColorAt(1, transparent)
painter.drawEllipse(...)
```

---

### 7.5 Image (Sprite Sheets)

**Renders image/sprite sheet frame.**

```python
"shape": "image",
"image_path": "assets/particle.png",
"sprite_rows": 4,      # For sprite sheets
"sprite_cols": 4,
"anim_speed": 1.0,     # Frames per game-frame
"tint_image": True     # Apply particle color
```

**Sprite Sheet Logic:**

```python
total_frames = rows * cols
current_frame = int(particle["anim_frame"]) % total_frames
row = current_frame // cols
col = current_frame % cols

frame_w = image.width / cols
frame_h = image.height / rows
source_rect = QRectF(col*frame_w, row*frame_h, frame_w, frame_h)
painter.drawPixmap(target_rect, image, source_rect)
```

**Tinting:**

```python
# v2.5 Optimized Tinting:
# 1. Draw image normally
painter.drawPixmap(target_rect, pix, source_rect)

# 2. Tint using CompositionMode_SourceIn on the main painter
# This colors existing pixels using the image's alpha as a mask
painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
painter.fillRect(target_rect, particle["draw_color"])

# 3. Reset mode for next particle
painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
```

---

### 7.6 Text

**Renders text characters.**

```python
"shape": "text",
"text_chars": "0123456789ABCDEF"
```

**Rendering:**

```python
font.setPixelSize(int(size))
painter.setFont(font)
painter.drawText(rect, Qt.AlignCenter, particle["char"])
```

**Use Cases:**

- Matrix rain
- Damage numbers
- Score popups

---

## 8. Behavior System

### 8.1 Turbulence

**Adds chaotic, noise-like motion.**

```python
"behaviors": ["turbulence"],
"turbulence_strength": 0.3,
"turbulence_freq": 0.05
```

**Algorithm:**

```python
noise_x = sin(x * freq + time) * strength
noise_y = cos(y * freq + time * 0.7) * strength
particle["vx"] += noise_x
particle["vy"] += noise_y
```

---

### 8.2 Orbit

**Particles circle their spawn point.**

```python
"behaviors": ["orbit"],
"orbit_speed": 0.05
```

**Algorithm:**

```python
if not initialized:
    particle["orbit_center"] = (spawn_x, spawn_y)
    particle["orbit_radius"] = size * (1.0 + variance)
    particle["orbit_angle"] = 0

angle += orbit_speed
x = center_x + cos(angle) * radius
y = center_y + sin(angle) * radius
```

---

### 8.3 Vortex

**Spiral motion toward a point.**

```python
"behaviors": ["vortex"],
"vortex_strength": 2.0,
"vortex_radius": 300,
"vortex_center": (400, 300)
```

**Algorithm:**

```python
dx = x - center_x
dy = y - center_y
dist = sqrt(dx² + dy²)

if dist < radius:
    force = strength * (1.0 - dist/radius)
    tangent_x = -dy / dist * force
    tangent_y = dx / dist * force
    particle["vx"] += tangent_x
    particle["vy"] += tangent_y
```

---

### 8.4 Mouse Interaction

**7 modes for mouse-reactive particles.**

```python
overlay.enable_mouse_interaction(
    mode="attract",
    strength=1.0,
    radius=300,
    falloff="smooth",
    click_only=False
)
```

**Modes:**

| Mode      | Effect                     | Algorithm                                |
| --------- | -------------------------- | ---------------------------------------- |
| `attract` | Pull toward mouse          | `force = strength * (1 - dist/radius)`   |
| `repel`   | Push away from mouse       | Same as attract, negative force          |
| `orbit`   | Circle around mouse        | Tangential force perpendicular to radius |
| `vortex`  | Spiral into mouse          | Combine attraction + orbit               |
| `avoid`   | Flee but maintain distance | Strong repel when too close              |
| `tunnel`  | Suck through mouse         | Strong attract, shoot through at center  |
| `chaos`   | Random forces near mouse   | `random.uniform(-1, 1) * force`          |

**Falloff Curves:**

- `linear`: `t = 1 - dist/radius`
- `quadratic`: `t = (1 - dist/radius)²`
- `inverse`: `t = 1 / (1 + dist*0.01)`
- `smooth`: `t² * (3 - 2t)` (smoothstep)

---

### 8.5 Force Fields

**Static zones affecting particles.**

```python
overlay.add_force_field(
    x=100, y=100, width=200, height=200,
    field_type="wind",
    strength=0.5,
    angle=45
)
```

**Types:**

| Type      | Effect                        |
| --------- | ----------------------------- |
| `wind`    | Directional push (uses angle) |
| `slow`    | Viscosity/drag (mud effect)   |
| `attract` | Pull toward center            |
| `repel`   | Push from center              |

---

## 9. Visual Effects

### 9.1 Color System

**Color Palette:**

```python
"color": ["#FF0000", "#00FF00", "#0000FF"]
```

Random selection per particle.

**Color Variance (HSV):**

```python
"hue_variance": 0.1,      # ±10% hue shift
"sat_variance": 0.2,      # ±20% saturation
"val_variance": 0.1       # ±10% value/brightness
```

**Color Curves:**

```python
"color_curve": [
    QColor("#FFFF00"),  # Yellow at birth
    QColor("#FF6600"),  # Orange midlife
    QColor("#FF0000")   # Red at death
]
```

---

### 9.2 Alpha System

**Alpha Curves:**

```python
"alpha_curve": [0, 128, 255, 255, 128, 0]
```

**Fade Helpers (NEW v2.5):**

```python
"fade_in_time": 10,   # Auto-generate fade in over 10 frames
"fade_out_time": 20   # Auto-generate fade out over 20 frames
```

Algorithm generates curve: `[0...255] → [255...255] → [255...0]`

---

### 9.3 Scale System

**Scale Curves:**

```python
"scale_curve": [0.5, 1.0, 1.5, 2.0, 1.0]
```

Interpolates particle size over lifetime:

```python
progress = life / max_life
scale = interpolate_curve(scale_curve, progress)
current_size = base_size * scale
```

---

### 9.4 Trails

**Trail rendering behind particles.**

```python
"trail_length": 10,      # Max trail points
"trail_width": 2,        # Line thickness
"trail_opacity": 100     # 0-255 alpha
```

**Implementation:**

```python
# Each frame append position
particle["trail"].append((particle["x"], particle["y"]))
if len(trail) > trail_length:
    trail = trail[-trail_length:]

# Positions are stored as QPointF objects during update
painter.drawPolyline(particle["trail"]) # Single C++ call
```

---

### 9.5 Blend Modes

**Compositing modes for rendering.**

```python
"blend_mode": "normal"  # or "add"
```

**Normal:** Standard alpha blending (default)
**Add:** Additive blending (particles brighten each other, glowing effect)

```python
if blend_mode == "add":
    painter.setCompositionMode(CompositionMode_Plus)
```

---

### 9.6 Rotation

**Particle rotation system.**

```python
"spin_min": -5,     # Degrees per frame
"spin_max": 5,
"align_rotation": False  # Rotate to face direction of travel
```

**Standard Rotation:**

```python
particle["rotation"] += particle["spin"]
```

**Aligned Rotation:**

```python
particle["rotation"] = atan2(particle["vy"], particle["vx"]) * 180/π
```

---

### 9.7 Stretch/Squash (NEW v2.5)

**Motion blur effect for fast particles.**

```python
"stretch_factor": 3.0  # Elongate 3x in direction of travel
```

**Algorithm:**

```python
if stretch_factor != 1.0 and speed > 0.1:
    painter.scale(stretch_factor, 1.0 / stretch_factor)
    # Particle stretched in direction of rotation
```

**Works with:** Circle, Rectangle, Image shapes

---

## 10. Performance Optimization

### 10.1 Flattened Particle Data (v2.5)

**Problem:** Dictionary lookups in tight loops.

**Before (v2.0):**

```python
for particle in particles:
    s = particle["settings"]
    particle["vy"] += s.get("gravity", 0.5)  # Dict lookup every frame
    particle["vx"] += s.get("wind", 0.0)      # Dict lookup every frame
    # ... 30+ more lookups
```

**After (v2.5):**

```python
# At spawn time:
particle["gravity"] = settings.get("gravity", 0.5)  # Once
particle["wind"] = settings.get("wind", 0.0)        # Once

# During update:
for particle in particles:
    particle["vy"] += particle["gravity"]  # Direct access
    particle["vx"] += particle["wind"]     # Direct access
```

**Performance Impact:**

- Before: ~3.6M dict lookups/sec @ 2000 particles
- After: ~360K dict lookups/sec @ 2000 particles
- **10x reduction in lookup overhead**

**Flattened Properties:**

```python
# Physics (accessed every frame)
"gravity", "wind", "drag"
"radial_accel", "tangential_accel"
"wall_bounce", "bounce_factor"
"align_rotation"

# Visuals (accessed every frame)
"shape", "blend_mode"
"sprite_rows", "sprite_cols", "tint_image"
"star_points", "stretch_factor"

# Trails (accessed if trail enabled)
"trail_length", "trail_width", "trail_opacity"
```

---

### 10.2 Off-Screen Culling

**Particles outside viewport are removed.**

```python
PADDING = 200  # Allow trails to extend off-screen

if (particle["y"] > height + PADDING or 
    particle["y"] < -PADDING or
    particle["x"] < -PADDING or 
    particle["x"] > width + PADDING):
    remove_particle()
```

---

### 10.3 Render Optimizations

**QPainter Hints:**

```python
painter.setRenderHint(QPainter.RenderHint.Antialiasing)
painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
```

**Minimal State Changes:**

- Cache QPixmap loads
- Reuse QColor objects
- Batch similar particles (future optimization)

---

### 10.4 Memory Management

**Particle Pooling (not yet implemented):**
Future optimization could reuse particle dicts instead of creating new ones.

**Current Strategy:**

- Create particle dicts on spawn
- Python GC handles cleanup
- No memory leaks observed in testing

---

### 10.5 Performance Targets

| Particle Count | Target FPS | Actual FPS (v2.5) | CPU Usage |
| -------------- | ---------- | ----------------- | --------- |
| 500            | 60         | 60                | ~5%       |
| 1000           | 60         | 60                | ~10%      |
| 2000           | 60         | 58-60             | ~20%      |
| 2500           | 60         | 55-60             | ~25%      |
| 3000           | 50+        | 45-55             | ~30%      |

**Test System:** Intel i7-9700K, 16GB RAM, Python 3.10, PySide6.6

---

## 11. Integration Guide

### 11.1 Basic Setup

**Step 1: Create overlay**

```python
from particle_engine_supreme import GlobalEffectOverlay

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create overlay after UI setup
        self.particle_overlay = GlobalEffectOverlay(self, use_physics=True)
```

**Step 2: Add effects**

```python
# Global effect (entire window)
self.particle_overlay.add_global_effect("snow", count=3)

# Widget-targeted effect
self.particle_overlay.add_target_effect(
    self.submit_button,
    "fire",
    count=5
)
```

**Step 3: Clean up (optional)**

```python
def closeEvent(self, event):
    self.particle_overlay.clear_effects()
    super().closeEvent(event)
```

---

### 11.2 Widget Collision Setup

**For particles to bounce off buttons, labels, etc:**

```python
# Register widgets as collision barriers
self.particle_overlay.add_collision_widget(self.label)
self.particle_overlay.add_collision_widget(self.button)

# Add physics-enabled particles
self.particle_overlay.add_global_effect(
    "bouncing_balls",
    collides=True,
    elasticity=0.8,
    friction=0.3
)
```

---

### 11.3 Mouse Interaction Setup

**Global mouse effects:**

```python
# All particles attracted to mouse
self.particle_overlay.enable_mouse_interaction(
    mode="attract",
    strength=1.0,
    radius=300,
    falloff="smooth"
)

# Change mode dynamically
self.particle_overlay.set_mouse_mode("repel")

# Disable
self.particle_overlay.disable_mouse_interaction()
```

---

### 11.4 Dynamic Effects

**Trigger bursts on demand:**

```python
def on_button_click(self):
    # Get button center
    center = self.button.rect().center()
    global_pos = self.button.mapToGlobal(center)
    local_pos = self.particle_overlay.mapFromGlobal(global_pos)

    # Trigger burst
    self.particle_overlay.trigger_burst(
        local_pos.x(),
        local_pos.y(),
        "explosion",
        count=30
    )
```

---

### 11.5 Force Field Zones

**Add wind tunnels, slow zones, etc:**

```python
# Wind blowing left-to-right
wind_zone = self.particle_overlay.add_force_field(
    x=100, y=200,
    width=300, height=100,
    field_type="wind",
    strength=2.0,
    angle=0  # Degrees
)

# Remove later
self.particle_overlay.layer.global_behaviors.remove(wind_zone)
```

---

### 11.6 Attraction Points

**Particles pulled toward widgets:**

```python
# Static attraction
self.particle_overlay.add_attraction_point(400, 300, strength=1.0)

# Follow a widget
self.health_attraction = self.particle_overlay.add_attraction_point(
    0, 0,
    strength=0.8,
    radius=200,
    widget=self.health_bar
)

# Update in your app's update loop
def update_effects(self):
    self.particle_overlay.update_attraction_point(self.health_attraction)
```

---

## 12. Preset System

### 12.1 Preset Structure

Presets are dictionaries in `particle_presets.py`:

```python
EFFECT_PRESETS = {
    "rain": {
        "count": 3,
        "interval": 1,
        "emitter_type": "rect",
        "shape": "rect",
        "size_min": 2,
        "size_max": 4,
        "speed_min": 10,
        "speed_max": 15,
        "angle_min": 85,
        "angle_max": 95,
        "gravity": 0.5,
        "color": ["#4488FF", "#6699FF"],
        "life_min": 120,
        "life_max": 180
    }
}
```

---

### 12.2 Creating Custom Presets

**Add to `particle_presets.py`:**

```python
"my_custom_effect": {
    "emitter_type": "cone",
    "cone_direction": 0,
    "cone_angle": 30,
    "count": 10,
    "shape": "star",
    "star_points": 5,
    "size_min": 5,
    "size_max": 10,
    "speed_min": 5,
    "speed_max": 10,
    "gravity": 0.2,
    "drag": 0.05,
    "color": ["#FFFF00", "#FF6600"],
    "blend_mode": "add",
    "fade_in_time": 5,
    "fade_out_time": 15,
    "behaviors": ["turbulence"],
    "turbulence_strength": 0.5
}
```

**Use in code:**

```python
overlay.add_target_effect(widget, "my_custom_effect")
```

---

### 12.3 Runtime Overrides

**Override any preset parameter:**

```python
overlay.add_target_effect(
    widget,
    "fire",
    count=20,           # Override count
    gravity=-0.5,       # Override gravity
    color=["#00FF00"]   # Override color
)
```

---

### 12.4 Fully Custom Effects

**Skip presets entirely:**

```python
overlay.add_custom_effect(
    target=self,
    emitter_type="grid",
    grid_rows=10,
    grid_cols=10,
    shape="circle",
    size_min=3,
    size_max=3,
    speed_min=1,
    speed_max=5,
    gravity=0.3,
    color=["#FF00FF"],
    life_min=60,
    life_max=120
)
```

---

## 13. Advanced Features

### 13.1 Sub-Emitter Chains

**Particles trigger effects at spawn, collision, or death.**

```python
"rocket": {
    "on_spawn_effect": "sparkle_trail",   # Continuous trail
    "on_collide_effect": "spark_burst",   # Impact effect
    "on_death_effect": "explosion"        # Final explosion
}
```

**Execution:**

- `on_spawn_effect` - Triggered every time a particle is born
- `on_collide_effect` - Triggered when particle hits widget (requires `collides=True`)
- `on_death_effect` - Triggered when particle lifetime expires

---

### 13.2 Velocity Inheritance (NEW v2.5)

**Particles inherit widget velocity.**

```python
"car_exhaust": {
    "inherit_velocity": 0.7,  # Inherit 70% of widget velocity
    "speed_min": 2,
    "speed_max": 4
}
```

**Algorithm:**

```python
# Track widget position
if hasattr(emitter, '_last_widget_pos'):
    current_pos = widget.mapToGlobal(widget.rect().center())
    widget_vx = (current_pos.x() - last_pos.x()) * inherit_velocity
    widget_vy = (current_pos.y() - last_pos.y()) * inherit_velocity
    particle["vx"] += widget_vx
    particle["vy"] += widget_vy
```

**Use Cases:**

- Moving vehicle trails
- Draggable widget effects
- Animated UI particles

---

### 13.3 Accumulation

**Particles pile up instead of dying (snow effect).**

```python
"accumulate": True,
"collides": True  # Requires physics
```

**Behavior:**

- Particles slow down when hitting ground
- Stop moving but remain visible
- Slowly shrink over extended lifetime

---

### 13.4 Sprite Sheet Animation

**Multi-frame sprite animation.**

```python
"shape": "image",
"image_path": "assets/flame_sheet.png",
"sprite_rows": 4,
"sprite_cols": 4,
"anim_speed": 0.5,        # Half speed
"random_start_frame": True # Randomize start
```

**Frame Calculation:**

```python
total_frames = rows * cols
particle["anim_frame"] += particle["anim_speed"]
current_frame = int(particle["anim_frame"]) % total_frames

row = current_frame // cols
col = current_frame % cols
```

---

### 13.5 Curve Interpolation

**Smooth value transitions over lifetime.**

**Linear Interpolation:**

```python
curve = [0, 128, 255, 128, 0]
progress = particle["life"] / particle["max_life"]  # 0.0 to 1.0
index = progress * (len(curve) - 1)
value = interpolate(curve[floor(index)], curve[ceil(index)], frac(index))
```

**Color Interpolation:**

```python
color_curve = [QColor("#FFFF00"), QColor("#FF0000")]
# Interpolates R, G, B separately
```

---

## 14. Troubleshooting

### 14.1 Common Issues

**Issue: Particles not visible**

- Check overlay is raised: `overlay.raise_()`
- Verify alpha not 0: Check `alpha_curve` or `fade_out_time`
- Ensure particles spawning: Check `count`, `interval`, `duration`

**Issue: Low FPS**

- Reduce particle count: `count=1` or `interval=3`
- Disable physics: `collides=False`
- Reduce trail length: `trail_length=5`
- Simplify behaviors: Remove turbulence/vortex

**Issue: Particles not following mouse**

- Verify mouse interaction enabled: `enable_mouse_interaction()`
- Check radius: Increase `mouse_radius=500`
- Test click-only: Set `click_only=False`

**Issue: Widget collision not working**

- Verify physics enabled: `GlobalEffectOverlay(parent, use_physics=True)`
- Check pymunk installed: `pip install pymunk`
- Register widget: `add_collision_widget(widget)`
- Enable collision: `collides=True` in preset

**Issue: Effects not clearing**

- Call `clear_effects()` before adding new effects
- Manually stop emitters: `emitter.active = False`
- Set duration: `duration=60` (60 frames = 1 second)

---

### 14.2 Debugging Tools

**Particle Count:**

```python
count = overlay.get_particle_count()
print(f"Active particles: {count}")
```

**Emitter Count:**

```python
count = overlay.get_emitter_count()
print(f"Active emitters: {count}")
```

**Manual Inspection:**

```python
for p in overlay.layer.particles:
    print(f"Pos: ({p['x']}, {p['y']}), Life: {p['life']}/{p['max_life']}")
```

---

### 14.3 Performance Profiling

**Using cProfile:**

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()

# Run effect for 5 seconds

profiler.disable()
profiler.print_stats(sort='cumtime')
```

**Key Metrics:**

- `_update_loop` - Should be <16ms for 60 FPS
- `_draw_particle` - Should be <0.01ms per particle
- `apply` (behaviors) - Should be <0.01ms per particle

---

## 15. API Reference

### 15.1 GlobalEffectOverlay

**Constructor:**

```python
GlobalEffectOverlay(parent_window: QWidget, use_physics: bool = True)
```

**Methods:**

```python
add_global_effect(effect_name: str, **kwargs) -> None
set_global_environment(wind: float, gravity: float) -> None
add_target_effect(target_widget: QWidget, effect_name: str, **kwargs) -> None
add_custom_effect(target: QWidget | QRect, **settings) -> None
trigger_burst(x: int, y: int, effect: str = "explosion", **kwargs) -> None
add_force_field(x: int, y: int, width: int, height: int, 
                field_type: str = "wind", strength: float = 0.5, 
                angle: float = 0) -> ForceFieldBehavior
add_attraction_point(x: int, y: int, strength: float = 0.5, 
                     radius: int | None = None, 
                     widget: QWidget | None = None) -> AttractionBehavior
update_attraction_point(attraction_behavior: AttractionBehavior) -> None
enable_mouse_interaction(mode: str = "attract", strength: float = 1.0, 
                         radius: int = 300, falloff: str = "smooth", 
                         click_only: bool = False) -> None
disable_mouse_interaction() -> None
set_mouse_mode(mode: str) -> None
add_collision_widget(widget: QWidget) -> None
remove_collision_widget(widget: QWidget) -> None
clear_effects() -> None
pause() -> None
resume() -> None
set_mouse_interactive(enabled: bool = True, effect: str = "splash") -> None
get_particle_count() -> int
get_emitter_count() -> int
```

---

### 15.2 VisualEffectLayer

**Key Attributes:**

```python
particles: List[Dict]           # Active particle list
emitters: List[ParticleEmitter] # Active emitter list
global_behaviors: List[ParticleBehavior]  # Global behaviors
physics_engine: PymunkPhysicsEngine | None
timer: QTimer                    # 60 FPS update timer
```

**Methods:**

```python
add_emitter(preset: str, target: QWidget | QRect, **kwargs) -> None
add_global_behavior(behavior: ParticleBehavior) -> None
trigger_sub_emitter(preset_name: str, x: float, y: float) -> None
burst_at(x: float, y: float, effect: str = "splash") -> None
enable_mouse_interaction(mode: str, ...) -> None
disable_mouse_interaction() -> None
set_mouse_mode(mode: str) -> None
update_mouse_state(pos: QPoint, pressed: bool) -> None
```

---

### 15.3 ParticleEmitter

**Constructor:**

```python
ParticleEmitter(preset_name: str, target_source: QWidget | QRect, 
                overrides: Dict | None = None)
```

**Attributes:**

```python
active: bool                    # Is emitter spawning particles
settings: Dict                  # Merged preset + overrides
palette: List[QColor]           # Color palette
cached_pixmap: QPixmap | None   # Cached image
behaviors: List[ParticleBehavior]  # Emitter-specific behaviors
```

**Methods:**

```python
emit(layer: VisualEffectLayer, particle_list: List) -> None
get_spawn_pos(layer: VisualEffectLayer) -> Tuple[float, float, QRect]
```

---

### 15.4 Configuration Parameters

**Complete parameter list for presets/overrides:**

```python
# Spawn Settings
count: int = 1
interval: int = 1
start_delay: int = 0
duration: int = -1  # -1 = infinite

# Emitter Geometry
emitter_type: str = "rect"  # rect, circle, ring, line, point, cone, grid, spiral
cone_direction: float = 0
cone_angle: float = 45
grid_rows: int = 3
grid_cols: int = 3
spiral_speed: float = 0.5

# Lifetime
life_min: int = 50
life_max: int = 100

# Physics Basics
gravity: float = 0.5
wind: float = 0.0
drag: float = 0.0

# Advanced Physics
radial_accel: float = 0.0
tangential_accel: float = 0.0
align_rotation: bool = False
inherit_velocity: float = 0.0

# Velocity
speed_min: float = 1.0
speed_max: float = 3.0
angle_min: float = 0
angle_max: float = 360

# Collision / Walls
collides: bool = False
elasticity: float = 0.5
friction: float = 0.5
wall_bounce: bool = False
bounce_factor: float = 0.8

# Appearance
shape: str = "circle"  # circle, rect, image, text, star, bubble
size_min: float = 5
size_max: float = 10
color: List[str] = ["#FFFFFF"]

# Color Variance
hue_variance: float = 0.0
sat_variance: float = 0.0
val_variance: float = 0.0

# Sprite Animation
sprite_rows: int = 1
sprite_cols: int = 1
anim_speed: float = 1.0
random_start_frame: bool = False

# Animation Curves
spin_min: float = 0
spin_max: float = 0
scale_curve: List[float] | None = None
alpha_curve: List[int] | None = None
color_curve: List[QColor] | None = None

# Fade Helpers
fade_in_time: int = 0
fade_out_time: int = 0

# Rendering
blend_mode: str = "normal"  # normal, add
trail_length: int = 0
trail_width: int = 2
trail_opacity: int = 100
stretch_factor: float = 1.0

# Shape Specifics
star_points: int = 5
image_path: str = ""
tint_image: bool = True
text_chars: str = "0123456789"

# Logic
accumulate: bool = False
on_spawn_effect: str | None = None
on_collide_effect: str | None = None
on_death_effect: str | None = None

# Behaviors
behaviors: List[str] = []  # ["turbulence", "orbit", "vortex", "mouse_interaction"]

# Behavior Parameters
turbulence_strength: float = 0.3
turbulence_freq: float = 0.05
orbit_speed: float = 0.05
vortex_strength: float = 2.0
vortex_radius: float = 300
vortex_center: Tuple[float, float] = (0, 0)
attraction_strength: float = 0.5
attraction_radius: float = 200

# Mouse Interaction
mouse_mode: str = "attract"  # attract, repel, orbit, vortex, avoid, tunnel, chaos
mouse_strength: float = 1.0
mouse_radius: float = 300
mouse_falloff: str = "smooth"  # linear, quadratic, inverse, smooth
mouse_click_only: bool = False
```

---

## Appendix A: Version History

### v2.5 (Current)

- ✅ Flattened particle data (10x performance improvement)
- ✅ Cone emitter (directional bursts)
- ✅ Grid emitter (pixel patterns)
- ✅ Spiral emitter (vortex spawning)
- ✅ Fade in/out helpers
- ✅ Stretch/squash (motion blur)
- ✅ Velocity inheritance
- ✅ Sub-emitter on spawn
- ✅ Attraction point widget API

### v2.1

- Hybrid physics system
- Wall bounce
- Mouse interaction (7 modes)
- Force fields
- Sprite sheet support

### v2.0

- Initial release
- Basic emitters (rect, circle, ring, line, point)
- 6 particle shapes
- Color/alpha/scale curves
- Trails and blend modes

---

## Appendix B: Dependencies

**Required:**

- Python 3.8+
- PySide6 6.0+

**Optional:**

- pymunk 6.0+ (for rigid body physics)

**Installation:**

```bash
pip install PySide6
pip install pymunk  # Optional
```

---

**Third-party Libraries:**

- PySide6 - GPL/Commercial
- pymunk - MIT License

---
