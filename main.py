"""
main.py - Main game application with event loop and rendering.
Entry point for the Dynamic ChemEngine.
"""

import pygame
import sys
from enum import Enum

from pygame_renderer import PygameRenderer
from game_mode import GameMode
from challenge import ChallengeLibrary
from chemical import Chemical
from flask import Flask
from dropper import Dropper
from thermometer import Thermometer
from hotplate import HotPlate
from particle_emitter import ParticleEmitter


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
        
        # Create flask
        flask = Flask(1.0, max_temperature=373.15)
        flask.bounds = {'x': 50, 'y': 100, 'width': 300, 'height': 500}
        
        # Create some common chemicals
        water = Chemical("H2O", 0.0, "#87CEEB", -285.8)      # Light blue
        acid = Chemical("H2SO4", 0.0, "#FF0000", -813)       # Red
        base = Chemical("NaOH", 0.0, "#0000FF", -427)        # Blue
        gas = Chemical("O2", 0.0, "#87CEEB", 0)              # Light blue
        
        # Create droppers
        droppers = [
            Dropper(400, 150, water, 0.2, width=60, height=80, label="Water"),
            Dropper(480, 150, acid, 0.1, width=60, height=80, label="Acid"),
            Dropper(560, 150, base, 0.1, width=60, height=80, label="Base"),
            Dropper(640, 150, gas, 0.05, width=60, height=80, label="O₂"),
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
        
        print("Challenge started! Use hotplate to control temperature.")
        print("SPACE to pause, ESC to return to menu")
    
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
                if self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
                    self.handle_mouse_click(event.pos)
            
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
