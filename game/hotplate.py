"""
HotPlate - Temperature control UI element.
"""


class HotPlate:
    """
    A heating control that adjusts flask temperature.
    Has on/off state and heat level control.
    """
    
    def __init__(self, x: float, y: float, max_heat_output: float = 200.0,
                 width: float = 60, height: float = 60, label: str = "Heat",
                 controller=None):
        """
        Initialize a hotplate.
        
        Args:
            x: Screen position x (pixels)
            y: Screen position y (pixels)
            max_heat_output: Maximum temperature change per second (K/s)
            width: Button width in pixels
            height: Button height in pixels
            label: Button label
        """
        self.x = float(x)
        self.y = float(y)
        self.max_heat_output = float(max_heat_output)
        self.width = float(width)
        self.height = float(height)
        self.label = label
        # Optional external controller (e.g., TemperatureChanger)
        self.controller = controller
        
        # State
        self.is_on = False
        # Mode: 'off', 'heat', 'cool'
        self.mode = 'off'
        self.heat_level = 0.5  # 0.0 to 1.0 (fraction of max output)
        self.is_hovered = False
        
        # Bounds (for collision detection)
        self.bounds = {
            'x': self.x - self.width / 2,
            'y': self.y - self.height / 2,
            'width': self.width,
            'height': self.height
        }
        # Whether this hotplate is currently placed in a sidebar (inactive)
        self.in_sidebar = False
        self.active = True
        # Initialize pygame.Rect for click detection and dragging
        try:
            import pygame
            self.rect = pygame.Rect(int(self.bounds['x']), int(self.bounds['y']), int(self.bounds['width']), int(self.bounds['height']))
        except Exception:
            self.rect = None
    
    def on_click(self, mouse_x: float, mouse_y: float) -> bool:
        """
        Handle click event.
        
        Args:
            mouse_x: Mouse x position
            mouse_y: Mouse y position
        
        Returns:
            True if hotplate was clicked (toggled)
        """
        # Only respond to clicks when active (allows sidebar tools to be clickable
        # if the UI wants them active while visually in the sidebar)
        if not getattr(self, 'active', True):
            return False
        bounds = self.bounds
        if (bounds['x'] <= mouse_x <= bounds['x'] + bounds['width'] and
            bounds['y'] <= mouse_y <= bounds['y'] + bounds['height']):
            # If an external controller drives the hotplate, clicking the main
            # body toggles controller enable/disable instead of raw on/off.
            if self.controller is not None:
                # Cycle mode: off -> heat -> cool -> off
                if getattr(self, 'mode', 'off') == 'off':
                    self.mode = 'heat'
                elif self.mode == 'heat':
                    self.mode = 'cool'
                else:
                    self.mode = 'off'
                # Reflect is_on for compatibility
                self.is_on = (self.mode != 'off')
            else:
                # No controller: simple toggle on/off
                self.is_on = not self.is_on
            return True
        return False
    
    def on_mouse_move(self, mouse_x: float, mouse_y: float) -> None:
        """Update hover state."""
        bounds = self.bounds
        self.is_hovered = (bounds['x'] <= mouse_x <= bounds['x'] + bounds['width'] and
                          bounds['y'] <= mouse_y <= bounds['y'] + bounds['height'])
    
    def set_heat_level(self, level: float) -> None:
        """
        Set heat intensity.
        
        Args:
            level: 0.0 (no heat) to 1.0 (max heat)
        """
        self.heat_level = max(0.0, min(1.0, level))
    
    def adjust_heat_level(self, delta: float) -> None:
        """Adjust heat level by delta."""
        self.set_heat_level(self.heat_level + delta)
    
    def toggle(self) -> None:
        """Toggle on/off state."""
        self.is_on = not self.is_on
    
    def get_heat_output(self) -> float:
        """
        Get current heat output rate.
        
        Returns:
            Temperature change per second (K/s)
        """
        # If an external controller is present, ask it to compute required output.
        # The controller expects (max_heat_output, current_temp_k) and returns K/s.
        # New behavior: support explicit heat/cool modes (fixed rates per request)
        if self.controller is not None:
            # If controller is present, use hotplate.mode to decide heating/cooling.
            if getattr(self, 'mode', 'off') == 'heat':
                return 5.0 * self.heat_level
            elif getattr(self, 'mode', 'off') == 'cool':
                return -5.0 * self.heat_level
            return 0.0
        else:
            if self.is_on:
                return self.max_heat_output * self.heat_level
            return 0.0
    
    def get_render_data(self) -> dict:
        """
        Get visual data for rendering.
        
        Returns:
            dict with hotplate visual properties
        """
        # Color based on mode/state
        if getattr(self, 'mode', 'off') == 'heat':
            color = "#FF6666"
        elif getattr(self, 'mode', 'off') == 'cool':
            color = "#66A7FF"
        else:
            color = "#808080"
        
        hover_color = "#FFAA00" if not self.is_on else color
        if self.is_hovered:
            color = hover_color
        
        extra = {}
        if self.controller is not None:
            extra['controller_target_k'] = getattr(self.controller, 'target_k', None)

        return {
            'x': self.bounds['x'],
            'y': self.bounds['y'],
            'width': self.width,
            'height': self.height,
            'color': color,
            'border_color': "#404040",
            'border_width': 2,
            'label': self.label,
            'heat_level': self.heat_level,
            'is_on': self.is_on,
            'heat_output': self.get_heat_output(),
            'max_heat': self.max_heat_output
            , 'in_sidebar': getattr(self, 'in_sidebar', False), 'active': getattr(self, 'active', True)
        , **extra
        }
    
    def __repr__(self) -> str:
        state = "ON" if self.is_on else "OFF"
        return f"HotPlate({state}, level={self.heat_level:.0%}, output={self.get_heat_output():.1f}K/s)"
