# particle_engine_supreme/particle_utilities.py
"""
# Copyright (c) 2025 Joshua Kitchens
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""

from PySide6.QtGui import QColor


def lerp(a, b, t):
    """Linear interpolation between two values."""
    return a + (b - a) * t

def interpolate_curve(curve, progress):
    """
    Smoothly interpolate through a list of values based on progress (0.0 - 1.0).
    Supports both numeric and color curves.
    """
    if not curve or len(curve) == 0:
        return 1.0 if isinstance(curve, list) else QColor(255, 255, 255)
    
    if len(curve) == 1:
        return curve[0] if not isinstance(curve[0], str) else QColor(curve[0])
    
    max_idx = len(curve) - 1
    pos = progress * max_idx
    idx = int(pos)
    
    if idx >= max_idx:
        val = curve[-1]
        return val if not isinstance(val, str) else QColor(val)
    
    t = pos - idx
    
    if isinstance(curve[idx], str):
        c1 = QColor(curve[idx])
        c2 = QColor(curve[idx + 1])
        return QColor(
            int(lerp(c1.red(), c2.red(), t)),
            int(lerp(c1.green(), c2.green(), t)),
            int(lerp(c1.blue(), c2.blue(), t)),
            int(lerp(c1.alpha(), c2.alpha(), t))
        )
    
    return lerp(curve[idx], curve[idx + 1], t)