"""
FX Creator Studio
The visual editor suite for Particle Engine Supreme.
"""

__version__ = "1.3.0"
__author__ = "Joshua Kitchens"

from .creator import ParticleEditor

from .components import CurveWidget

from .constants import (
    TOOLTIPS, 
    KNOWN_PRESETS, 
    EMITTER_TYPES, 
    MOUSE_MODES, 
    FALLOFF_MODES
)

from .tabs import (
    PhysicsTab,
    VisualsTab,
    CurvesTab,
    BehaviorsTab
)

def launch():
    """
    Start the FX Creator standalone window.
    Usage:
        import fx_creator
        fx_creator.launch()
    """
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    window = ParticleEditor()
    window.show()
    
    if not QApplication.instance().activeWindow(): 
        sys.exit(app.exec())
    else:
        app.exec()

__all__ = [
    "ParticleEditor",
    "CurveWidget",
    "PhysicsTab",
    "VisualsTab",
    "CurvesTab",
    "BehaviorsTab",
    "TOOLTIPS",
    "KNOWN_PRESETS",
    "EMITTER_TYPES",
    "MOUSE_MODES",
    "FALLOFF_MODES",
    "launch"
]