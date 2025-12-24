"""
Particle Engine Supreme
A high-performance, physics-enabled particle system for PyQt6.
"""

__version__ = "1.3.0"
__author__ = "Joshua Kitchens"

from .effect_overlay import GlobalEffectOverlay
from .particle_engine import VisualEffectLayer

from .particle_emitter import ParticleEmitter
from .physics_engine import PymunkPhysicsEngine

from .particle_presets import EFFECT_PRESETS
from .particle_data import DEFAULT_PROFILE

try:
    from .particle_behaviors import (
        ParticleBehavior,
        ForceFieldBehavior,
        TurbulenceBehavior,
        MouseInteractionBehavior,
        OrbitBehavior,
        VortexBehavior,
        AttractionBehavior
    )
except ImportError:
    pass

from .particle_utilities import interpolate_curve, lerp

__all__ = [
    "GlobalEffectOverlay",
    "VisualEffectLayer",
    "ParticleEmitter",
    "PymunkPhysicsEngine",
    "EFFECT_PRESETS",
    "DEFAULT_PROFILE",
    "ParticleBehavior",
    "ForceFieldBehavior",
    "TurbulenceBehavior",
    "MouseInteractionBehavior",
    "OrbitBehavior",
    "VortexBehavior",
    "AttractionBehavior",
    "interpolate_curve",
    "lerp",
]