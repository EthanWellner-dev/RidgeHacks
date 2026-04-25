"""
run.py - Launcher script for Dynamic ChemEngine.
Handles pygame installation and starts the game.
"""

import sys
import subprocess


def check_pygame():
    """Check if pygame is installed, install if needed."""
    try:
        import pygame
        import mendeleev
        print(f"✓ pygame {pygame.version.vernum} is installed")
        print(f"✓ mendeleev {mendeleev.__version__} is installed")
        return True
    except ImportError as e:
        print(f"pygame or mendeleev is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mendeleev"])
            print("✓ pygame installed successfully")
            print("✓ mendeleev installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install pygame or mendeleev")
            print("Please install manually: pip install pygame mendeleev")
            return False


def main():
    """Main launcher."""
    print("=" * 60)
    print("Dynamic ChemEngine - Interactive Chemistry Simulator")
    print("=" * 60)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_pygame():
        sys.exit(1)
    
    print("\nAll dependencies satisfied!")
    print("\nStarting game...\n")
    
    # Import and run
    try:
        from main import GameApplication
        app = GameApplication(width=1200, height=800)
        app.run()
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
