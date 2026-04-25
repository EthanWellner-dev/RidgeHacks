"""
GameMode - Orchestrates game states and modes (Sandbox, Challenge, Menu).
"""

from chemistry.flask import Flask
from game.challenge import Challenge
from game.dropper import Dropper
from game.thermometer import Thermometer
from game.hotplate import HotPlate


class GameMode:
    """
    Encapsulates either Sandbox or Challenge game mode.
    Manages Flask, UI elements, input handling, and game flow.
    """
    
    def __init__(self, mode_type: str = "sandbox"):
        """
        Initialize game mode.
        
        Args:
            mode_type: "sandbox", "challenge", or "menu"
        """
        self.mode_type = mode_type.lower()
        self.flask = None
        self.challenge = None
        self.challenge_scroll = 0.0  # vertical scroll offset for challenge objectives
        
        # UI Elements
        self.ui_elements = []  # [Dropper, Thermometer, HotPlate, ...]
        self.droppers = []
        self.thermometer = None
        self.hotplate = None
        
        # Game state
        self.is_paused = False
        self.is_active = False
        self.state_message = ""
    
    def initialize_sandbox(self, flask: Flask, droppers: list = None, 
                          thermometer: Thermometer = None,
                          hotplate: HotPlate = None) -> None:
        """
        Set up sandbox mode.
        
        Args:
            flask: Flask instance
            droppers: List of Dropper objects
            thermometer: Thermometer UI element
            hotplate: HotPlate UI element
        """
        self.mode_type = "sandbox"
        self.flask = flask
        self.challenge = None
        
        self.droppers = droppers or []
        self.thermometer = thermometer
        self.hotplate = hotplate
        
        self.ui_elements = self.droppers.copy()
        if self.thermometer:
            self.ui_elements.append(self.thermometer)
        if self.hotplate:
            self.ui_elements.append(self.hotplate)
        
        self.is_active = True
        self.state_message = "Sandbox Mode - Experiment freely!"
    
    def initialize_challenge(self, challenge: Challenge,
                            thermometer: Thermometer = None,
                            hotplate: HotPlate = None) -> None:
        """
        Set up challenge mode.
        
        Args:
            challenge: Challenge instance
            thermometer: Thermometer UI element
            hotplate: HotPlate UI element
        """
        self.mode_type = "challenge"
        self.challenge = challenge
        self.flask = challenge.initialize_flask()
        
        # Setup UI
        self.droppers = []  # Challenges may not allow free droppers
        self.thermometer = thermometer
        self.hotplate = hotplate
        
        self.ui_elements = []
        if self.thermometer:
            self.ui_elements.append(self.thermometer)
        if self.hotplate:
            self.ui_elements.append(self.hotplate)
        
        self.is_active = True
        self.state_message = challenge.description
    
    def handle_input(self, event: dict) -> None:
        """
        Process input events.
        
        Args:
            event: dict with 'type' and event-specific data
                - {'type': 'mouse_click', 'x': x, 'y': y}
                - {'type': 'mouse_move', 'x': x, 'y': y}
                - {'type': 'key_press', 'key': key_name}
        """
        if not self.is_active:
            return
        
        event_type = event.get('type', '')
        
        if event_type == 'mouse_click':
            self.on_mouse_click(event.get('x', 0), event.get('y', 0))
        elif event_type == 'mouse_move':
            self.on_mouse_move(event.get('x', 0), event.get('y', 0))
        elif event_type == 'mouse_wheel':
            # Adjust scroll for challenge objectives
            if self.mode_type == 'challenge':
                # event['y'] is positive when scrolling up
                self.challenge_scroll -= event.get('y', 0) * 20
                # clamp to reasonable range
                self.challenge_scroll = max(-1000, min(1000, self.challenge_scroll))
        elif event_type == 'key_press':
            self.on_key_press(event.get('key', ''))
    
    def on_mouse_click(self, mouse_x: float, mouse_y: float) -> None:
        """Handle mouse click."""
        # Check dropper clicks
        for dropper in self.droppers:
            if dropper.on_mouse_down(mouse_x, mouse_y):
                dispense_data = dropper.dispense()
                self.flask.add_reactant(dispense_data['chemical'], dispense_data['moles'])
        
        # Check hotplate click
        if self.hotplate:
            if self.hotplate.on_click(mouse_x, mouse_y):
                pass  # Toggled on/off
    
    def on_mouse_move(self, mouse_x: float, mouse_y: float) -> None:
        """Handle mouse move."""
        for dropper in self.droppers:
            dropper.on_mouse_move(mouse_x, mouse_y)
        
        if self.hotplate:
            self.hotplate.on_mouse_move(mouse_x, mouse_y)
    
    def on_key_press(self, key_name: str) -> None:
        """Handle keyboard input."""
        if key_name == "space":
            self.is_paused = not self.is_paused
        elif key_name == "r":
            # Reset (if applicable)
            if self.flask:
                self.flask.reset()
        elif key_name == "escape":
            self.is_active = False
    
    def update(self, delta_time: float) -> dict:
        """
        Update game state each frame.
        
        Args:
            delta_time: Time step in seconds
        
        Returns:
            dict with update information
        """
        if not self.is_active or self.is_paused:
            return {'status': 'paused', 'message': self.state_message}
        
        # Update UI elements
        for dropper in self.droppers:
            dropper.update(delta_time)
        
        # Update flask
        flask_update = self.flask.update(delta_time)
        
        # Apply hotplate heat
        if self.hotplate:
            heat_output = self.hotplate.get_heat_output()
            self.flask.adjust_temperature(heat_output * delta_time)
        
        # Update thermometer display
        if self.thermometer:
            self.thermometer.set_temperature_kelvin(self.flask.chemical_state.temperature)
        
        # Check challenge state (if in challenge mode)
        if self.mode_type == "challenge" and self.challenge:
            challenge_update = self.challenge.update(delta_time)
            if challenge_update['status'] in ['won', 'lost']:
                self.is_active = False
                self.state_message = challenge_update['message']
                return {
                    'status': challenge_update['status'],
                    'message': challenge_update['message']
                }
        
        return {
            'status': 'in_progress',
            'message': self.state_message,
            'flask_data': self.flask.get_visual_data()
        }
    
    def get_render_data(self) -> dict:
        """
        Get all data needed for rendering.
        
        Returns:
            dict with flask, UI elements, and text data
        """
        data = {
            'mode': self.mode_type,
            'is_paused': self.is_paused,
            'state_message': self.state_message,
            'flask': self.flask.get_visual_data() if self.flask else None,
            'particles': [],
            'ui_elements': []
        }
        
        # Add particles
        if self.flask:
            for emitter in self.flask.particle_emitters:
                data['particles'].extend(emitter.get_particles_to_render())
        
        # Add UI element render data
        for dropper in self.droppers:
            data['ui_elements'].append({
                'type': 'dropper',
                'data': dropper.get_render_data()
            })
        
        if self.thermometer:
            data['ui_elements'].append({
                'type': 'thermometer',
                'data': self.thermometer.get_render_data()
            })
        
        if self.hotplate:
            data['ui_elements'].append({
                'type': 'hotplate',
                'data': self.hotplate.get_render_data()
            })
        
        # Challenge-specific data
        if self.mode_type == "challenge" and self.challenge:
            challenge_data = self.challenge.get_render_data()
            # Include scroll offset for renderer to display objectives panel
            challenge_data['scroll_offset'] = self.challenge_scroll
            data['challenge'] = challenge_data
        
        return data
    
    def __repr__(self) -> str:
        return f"GameMode({self.mode_type}, active={self.is_active})"
