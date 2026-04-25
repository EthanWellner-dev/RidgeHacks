"""
verify_imports.py - Verify all modules import correctly.
"""

import sys
import traceback


def verify_module(module_name, description=""):
    """Verify a module imports successfully."""
    try:
        __import__(module_name)
        print(f"✓ {module_name:<20} {description}")
        return True
    except ImportError as e:
        print(f"✗ {module_name:<20} FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ {module_name:<20} ERROR: {e}")
        return False


def main():
    """Verify all imports."""
    print("=" * 70)
    print("Dynamic ChemEngine - Import Verification")
    print("=" * 70)
    print()
    
    modules = [
        # Core chemistry
        ("chemical", "Chemical substances"),
        ("reaction", "Reversible reactions"),
        ("chemical_state", "State management"),
        ("flask", "Main container"),
        
        # Particles
        ("particle", "Individual particles"),
        ("particle_emitter", "Particle spawning"),
        
        # UI
        ("dropper", "Chemical dropper UI"),
        ("thermometer", "Temperature gauge"),
        ("hotplate", "Heat control"),
        
        # Game logic
        ("challenge", "Challenge system"),
        ("game_mode", "Game orchestration"),
        ("rigid_body", "Physics bodies"),
        
        # Rendering & main
        ("config", "Configuration"),
        ("pygame_renderer", "Pygame rendering"),
        ("main", "Game application"),
        ("run", "Launcher"),
    ]
    
    print("Core Modules:")
    print("-" * 70)
    
    results = []
    for module, desc in modules:
        result = verify_module(module, desc)
        results.append(result)
    
    print()
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} modules imported successfully")
    print("=" * 70)
    
    if all(results):
        print("\n✓ ALL IMPORTS SUCCESSFUL - Game is ready to run!")
        print("\nTo start the game:")
        print("  python run.py")
        return 0
    else:
        print("\n✗ Some imports failed. See errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
