from pygame_renderer import PygameRenderer
from game.game_mode import GameMode
from game.challenge import ChallengeLibrary
from chemistry.chemical import Chemical
from chemistry.flask import Flask
from game.dropper import Dropper
from game.thermometer import Thermometer
from game.hotplate import HotPlate
from game.temp_changer import TemperatureChanger
from game.stopwatch import Stopwatch
from chemistry.particle_emitter import ParticleEmitter
import json
import os
import pygame
from enum import Enum

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
        
        # Universal drag state for sidebar tools
        self.dragging_tool = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # --- ADDED: State tracker for flask temperature ---
        self.last_flask_temp = None

    
    def initialize(self) -> None:
        """Initialize the application."""
        self.renderer.initialize()
        print("Big Alchemy initialized")
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
        
        # Expanded starter chemical library for left sidebar
        water = Chemical("H2O",[("H", 2), ("O", 1)], 0.0, "#87CEEB", -285.8)
        acids = [
            Chemical('HCl', [('H',1),('Cl',1)], 0.0, '#FF6666', -92.3),
            Chemical('H2SO4', [('H',2),('S',1),('O',4)], 0.0, '#FF4444', -814.0),
            Chemical('HNO3', [('H',1),'N' if False else ('N',1),('O',3)], 0.0, '#FF5555', -207.0),
            Chemical('CH3COOH', [], 0.0, '#FFA0A0', -484.0),
        ]
        bases = [
            Chemical('NaOH', [('Na',1),('O',1),('H',1)], 0.0, '#0000FF', -470.0),
            Chemical('KOH', [('K',1),('O',1),('H',1)], 0.0, '#3366FF', -420.0),
            Chemical('NH3', [('N',1),('H',3)], 0.0, '#CCCCFF', -46.0)
        ]
        gases = [Chemical('O2', [('O',2)], 0.0, '#87CEEB', 0.0)]

        left_x = 40
        start_y = 120
        spacing_y = 110
        droppers = []
        idx = 0
        # Water first
        droppers.append(Dropper(left_x, start_y + idx * spacing_y, water, 0.2, width=80, height=90, label="Water"))
        idx += 1
        # Acids
        for a in acids:
            droppers.append(Dropper(left_x, start_y + idx * spacing_y, a, 0.1, width=80, height=90, label=a.name))
            idx += 1
        # Bases
        for b in bases:
            droppers.append(Dropper(left_x, start_y + idx * spacing_y, b, 0.1, width=80, height=90, label=b.name))
            idx += 1
        # Some gases
        for g in gases:
            droppers.append(Dropper(left_x, start_y + idx * spacing_y, g, 0.05, width=80, height=90, label=g.name))
            idx += 1
        
        # Tools initialized in the Right Sidebar area
        right_x = self.width - 250
        thermometer = Thermometer(right_x, 150, -10, 120, width=80, height=80)
        temp_changer = TemperatureChanger(right_x, 230, min_temp_k=250.0, max_temp_k=400.0, initial_target_k=293.15, width=80, height=60)
        hotplate = HotPlate(right_x, 320, max_heat_output=50, controller=temp_changer)
        stopwatch = Stopwatch(right_x, 410, width=120, height=60)
        
        emitter = ParticleEmitter(200, 300, spawn_rate=0, velocity_magnitude=150, 
                                 color_hex="#FF8800", lifetime=2.0)
        flask.add_particle_emitter(emitter)
        
        self.game_mode = GameMode()
        self.game_mode.initialize_sandbox(flask, droppers, thermometer, hotplate, temp_changer=temp_changer, stopwatch=stopwatch)
        
        print("Sandbox mode ready.")
    
    def setup_challenge_mode(self, challenge_index: int = 0) -> None:
        """Setup challenge mode."""
        challenges =[
            ChallengeLibrary.create_color_shift_challenge(),
            ChallengeLibrary.create_gas_production_challenge(),
            ChallengeLibrary.create_equilibrium_balance_challenge(),
        ]
        challenge = challenges[min(challenge_index, len(challenges) - 1)]
        
        print(f"\n=== Starting Challenge: {challenge.name} ===")
        
        right_x = self.width - 250
        thermometer = Thermometer(right_x, 150, -10, 120, width=80, height=80)
        temp_changer = TemperatureChanger(right_x, 230, min_temp_k=250.0, max_temp_k=400.0, initial_target_k=293.15, width=80, height=60)
        hotplate = HotPlate(right_x, 320, max_heat_output=50, controller=temp_changer)
        stopwatch = Stopwatch(right_x, 410, width=120, height=60)
        
        self.game_mode = GameMode()
        self.game_mode.initialize_challenge(challenge, thermometer, hotplate, temp_changer=temp_changer, stopwatch=stopwatch)

        if self.game_mode and self.game_mode.flask:
            self.game_mode.flask.bounds = {
                'x': int(self.width // 2 - 200),
                'y': 100,
                'width': 400,
                'height': 500
            }

        save_path = os.path.join(os.getcwd(), 'save.json')
        molecules = {}
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                molecules = saved.get('chemicals', {}).get('molecules', {})
        except Exception:
            pass

        known = {
            'H2O': Chemical('H2O', [('H',2),('O',1)], 0.0, '#87CEEB', -285.8),
            'HCl': Chemical('HCl', [('H',1),('Cl',1)], 0.0, '#FF6666', -92.3),
            'NH3': Chemical('NH3',[('N',1),('H',3)], 0.0, '#CCCCFF', -45.9),
            'NaOH': Chemical('NaOH', [('Na',1),('O',1),('H',1)], 0.0, '#AAAAFF', -137.1),
            'O2': Chemical('O2', [('O',2)], 0.0, '#87CEEB', 0.0)
        }

        left_x = 40
        start_y = 140
        spacing_y = 110
        challenge_droppers =[]
        idx = 0
        for name, enabled in molecules.items():
            if not enabled: continue
            chem = known.get(name, Chemical(name,[], 0.0, '#808080', 0.0))
            challenge_droppers.append(Dropper(left_x, start_y + idx * spacing_y, chem, 0.1, width=80, height=90, label=name))
            idx += 1

        self.game_mode.droppers = challenge_droppers
        for d in challenge_droppers:
            self.game_mode.ui_elements.insert(0, d)

        if hasattr(self.game_mode, 'ph_strip') and self.game_mode.ph_strip is not None:
            self.game_mode.ph_strip['x'] = right_x
            self.game_mode.ph_strip['y'] = 410
            self.game_mode.ph_strip['width'] = 80
            self.game_mode.ph_strip['height'] = 80
            
    def handle_tool_drag_start(self, pos: tuple) -> bool:
        """Safely intercept tools out of the right sidebar to guarantee they can be dragged."""
        mx, my = pos
        if not self.game_mode: return False
        
        render_data = self.game_mode.get_render_data()
        
        for elm in render_data.get('ui_elements',[]):
            t = elm.get('type')
            d = elm.get('data')
            obj = elm.get('obj')
            
            x = d.get('x', 0)
            y = d.get('y', 0)
            w = d.get('width', 80)
            h = d.get('height', 80)
            
            if x <= mx <= x + w and y <= my <= y + h:
                if t in ('thermometer', 'hotplate') and obj is not None:
                    self.dragging_tool = obj
                    self.drag_offset_x = getattr(obj, 'x', x) - mx
                    self.drag_offset_y = getattr(obj, 'y', y) - my
                    
                    # If it's in the right sidebar, swallow the click so we can drag it 
                    # without the backend blocking it or accidentally pressing internal buttons
                    if x >= self.width - 320:
                        # Do not swallow the click; allow backend to receive it so
                        # sidebar controls (hotplate/thermometer/stopwatch) respond.
                        return False
                    # If it's already dragged out, don't return true (let the backend get the click 
                    # for the Hotplate On/Off toggle) but keep it as the active dragging_tool.
                    return False
        return False

    def handle_tool_drag_move(self, pos: tuple) -> None:
        """Apply manual physics update to dragging tools."""
        if self.dragging_tool:
            mx, my = pos
            new_x = mx + self.drag_offset_x
            new_y = my + self.drag_offset_y
            
            if hasattr(self.dragging_tool, 'x'): self.dragging_tool.x = new_x
            if hasattr(self.dragging_tool, 'y'): self.dragging_tool.y = new_y
            
            if hasattr(self.dragging_tool, 'bounds') and isinstance(self.dragging_tool.bounds, dict):
                self.dragging_tool.bounds['x'] = new_x
                self.dragging_tool.bounds['y'] = new_y
                
            if hasattr(self.dragging_tool, 'rect') and self.dragging_tool.rect:
                self.dragging_tool.rect.x = new_x
                self.dragging_tool.rect.y = new_y
                
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = AppState.QUIT
            
            elif event.type == pygame.KEYDOWN:
                if self.state == AppState.MENU: self.handle_menu_input(event.key)
                elif self.state in[AppState.SANDBOX, AppState.CHALLENGE]: self.handle_game_input(event.key)
                elif self.state == AppState.PAUSED: self.handle_pause_input(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == AppState.MENU:
                    self.handle_menu_mouse_click(event.pos)
                elif self.state in[AppState.SANDBOX, AppState.CHALLENGE]:
                    if not self.handle_tool_drag_start(event.pos):
                        self.game_mode.handle_input({'type': 'mouse_down', 'x': event.pos[0], 'y': event.pos[1], 'button': event.button})

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.state in[AppState.SANDBOX, AppState.CHALLENGE]:
                    self.dragging_tool = None
                    self.game_mode.handle_input({'type': 'mouse_up', 'x': event.pos[0], 'y': event.pos[1], 'button': event.button})
                    # Also send a high-level click event so UI elements that expect
                    # a simple click (not down/up) can respond (React button, Stopwatch, Hotplate)
                    try:
                        self.game_mode.handle_input({'type': 'mouse_click', 'x': event.pos[0], 'y': event.pos[1]})
                    except Exception:
                        pass

            elif event.type == pygame.MOUSEMOTION:
                if self.state in [AppState.SANDBOX, AppState.CHALLENGE]:
                    if self.dragging_tool:
                        self.handle_tool_drag_move(event.pos)
                    else:
                        self.handle_mouse_move(event.pos)
                        
            elif event.type == pygame.MOUSEWHEEL:
                if self.state in [AppState.SANDBOX, AppState.CHALLENGE] and self.game_mode:
                    # Determine which sidebar the mouse is over and forward delta
                    mx, my = pygame.mouse.get_pos()
                    left_width, right_width, padding = 140, 300, 20
                    left_x = padding
                    left_w = left_width
                    right_x = self.width - right_width - padding
                    target = None
                    if left_x <= mx <= left_x + left_w:
                        target = 'left'
                    elif right_x <= mx <= right_x + right_width:
                        target = 'right'
                    self.game_mode.handle_input({'type': 'mouse_wheel', 'delta': event.y, 'target': target, 'x': mx, 'y': my})

            elif event.type == pygame.VIDEORESIZE:
                # Update the window to the new size
                self.renderer.updateSize(event.w, event.h)
    def handle_menu_input(self, key: int) -> None:
        if key == pygame.K_UP: self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN: self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
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
        if key == pygame.K_SPACE: self.state = AppState.PAUSED
        elif key == pygame.K_ESCAPE: 
            self.state = AppState.MENU
            self.last_flask_temp = None  # Reset tracking on exit to menu
        elif key == pygame.K_r: self.game_mode.handle_input({'type': 'key_press', 'key': 'r'})

    def handle_pause_input(self, key: int) -> None:
        if key == pygame.K_SPACE:
            if self.state == AppState.PAUSED:
                self.state = AppState.SANDBOX if self.game_mode.mode_type == "sandbox" else AppState.CHALLENGE
        elif key == pygame.K_ESCAPE:
            self.state = AppState.MENU
            self.last_flask_temp = None  # Reset tracking on exit to menu
            
    def handle_mouse_move(self, pos: tuple) -> None:
        self.game_mode.handle_input({'type': 'mouse_move', 'x': pos[0], 'y': pos[1]})

    def handle_menu_mouse_click(self, pos: tuple) -> None:
        mx, my = pos
        center_x = self.width // 2
        y_pos = 300
        
        for i, option in enumerate(self.menu_options):
            font = self.renderer.fonts.get('large', pygame.font.Font(None, 24))
            option_rect = font.render(option, True, (0, 0, 0)).get_rect(center=(center_x, y_pos))
            if option_rect.collidepoint(mx, my):
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
            y_pos += 80
    
    def update(self, delta_time: float) -> None:
        if self.state in (AppState.SANDBOX, AppState.CHALLENGE):
            result = self.game_mode.update(delta_time)
            
            # --- ADDED LOGIC: Check for reactions and temperature changes ---
            if self.game_mode and getattr(self.game_mode, 'flask', None):
                flask = self.game_mode.flask

                # Avoid running the long-running `flask.react()` simulation every frame.
                # Reactions and reaction discovery are triggered when chemicals are
                # added via `ChemicalState.add_chemical` (called by `flask.add_reactant`).
                # Here we only track temperature changes for UI/side effects.
                current_temp = None
                if hasattr(flask, 'chemical_state') and hasattr(flask.chemical_state, 'get_average_temperature'):
                    current_temp = flask.chemical_state.get_average_temperature()

                if current_temp is not None:
                    if self.last_flask_temp is not None and current_temp != self.last_flask_temp:
                        if hasattr(flask, 'temp_change'):
                            flask.temp_change()
                    self.last_flask_temp = current_temp
            # ----------------------------------------------------------------

            if result.get('status') in ['won', 'lost']:
                print(f"\nGame Over: {result['message']}")
                self.state = AppState.MENU
                self.last_flask_temp = None  # Reset tracking on game over

    
    def render(self) -> None:
        self.renderer.clear()
        
        if self.state == AppState.MENU:
            self.renderer.render_main_menu(self.menu_selected)
            
        elif self.state in[AppState.SANDBOX, AppState.CHALLENGE]:
            render_data = self.game_mode.get_render_data()

            left_width, right_width, padding = 140, 300, 20
            self.renderer.render_sidebars(left_width=left_width, right_width=right_width, padding=padding)

            left_x, left_w = padding, left_width
            right_x, right_w = self.width - right_width - padding, right_width

            # Completely orchestrated rendering loop scaling correctly inside vs outside the sidebars
            for elm in render_data.get('ui_elements',[]):
                t = elm.get('type')
                d = elm.get('data')
                obj = elm.get('obj')

                # Calculate True backend X
                cx = getattr(obj, 'x', None)
                if cx is None:
                    bounds = getattr(obj, 'bounds', {})
                    cx = bounds.get('x', d.get('x', 0)) if isinstance(bounds, dict) else d.get('x', 0)
                cx = int(cx)

                in_left = (cx >= left_x and cx <= left_x + left_w)
                in_right = (cx >= right_x and cx <= right_x + right_w)
                in_sidebar = in_left or in_right

                # Expand/Shrink tools dynamically
                if t in ('thermometer', 'hotplate', 'ph_strip'):
                    if in_right:
                        d['width'], d['height'] = 80, 80  # Made them significantly larger
                        
                        # Stop function logic when stowed in the right sidebar
                        if t == 'hotplate':
                            d['is_on'] = False
                            if obj and hasattr(obj, 'is_on'):
                                obj.is_on = False
                    else:
                        # Full size configuration in main interactive area
                        if t == 'thermometer': d['width'], d['height'] = 50, 300
                        elif t == 'hotplate': d['width'], d['height'] = 200, 60
                        elif t == 'ph_strip': d['width'], d['height'] = 40, 200

                d['in_sidebar'] = in_sidebar

                # Map visually computed bounds BACK to backend objects perfectly
                if obj is not None:
                    obj.in_sidebar = in_sidebar
                    
                    ox = cx 
                    oy = getattr(obj, 'y', None)
                    if oy is None:
                        bounds = getattr(obj, 'bounds', {})
                        oy = bounds.get('y', d.get('y', 0)) if isinstance(bounds, dict) else d.get('y', 0)
                    oy = int(oy)
                    
                    ow = int(d.get('width', getattr(obj, 'width', 0)))
                    oh = int(d.get('height', getattr(obj, 'height', 0)))
                    
                    d['x'], d['y'] = ox, oy
                    
                    if hasattr(obj, 'x'): obj.x = ox
                    if hasattr(obj, 'y'): obj.y = oy
                    if hasattr(obj, 'width'): obj.width = ow
                    if hasattr(obj, 'height'): obj.height = oh
                    
                    if hasattr(obj, 'bounds') and isinstance(obj.bounds, dict):
                        obj.bounds.update({'x': ox, 'y': oy, 'width': ow, 'height': oh})
                        
                    # CRITICAL FIX: The reason they ignored mouse clicks native to the backend
                    # is because Pygame handles collisions using self.rect. This forces synchrony.
                    if hasattr(obj, 'rect') and obj.rect is not None:
                        obj.rect.x = ox
                        obj.rect.y = oy
                        obj.rect.width = ow
                        obj.rect.height = oh

            if render_data['flask']: self.renderer.render_flask(render_data['flask'])
            if render_data['particles']: self.renderer.render_particles(render_data['particles'])
            if self.game_mode.mode_type == "challenge" and 'challenge' in render_data:
                self.renderer.render_challenge_info(render_data['challenge'])
            if render_data['ui_elements']: self.renderer.render_ui_elements(render_data['ui_elements'])
            if render_data.get('state_message'):
                self.renderer.render_status_message(render_data['state_message'], x=20, y=self.height - 40)
        
        self.renderer.render_fps(self.clock.get_fps())
        if self.state == AppState.PAUSED: self.renderer.render_pause_overlay()
        self.renderer.flip()
    
    def run(self) -> None:
        self.initialize()
        while self.running and self.state != AppState.QUIT:
            delta_time = self.clock.tick(self.fps) / 1000.0 
            self.handle_events()
            if self.state != AppState.PAUSED: self.update(delta_time)
            self.render()
        self.renderer.quit()

