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
        # Drag state for droppers
        self.dragging_dropper = None
        self.drag_pos = (0, 0)
        
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
        # pH strip UI
        self.ph_strip = {
            'x':  self.flask.bounds['x'] + self.flask.bounds['width'] + 40,
            'y': 200,
            'width': 40,
            'height': 200,
            'dragging': False,
            'current_ph': None
        }
    
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
        # pH strip UI (right sidebar)
        self.ph_strip = {
            'x': int(self.flask.bounds['x'] + self.flask.bounds['width'] + 40),
            'y': 200,
            'width': 40,
            'height': 200,
            'dragging': False,
            'current_ph': None
        }
    
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
        elif event_type == 'mouse_down':
            self.on_mouse_down(event.get('x', 0), event.get('y', 0), event.get('button', 1))
        elif event_type == 'mouse_up':
            self.on_mouse_up(event.get('x', 0), event.get('y', 0), event.get('button', 1))
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
        # Update hover states for droppers when not dragging
        if not self.dragging_dropper:
            for dropper in self.droppers:
                dropper.on_mouse_move(mouse_x, mouse_y)

        # Update drag position if dragging
        if self.dragging_dropper:
            self.drag_pos = (mouse_x, mouse_y)

        # Dragging pH strip
        if hasattr(self, 'ph_strip') and self.ph_strip and self.ph_strip.get('dragging'):
            off_x, off_y = self.ph_strip.get('drag_offset', (0, 0))
            self.ph_strip['x'] = int(mouse_x - off_x)
            self.ph_strip['y'] = int(mouse_y - off_y)

        if self.hotplate:
            self.hotplate.on_mouse_move(mouse_x, mouse_y)

    def on_mouse_down(self, mouse_x: float, mouse_y: float, button: int = 1) -> None:
        """Start drag/press behavior for droppers."""
        # pH strip takes priority if clicked
        if hasattr(self, 'ph_strip') and self.ph_strip:
            pbx = self.ph_strip['x']
            pby = self.ph_strip['y']
            pbw = self.ph_strip['width']
            pbh = self.ph_strip['height']
            if pbx <= mouse_x <= pbx + pbw and pby <= mouse_y <= pby + pbh:
                self.ph_strip['dragging'] = True
                self.ph_strip['drag_offset'] = (mouse_x - pbx, mouse_y - pby)
                return

        # Start dragging if a dropper is pressed
        for dropper in self.droppers:
            if dropper.on_mouse_down(mouse_x, mouse_y):
                self.dragging_dropper = dropper
                self.drag_pos = (mouse_x, mouse_y)
                return

        # Hotplate press
        if self.hotplate:
            if self.hotplate.on_click(mouse_x, mouse_y):
                return

    def on_mouse_up(self, mouse_x: float, mouse_y: float, button: int = 1) -> None:
        """Handle mouse release; drop a dragged chemical into flask if over it."""
        # finish dragging pH strip
        if hasattr(self, 'ph_strip') and self.ph_strip and self.ph_strip.get('dragging'):
            self.ph_strip['dragging'] = False
            self.ph_strip.pop('drag_offset', None)
            return

        if self.dragging_dropper:
            # check if released over flask bounds
            if self.flask:
                bounds = self.flask.get_visual_data().get('bounds', {})
                bx = bounds.get('x', 0)
                by = bounds.get('y', 0)
                bw = bounds.get('width', 0)
                bh = bounds.get('height', 0)
                if bx <= mouse_x <= bx + bw and by <= mouse_y <= by + bh:
                    # Dispense into flask
                    dispense_data = self.dragging_dropper.dispense()
                    self.flask.add_reactant(dispense_data['chemical'], dispense_data['moles'])

            # end drag
            self.dragging_dropper.on_mouse_up()
            self.dragging_dropper = None
            return

        # Hotplate release
        if self.hotplate:
            if hasattr(self.hotplate, 'on_mouse_up'):
                self.hotplate.on_mouse_up()
    
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
            # Support hold-dispense (titration droppers)
            if hasattr(dropper, 'get_hold_dispense'):
                hold = dropper.get_hold_dispense(delta_time)
                if hold:
                    self.flask.add_reactant(hold['chemical'], hold['moles'])
        
        # Update flask
        flask_update = self.flask.update(delta_time)
        
        # Apply hotplate heat
        if self.hotplate:
            heat_output = self.hotplate.get_heat_output()
            self.flask.adjust_temperature(heat_output * delta_time)
        
        # Update thermometer display
        if self.thermometer:
            self.thermometer.set_temperature_kelvin(self.flask.chemical_state.temperature)

        # Update pH strip current reading if overlapping flask
        if hasattr(self, 'ph_strip') and self.ph_strip and self.flask:
            ph_val = self.flask.get_ph()
            # If the ph_strip rectangle intersects flask bounds, set current_ph
            pbx = self.ph_strip['x']
            pby = self.ph_strip['y']
            pbw = self.ph_strip['width']
            pbh = self.ph_strip['height']
            fb = self.flask.get_visual_data().get('bounds', {})
            fx, fy, fw, fh = fb.get('x', 0), fb.get('y', 0), fb.get('width', 0), fb.get('height', 0)
            # overlap test
            overlap = not (pbx + pbw < fx or pbx > fx + fw or pby + pbh < fy or pby > fy + fh)
            self.ph_strip['current_ph'] = ph_val if overlap else None
        
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

        # Add pH strip render data
        if hasattr(self, 'ph_strip') and self.ph_strip:
            data['ui_elements'].append({
                'type': 'ph_strip',
                'data': self.ph_strip.copy()
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

        # Drag preview (if dragging a dropper)
        if self.dragging_dropper:
            dx, dy = self.drag_pos
            preview = {
                'x': dx - self.dragging_dropper.width // 2,
                'y': dy - self.dragging_dropper.height // 2,
                'width': self.dragging_dropper.width,
                'height': self.dragging_dropper.height,
                'label': self.dragging_dropper.label,
                'color': self.dragging_dropper.chemical.color_hex if self.dragging_dropper.chemical else '#808080',
                'border_color': self.dragging_dropper.chemical.color_hex if self.dragging_dropper.chemical else '#FFFFFF'
            }
            data['ui_elements'].append({'type': 'drag_preview', 'data': preview})
        
        # Challenge-specific data
        if self.mode_type == "challenge" and self.challenge:
            challenge_data = self.challenge.get_render_data()
            # Include scroll offset for renderer to display objectives panel
            challenge_data['scroll_offset'] = self.challenge_scroll
            data['challenge'] = challenge_data
        
        return data
    
    def __repr__(self) -> str:
        return f"GameMode({self.mode_type}, active={self.is_active})"
