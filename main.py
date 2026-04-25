"""
main.py - Main game application with event loop and rendering.
Entry point for the Dynamic ChemEngine.
"""

import pygame
import sys
from enum import Enum

from pygame_renderer import PygameRenderer
from game.game_mode import GameMode
from game.challenge import ChallengeLibrary
from chemistry.chemical import Chemical
from chemistry.flask import Flask
from game.dropper import Dropper
from game.thermometer import Thermometer
from game.hotplate import HotPlate
from chemistry.particle_emitter import ParticleEmitter
import json
import os


class AppState(Enum):
    """Application states."""
    MENU = 1
    SANDBOX = 2
    CHALLENGE = 3
    PAUSED = 4
    QUIT = 5


class GameApplication:
    """
    Main game application orchestrating all systems.
    """
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize game application.
        
        Args:
            width: Window width
            height: Window height
        """
        self.width = width
        self.height = height
        
        # Rendering
        self.renderer = PygameRenderer(width, height)
        
        # Game state
        self.state = AppState.MENU
        self.game_mode = None
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        # Menu state
        self.menu_selected = 0
        self.menu_options = ["Sandbox Mode", "Challenge Mode", "Quit"]
    
    def initialize(self) -> None:
        """Initialize the application."""
        self.renderer.initialize()
        print("Dynamic ChemEngine initialized")
        print(f"Window: {self.width}x{self.height}")
        print("Press UP/DOWN to navigate menu, ENTER to select")
    
    def setup_sandbox_mode(self) -> None:
        """Setup sandbox mode with free chemistry experimentation."""
        print("\n=== Starting Sandbox Mode ===")
        
        # Create flask (centered)
        flask = Flask(1.0, max_temperature=373.15)
        flask.bounds = {
            'x': int(self.width // 2 - 200),
            'y': 100,
            'width': 400,
            'height': 500
        }
        
        # Create some common chemicals
        water = Chemical("H2O", [("H", 2), ("O", 1)], 0.0, "#87CEEB", -285.8)      # Light blue
        acid = Chemical("H2SO4", [("H", 2), ("S", 1), ("O", 4)], 0.0, "#FF0000", -813)       # Red
        base = Chemical("NaOH", [("Na", 1), ("O", 1), ("H", 1)], 0.0, "#0000FF", -427)        # Blue
        gas = Chemical("O2", [("O", 2)], 0.0, "#87CEEB", 0)              # Light blue
        
        # Create droppers
        # Place droppers in a left-side column
        left_x = 40
        start_y = 140
        spacing_y = 110
        droppers = [
            Dropper(left_x, start_y + 0 * spacing_y, water, 0.2, width=80, height=90, label="Water"),
            Dropper(left_x, start_y + 1 * spacing_y, acid, 0.1, width=80, height=90, label="Acid"),
            Dropper(left_x, start_y + 2 * spacing_y, base, 0.1, width=80, height=90, label="Base"),
            Dropper(left_x, start_y + 3 * spacing_y, gas, 0.05, width=80, height=90, label="O₂"),
        ]
        
        # Create thermometer
        thermometer = Thermometer(850, 100, -10, 120, width=50, height=300)
        
        # Create hotplate
        hotplate = HotPlate(950, 250, max_heat_output=50)
        
        # Create particle emitter for effects
        emitter = ParticleEmitter(200, 300, spawn_rate=0, velocity_magnitude=150, 
                                 color_hex="#FF8800", lifetime=2.0)
        flask.add_particle_emitter(emitter)
        
        # Setup game mode
        self.game_mode = GameMode()
        self.game_mode.initialize_sandbox(flask, droppers, thermometer, hotplate)
        
        print("Sandbox mode ready:")
        print("- Click droppers to add chemicals")
        print("- Click hotplate to toggle heating")
        print("- SPACE to pause, ESC to return to menu")
    
    def setup_challenge_mode(self, challenge_index: int = 0) -> None:
        """
        Setup challenge mode.
        
        Args:
            challenge_index: Which challenge to load (0-2)
        """
        challenges = [
            ChallengeLibrary.create_color_shift_challenge(),
            ChallengeLibrary.create_gas_production_challenge(),
            ChallengeLibrary.create_equilibrium_balance_challenge(),
        ]
        
        challenge = challenges[min(challenge_index, len(challenges) - 1)]
        
        print(f"\n=== Starting Challenge: {challenge.name} ===")
        print(f"Objective: {challenge.description}")
        
        # Setup UI
        thermometer = Thermometer(850, 100, -10, 120, width=50, height=300)
        hotplate = HotPlate(950, 250, max_heat_output=50)
        
        # Setup game mode
        self.game_mode = GameMode()
        self.game_mode.initialize_challenge(challenge, thermometer, hotplate)

        # Center the flask for the challenge view
        if self.game_mode and self.game_mode.flask:
            self.game_mode.flask.bounds = {
                'x': int(self.width // 2 - 200),
                'y': 100,
                'width': 400,
                'height': 500
            }
        
        print("Challenge started! Use hotplate to control temperature.")
        print("SPACE to pause, ESC to return to menu")
        # Load available chemicals from save.json (only those set to true)
        save_path = os.path.join(os.getcwd(), 'save.json')
        molecules = {}
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                molecules = saved.get('chemicals', {}).get('molecules', {})
        except Exception:
            molecules = {}

        # Map known molecule names to basic Chemical definitions (fallback simple values)
        known = {
            'H2O': Chemical('H2O', [('H',2),('O',1)], 0.0, '#87CEEB', -285.8),
            'HCl': Chemical('HCl', [('H',1),('Cl',1)], 0.0, '#FF6666', -92.3),
            'NH3': Chemical('NH3', [('N',1),('H',3)], 0.0, '#CCCCFF', -45.9),
            'NaOH': Chemical('NaOH', [('Na',1),('O',1),('H',1)], 0.0, '#AAAAFF', -137.1),
            'O2': Chemical('O2', [('O',2)], 0.0, '#87CEEB', 0.0)
        }

        left_x = 40
        start_y = 140
        spacing_y = 110
        challenge_droppers = []
        idx = 0
        for name, enabled in molecules.items():
            if not enabled:
                continue
            chem = known.get(name)
            if not chem:
                chem = Chemical(name, [], 0.0, '#808080', 0.0)
            challenge_droppers.append(Dropper(left_x, start_y + idx * spacing_y, chem, 0.1, width=80, height=90, label=name))
            idx += 1

        # Attach droppers to the game mode so user can add reagents in challenge
        self.game_mode.droppers = challenge_droppers
        # Ensure UI elements include droppers
        for d in challenge_droppers:
            self.game_mode.ui_elements.insert(0, d)

        # Position the draggable pH strip in the right sidebar area
        sidebar_w = 300
        sidebar_x = int(self.width - sidebar_w - 20)
        if hasattr(self.game_mode, 'ph_strip') and self.game_mode.ph_strip is not None:
            self.game_mode.ph_strip['x'] = sidebar_x + 20
            self.game_mode.ph_strip['y'] = 120
    
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = AppState.QUIT
            
            elif event.type == pygame.KEYDOWN:
                if self.state == AppState.MENU:
                    self.handle_menu_input(event.key)
                elif self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
                    self.handle_game_input(event.key)
                elif self.state == AppState.PAUSED:
                    self.handle_pause_input(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left-click handling for menu and game
                if self.state == AppState.MENU:
                    self.handle_menu_mouse_click(event.pos)
                elif self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
                    # notify game mode of mouse down
                    self.game_mode.handle_input({'type': 'mouse_down', 'x': event.pos[0], 'y': event.pos[1], 'button': event.button})

            elif event.type == pygame.MOUSEBUTTONUP:
                # Mouse button released
                if self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
                    self.game_mode.handle_input({'type': 'mouse_up', 'x': event.pos[0], 'y': event.pos[1], 'button': event.button})

            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel scrolling (vertical) - forward to game mode for challenge objectives
                if self.state in [AppState.SANDBOX, AppState.CHALLENGE] and self.game_mode:
                    self.game_mode.handle_input({'type': 'mouse_wheel', 'y': event.y})
            
            elif event.type == pygame.MOUSEMOTION:
                if self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
                    self.handle_mouse_move(event.pos)
    
    def handle_menu_input(self, key: int) -> None:
        """Handle menu navigation input."""
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
        
        elif key == pygame.K_RETURN:
            if self.menu_selected == 0:
                self.setup_sandbox_mode()
                self.state = AppState.SANDBOX
            elif self.menu_selected == 1:
                self.setup_challenge_mode(0)
                self.state = AppState.CHALLENGE
            elif self.menu_selected == 2:
                self.running = False
                self.state = AppState.QUIT
    
    def handle_game_input(self, key: int) -> None:
        """Handle in-game input."""
        if key == pygame.K_SPACE:
            self.state = AppState.PAUSED
            print("Game paused")
        
        elif key == pygame.K_ESCAPE:
            self.state = AppState.MENU
            self.menu_selected = 0
            print("Returning to menu")
        
        elif key == pygame.K_r:
            self.game_mode.handle_input({'type': 'key_press', 'key': 'r'})
    
    def handle_pause_input(self, key: int) -> None:
        """Handle pause menu input."""
        if key == pygame.K_SPACE:
            if self.state == AppState.PAUSED:
                self.state = AppState.SANDBOX if self.game_mode.mode_type == "sandbox" else AppState.CHALLENGE
                print("Game resumed")
        
        elif key == pygame.K_ESCAPE:
            self.state = AppState.MENU
            self.menu_selected = 0
            print("Returning to menu")
    
    def handle_mouse_click(self, pos: tuple) -> None:
        """Handle mouse click."""
        self.game_mode.handle_input({
            'type': 'mouse_click',
            'x': pos[0],
            'y': pos[1]
        })
    
    def handle_mouse_move(self, pos: tuple) -> None:
        """Handle mouse move."""
        self.game_mode.handle_input({
            'type': 'mouse_move',
            'x': pos[0],
            'y': pos[1]
        })

    def handle_menu_mouse_click(self, pos: tuple) -> None:
        """Handle mouse clicks on the main menu options."""
        mx, my = pos
        # Menu layout matches renderer.render_main_menu
        center_x = self.width // 2
        y_pos = 300
        spacing = 80
        options = self.menu_options

        for i, option in enumerate(options):
            # Use renderer font metrics to build bounding rect
            font = self.renderer.fonts.get('large')
            if not font:
                # Fonts may not be loaded yet
                font = pygame.font.Font(None, 24)

            option_surface = font.render(option, True, (0, 0, 0))
            option_rect = option_surface.get_rect(center=(center_x, y_pos))

            if option_rect.collidepoint(mx, my):
                # Trigger same actions as keyboard ENTER
                if i == 0:
                    self.setup_sandbox_mode()
                    self.state = AppState.SANDBOX
                elif i == 1:
                    self.setup_challenge_mode(0)
                    self.state = AppState.CHALLENGE
                elif i == 2:
                    self.running = False
                    self.state = AppState.QUIT

                return

            y_pos += spacing
    
    def update(self, delta_time: float) -> None:
        """Update game state."""
        if self.state == AppState.SANDBOX or self.state == AppState.CHALLENGE:
            result = self.game_mode.update(delta_time)
            
            # Check for game end conditions
            if result.get('status') in ['won', 'lost']:
                print(f"\nGame Over: {result['message']}")
                self.state = AppState.MENU
                self.menu_selected = 0
    
    def render(self) -> None:
        """Render frame."""
        self.renderer.clear()
        
        if self.state == AppState.MENU:
            self.renderer.render_main_menu(self.menu_selected)
        
        elif self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
            render_data = self.game_mode.get_render_data()

            # Draw sidebars (background + separators)
            left_width = 140
            right_width = 300
            padding = 20
            self.renderer.render_sidebars(left_width=left_width, right_width=right_width, padding=padding)

            # Sidebar rectangles (for hit-testing and state)
            left_x = padding
            left_y = padding
            left_w = left_width
            left_h = self.height - padding * 2

            right_x = self.width - right_width - padding
            right_y = padding
            right_w = right_width
            right_h = self.height - padding * 2

            # Ensure right-sidebar UI elements (pH strip, thermometer, hotplate)
            # are positioned within the dedicated right column. Also sync object
            # bounds and set in_sidebar/active flags so they are inert until
            # dragged into the main area.
            sidebar_inner_x = right_x + 20
            y_start = 120
            y_spacing = 120
            idx_right = 0
            # Iterate and apply sidebar positioning and object sync
            for elm in render_data.get('ui_elements', []):
                t = elm.get('type')
                d = elm.get('data')
                obj = elm.get('obj')

                # if this is a right-sidebar tool, place it in the column
                if t in ('ph_strip', 'thermometer', 'hotplate'):
                    d['x'] = sidebar_inner_x
                    d['y'] = y_start + idx_right * y_spacing
                    # reasonable defaults
                    if 'width' not in d:
                        d['width'] = 40 if t == 'ph_strip' else d.get('width', 60)
                    if 'height' not in d:
                        d['height'] = 200 if t == 'ph_strip' else d.get('height', 60)
                    # mark as in sidebar
                    if t == 'ph_strip':
                        d['in_sidebar'] = True
                    idx_right += 1

                # Sync back to object bounds if object reference exists
                if obj is not None:
                    # place object's bounds to the render-data position so click math matches visuals
                    ox = int(d.get('x', obj.bounds.get('x', 0)))
                    oy = int(d.get('y', obj.bounds.get('y', 0)))
                    ow = int(d.get('width', obj.bounds.get('width', obj.width if hasattr(obj, 'width') else 0)))
                    oh = int(d.get('height', obj.bounds.get('height', obj.height if hasattr(obj, 'height') else 0)))
                    # update object position and bounds
                    if hasattr(obj, 'x'):
                        try:
                            obj.x = ox
                        except Exception:
                            pass
                    if hasattr(obj, 'y'):
                        try:
                            obj.y = oy
                        except Exception:
                            pass
                    obj.bounds = {'x': ox, 'y': oy, 'width': ow, 'height': oh}

                    # Determine whether object sits in left or right sidebar
                    in_left = (ox >= left_x and ox <= left_x + left_w)
                    in_right = (ox >= right_x and ox <= right_x + right_w)

                    if in_left or in_right:
                        obj.in_sidebar = True
                        obj.active = False
                    else:
                        obj.in_sidebar = False
                        obj.active = True

                # For ph_strip data without obj, set in_sidebar flag
                if t == 'ph_strip' and isinstance(d, dict):
                    px = int(d.get('x', 0))
                    py = int(d.get('y', 0))
                    pw = int(d.get('width', 40))
                    ph = int(d.get('height', 200))
                    in_left = (px >= left_x and px <= left_x + left_w)
                    in_right = (px >= right_x and px <= right_x + right_w)
                    d['in_sidebar'] = in_left or in_right

            # Render flask
            if render_data['flask']:
                self.renderer.render_flask(render_data['flask'])
            
            # Render particles
            if render_data['particles']:
                self.renderer.render_particles(render_data['particles'])
            
            # Render UI elements
            if render_data['ui_elements']:
                self.renderer.render_ui_elements(render_data['ui_elements'])
            
            # Render challenge info (if in challenge mode)
            if self.game_mode.mode_type == "challenge" and 'challenge' in render_data:
                self.renderer.render_challenge_info(render_data['challenge'])
            
            # Render status message
            if render_data.get('state_message'):
                self.renderer.render_status_message(render_data['state_message'], 
                                                   x=20, y=self.height - 40)
        
        # Render FPS
        self.renderer.render_fps(self.clock.get_fps())
        
        # Render pause overlay
        if self.state == AppState.PAUSED:
            self.renderer.render_pause_overlay()
        
        # Update display
        self.renderer.flip()
    
    def run(self) -> None:
        """Main game loop."""
        self.initialize()
        
        print("\nStarting main game loop...")
        
        while self.running and self.state != AppState.QUIT:
            # Cap framerate
            delta_time = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            
            # Handle input
            self.handle_events()
            
            # Update
            if self.state != AppState.PAUSED:
                self.update(delta_time)
            
            # Render
            self.render()
        
        # Cleanup
        self.renderer.quit()
        print("\nGame closed. Thanks for playing!")


def main():
    """Main entry point."""
    try:
        app = GameApplication(width=1200, height=800)
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
