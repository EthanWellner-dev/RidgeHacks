"""
main.py - Main game application with event loop and rendering.
Entry point for the Dynamic ChemEngine.
"""

import sys


from game.gameApplication import GameApplication

def main():
    try:
        app = GameApplication(width=1200, height=800)
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()